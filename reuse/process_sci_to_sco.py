from transformers import AutoModelForSequenceClassification, AutoTokenizer
import json
import torch


def sequence_classification(sci, model_path, batch_size=8, sequence_max_length=512):
    """
    主函数: 使用mengzi模型对sci数据进行分类，返回带有分类结果的数据sco
    """

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=3)
    model.eval()
    model.to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    inputs = [s['text'] for s in sci]

    def predict_sequence_classification(inputs):
        outputs = []
        for i in range(0, len(sci), batch_size):
            batch = inputs[i:i + batch_size]
            input_ids = tokenizer(batch, padding="max_length", truncation=True, max_length=sequence_max_length, return_tensors="pt").input_ids
            input_ids = input_ids.to(device)
            logits = model(input_ids = input_ids).logits
            _, output = torch.max(logits, dim=1)
            output = output.cpu().numpy().tolist()
            outputs.extend(output)
        return outputs

    with torch.no_grad():
        outputs = predict_sequence_classification(inputs)
    sco = sci.copy()
    for i, output in enumerate(outputs):
        sco[i]["type"] = str(output)
    
    return sco




if __name__ == "__main__":
    sci_data = json.load(open("cache/sci.json", "r", encoding="utf-8"))
    sco_data = sequence_classification(sci_data, "../model/trained/encoder/mengzi_rule_filtering")
    json.dump(sco_data, open("cache/sco.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)



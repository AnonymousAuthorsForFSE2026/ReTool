import json
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextIteratorStreamer
from peft import PeftConfig, PeftModel
import torch
from tqdm import tqdm
import threading

max_new_tokens = 1024 * 2

def rule_formalization(fi, model_name_or_path, setting=None):
    if all([model not in model_name_or_path for model in ["llama2", "llama3", "qwen2", "internlm2", "glm4", 'qwen1.5', 'chatglm3']]):
        raise ValueError("模型类型错误，必须为llama2, llama3, qwen2, internlm2, glm4, qwen1.5, chatglm3之一，输入的模型为: " + model_name_or_path)
    device_map = "cuda:0" if torch.cuda.is_available() else "auto"
    print("### 任务: 规则抽取\n加载模型中...")

    if "lora" in model_name_or_path:
        bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
        peft_config = PeftConfig.from_pretrained(model_name_or_path)
        model = AutoModelForCausalLM.from_pretrained(peft_config.base_model_name_or_path, device_map=device_map, torch_dtype=torch.float16 if "glm4" not in model_name_or_path and "chatglm3" not in model_name_or_path else torch.float32, trust_remote_code=True, attn_implementation="flash_attention_2" if "glm4" not in model_name_or_path and "chatglm3" not in model_name_or_path else None, quantization_config=bnb_config)
        model = PeftModel.from_pretrained(model, model_name_or_path, device_map=device_map)
        model.eval()
        tokenizer = AutoTokenizer.from_pretrained(peft_config.base_model_name_or_path, use_fast=False, trust_remote_code=True)
    elif "ft" in model_name_or_path:
        model = AutoModelForCausalLM.from_pretrained(model_name_or_path, device_map=device_map, trust_remote_code=True, attn_implementation="flash_attention_2" if "glm4" not in model_name_or_path and "chatglm3" not in model_name_or_path else None, torch_dtype=torch.float16, return_dict=True)
        model.eval()
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=False, trust_remote_code=True)

    fo = fi.copy()
    print(f"加载模型完成，模型类型: {model.__class__.__name__}\n开始抽取规则...")

    def predict_rule_extraction(input_ids, repetition_penalty=1.0):
        generate_input = {
            "input_ids": input_ids,
            "max_new_tokens": max_new_tokens,
            "do_sample": False,
            "top_k": 50,
            "top_p": 1.0,
            "temperature": 1.0,
            "repetition_penalty": repetition_penalty
        }
        streamer = TextIteratorStreamer(tokenizer)
        generate_input['streamer'] = streamer
        thread = threading.Thread(target=model.generate, kwargs=generate_input)
        thread.start()
        output = ""
        for token in streamer:
            output += token
            print(token, end="", flush=True)
        print()
        thread.join()
        return output

    for rule in tqdm(fo):
        prompt = ""
        if "llama2" in model_name_or_path:
            prompt = f"<s>Human:给出一条规则，请你尽可能全面地将规则中的关键信息抽取出来。\n规则:{rule['text']}\n</s><s>Assistant:"
        elif "llama3" in model_name_or_path:
            prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n你是一个金融科技领域的专家。给出一条规则，请你抽取其中的规则元素并组合成R规则的形式。如果组合后的R规则存在冲突，则将其分成多条不冲突的R规则。<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n规则:{rule['text']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        elif "internlm2" in model_name_or_path:
            prompt = f"<s><|im_start|>system\n你是一个金融科技领域的专家。给出一条规则，请你抽取其中的规则元素并组合成R规则的形式。如果组合后的R规则存在冲突，则将其分成多条不冲突的R规则。<|im_end|>\n<|im_start|>user\n规则:{rule['text']}<|im_end|>\n<|im_start|>assistant\n"
        elif "qwen2" in model_name_or_path or "qwen1.5" in model_name_or_path:
            prompt = f"<|im_start|>system\n你是一个金融科技领域的专家。给出一条规则，请你抽取其中的规则元素并组合成R规则的形式。如果组合后的R规则存在冲突，则将其分成多条不冲突的R规则。<|im_end|>\n<|im_start|>user\n规则:{rule['text']}<|im_end|>\n<|im_start|>assistant\n"
        elif "glm4" in model_name_or_path:
            prompt = f"[gMASK]<sop><|system|>\n你是一个金融科技领域的专家。给出一条规则，请你抽取其中的规则元素并组合成R规则的形式。如果组合后的R规则存在冲突，则将其分成多条不冲突的R规则。<|user|>\n规则:{rule['text']}<|assistant|>\n"
        elif "chatglm3" in model_name_or_path:
            prompt = f"[gMASK]sop<|system|>\n你是一个金融科技领域的专家。给出一条规则，请你抽取其中的规则元素并组合成R规则的形式。如果组合后的R规则存在冲突，则将其分成多条不冲突的R规则。\n<|user|>\n规则:{rule['text']}\n<|assistant|>\n"
        
        
        if setting is not None:
            a, b = prompt.split("规则")
            s = "已知"
            if "market" in setting:
                s += f"交易市场：{setting['market']}，"
            if "variety" in setting:
                s += f"交易品种/业务：{setting['variety']}。\n"
            if len(s) > 2:
                prompt = a + s + "规则" + b

        with torch.no_grad():
            input_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).input_ids
            if torch.cuda.is_available():
                input_ids = input_ids.to('cuda')
            label = predict_rule_extraction(input_ids)
            repetition_penalty = 1.0
            while abs(max_new_tokens - len(label)) < 5:
                repetition_penalty += 0.1
                label = predict_rule_extraction(input_ids, repetition_penalty=repetition_penalty)
        rule['prediction'] = label

    return fo


if __name__ == "__main__":
    fi_data = json.load(open("cache/fi.json", "r", encoding="utf-8"))
    model_name_or_path = "../model/trained/glm4_lora"
    fo_data = rule_formalization(fi_data, model_name_or_path)
    json.dump(fo_data, open("cache/fo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)

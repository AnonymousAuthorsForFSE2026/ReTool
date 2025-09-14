import json
import os

def count(datas):
    if not datas:
        return 0
    if isinstance(datas[0], list):
        return sum(count(data) for data in datas)
    return len(datas)


if __name__ == "__main__":
    result = {"ours": {}, "glm-4": {}, "gpt-4": {}, "llm4fin": {}}
    for file in os.listdir("ours_result"):
        if "upd_testcase" not in file:
            continue
        datas = json.load(open(os.path.join("ours_result", file), "r", encoding="utf-8"))
        num = count(datas)
        result["ours"][file.split("_")[0]] = num
    for file in os.listdir("glm_result"):
        if "upd_testcase" not in file:
            continue
        datas = json.load(open(os.path.join("glm_result", file), "r", encoding="utf-8"))
        num = count(datas)
        result["glm-4"][file.split("_")[0]] = num
    for file in os.listdir("gpt_result"):
        if "upd_testcase" not in file:
            continue
        datas = json.load(open(os.path.join("gpt_result", file), "r", encoding="utf-8"))
        num = count(datas)
        result["gpt-4"][file.split("_")[0]] = num
    for file in os.listdir("llm4fin_result"):
        if "upd_testcase" not in file:
            continue
        datas = json.load(open(os.path.join("llm4fin_result", file), "r", encoding="utf-8"))
        num = count(datas)
        result["llm4fin"][file.split("_")[0]] = num
    
    print(result)
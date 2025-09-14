import json
from experiment.exp1.compute_acc import judge_same

gpt_change = {
    "dataset1": [],
    "dataset2": [],
    "dataset6": [],
    "dataset7": [],
    "dataset9": [],
    "dataset11": []
}

glm_change = {
    "dataset1": [],
    "dataset2": [],
    "dataset6": [],
    "dataset7": [],
    "dataset9": [],
    "dataset11": []
}

grok_change = {
    "dataset1": [],
    "dataset2": [],
    "dataset6": [],
    "dataset7": [],
    "dataset9": [],
    "dataset11": []
}


def generate_llm_change(ini_testcase, llm_testcase, index):
    for testcase in llm_testcase:
        if not isinstance(testcase, list):
            print(testcase)
    changes = []
    ini_testcase = [t for tc in ini_testcase for t in tc]
    llm_testcase = [t for tc in llm_testcase for t in tc]
    # 若case在init不在now，说明删掉；若case在now不在init，说明添加。修改被包含在其中（case不同）
    for it in ini_testcase:
        find = False
        for lt in llm_testcase:
            if judge_same(0, 0, it, lt):
                find = True
                break
        if not find:  # 被删掉
            ids = it['rule'].split(",")
            if index == 1 or index == 2:
                new_ids = []
                for id in ids:
                    id = ".".join(id.split(".")[:3])
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            elif index == 3 or index == 7:
                new_ids = []
                for id in ids:
                    id = ".".join(id.split(".")[:2])
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            elif index == 4 or index == 5:
                new_ids = []
                for id in ids:
                    id = id.split("条")[0] + "条"
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            elif index in [6, 8, 9, 10]:
                new_ids = []
                for id in ids:
                    id = id.split(".")[0]
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            elif index == 11:
                new_ids = []
                for id in ids:
                    id = ".".join(id.split(".")[:-2])
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            for id in ids:
                if id not in changes:
                    changes.append(id)
    
    for lt in llm_testcase:
        find = False
        for it in ini_testcase:
            if judge_same(0, 0, it, lt):
                find = True
                break
        if not find:  # 新增
            ids = lt['rule'].split(",")
            if index == 1 or index == 2:
                new_ids = []
                for id in ids:
                    id = ".".join(id.split(".")[:3])
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            elif index == 3 or index == 7:
                new_ids = []
                for id in ids:
                    id = ".".join(id.split(".")[:2])
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            elif index == 4 or index == 5:
                new_ids = []
                for id in ids:
                    id = id.split("条")[0] + "条"
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            elif index in [6, 8, 9, 10]:
                new_ids = []
                for id in ids:
                    id = id.split(".")[0]
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            elif index == 11:
                new_ids = []
                for id in ids:
                    id = ".".join(id.split(".")[:-2])
                    if id not in new_ids:
                        new_ids.append(id)
                ids = new_ids
            for id in ids:
                if id not in changes:
                    changes.append(id)
    
    return changes





if __name__ == "__main__":
    for i in [1, 2, 6, 7, 9, 11]:
        ini_testcase = json.load(open(f"data/dataset{i}_ini_testcase.json", "r", encoding="utf-8"))
        glm_testcase = json.load(open(f"glm_result/dataset{i}_upd_testcase.json", "r", encoding="utf-8"))
        gpt_testcase = json.load(open(f"gpt_result/dataset{i}_upd_testcase.json", "r", encoding="utf-8"))
        grok_testcase = json.load(open(f"grok_result/dataset{i}_upd_testcase.json", "r", encoding="utf-8"))

        glm_change[f"dataset{i}"] = generate_llm_change(ini_testcase, glm_testcase, i)
        gpt_change[f"dataset{i}"] = generate_llm_change(ini_testcase, gpt_testcase, i)
        grok_change[f"dataset{i}"] = generate_llm_change(ini_testcase, grok_testcase, i)

    json.dump(glm_change, open("glm_result/change.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    json.dump(gpt_change, open("gpt_result/change.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    json.dump(grok_change, open("grok_result/change.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
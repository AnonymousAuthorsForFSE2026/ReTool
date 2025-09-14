import json
import os
from nltk import edit_distance
import re
import argparse



threshold = 0.99

def compute_reuseable_testcase(change_file, ini_testcase_dir):
    """
    计算可重用的测试用例，读取change，从ini_testcase中删掉change中规则对应的用例，留下的就是可以重用的
    """
    reused_testcases, testcases = {}, {}
    change = json.load(open(change_file, "r", encoding="utf-8"))
    for dataset in sorted(list(change.keys())):
        changed_rule_ids = change[dataset]
        testcase = json.load(open(f"{ini_testcase_dir}/{dataset}_upd_testcase.json", "r", encoding="utf-8"))
        testcase = [t for tc in testcase for t in tc]
        reused_testcase = []
        for tc in testcase:
            tc_rule_ids = tc['rule'].split(",")
            find = False  # 判断tc是否可重用，即tc中是否为change_rule_ids中的规则的用例
            for changed_rule_id in changed_rule_ids:
                for tc_rule_id in tc_rule_ids:
                    if tc_rule_id.startswith(changed_rule_id) and (tc_rule_id == changed_rule_id or tc_rule_id[len(changed_rule_id)] == "."):
                        find = True
                        break
                if find:
                    break
            if not find:
                reused_testcase.append(tc)
        reused_testcases[dataset] = reused_testcase
        testcases[dataset] = testcase
    
    return reused_testcases, testcases



def str_same(s1, s2):
    """
    s1和s2的相似度大于threshold
    """
    if len(s1) == 0 or len(s2) == 0:
        return False
    return 1 - edit_distance(s1, s2) / max(len(s1), len(s2)) > threshold
    

def judge_same(t1, t2, strict):
    """
    t1和t2有threshold的元素相似，每个元素中value的相似度大于threshold
    """
    t1_keys, t1_values, t2_keys, t2_values = [], {}, [], {}
    for k, v in t1.items():
        if k == "testid" or k == "rule":
            continue
        # 将key结尾的数字去掉
        k = re.sub(r'\d+$', '', k)
        if k in t1_keys:
            t1_values[k].append(v)
        else:
            t1_keys.append(k)
            t1_values[k] = [v]
    for k, v in t2.items():
        if k == "testid" or k == "rule":
            continue
        k = re.sub(r'\d+$', '', k)
        if k in t2_keys:
            t2_values[k].append(v)
        else:
            t2_keys.append(k)
            t2_values[k] = [v]
    
    if not strict:
        # 模糊匹配法
        t1_like = 0
        for k1 in t1_keys:
            v1 = t1_values[k1]
            for k2 in t2_keys:
                v2 = t2_values[k2]
                if not str_same(k1, k2):
                    continue
                v1_like = 0
                for vi in v1:
                    for vj in v2:
                        if str_same(vi, vj):
                            v1_like += 1
                            break
                v1_like /= len(v1)
                if v1_like > threshold:
                    t1_like += 1
                    break
        return t1_like / len(t1_keys) > threshold
    else:
        t1_keys, t2_keys = sorted(t1_keys), sorted(t2_keys)
        if t1_keys != t2_keys:
            return False
        for k in t1_keys:
            if sorted(t1_values[k]) != sorted(t2_values[k]):
                return False
        return True

def compute_testcase_reuse_rate(new_testcases, reused_testcases, num_all_testcases):
    """
    计算复用率，复用率 = 重用的、正确的资源数 / 总资源数
    """
    testcases = json.load(open(new_testcases, "r", encoding="utf-8"))
    testcases = [t for tc in testcases for t in tc]
    accuracy = 0
    for reused_testcase in reused_testcases:
        for new_testcase in testcases:
            if judge_same(reused_testcase, new_testcase, strict=False):
                accuracy += 1
                break
    accuracy1 = 0
    for new_testcase in testcases:
        for reused_testcase in reused_testcases:
            if judge_same(reused_testcase, new_testcase, strict=True):
                accuracy1 += 1
                break
    recall = accuracy / num_all_testcases
    precision = accuracy1 / len(testcases)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1, len(testcases)


def compute_reuseable_scenario(change_file, ini_scenario_dir):
    """
    计算可重用的测试用例，读取change，从dataset1_ini_linked_scenario中删掉change中规则对应的场景，留下的就是可以重用的
    """
    reused_scenarios, scenarios = {}, {}
    change = json.load(open(change_file, "r", encoding="utf-8"))
    for dataset in sorted(list(change.keys())):
        changed_rule_ids = change[dataset]
        scenario = json.load(open(f"{ini_scenario_dir}/{dataset}_ini_linked_scenario.json", "r", encoding="utf-8"))
        reused_scenario = []
        for scen in scenario:
            find = False
            for rule in scen:
                rule_ids = rule['rule'].split(",")
                for changed_rule_id in changed_rule_ids:
                    for rule_id in rule_ids:
                        if rule_id.startswith(changed_rule_id) and (rule_id == changed_rule_id or rule_id[len(changed_rule_id)] == "."):
                            find = True
                            break
                    if find:
                        break
                if find:
                    break
            if not find:
                reused_scenario.append(scen)
        reused_scenarios[dataset] = reused_scenario
        scenarios[dataset] = scenario
    
    return reused_scenarios, scenarios


def judge_scenario_same(s1, s2):
    s1_keys, s1_values, s2_keys, s2_values = [], {}, [], {}
    for rule in s1:
        for condition in rule['conditions'] + rule['consequences']:
            if condition[0] in s1_keys:
                s1_values[condition[0]].append(condition[2])
            else:
                s1_keys.append(condition[0])
                s1_values[condition[0]] = [condition[2]]
    for rule in s2:
        for condition in rule['conditions'] + rule['consequences']:
            if condition[0] in s2_keys:
                s2_values[condition[0]].append(condition[2])
            else:
                s2_keys.append(condition[0])
                s2_values[condition[0]] = [condition[2]]
    
    s1_keys, s2_keys = sorted(s1_keys), sorted(s2_keys)
    for k in s1_keys:
        s1_values[k] = sorted(s1_values[k])
    for k in s2_keys:
        s2_values[k] = sorted(s2_values[k])
    
    s1_like = 0
    for k1 in s1_keys:
        v1 = s1_values[k1]
        for k2 in s2_keys:
            v2 = s2_values[k2]
            if not str_same(k1, k2):
                continue
            v1_like = 0
            for vi in v1:
                for vj in v2:
                    if str_same(vi, vj):
                        v1_like += 1
                        break
            v1_like /= len(v1)
            if v1_like > threshold:
                s1_like += 1
                break
    return s1_like / len(s1_keys) > threshold


def compute_scenario_reuse_rate(new_scenarios, reused_scenarios, num_all_scenarios):
    scenarios = json.load(open(new_scenarios, "r", encoding="utf-8"))
    accuracy = 0
    for reused_scenario in reused_scenarios:
        for new_scenario in scenarios:
            if judge_scenario_same(reused_scenario, new_scenario):
                accuracy += 1
                break
    accuracy1 = 0
    for new_scenario in scenarios:
        for reused_scenario in reused_scenarios:
            if judge_scenario_same(reused_scenario, new_scenario):
                accuracy1 += 1
                break
    precision = accuracy1 / len(scenarios)
    recall = accuracy / num_all_scenarios
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1, len(scenarios)






def compute_reuse_ours(d):
    result = {}
    reused_testcases, all_testcases = compute_reuseable_testcase("data/change.json", "data")
    reused_scenarios, all_scenarios = compute_reuseable_scenario("data/change.json", "data")
    for file in sorted(os.listdir("ours_result")):
        if "change" in file or "scenario" in file:
            continue
        if d not in file:
            continue
        dataset = file.split("_")[0]
        precision, recall, f1, num = compute_testcase_reuse_rate(f"ours_result/{file}", reused_testcases[dataset], len(all_testcases[dataset]))
        precision_scenario, recall_scenario, f1_scenario, num_sc = compute_scenario_reuse_rate(f"ours_result/{dataset}_upd_scenario.json", reused_scenarios[dataset], len(all_scenarios[dataset]))

        result[dataset] = {
            "testcase_reuse_rate_precision": precision,
            "testcase_reuse_rate_recall": recall,
            "testcase_reuse_rate_f1": f1,
            "testcase_max_reuse_rate_precision": len(reused_testcases[dataset]) / num ,
            "testcase_max_reuse_rate_recall": len(reused_testcases[dataset]) / len(all_testcases[dataset]),
            "testcase_max_reuse_rate_f1": 2 * (len(reused_testcases[dataset]) / num) * (len(reused_testcases[dataset]) / len(all_testcases[dataset])) / (len(reused_testcases[dataset]) / num + len(reused_testcases[dataset]) / len(all_testcases[dataset])),
            "scenario_reuse_rate_precision": precision_scenario,
            "scenario_reuse_rate_recall": recall_scenario,
            "scenario_reuse_rate_f1": f1_scenario,
            "scenario_max_reuse_rate_precision": len(reused_scenarios[dataset]) / num_sc,
            "scenario_max_reuse_rate_recall": len(reused_scenarios[dataset]) / len(all_scenarios[dataset]),
            "scenario_max_reuse_rate_f1": 2 * (len(reused_scenarios[dataset]) / num_sc) * (len(reused_scenarios[dataset]) / len(all_scenarios[dataset])) / (len(reused_scenarios[dataset]) / num_sc + len(reused_scenarios[dataset]) / len(all_scenarios[dataset]))
        }

    json.dump(result, open(f"log/ours_result_{d[:-1]}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)




def compute_reuse_glm(d):
    result = {}
    reused_testcases, all_testcases = compute_reuseable_testcase("data/change.json", "data")
    reused_scenarios, all_scenarios = compute_reuseable_scenario("data/change.json", "data")
    for file in sorted(os.listdir("glm_result")):
        if "change" in file or "scenario" in file:
            continue
        if d not in file:
            continue
        dataset = file.split("_")[0]
        precision, recall, f1, num = compute_testcase_reuse_rate(f"glm_result/{file}", reused_testcases[dataset], len(all_testcases[dataset]))
        precision_scenario, recall_scenario, f1_scenario, num_sc = compute_scenario_reuse_rate(f"glm_result/{dataset}_upd_scenario.json", reused_scenarios[dataset], len(all_scenarios[dataset]))

        # FIXME: 这个max_precision计算有问题，不能从重用率角度考虑问题，需要考虑真实重用/我们重用/我们正确重用的precision、recall、f1
        result[dataset] = {
            "testcase_reuse_rate_precision": precision,
            "testcase_reuse_rate_recall": recall,
            "testcase_reuse_rate_f1": f1,
            "testcase_max_reuse_rate_precision": len(reused_testcases[dataset]) / num ,
            "testcase_max_reuse_rate_recall": len(reused_testcases[dataset]) / len(all_testcases[dataset]),
            "testcase_max_reuse_rate_f1": 2 * (len(reused_testcases[dataset]) / num) * (len(reused_testcases[dataset]) / len(all_testcases[dataset])) / (len(reused_testcases[dataset]) / num + len(reused_testcases[dataset]) / len(all_testcases[dataset])),
            "scenario_reuse_rate_precision": precision_scenario,
            "scenario_reuse_rate_recall": recall_scenario,
            "scenario_reuse_rate_f1": f1_scenario,
            "scenario_max_reuse_rate_precision": len(reused_scenarios[dataset]) / num_sc,
            "scenario_max_reuse_rate_recall": len(reused_scenarios[dataset]) / len(all_scenarios[dataset]),
            "scenario_max_reuse_rate_f1": 2 * (len(reused_scenarios[dataset]) / num_sc) * (len(reused_scenarios[dataset]) / len(all_scenarios[dataset])) / (len(reused_scenarios[dataset]) / num_sc + len(reused_scenarios[dataset]) / len(all_scenarios[dataset]))
        }

    json.dump(result, open(f"log/glm_result_{d[:-1]}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)


def compute_reuse_gpt(d):
    result = {}
    reused_testcases, all_testcases = compute_reuseable_testcase("data/change.json", "data")
    reused_scenarios, all_scenarios = compute_reuseable_scenario("data/change.json", "data")
    for file in sorted(os.listdir("gpt_result")):
        if "change" in file or "scenario" in file:
            continue
        if d not in file:
            continue
        dataset = file.split("_")[0]
        precision, recall, f1, num = compute_testcase_reuse_rate(f"gpt_result/{file}", reused_testcases[dataset], len(all_testcases[dataset]))
        precision_scenario, recall_scenario, f1_scenario, num_sc = compute_scenario_reuse_rate(f"gpt_result/{dataset}_upd_scenario.json", reused_scenarios[dataset], len(all_scenarios[dataset]))

        result[dataset] = {
            "testcase_reuse_rate_precision": precision,
            "testcase_reuse_rate_recall": recall,
            "testcase_reuse_rate_f1": f1,
            "testcase_max_reuse_rate_precision": len(reused_testcases[dataset]) / num ,
            "testcase_max_reuse_rate_recall": len(reused_testcases[dataset]) / len(all_testcases[dataset]),
            "testcase_max_reuse_rate_f1": 2 * (len(reused_testcases[dataset]) / num) * (len(reused_testcases[dataset]) / len(all_testcases[dataset])) / (len(reused_testcases[dataset]) / num + len(reused_testcases[dataset]) / len(all_testcases[dataset])),
            "scenario_reuse_rate_precision": precision_scenario,
            "scenario_reuse_rate_recall": recall_scenario,
            "scenario_reuse_rate_f1": f1_scenario,
            "scenario_max_reuse_rate_precision": len(reused_scenarios[dataset]) / num_sc,
            "scenario_max_reuse_rate_recall": len(reused_scenarios[dataset]) / len(all_scenarios[dataset]),
            "scenario_max_reuse_rate_f1": 2 * (len(reused_scenarios[dataset]) / num_sc) * (len(reused_scenarios[dataset]) / len(all_scenarios[dataset])) / (len(reused_scenarios[dataset]) / num_sc + len(reused_scenarios[dataset]) / len(all_scenarios[dataset]))
        }

    json.dump(result, open(f"log/gpt_result_{d[:-1]}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)



def compute_reuse_grok(d):
    result = {}
    reused_testcases, all_testcases = compute_reuseable_testcase("data/change.json", "data")
    reused_scenarios, all_scenarios = compute_reuseable_scenario("data/change.json", "data")
    for file in sorted(os.listdir("grok_result")):
        if "change" in file or "scenario" in file:
            continue
        if d not in file:
            continue
        dataset = file.split("_")[0]
        precision, recall, f1, num = compute_testcase_reuse_rate(f"grok_result/{file}", reused_testcases[dataset], len(all_testcases[dataset]))
        precision_scenario, recall_scenario, f1_scenario, num_sc = compute_scenario_reuse_rate(f"grok_result/{dataset}_upd_scenario.json", reused_scenarios[dataset], len(all_scenarios[dataset]))

        result[dataset] = {
            "testcase_reuse_rate_precision": precision,
            "testcase_reuse_rate_recall": recall,
            "testcase_reuse_rate_f1": f1,
            "testcase_max_reuse_rate_precision": len(reused_testcases[dataset]) / num ,
            "testcase_max_reuse_rate_recall": len(reused_testcases[dataset]) / len(all_testcases[dataset]),
            "testcase_max_reuse_rate_f1": 2 * (len(reused_testcases[dataset]) / num) * (len(reused_testcases[dataset]) / len(all_testcases[dataset])) / (len(reused_testcases[dataset]) / num + len(reused_testcases[dataset]) / len(all_testcases[dataset])),
            "scenario_reuse_rate_precision": precision_scenario,
            "scenario_reuse_rate_recall": recall_scenario,
            "scenario_reuse_rate_f1": f1_scenario,
            "scenario_max_reuse_rate_precision": len(reused_scenarios[dataset]) / num_sc,
            "scenario_max_reuse_rate_recall": len(reused_scenarios[dataset]) / len(all_scenarios[dataset]),
            "scenario_max_reuse_rate_f1": 2 * (len(reused_scenarios[dataset]) / num_sc) * (len(reused_scenarios[dataset]) / len(all_scenarios[dataset])) / (len(reused_scenarios[dataset]) / num_sc + len(reused_scenarios[dataset]) / len(all_scenarios[dataset]))
        }

    json.dump(result, open(f"log/grok_result_{d[:-1]}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)






if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="dataset1")
    parser.add_argument("--method", type=str)
    args = parser.parse_args()
    dataset = args.dataset
    method = args.method
    if method == "ours":
        compute_reuse_ours(dataset)
    elif method == "gpt":
        compute_reuse_gpt(dataset)
    elif method == "glm":
        compute_reuse_glm(dataset)
    elif method == "grok":
        compute_reuse_grok(dataset)
    else:
        ...

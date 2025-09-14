import json

def count_changed_rule_testcase():
    change = json.load(open("data/change.json", "r", encoding="utf-8"))
    for i in range(1, 12):
        change_rules = change[f"dataset{i}"]
        scenarios = json.load(open(f"data/dataset{i}_ini_linked_scenario.json", "r", encoding="utf-8"))
        scenarios = [s for sc in scenarios for s in sc]
        testcases = json.load(open(f"data/dataset{i}_ini_testcase.json", "r", encoding="utf-8"))
        testcases = [t for tc in testcases for t in tc]
        change_testcases = []
        for testcase in testcases:
            rule_ids = testcase["rule"].split(",")
            for id in change_rules:
                find = False
                for rule_id in rule_ids:
                    if rule_id.startswith(id) and (rule_id == id or rule_id[len(id)] == "."):
                        change_testcases.append(testcase['testid'])
                        find = True
                        break
                if find:
                    break
        change_scenarios = []
        for scenario in scenarios:
            rule_ids = scenario['rule'].split(",")
            for id in change_rules:
                find = False
                for rule_id in rule_ids:
                    if rule_id.startswith(id) and (rule_id == id or rule_id[len(id)] == "."):
                        change_scenarios.append(scenario['rule'])
                        find = True
                        break
                if find:
                    break
        print(f"dataset{i}，测试场景数：{len(scenarios)}，测试用例数：{len(testcases)}，更新的规则数：{len(change_rules)}，受影响的测试场景数：{len(change_scenarios)}，受影响的测试用例数：{len(change_testcases)}")


if __name__ == "__main__":
    count_changed_rule_testcase()
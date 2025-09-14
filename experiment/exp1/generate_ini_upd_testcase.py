from reuse.generate_test_case import generate_test_case
import os
import json
import shutil


def generate_testcase_for_data():
    for file in sorted(os.listdir("data")):
        # if "rule" not in file or "upd" in file:
        if "rule" not in file:
            continue
        # if "dataset11" not in file:
        #     continue

        print(f"开始处理 {file}")
        generate_test_case("../../model/trained/mengzi_rule_filtering", "../../model/trained/glm4_lora_exp", "../../data/domain_knowledge/classification_knowledge.json", "../../data/domain_knowledge/knowledge.json", "cache/setting.json", f"data/{file}", "cache/sci.json", "cache/sco.json", "cache/fi.json", "cache/fo.json", "cache/r1.mydsl", "cache/r2.mydsl", "cache/r3.mydsl", "cache/testcase.json", skip_sc=True if any(x in file for x in ["dataset6", "dataset7", "dataset8", "dataset9", "dataset10"]) else False)

        testcases = json.load(open("cache/testcase.json", "r", encoding="utf-8"))
        json.dump(testcases, open(f"data/{file.split('.')[0][:-5]}_testcase.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        linked_scenario = json.load(open("cache/linked_scenario.json", "r", encoding="utf-8"))
        json.dump(linked_scenario, open(f"data/{file.split('.')[0][:-5]}_linked_scenario.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        fi = json.load(open("cache/fi.json", "r", encoding="utf-8"))
        testcases = [t for tc in testcases for t in tc]

        print(f"处理完成{file}，包含{len(fi)}条规则，{len(linked_scenario)}个需求场景，{len(testcases)}条测试用例")





def copy_files(src_dir, dest_dir):
    # 检查目标目录是否存在，如果不存在则创建
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # 遍历源目录
    for filename in os.listdir(src_dir):
        # 拼接完整的文件路径
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)
        
        # 检查这是一个文件还是目录
        if os.path.isfile(src_file):
            # 复制文件
            shutil.copy(src_file, dest_file)
        elif os.path.isdir(src_file):
            # 递归复制目录
            copy_files(src_file, dest_file)




if __name__ == "__main__":
    generate_testcase_for_data()
    copy_files("data", "../exp2/data")
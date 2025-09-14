import json
import os
import time
from reuse.update_testcase import update_testcase
from experiment.exp1.generate_ini_upd_testcase import copy_files


if __name__ == "__main__":
    all_files = [file for file in sorted(os.listdir("data")) if "rule" in file]
    for i in range(0, len(all_files), 2):
        ini_file = all_files[i]
        upd_file = all_files[i+1]
        if "dataset1" not in ini_file and "dataset2" not in ini_file and "dataset6" not in ini_file and "dataset7" not in ini_file and "dataset9" not in ini_file and "dataset11" not in ini_file:
            continue
        print(f"Processing {upd_file}...")
        begin_time = time.time()
        new_testcases, change, new_scenario = update_testcase(f"data/{ini_file}", f"data/{ini_file.split('.')[0][:-5]}_testcase.json", f"data/{upd_file}", "../../model/trained/mengzi_rule_filtering", "../../model/trained/glm4_lora_exp", "../../data/domain_knowledge/classification_knowledge.json", "../../data/domain_knowledge/knowledge.json", skip_sc = True if any(item in ini_file for item in ["dataset6", "dataset7", "dataset8", "dataset9", "dataset10"]) else False)

        json.dump(new_testcases, open(f"ours_result/{ini_file.split('.')[0][:-9]}_upd_testcase.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        json.dump(change, open(f"ours_result/{ini_file.split('_')[0]}_change.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        json.dump(new_scenario, open(f"ours_result/{ini_file.split('_')[0]}_upd_scenario.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        print(f"{upd_file} finished in {time.time()-begin_time} seconds")
    
    copy_files("ours_result", "../exp2/ours_result")
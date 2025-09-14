import json

datas = json.load(open("formalization_data.json", "r", encoding="utf-8"))
print(len(datas))
exit(0)
keys = {}


for data in datas:
    answer = data["answer"]
    for line in answer.split("\n"):
        if "if" in line or "then" in line:
            words = line.split(" ")[1:]
            for i in range(0, len(words), 4):
                if words[i] in keys:
                    keys[words[i]] += 1
                else:
                    keys[words[i]] = 1

from pprint import pprint

keys = sorted(keys.items(), key=lambda x: x[1], reverse=True)
pprint(keys)
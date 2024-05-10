import json
with open("evaluation.json", 'r') as file:
    evaluation = json.load(file)


for elems in evaluation["evaluations"]:
    print(elems["eval_score"])
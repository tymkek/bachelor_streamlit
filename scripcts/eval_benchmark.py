import json
with open("evaluation.json", 'r') as file:
    evaluation = json.load(file)

benchmark = {"q1": [], "q2": [], "q3": [], "q4": [], "q5": []}


benchmark["q1"].append(evaluation["evaluations"][0]["eval_score"])
benchmark["q2"].append(evaluation["evaluations"][1]["eval_score"])
benchmark["q3"].append(evaluation["evaluations"][2]["eval_score"])
benchmark["q4"].append(evaluation["evaluations"][3]["eval_score"])
benchmark["q5"].append(evaluation["evaluations"][4]["eval_score"])

print(benchmark)
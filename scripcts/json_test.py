import json

with open("sigma_questions.json", 'r') as file:
    questions = json.load(file)

for q in questions["questions"]:
    print(q["question"])
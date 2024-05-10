import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd
from collections import Counter

load_dotenv()
class EvalFunction():
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.article = open("../config/sigma.txt")
        self.article = self.article.read()
        with open("../config/sigma_benchmark.json", 'r') as file:
            self.questions = json.load(file)

        self.functions = [
            {
                "name": "evaluate_answers",
                "description": "Evaluates given answers on a scale: excellent, good, average, bad, very bad. Gives explanation for that decision.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "evaluations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties":{
                                    "question": {"type": "string", "description": "Question whose answer is being evaluated"},
                                    "answer": {"type": "string", "description": "Answer to that question"},
                                    "eval_score": {"type": "string", "description": "Evaluation score of that answer on a scale: excellent, good, average, bad, very bad"},
                                    "explanation": {"type": "string", "description": "Short explanation on evaluation"}
                                }
                            }
                        }
                    }
                }

            }
        ]
    def get_response(self):

        response = self.client.chat.completions.create(
        model = "gpt-4-1106-preview",
        messages = [
            {
                "role": "system",
                "content": "You will be given, a text, json file with questions and answers to that text. Evaluate each answer on a scale: excellent, good, average, bad, very bad"
            },
            {
                "role": "user",
                "content": f"Text{self.article}, questions with answers in JSON format {self.questions}"
            }
            ],
                functions = self.functions,
                function_call={
                "name": "evaluate_answers"
                }
            )

        arguments = response.choices[0].message.function_call.arguments
        json_obj = json.loads(arguments)
        return json_obj
    
    def benchmark(self, n):
        result = {self.questions["questions"][0]["answer"]: [],
                  self.questions["questions"][1]["answer"]: [],
                  self.questions["questions"][2]["answer"]: [],
                  self.questions["questions"][3]["answer"]: [],
                  self.questions["questions"][4]["answer"]: []}
        
        
        
        for i in range(n):
            evaluation = self.get_response()
            for evals in evaluation["evaluations"]:
                result[evals["answer"]].append(evals["eval_score"])
        
        for key, value in result.items():
            print(key, Counter(value))

        with open('output_file.json', 'w') as file:
            json.dump(result, file, indent=4) 
        

eval_fun = EvalFunction()
eval_fun.benchmark(10)
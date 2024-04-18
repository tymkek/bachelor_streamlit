import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
article = open("../files/books.txt")
article = article.read()
with open("../files/books_questions", 'r') as file:
    questions = json.load(file)

with open("answers.json", "r") as file:
    answers = json.load(file)

functions = [
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

response = client.chat.completions.create(
    model = "gpt-4-1106-preview",
    messages = [
        {
            "role": "system",
            "content": "You will be given, a text, questions to that text and answers to those questions. Evaluate each question on a scale: excellent, good, average, bad, very bad"
        },
        {
            "role": "user",
            "content": f"Text{article}, questions in JSON format {questions}, answers in JSON format{answers}"
        }
    ],
    functions = functions,
    function_call={
        "name": "evaluate_answers"
    }
)

arguments = response.choices[0].message.function_call.arguments
json_obj = json.loads(arguments)

with open("evaluation.json", "w") as file:
    json.dump(json_obj, file)

print(json_obj)
import ast
from openai import OpenAI

def get_gpt_response(prompt):
    with open("api_key.txt", "r") as f:
        api_key = f.read()

    client = OpenAI(api_key=api_key)

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "Give a two-line description about this situation. Assume that I am not a medical professional and have no prior training."},
            {"role": "user", "content": prompt}
        ]
    )

    return chat_completion.choices[0].message.content

def create_medical_json(input_string, filename):
    with open(filename, "r") as file:
        data = file.read()
        medical_instructions = ast.literal_eval(data)

    data = {
        "condition": input_string,
        "instructions": medical_instructions[input_string]['instructions'],
        "videoUrl": medical_instructions[input_string]['video_link']
    }

    return data

def create_unknown_medical_json(input_string):
    data = {
        "condition": input_string,
        "instructions": get_gpt_response(input_string)
    }

    return data
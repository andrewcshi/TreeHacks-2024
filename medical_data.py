import json
from openai import OpenAI
import os

def get_gpt_response(prompt):
    api_key = os.getenv('TOGETHER_API_KEY')

    client = OpenAI(
        api_key=api_key, 
        base_url='https://api.together.xyz'
    )

    chat_completion = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[
            {"role": "system", "content": "Give a two-line description about this situation. Assume that I am not a medical professional and have no prior training."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        stop=["Prompt", "\n", "."]
    )

    return chat_completion.choices[0].message.content

def create_medical_json(input_string, medical_filename, timestamps_filename):
    with open(medical_filename, "r") as file:
        medical_instructions = json.load(file)

    with open(timestamps_filename, "r") as file:
        timestamps_data = json.load(file)

    data = {
        "condition": input_string,
        "instructions": medical_instructions[input_string]['instructions'],
        "videoUrl": medical_instructions[input_string]['video_link'],
        "videoTimestamps": timestamps_data[input_string] if input_string in timestamps_data else None
    }

    return data

def create_unknown_medical_json(input_string):
    data = {
        "condition": input_string,
        "instructions": get_gpt_response(input_string)
    }

    return data
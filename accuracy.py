import ast
import json
from openai import OpenAI

prepend = "Identify the medical condition described in the following voice-to-text translation: "
postpend = "Choose from one of the following conditions: Cardiac Arrest, Stroke, Anaphylaxis, Asthma, Seizure, Choking, Deep Cut, Burn. Again, choose "\
                "only from the list of conditions I provided you and no external sources. You must choose one of the conditions provided. Return just the medical condition "\
                "and no other words. Your response should be one word, or in the case of Cardiac Arrest, two words."

def get_gpt_response(prompt):
    with open("api_key.txt", "r") as f:
        api_key = f.read()

    client = OpenAI(api_key=api_key)

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Provide output in valid JSON."},
            {"role": "user", "content": prepend + prompt + postpend}
        ]
    )

    # Assuming the API returns a JSON response, extract and return the content
    return chat_completion.choices[0].message.content

def calculate_accuracy(filename):
    with open(filename, "r") as file:
        data = file.read()
        dictionary = ast.literal_eval(data)

    for key in dictionary:
        num_correct = 0
        total = 0
        for description in dictionary[key]:
            gpt_response = get_gpt_response(description)
            print(gpt_response)
            if key.lower() in gpt_response.lower():
                num_correct += 1
            total += 1
        print(f"Accuracy for {key}: {num_correct / total}")

calculate_accuracy('conditions.txt')
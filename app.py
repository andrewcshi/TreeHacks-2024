from flask import Flask, request, jsonify
import os
from openai import OpenAI
from medical_data import create_medical_json, create_unknown_medical_json

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the GPT API Output Server!"

##### TRAINING ASSISTANCE #####

def get_condition_info(prompt):
    return create_medical_json(prompt, "medical_instructions.json", "timestamps.json")

@app.route('/training', methods=['POST'])
def get_training_output():
    data = request.get_json()
    prompt = data.get('prompt')
    return get_condition_info(prompt)

##### EMERGENCY ASSISTANCE #####

prepend = "Identify the medical condition described in the following voice-to-text translation: "\
            "The condition is going to describe one and only one of the following categories of medical conditions: Cardiac Arrest, "\
            "Anaphylaxia, Asthma, Seizure, Choking, Deep Cut, Burn. Return one term, no more. Do not return me a list of multiple possible conditions "\
            "or any other text in your response. If the medical condition described does not fit into these three categories, return the following text exactly: \"General First Aid Care\" "\
            "Do not return any other values aside from this list I provided, or the text \"General First Aid Care\"."\
            "Remember, you are not allowed to return anything other than one of the elements in this list: [Cardiac Arrest, Anaphylaxis, Asthma, Seizure, Choking, Deep Cut, Burn, General First Aid Care]"\
            "Prompt: The person won't respond when I tap their shoulders; they're just lying there unresponsive."\
            "Response: Cardiac Arrest"\
            "Prompt: They're breathing really fast, it looks like they're struggling with every breath."\
            "Response: Asthma"\
            "Prompt: They mentioned feeling really tired and weak just before this happened."\
            "Response: Fatigue"\
            "Prompt: They're experiencing a rapid heartbeat, saying it feels like it's racing."\
            "Response: Hypoglycemia"\
            "Prompt: They're a little tired today and low in energy."\
            "Response: General First Aid Care"\
            "Prompt: "
            
postpend = "Response: "
            
known_conditions = ["Cardiac Arrest", "Anaphylaxis", "Asthma", "Seizure", "Choking", "Deep Cut", "Burn", "General First Aid Care"]

chat_history = []

@app.route('/chat_history', methods=['DELETE'])
def clear_history():
    global chat_history
    chat_history = []
    return chat_history

@app.route('/assist', methods=['POST'])
def get_gpt_output():
    if request.is_json:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if prompt:
            gpt_response = get_gpt_response(prompt)
            return jsonify({"status": "success", "data": gpt_response}), 200
        else:
            return jsonify({"status": "error", "message": "No prompt provided"}), 400
    else:
        return jsonify({"status": "error", "message": "Request body must be JSON"}), 400

def get_gpt_response(prompt):
    api_key = os.getenv('TOGETHER_API_KEY')
    
    client = OpenAI(
        api_key=api_key, 
        base_url='https://api.together.xyz'
    )

    messages = []
    if len(messages) == 0:
        messages = chat_history + [
            {"role": "system", "content": "Please only return one or two words in your response."},
            {"role": "user", "content": prepend + prompt + postpend}
        ]
    else:
        messages = chat_history + [
            {"role": "system", "content": "Please respond to the prompt."},
            {"role": "user", "content": prompt}
        ]

    chat_completion = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=messages,
        temperature=0.0,
        stop=["Prompt", "\n", "."]
    )

    chat_history.extend([
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": chat_completion.choices[0].message.content}
    ])
    
    medical_condition =  chat_completion.choices[0].message.content.strip()
    medical_condition = "General First Aid Care" if medical_condition not in known_conditions else medical_condition
    return create_medical_json(medical_condition, "medical_instructions.json", "timestamps.json")

if __name__ == '__main__':
    app.run(debug=True)

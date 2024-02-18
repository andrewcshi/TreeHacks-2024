from flask import Flask, request, jsonify
from openai import OpenAI
from medical_data import create_medical_json, create_unknown_medical_json

app = Flask(__name__)

# Route to display a simple message at the root
@app.route('/')
def home():
    return "Welcome to the GPT API Output Server!"

##### TRAINING ASSISTANCE #####

def get_condition_info(prompt):
    return create_medical_json(prompt, "medical_instructions.txt")

@app.route('/training_output', methods=['POST'])
def get_training_output():
    data = request.get_json()
    prompt = data.get('prompt')
    return get_condition_info(prompt)

##### EMERGENCY ASSISTANCE #####

prepend = "Identify the condition described in the following voice-to-text translation: "
postpend = "If it matches any one of these following conditions -- Cardiac Arrest, Anaphylaxis, Asthma, "\
                "Seizure, Choking, Deep Cut, Burn -- return just the medical condition "\
                "and no other words. In this case, your response should be one or two words."\
                "If the condition is "\
                "a medical condition not listed above, return a maximum of five key words describing the medical condition "\
                "Assume that I am not a medical professional and have no prior training. "\
                "If the condition is not medical, simply return the two words \"Not Medical\"."
known_conditions = ["Cardiac Arrest", "Anaphylaxis", "Asthma", "Seizure", "Choking", "Deep Cut", "Burn"]

@app.route('/get_gpt_output', methods=['POST'])
def get_gpt_output():
    if request.is_json:
        # Extract the prompt from the incoming JSON request
        data = request.get_json()
        prompt = data.get('prompt')
        
        if prompt:
            # Call the function and get the GPT-3 response
            gpt_response = get_gpt_response(prompt)
            return jsonify({"status": "success", "data": gpt_response}), 200
        else:
            return jsonify({"status": "error", "message": "No prompt provided"}), 400
    else:
        return jsonify({"status": "error", "message": "Request body must be JSON"}), 400

def get_gpt_response(prompt):
    with open("api_key.txt", "r") as f:
        api_key = f.read()

    client = OpenAI(api_key=api_key)

    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Please analyze the prompt I provide."},
            {"role": "user", "content": prepend + prompt + postpend}
        ]
    )
    
    medical_condition =  chat_completion.choices[0].message.content
    if medical_condition in known_conditions:
        return create_medical_json(medical_condition, "medical_instructions.txt")
    else:
        return create_unknown_medical_json(medical_condition)

if __name__ == '__main__':
    app.run(debug=True)

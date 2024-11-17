from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)
CORS(app)

# Load the pre-trained DialoGPT model
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Track conversation history
chat_history = []

@app.route('/chat', methods=['POST'])
def chat():
    global chat_history  # Keep track of the conversation
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Add the user's message to the chat history
        chat_history.append({"role": "user", "content": user_message})

        # Format the history for input to the model
        formatted_history = ""
        for entry in chat_history:
            formatted_history += f"{entry['role']}: {entry['content']} {tokenizer.eos_token}"

        # Tokenize and generate response
        input_ids = tokenizer.encode(formatted_history, return_tensors="pt")
        # attention_mask = (input_ids != tokenizer.pad_token_id).to(torch.int64) 
        chat_history_ids = model.generate(input_ids, max_length=500, pad_token_id=tokenizer.eos_token_id)

        # Decode and save the response
        response = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        chat_history.append({"role": "assistant", "content": response})

        return jsonify({"reply": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

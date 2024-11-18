from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = Flask(__name__)
CORS(app)

# Load the pre-trained GPT-2 model and tokenizer
model_name = "gpt2"  # GPT-2 model (you can try gpt2-medium or gpt2-large for better performance)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Custom response generation: add a company-specific prompt to guide GPT-2 responses
company_prompt = "You are a customer support agent for NextGenSoftware technology company. Your job is to assist users with their software-related issues, explain features, payments, services, availability, and help them navigate the platform. Be polite and professional in your responses."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Format the input for the model with company-specific context and the user message
        input_text = company_prompt + "\n" + user_message + "\n"

        # Tokenize the input text
        input_ids = tokenizer.encode(input_text, return_tensors="pt")

        # Generate a response based on the input with controlled length and diversity
        chat_history_ids = model.generate(
            input_ids,
            max_length=150,  # Limit the response length
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=2,  # Prevent repeating n-grams
            temperature=0.7,  # Control creativity, lower values are more focused
            top_p=0.9,  # Nucleus sampling, higher values make output more diverse
            top_k=50  # Limits sampling to top-k tokens for diversity
        )

        # Decode the response and remove special tokens
        response = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

        # Return the response
        return jsonify({"reply": response.strip()})  # Strip any unwanted leading/trailing spaces

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

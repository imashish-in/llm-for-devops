from flask import Flask, request, jsonify
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load model with transformers
model = None
tokenizer = None

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    
    logger.info("Attempting to load DialoGPT-medium model with transformers...")
    
    # Use DialoGPT-medium model (open access, no authentication required)
    model_name = "microsoft/DialoGPT-medium"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Add padding token if not present
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    logger.info("DialoGPT-medium model loaded successfully!")
    
except Exception as e:
    logger.error(f"Failed to load DialoGPT-medium model: {e}")
    raise e

@app.route("/health", methods=["GET"])
def health():
    if model is not None:
        return jsonify({"status": "healthy", "message": "DialoGPT-medium model is loaded and ready"})
    else:
        return jsonify({"status": "unhealthy", "error": "No model loaded"}), 500

@app.route("/generate", methods=["POST"])
def generate():
    try:
        prompt = request.json.get("prompt", "")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        if model is not None:
            logger.info(f"Generating response for prompt: {prompt[:50]}...")
            
            # Encode the input
            inputs = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt", max_length=1024, truncation=True)
            attention_mask = torch.ones_like(inputs)
            
            # Generate response with better parameters
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_new_tokens=256,  # Allow up to 256 new tokens
                    num_return_sequences=1,
                    temperature=0.8,  # Slightly higher temperature for more creative responses
                    do_sample=True,
                    top_p=0.9,  # Add nucleus sampling
                    top_k=50,   # Add top-k sampling
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    repetition_penalty=1.1  # Prevent repetitive responses
                )
            
            # Decode the response
            full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated response (remove the input prompt)
            response = full_response[len(prompt):].strip()
            
            # Clean up any remaining special tokens
            response = response.replace("<|endoftext|>", "").replace("<|eot_id|>", "").strip()
            
            # If response is empty or too short, try a different approach
            if not response or len(response) < 5:
                # Try with a simpler generation approach
                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        attention_mask=attention_mask,
                        max_new_tokens=128,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id,
                        eos_token_id=tokenizer.eos_token_id
                    )
                
                full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = full_response[len(prompt):].strip()
            
            logger.info("Response generated successfully")
            return jsonify({"response": response})
        else:
            return jsonify({"error": "Model not loaded"}), 500
            
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

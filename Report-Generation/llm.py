from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, logging
import tensorflow as tf

# Flask app initialization
app = Flask(__name__)

# ------------------ GPU Configurations ------------------

# Enable TensorFlow GPU memory growth (prevents full allocation at startup)
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("TensorFlow memory growth enabled.")
    except RuntimeError as e:
        print(f"Error enabling memory growth: {e}")

# ------------------ Model Loading ------------------

# Choose the model
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"

# Load tokenizer and model with optimizations
print("Loading model...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",  # Automatically use available GPU
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,  # Mixed precision
    )
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# ------------------ Routes ------------------

# Function to parse metrics from input strings
def parse_metric(metric):
    try:
        # Strip curly braces and split by commas to parse values
        return [float(x.strip()) for x in metric.strip('{}').split(',')]
    except ValueError as e:
        logging.error(f"Error parsing metric {metric}: {e}")
        return []

@app.route("/generate", methods=["POST"])
def generate_text():
    """
    Generate a detailed environmental report based on query parameters and metrics.
    """
    # Retrieve query parameters
    country = request.args.get("country")
    aqi = request.args.get("aqi")
    pm25 = request.args.get("pm25")
    pm10 = request.args.get("pm10")
    so2 = request.args.get("so2")
    o3 = request.args.get("o3")

    #Parse metrics
    aqi = parse_metric(aqi)
    pm25 = parse_metric(pm25)
    pm10 = parse_metric(pm10)
    so2 = parse_metric(so2)
    o3 = parse_metric(o3)

    # Construct the prompt for the model
    prompt = f"""
    You are an environmental data analyst. Based on the following data for {country} and the list of predictions for the following year, generate a detailed report in a paragraph form:

    - Air Quality Index (AQI): {aqi}
    - PM2.5 (Particulate Matter 2.5): {pm25}
    - PM10 (Particulate Matter 10): {pm10}
    - Sulfur Dioxide (SO2): {so2}
    - Ozone (O3): {o3}

    Provide an interpretation of these metrics, explain the air quality status for the next year, and offer recommendations or insights based on the given values. Include a summary of the potential environmental impact on health for that month and any relevant context based on typical levels for each pollutant.
    """

    try:
        # Generate the report using the model
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
        output = model.generate(
            input_ids, 
            max_length=1500, 
            temperature=0.7, 
            num_return_sequences=1
        )

        # Decode and return the generated text
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        generated_text=generated_text[len(prompt):]
        return jsonify({
            "Report": generated_text
        })

    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return jsonify({"error": str(e)}), 500

# ------------------ Main ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

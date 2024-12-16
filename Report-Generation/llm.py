import logging
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Load model and tokenizer
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

def parse_metric(metric):
    if metric:
        try:
            return [float(x.strip()) for x in metric.strip('{}').split(',')]
        except ValueError as e:
            logging.error(f"Error parsing metric {metric}: {e}")
            return []
    return []

@app.route('/generate', methods=['POST'])
def generate_text():
    # Retrieve query parameters
    country = request.args.get('country')
    month = request.args.get('month')
    aqi = request.args.get('aqi')
    pm25 = request.args.get('pm25')
    pm10 = request.args.get('pm10')
    no2 = request.args.get('no2')
    so2 = request.args.get('so2')
    o3 = request.args.get('o3')

    try:
        month = int(month)
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Parse metrics
    aqi = parse_metric(aqi)
    pm25 = parse_metric(pm25)
    pm10 = parse_metric(pm10)
    no2 = parse_metric(no2)
    so2 = parse_metric(so2)
    o3 = parse_metric(o3)

    # Prepare data for the specified month
    data_for_month = {
        "aqi": aqi[month - 1],
        "pm25": pm25[month - 1],
        "pm10": pm10[month - 1],
        "no2": no2[month - 1],
        "so2": so2[month - 1],
        "o3": o3[month - 1]
    }

    # Construct the prompt for the model
    prompt = f"""
    You are an environmental data analyst. Based on the following data for {country} in month {month}, generate a detailed report:

    - Air Quality Index (AQI): {data_for_month["aqi"]}
    - PM2.5 (Particulate Matter 2.5): {data_for_month["pm25"]}
    - PM10 (Particulate Matter 10): {data_for_month["pm10"]}
    - Nitrogen Dioxide (NO2): {data_for_month["no2"]}
    - Sulfur Dioxide (SO2): {data_for_month["so2"]}
    - Ozone (O3): {data_for_month["o3"]}

    Provide an interpretation of these metrics, explain the air quality status for the month, and offer recommendations or insights based on the given values. Include a summary of the potential environmental impact on health for that month and any relevant context based on typical levels for each pollutant.
    """

    # Generate Report
    try:
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(inputs["input_ids"], max_length=3000)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        logging.error(f"Error during text generation: {e}")
        return jsonify({"error": "Failed to generate text"}), 500

    return jsonify({"generated_text": result})

if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)
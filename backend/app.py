from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from prophet import Prophet
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API is working"

@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        file = request.files['file']
        df = pd.read_csv(file)

        # VALIDATION
        if 'Year' not in df.columns or 'Total_Enrollees' not in df.columns:
            return jsonify({"error": "Dataset must contain Year and Total_Enrollees"}), 400

        if not pd.api.types.is_numeric_dtype(df['Year']) or not pd.api.types.is_numeric_dtype(df['Total_Enrollees']):
            return jsonify({"error": "Columns must be numeric"}), 400

        # PREPARE DATA
        df['ds'] = pd.to_datetime(df['Year'], format='%Y')
        df['y'] = df['Total_Enrollees']

        # MODEL
        model = Prophet()
        model.fit(df[['ds','y']])

        future = model.make_future_dataframe(periods=3, freq='YE')
        forecast = model.predict(future)

        latest = forecast.iloc[-1]
        total = int(latest['yhat'])

        # RESOURCE ALLOCATION
        academic_rooms = int((total * 0.65) / 40)
        tvl_rooms = int((total * 0.35) / 40)

        return jsonify({
            "year": str(latest['ds'])[:4],
            "enrollees": total,
            "academic_rooms": academic_rooms,
            "tvl_rooms": tvl_rooms,
            "academic_teachers": academic_rooms,
            "tvl_teachers": tvl_rooms
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from prophet import Prophet
import os

app = Flask(__name__)
CORS(app)  # allow frontend to fetch data

# ✅ ROOT route (test)
@app.route('/')
def home():
    return "✅ NCR Forecast API is running"

# ✅ FORECAST route
@app.route('/forecast', methods=['POST', 'GET'])
def forecast():
    if request.method == 'GET':
        return "⚠️ Use POST method with a CSV file to get forecast."

    try:
        # Check if file exists
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        df = pd.read_csv(file)

        # Validate required columns
        required_cols = ['Year', 'Total_Enrollees']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({"error": f"Missing column: {col}"}), 400

        # Validate numeric types
        if not pd.api.types.is_numeric_dtype(df['Year']):
            return jsonify({"error": "Year must be numeric"}), 400
        if not pd.api.types.is_numeric_dtype(df['Total_Enrollees']):
            return jsonify({"error": "Total_Enrollees must be numeric"}), 400

        # Prepare data for Prophet
        df['ds'] = pd.to_datetime(df['Year'], format='%Y')
        df['y'] = df['Total_Enrollees']

        model = Prophet()
        model.fit(df[['ds', 'y']])

        future = model.make_future_dataframe(periods=3, freq='YE')
        forecast_df = model.predict(future)

        latest = forecast_df.iloc[-1]
        total = int(latest['yhat'])

        # Resource allocation
        academic_rooms = int((total * 0.65) / 40)
        tvl_rooms = int((total * 0.35) / 40)

        result = {
            "year": str(latest['ds'])[:4],
            "enrollees": total,
            "academic_rooms": academic_rooms,
            "tvl_rooms": tvl_rooms,
            "academic_teachers": academic_rooms,
            "tvl_teachers": tvl_rooms
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Run Render-ready
if __name__ == "__main__":
    port = int(os.environ["10000"])  # 🔥 must use Render-provided PORT
    app.run(host='0.0.0.0', port=port)

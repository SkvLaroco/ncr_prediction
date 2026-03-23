from flask import Flask, request, jsonify
import pandas as pd
from prophet import Prophet

app = Flask(__name__)

@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        file = request.files['file']
        df = pd.read_csv(file)

        # Validate
        if 'Year' not in df.columns or 'Total_Enrollees' not in df.columns:
            return jsonify({"error": "Invalid dataset format"}), 400

        df['ds'] = pd.to_datetime(df['Year'], format='%Y')
        df['y'] = df['Total_Enrollees']

        model = Prophet()
        model.fit(df[['ds','y']])

        future = model.make_future_dataframe(periods=3, freq='YE')
        forecast = model.predict(future)

        latest = forecast.iloc[-1]

        result = {
            "year": str(latest['ds'])[:4],
            "enrollees": int(latest['yhat']),
            "academic_rooms": int((latest['yhat'] * 0.65)/40),
            "tvl_rooms": int((latest['yhat'] * 0.35)/40)
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.run(host='0.0.0.0', port=10000)
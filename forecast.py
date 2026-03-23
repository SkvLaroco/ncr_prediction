import pandas as pd
from prophet import Prophet
import sys

try:
    # Load dataset
    df = pd.read_csv("NCR_Total_Enrollees.csv")

    # Validate columns
    required_cols = ['Year', 'Total_Enrollees']
    for col in required_cols:
        if col not in df.columns:
            raise Exception(f"Missing required column: {col}")

    # Prepare data
    df['Date'] = pd.to_datetime(df['Year'], format='%Y')
    df = df[['Date', 'Total_Enrollees']]
    df = df.rename(columns={'Date': 'ds', 'Total_Enrollees': 'y'})

    # Train model
    model = Prophet()
    model.fit(df)

    # Forecast next 3 years
    future = model.make_future_dataframe(periods=3, freq='YE')
    forecast = model.predict(future)

    # ===============================
    # RESOURCE ALLOCATION
    # ===============================
    CLASS_SIZE = 40
    ACADEMIC_RATIO = 0.65
    TVL_RATIO = 0.35

    forecast['Academic_Students'] = forecast['yhat'] * ACADEMIC_RATIO
    forecast['TVL_Students'] = forecast['yhat'] * TVL_RATIO

    forecast['Academic_Classrooms'] = forecast['Academic_Students'] / CLASS_SIZE
    forecast['TVL_Classrooms'] = forecast['TVL_Students'] / CLASS_SIZE

    forecast['Academic_Teachers'] = forecast['Academic_Classrooms']
    forecast['TVL_Teachers'] = forecast['TVL_Classrooms']

    # Final output
    forecast_output = forecast[['ds', 'yhat',
                                'Academic_Classrooms', 'TVL_Classrooms',
                                'Academic_Teachers', 'TVL_Teachers']].copy()

    forecast_output = forecast_output.round(0)

    # Save CSV
    forecast_output.to_csv("forecast.csv", index=False)

    # ===============================
    # PDF REPORT
    # ===============================
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    doc = SimpleDocTemplate("forecast_report.pdf")
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("NCR SHS Enrollment Forecast Report", styles['Title']))
    elements.append(Spacer(1, 12))

    latest = forecast_output.iloc[-1]

    elements.append(Paragraph(f"Year: {str(latest['ds'])[:4]}", styles['Normal']))
    elements.append(Paragraph(f"Projected Enrollees: {int(latest['yhat'])}", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Resource Allocation:", styles['Heading2']))
    elements.append(Paragraph(f"Academic Classrooms: {int(latest['Academic_Classrooms'])}", styles['Normal']))
    elements.append(Paragraph(f"TVL Classrooms: {int(latest['TVL_Classrooms'])}", styles['Normal']))
    elements.append(Paragraph(f"Academic Teachers: {int(latest['Academic_Teachers'])}", styles['Normal']))
    elements.append(Paragraph(f"TVL Teachers: {int(latest['TVL_Teachers'])}", styles['Normal']))

    doc.build(elements)

    print("SUCCESS: Forecast and PDF generated.")

except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
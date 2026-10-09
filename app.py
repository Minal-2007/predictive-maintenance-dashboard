
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px

st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    page_icon="⚙️",
    layout="wide"
)

@st.cache_resource
def load_artifacts():
    model = joblib.load("best_model.pkl")
    scaler = joblib.load("scaler.pkl")
    return model, scaler

st.title("⚙️ Predictive Health Maintenance Dashboard")
st.write(
    "Predict potential machine failure using operating conditions."
)

try:
    model, scaler = load_artifacts()
except Exception as e:
    st.error(f"Unable to load model or scaler: {e}")
    st.info(
        "Ensure best_model.pkl and scaler.pkl are in the same folder as app.py."
    )
    st.stop()

st.sidebar.header("Machine Parameters")

air_temp = st.sidebar.number_input(
    "Air temperature (K)", min_value=250.0,
    max_value=350.0, value=300.0
)

process_temp = st.sidebar.number_input(
    "Process temperature (K)", min_value=250.0,
    max_value=400.0, value=310.0
)

rot_speed = st.sidebar.number_input(
    "Rotational speed (rpm)", min_value=0,
    max_value=5000, value=1500
)

torque = st.sidebar.number_input(
    "Torque (Nm)", min_value=0.0,
    max_value=150.0, value=40.0
)

tool_wear = st.sidebar.number_input(
    "Tool wear (min)", min_value=0,
    max_value=300, value=100
)

if st.button("Predict Machine Health", type="primary"):
    input_df = pd.DataFrame([{
        "Air temperature [K]": air_temp,
        "Process temperature [K]": process_temp,
        "Rotational speed [rpm]": rot_speed,
        "Torque [Nm]": torque,
        "Tool wear [min]": tool_wear
    }])

    try:
        scaled_input = scaler.transform(input_df)
        prediction = model.predict(scaled_input)[0]

        st.subheader("Prediction Result")

        if prediction == 1:
            st.error("⚠️ Potential machine failure detected!")
        else:
            st.success("✅ No failure predicted for these conditions.")

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(scaled_input)[0]
            classes = list(model.classes_)

            if 1 in classes:
                failure_probability = probabilities[classes.index(1)]
                st.metric(
                    "Estimated Failure Probability",
                    f"{failure_probability * 100:.2f}%"
                )

                chart_df = pd.DataFrame({
                    "Outcome": ["No Failure", "Failure"],
                    "Probability (%)": [
                        (1 - failure_probability) * 100,
                        failure_probability * 100
                    ]
                })

                fig = px.bar(
                    chart_df,
                    x="Outcome",
                    y="Probability (%)",
                    title="Model Prediction Probabilities",
                    range_y=[0, 100]
                )
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Prediction failed: {e}")
        st.warning(
            "Check that the model and scaler use these same five features, "
            "in this exact order, and that the scaler was fitted on a "
            "DataFrame with matching column names."
        )

st.caption(
    "Note: This is a model-based prediction, not a guarantee of machine safety."
)


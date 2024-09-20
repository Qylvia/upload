import streamlit as st
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt

model = joblib.load('LogisticRegression.pkl')

INRG_stage_option = {
    0: 'Normal(0)',
    1: 'Abnormal(1)',
}
feature_names = ['AGE', 'LDH', 'INRG_STAGE', 'RAD_SCORE']
st.title('NB Classification')
age = st.number_input('Age:')
LDH = st.number_input('LDH:')
rad_score = st.number_input('Rad_Score:')
INRG_stage = st.selectbox('INRG_stage: ', options=list(INRG_stage_option.keys()),
                          format_func=lambda x: INRG_stage_option[x])
feature_values = [age, LDH, INRG_stage, rad_score]
features = np.array([feature_values])
if st.button("Predict"):
    # Predict class and probabilities
    predicted_class = model.predict(features)[0]
    predicted_proba = model.predict_proba(features)[0]
    # Display prediction results
    st.write(f"**Predicted Class:** {predicted_class}")
    st.write(f"**Prediction Probabilities:** {predicted_proba}")
    # Generate advice based on prediction results    
    probability = predicted_proba[predicted_class] * 100
    if predicted_class == 1:
        advice = (
            f"According to our model, you have a high risk of heart disease. "
            f"The model predicts that your probability of having heart disease is {probability:.1f}%. "
            "While this is just an estimate, it suggests that you may be at significant risk. "
            "I recommend that you consult a cardiologist as soon as possible for further evaluation and "
            "to ensure you receive an accurate diagnosis and necessary treatment."
        )
    else:
        advice = (
            f"According to our model, you have a low risk of heart disease. "
            f"The model predicts that your probability of not having heart disease is {probability:.1f}%. "
            "However, maintaining a healthy lifestyle is still very important. "
            "I recommend regular check-ups to monitor your heart health, "
            "and to seek medical advice promptly if you experience any symptoms."
        )
    st.write(advice)
    # Calculate SHAP values and display force plot
    explainer = shap.Explainer(model)
    shap_values = explainer.shap_values(pd.DataFrame([feature_values], columns=feature_names))
    shap.force_plot(explainer.expected_value[0], shap_values[:,0], pd.DataFrame([feature_values], columns=feature_names))
    plt.savefig("shap_force_plot.png", bbox_inches='tight', dpi=1200)
    st.image("shap_force_plot.png")

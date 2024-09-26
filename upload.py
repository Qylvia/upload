import streamlit as st
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt


model = joblib.load('model.pkl')

INRG_stage_option = {
    0: 'Normal(0)',
    1: 'Abnormal(1)',
}
feature_names = ['AGE', 'LDH', 'INRG_STAGE']
st.title('神母细胞瘤分型')
whole_feature = ['CT_TR_original_firstorder_Median',
                 'PET_TR_original_ngtdm_Contrast',
                 'PET_TR_original_gldm_SmallDependenceLowGrayLevelEmphasis',
                 'CT_TR_original_shape_Elongation',
                 'CT_TR_original_glcm_InverseVariance',
                 'PET_TR_original_glrlm_LongRunLowGrayLevelEmphasis',
                 'PET_TR_original_glszm_LargeAreaHighGrayLevelEmphasis',
                 'CT_TR_original_firstorder_10Percentile',
                 'PET_TR_original_glcm_DifferenceEntropy',
                 'PET_TR_original_gldm_LargeDependenceHighGrayLevelEmphasis',
                 'PET_TR_original_firstorder_10Percentile',
                 'CT_TR_original_firstorder_Mean', 'PET_TR_original_ngtdm_Busyness',
                 'PET_TR_original_firstorder_Skewness',
                 'PET_TR_original_firstorder_Energy',
                 'CT_TR_original_gldm_DependenceVariance',
                 'CT_TR_original_gldm_LargeDependenceEmphasis',
                 'CT_TR_original_shape_MajorAxisLength',
                 'CT_TR_original_glrlm_RunEntropy', 'CT_TR_original_ngtdm_Contrast',
                 'CT_TR_original_gldm_DependenceNonUniformityNormalized',
                 'CT_TR_original_glcm_Correlation',
                 'CT_TR_original_shape_LeastAxisLength',
                 'PET_TR_original_firstorder_Maximum',
                 'PET_TR_original_glcm_Correlation', '2DPET_DL_0', '2DCT_DL_92',
                 '2DPET_DL_1', '2DCT_DL_187', '2DCT_DL_116', '2DCT_DL_120']

INRG_stage = st.selectbox('INRG_stage: ', options=list(INRG_stage_option.keys()),
                          format_func=lambda x: INRG_stage_option[x])
uploaded_file = st.file_uploader("请选择文件进行上传", type=None)
if uploaded_file is not None:
    patient = st.number_input("输入想预测的病人所在行数：")
    df = pd.read_csv(uploaded_file)
    df = df[whole_feature]
    first_row = df.iloc[patient]
    st.write(f"数值为：")
    st.write(first_row)

    age = st.number_input('Age:')
    LDH = st.number_input('LDH:')
    cli_data = [age, LDH, INRG_stage]
    feature_values = pd.concat([cli_data, first_row], axis=0)
    features = np.array([feature_values])
    cutoff = 0.4606228354851223
    
    # 检查是否有文件上传
    if st.button("Predict"):
        # Predict class and probabilities
        predicted_proba = model.predict_proba(features)[0]
        if predicted_proba > cutoff:
            predicted_class = 1
        else:
            predicted_class = 0
        # Display prediction results
        st.write(f"**Predicted Class:** {predicted_class}")
        st.write(f"**Prediction Probabilities:** {predicted_proba}")
        # Generate advice based on prediction results    p
        probability = predicted_proba[predicted_class] * 100
        # 读取 CSV 文件

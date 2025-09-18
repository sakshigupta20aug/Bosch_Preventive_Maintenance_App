# scripts/app_model.py
"""
Streamlit App 2 – Predictive Model Dashboard with Login + Sidebar Navigation
Uses trained model to make predictions and display evaluation metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import json
from pathlib import Path

# -------------------
# Page Config
# -------------------
st.set_page_config(page_title="Bosch Preventive Maintenance - Model", layout="wide")

# -------------------
# Paths
# -------------------
project_dir = Path(r"C:\Users\Admin\Downloads\Internship\Bosch_PMP")
model_fp = project_dir / "models" / "classification_model.pkl"
metrics_fp = project_dir / "models" / "classification_metrics.json"
fig_dir = project_dir / "reports" / "figures"

# -------------------
# Authentication
# -------------------
USERS = {"admin": "password123", "sakshi": "bosch2025"}

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid username or password")

# -------------------
# Load Model & Metrics
# -------------------
@st.cache_resource
def load_model():
    with open(model_fp, "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_metrics():
    with open(metrics_fp, "r") as f:
        return json.load(f)

# -------------------
# Pages
# -------------------
def page_overview():
    st.header("Model Overview")
    metrics = load_metrics()

    st.subheader("📊 Classification Report")
    st.text(metrics["classification_report"])

    st.subheader("✅ Key Metrics")
    st.json({
        "ROC AUC": round(metrics["roc_auc"],4),
        "PR AUC": round(metrics["pr_auc"],4),
        "Positive Rate (test set)": f"{metrics['positive_rate_test']*100:.2f}%"
    })

    st.subheader("🔲 Confusion Matrix")
    cm = metrics["confusion_matrix"]
    cm_df = pd.DataFrame(cm, index=["Actual Pass (0)", "Actual Fail (1)"], 
                              columns=["Pred Pass (0)", "Pred Fail (1)"])
    st.dataframe(cm_df, use_container_width=True)

    st.subheader("📉 Saved Figures")
    st.image(str(fig_dir / "confusion_matrix.png"), caption="Confusion Matrix Plot")
    st.image(str(fig_dir / "precision_recall_curve.png"), caption="Precision-Recall Curve")

def page_predict():
    st.header("Upload Data for Prediction")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        df_new = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df_new.head(10), use_container_width=True)

        # Load model
        model = load_model()

        # Get training feature names from model
        model_features = model.get_booster().feature_names

        # Drop columns not in model features (e.g., Id, target)
        X_new = df_new.copy()
        for col in X_new.columns:
            if col not in model_features:
                X_new = X_new.drop(columns=[col])

        # Reorder columns to match training
        X_new = X_new[model_features]

        # Make predictions
        preds = model.predict(X_new)
        df_new["prediction"] = preds

        # --- Summary ---
        fail_rate = (df_new["prediction"].mean() * 100).round(2)
        st.subheader("📊 Prediction Summary")
        st.write(f"✅ Predicted Pass: {(100 - fail_rate):.2f}%")
        st.write(f"⚠️ Predicted Fail: {fail_rate:.2f}%")

        # Plot prediction distribution
        st.subheader("📉 Prediction Distribution")
        counts = df_new["prediction"].value_counts().reindex([0, 1], fill_value=0)
        fig, ax = plt.subplots()
        counts.plot(kind="bar", ax=ax, color=["green", "red"])
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Pass (0)", "Fail (1)"], rotation=0)
        ax.set_ylabel("Count")
        plt.tight_layout()
        st.pyplot(fig)

        # --- Preview ---
        st.subheader("Predicted Data (first 20 rows)")
        st.dataframe(df_new.head(20), use_container_width=True)

        # --- Download ---
        csv = df_new.to_csv(index=False).encode("utf-8")
        st.download_button("Download predictions CSV", csv, file_name="predictions.csv")

def page_about():
    st.header("About This App")
    st.markdown("""
    - **App 2 (Model Dashboard)** demonstrates predictive analytics using the trained XGBoost model.  
    - Features:  
      - View model performance metrics (ROC AUC, PR AUC, Confusion Matrix).  
      - Upload new data to generate predictions.  
      - View predicted failure rate and distribution.  
      - Download prediction results as CSV.  
    - Complements **App 1 (Analytics Dashboard)** for complete Preventive Maintenance solution.
    """)

# -------------------
# Dashboard Controller
# -------------------
def dashboard():
    st.title("🤖 Bosch Preventive Maintenance – Model Dashboard")

    menu = st.sidebar.radio(
        "Navigation",
        ["Model Overview","Predict New Data","About"]
    )

    if menu=="Model Overview": page_overview()
    elif menu=="Predict New Data": page_predict()
    elif menu=="About": page_about()

# -------------------
# App Execution
# -------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    dashboard()

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
# Paths (LOCAL + GitHub fallback)
# -------------------
LOCAL_MODEL = Path("models/classification_model.pkl")
LOCAL_METRICS = Path("models/classification_metrics.json")
LOCAL_FIG_DIR = Path("reports/figures")

# 👉 Replace <your-username>/<your-repo> with your GitHub repo
GITHUB_MODEL = "https://raw.githubusercontent.com/<your-username>/<your-repo>/main/models/classification_model.pkl"
GITHUB_METRICS = "https://raw.githubusercontent.com/<your-username>/<your-repo>/main/models/classification_metrics.json"

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
    try:
        if LOCAL_MODEL.exists():
            with open(LOCAL_MODEL, "rb") as f:
                return pickle.load(f)
        else:
            import requests, io
            r = requests.get(GITHUB_MODEL)
            return pickle.load(io.BytesIO(r.content))
    except Exception as e:
        st.error(f"❌ Could not load model: {e}")
        return None

@st.cache_data
def load_metrics():
    try:
        if LOCAL_METRICS.exists():
            with open(LOCAL_METRICS, "r") as f:
                return json.load(f)
        else:
            import requests
            r = requests.get(GITHUB_METRICS)
            return r.json()
    except Exception as e:
        st.error(f"❌ Could not load metrics: {e}")
        return None

# -------------------
# Pages
# -------------------
def page_overview():
    st.header("Model Overview")
    metrics = load_metrics()
    if not metrics:
        st.warning("Metrics not available.")
        return

    # --- Classification Report ---
    st.subheader("📊 Classification Report")
    clf_report = metrics.get("classification_report", {})
    if clf_report:
        report_df = pd.DataFrame(clf_report).T.round(3)
        st.dataframe(report_df, use_container_width=True)
    else:
        st.warning("Classification report not available.")

    # --- Key Metrics ---
    st.subheader("✅ Key Metrics")
    st.json({
        "ROC AUC": round(metrics.get("roc_auc", 0),4),
        "PR AUC": round(metrics.get("pr_auc", 0),4),
        "Positive Rate (test set)": f"{metrics.get('positive_rate_test',0)*100:.2f}%"
    })

    # --- Confusion Matrix ---
    st.subheader("🔲 Confusion Matrix")
    cm = metrics.get("confusion_matrix", [[0,0],[0,0]])
    cm_df = pd.DataFrame(cm, index=["Actual Pass (0)", "Actual Fail (1)"], 
                              columns=["Pred Pass (0)", "Pred Fail (1)"])
    st.dataframe(cm_df, use_container_width=True)

    # --- Saved Figures ---
    st.subheader("📉 Saved Figures")
    if (LOCAL_FIG_DIR / "confusion_matrix.png").exists():
        st.image(str(LOCAL_FIG_DIR / "confusion_matrix.png"), caption="Confusion Matrix Plot")
    if (LOCAL_FIG_DIR / "precision_recall_curve.png").exists():
        st.image(str(LOCAL_FIG_DIR / "precision_recall_curve.png"), caption="Precision-Recall Curve")

def page_predict():
    st.header("Upload Data for Prediction")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        df_new = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df_new.head(10), use_container_width=True)

        model = load_model()
        if model is None:
            st.error("Model not loaded.")
            return

        # Get feature names
        try:
            model_features = model.get_booster().feature_names
        except:
            st.warning("⚠️ Model does not expose feature names. Using uploaded columns.")
            model_features = list(df_new.columns)

        # Align features
        X_new = df_new.copy()
        for col in X_new.columns:
            if col not in model_features:
                X_new = X_new.drop(columns=[col])
        X_new = X_new[model_features]

        # Predictions
        preds = model.predict(X_new)
        df_new["prediction"] = preds

        # --- Summary ---
        fail_rate = (df_new["prediction"].mean() * 100).round(2)
        st.subheader("📊 Prediction Summary")
        st.write(f"✅ Predicted Pass: {(100 - fail_rate):.2f}%")
        st.write(f"⚠️ Predicted Fail: {fail_rate:.2f}%")

        # --- Prediction Distribution ---
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

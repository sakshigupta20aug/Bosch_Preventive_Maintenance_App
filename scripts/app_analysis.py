# scripts/app_analysis.py
"""
Streamlit App 1 – Analytics Dashboard with Login + Sidebar Navigation
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# -------------------
# Page Config
# -------------------
st.set_page_config(page_title="Bosch Preventive Maintenance - Analytics", layout="wide")

# -------------------
# Dataset Path (LOCAL + CLOUD handling)
# -------------------
LOCAL_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "bosch_clean.csv"

# ✅ Replace with your GitHub username & repo name
GITHUB_RAW = "https://raw.githubusercontent.com/sakshigupta20aug/Bosch_Preventive_Maintenance_App/main/data/processed/bosch_clean.csv"

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
# Load Data
# -------------------
@st.cache_data
def load_data():
    try:
        if LOCAL_PATH.exists():
            return pd.read_csv(LOCAL_PATH, low_memory=False)
        else:
            return pd.read_csv(GITHUB_RAW, low_memory=False)
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        return None

def plt_to_streamlit(fig):
    st.pyplot(fig)
    plt.close(fig)

# -------------------
# Dashboard Pages
# -------------------
def page_overview(df):
    st.header("Dataset Overview")
    st.write("Shape:", df.shape)
    with st.expander("View Dataset"):
        st.dataframe(df.head(10), use_container_width=True)

def page_class_distribution(df):
    st.header("Class Distribution")
    counts = df["target"].value_counts().reindex([0,1], fill_value=0)
    fig, ax = plt.subplots()
    counts.plot(kind="bar", ax=ax, color=["green","red"])
    ax.set_xticks([0,1])
    ax.set_xticklabels(["Pass (0)", "Fail (1)"], rotation=0)
    ax.set_ylabel("Count")
    plt_to_streamlit(fig)
    with st.expander("View Counts Table"):
        st.dataframe(counts.to_frame("Count"), use_container_width=True)

def page_cycle_time(df):
    st.header("Cycle Time Analysis")
    if "cycle_time" not in df.columns:
        st.warning("No 'cycle_time' column.")
        return
    cycle = pd.to_numeric(df["cycle_time"], errors="coerce").dropna()
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        sns.histplot(cycle, bins=60, kde=False, ax=ax)
        ax.set_title("Distribution")
        plt_to_streamlit(fig)
    with col2:
        fig, ax = plt.subplots()
        sns.boxplot(x=cycle, ax=ax, color="lightcoral")
        ax.set_title("Boxplot")
        plt_to_streamlit(fig)

def page_failure_buckets(df):
    st.header("Failure Rate by Cycle Time Bucket")
    if "cycle_time" not in df.columns:
        st.warning("No 'cycle_time' column.")
        return
    cycle_vals = pd.to_numeric(df["cycle_time"], errors="coerce")
    df["cycle_bucket"] = pd.cut(cycle_vals, bins=[-1,500,1000,2000,np.inf],
                                labels=["<500","500-1000","1000-2000",">2000"])
    summary = (df.groupby("cycle_bucket")["target"]
                 .agg(total="count", failed="sum").reset_index())
    summary["failure_rate_%"] = (summary["failed"]/summary["total"]*100).round(2)
    with st.expander("View Table"):
        st.dataframe(summary, use_container_width=True)
    fig, ax = plt.subplots()
    sns.barplot(x="cycle_bucket", y="failure_rate_%", data=summary, ax=ax, palette="viridis")
    plt_to_streamlit(fig)

def page_feature_averages(df):
    st.header("Feature Averages (Pass vs Fail)")
    cols = [c for c in ["num_mean","num_median","cycle_time"] if c in df.columns]
    if not cols: 
        st.warning("No numeric summary columns found.")
        return
    summary = df.groupby("target")[cols].mean().round(4)
    with st.expander("View Table"):
        st.dataframe(summary, use_container_width=True)
    fig, ax = plt.subplots()
    summary.T.plot(kind="bar", ax=ax)
    ax.set_ylabel("Average Value")
    plt_to_streamlit(fig)

def page_correlations(df):
    st.header("Top Correlated Features")
    num_cols = [c for c in df.columns if df[c].dtype in [np.int64,np.float64]]
    if "target" not in df.columns or len(num_cols)<2:
        st.warning("Not enough numeric data for correlations.")
        return
    sample = df[num_cols].dropna().sample(n=min(20000,len(df)), random_state=42)
    corrs = sample.corr()["target"].abs().drop("target").sort_values(ascending=False).head(15)
    with st.expander("View Table"):
        st.dataframe(corrs.to_frame("abs_corr"), use_container_width=True)
    fig, ax = plt.subplots(figsize=(7,4))
    corrs.plot(kind="bar", ax=ax)
    plt_to_streamlit(fig)

def page_missing(df):
    st.header("Missing Values")
    with st.expander("View Table"):
        st.dataframe(df.isna().sum().sort_values(ascending=False).head(20), use_container_width=True)

def page_top_records(df):
    st.header("Top Records")
    with st.expander("View Table"):
        st.dataframe(df.head(20), use_container_width=True)

# -------------------
# Dashboard Controller
# -------------------
def dashboard():
    df = load_data()
    if df is None:
        st.error("Dataset not found. Please check path or GitHub link.")
        return

    st.title("📊 Bosch Preventive Maintenance – Analytics Dashboard")

    menu = st.sidebar.radio(
        "Navigation",
        ["Overview","Class Distribution","Cycle Time","Failure Buckets",
         "Feature Averages","Correlations","Missing Values","Top Records"]
    )

    if menu=="Overview": page_overview(df)
    elif menu=="Class Distribution": page_class_distribution(df)
    elif menu=="Cycle Time": page_cycle_time(df)
    elif menu=="Failure Buckets": page_failure_buckets(df)
    elif menu=="Feature Averages": page_feature_averages(df)
    elif menu=="Correlations": page_correlations(df)
    elif menu=="Missing Values": page_missing(df)
    elif menu=="Top Records": page_top_records(df)

# -------------------
# App Execution
# -------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    dashboard()

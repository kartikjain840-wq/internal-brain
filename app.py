import streamlit as st
import pandas as pd
import os
import gdown
import nltk
from PyPDF2 import PdfReader
from nltk.tokenize import sent_tokenize

nltk.download("punkt")

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Operational Excellence File Intelligence Dashboard",
    layout="wide"
)

st.title("📊 Operational Excellence File Intelligence Dashboard")

# ================= SIMPLE SUMMARIZER =================
def summarize_text(text, max_sentences=5):
    if not text or len(text.split()) < 100:
        return "Not enough content to summarize."

    sentences = sent_tokenize(text)
    return " ".join(sentences[:max_sentences])

# ================= INSIGHT EXTRACTION =================
def extract_insights(text):
    insights = {"Cost": [], "Time": [], "Quality": [], "Process": []}
    for line in text.lower().split("."):
        if any(k in line for k in ["cost", "saving", "expense"]):
            insights["Cost"].append(line)
        if any(k in line for k in ["time", "delay", "cycle"]):
            insights["Time"].append(line)
        if any(k in line for k in ["defect", "error", "quality"]):
            insights["Quality"].append(line)
        if any(k in line for k in ["process", "automation", "workflow"]):
            insights["Process"].append(line)
    return insights

# ================= GOOGLE DRIVE =================
st.subheader("🔗 Load Files from Google Drive")
drive_url = st.text_input("Paste Google Drive folder link (Viewer access)")

DOWNLOAD_DIR = "drive_files"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

if st.button("Load Files") and drive_url:
    gdown.download_folder(drive_url, output=DOWNLOAD_DIR, quiet=True, use_cookies=False)
    st.success("Files loaded")

# ================= FILE READER =================
def read_file(path):
    if path.endswith(".csv"):
        return pd.read_csv(path).to_string()
    elif path.endswith(".xlsx"):
        return pd.read_excel(path).to_string()
    elif path.endswith(".pdf"):
        reader = PdfReader(path)
        return " ".join(p.extract_text() for p in reader.pages if p.extract_text())
    elif path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# ================= DISPLAY =================
files = []
if os.path.exists(DOWNLOAD_DIR):
    files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith((".csv", ".xlsx", ".pdf", ".txt"))]

if files:
    selected = st.selectbox("Select file", files)
    path = os.path.join(DOWNLOAD_DIR, selected)
    text = read_file(path)

    # KPIs
    st.subheader("📌 KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Word Count", len(text.split()))
    c2.metric("File Size (KB)", round(os.path.getsize(path)/1024, 2))
    c3.metric("File Type", selected.split(".")[-1].upper())
    c4.metric("Summary", "Available")

    # Content
    col1, col2 = st.columns(2)
    col1.text_area("Content", text[:5000], height=300)
    col2.success(summarize_text(text))

    # Insights
    st.subheader("📊 Consulting Insights")
    insights = extract_insights(text)
    for k, v in insights.items():
        st.markdown(f"### {k}")
        st.write(v[:3] if v else "No signals detected")

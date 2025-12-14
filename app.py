import streamlit as st
import pandas as pd
import os
import gdown
from PyPDF2 import PdfReader
from transformers import pipeline

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Operational Excellence File Intelligence Dashboard",
    layout="wide"
)

st.title("📊 Operational Excellence File Intelligence Dashboard")

# ================= LOAD SUMMARIZER =================
@st.cache_resource
def load_summarizer():
    return pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6"
    )

summarizer = load_summarizer()

# ================= SAFE SUMMARIZATION =================
def summarize_text(text):
    if not text:
        return None

    words = text.split()
    if len(words) < 80:
        return None

    try:
        result = summarizer(
            text[:3000],
            max_length=150,
            min_length=60,
            do_sample=False
        )
        return result[0]["summary_text"] if result else None
    except Exception:
        return None

# ================= INSIGHT EXTRACTION =================
def extract_insights(text):
    insights = {
        "Cost": [],
        "Time": [],
        "Quality": [],
        "Process": []
    }

    lines = text.lower().split(".")
    for line in lines:
        if any(k in line for k in ["cost", "expense", "reduction", "saving"]):
            insights["Cost"].append(line.strip())
        if any(k in line for k in ["time", "cycle", "delay", "speed"]):
            insights["Time"].append(line.strip())
        if any(k in line for k in ["defect", "error", "quality", "rework"]):
            insights["Quality"].append(line.strip())
        if any(k in line for k in ["process", "workflow", "automation", "standard"]):
            insights["Process"].append(line.strip())

    return insights

# ================= GOOGLE DRIVE INPUT =================
st.subheader("🔗 Load Files from Google Drive")

drive_url = st.text_input(
    "Paste Google Drive FOLDER link (Anyone with link → Viewer)"
)

DOWNLOAD_DIR = "drive_files"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

if st.button("Load Files") and drive_url:
    with st.spinner("Downloading files..."):
        gdown.download_folder(
            drive_url,
            output=DOWNLOAD_DIR,
            quiet=True,
            use_cookies=False
        )
    st.success("Files loaded successfully")

# ================= FILE READERS =================
def read_file(path):
    try:
        if path.endswith(".csv"):
            return pd.read_csv(path).to_string()
        elif path.endswith(".xlsx"):
            return pd.read_excel(path).to_string()
        elif path.endswith(".pdf"):
            reader = PdfReader(path)
            return " ".join(
                page.extract_text()
                for page in reader.pages
                if page.extract_text()
            )
        elif path.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        return ""

# ================= DISPLAY =================
if os.path.exists(DOWNLOAD_DIR):

    files = [
        f for f in os.listdir(DOWNLOAD_DIR)
        if f.lower().endswith((".csv", ".xlsx", ".pdf", ".txt"))
    ]

    if files:
        selected_file = st.selectbox("Select a file", files)
        file_path = os.path.join(DOWNLOAD_DIR, selected_file)

        raw_text = read_file(file_path)
        summary = summarize_text(raw_text)

        # ================= KPI CARDS =================
        st.subheader("📌 Document KPIs")
        k1, k2, k3, k4 = st.columns(4)

        k1.metric("Word Count", len(raw_text.split()))
        k2.metric("File Size (KB)", round(os.path.getsize(file_path) / 1024, 2))
        k3.metric("File Type", selected_file.split(".")[-1].upper())
        k4.metric("Summary Status", "Generated" if summary else "Not Generated")

        # ================= CONTENT =================
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Extracted Content")
            st.text_area("Content", raw_text[:5000], height=300)

        with col2:
            st.subheader("🧠 AI Summary")
            st.success(summary if summary else "Summary not available")

        # ================= INSIGHTS =================
        st.divider()
        st.subheader("📊 Consulting Insights Extracted")

        insights = extract_insights(raw_text)

        for key, values in insights.items():
            st.markdown(f"### {key} Insights")
            if values:
                for v in values[:3]:
                    st.write(f"• {v.capitalize()}")
            else:
                st.write("No significant signals detected.")

        # ================= CONSULTING SNAPSHOT =================
        st.divider()
        st.subheader("🏭 Operational Excellence Snapshot")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("""
            **Tools Used**
            • Lean Six Sigma  
            • Process Mapping  
            • Power BI / Tableau  
            • RPA  
            • ERP Analytics  
            """)

        with c2:
            st.markdown("""
            **Impact Created**
            • Cost reduction  
            • Cycle time improvement  
            • Quality enhancement  
            • Productivity uplift  
            """)

        with c3:
            st.markdown("""
            **Industries**
            • Manufacturing  
            • FMCG  
            • BFSI  
            • Logistics  
            • Energy  
            """)

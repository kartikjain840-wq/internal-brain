import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader
from transformers import pipeline

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Operational Excellence Dashboard",
    layout="wide"
)

st.title("📊 Operational Excellence File Intelligence Dashboard")

# ---------- AI SUMMARIZER ----------
@st.cache_resource
def load_summarizer():
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn"
    )

summarizer = load_summarizer()

def summarize_text(text):
    if not text or len(text.split()) < 80:
        return text
    result = summarizer(
        text,
        max_length=150,
        min_length=60,
        do_sample=False
    )
    return result[0]["summary_text"]

# ---------- FILE READERS ----------
def read_file(file_path):
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path).to_string()

        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path).to_string()

        elif file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            return " ".join(
                page.extract_text()
                for page in reader.pages
                if page.extract_text()
            )

        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        else:
            return "Unsupported file format."

    except Exception as e:
        return f"Error reading file: {e}"

# ---------- INPUT ----------
folder_path = st.text_input(
    "Enter folder path (example: C:/Consulting_Data)",
    value=""
)

# ---------- MAIN ----------
if folder_path:

    if os.path.exists(folder_path):

        files = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith((".csv", ".xlsx", ".pdf", ".txt"))
        ]

        if files:
            selected_file = st.selectbox("Select a file", files)
            file_path = os.path.join(folder_path, selected_file)

            raw_text = read_file(file_path)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📄 Extracted Content")
                st.text_area(
                    "Content",
                    raw_text[:5000],
                    height=300
                )

            with col2:
                st.subheader("🧠 AI Summary")
                summary = summarize_text(raw_text)
                st.success(summary)

            # ---------- CONSULTING SNAPSHOT ----------
            st.divider()
            st.subheader("🏭 Operational Excellence Snapshot")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown("### 🛠 Tools Used")
                st.markdown("""
                • Lean Six Sigma (DMAIC)  
                • Process Mapping (VSM, SIPOC)  
                • Excel Solver & VBA  
                • Power BI / Tableau  
                • RPA (UiPath / Power Automate)  
                • SAP / ERP Analytics  
                """)

            with c2:
                st.markdown("### 📈 Impact Created")
                st.markdown("""
                • 15–30% cost reduction  
                • 20–40% cycle time improvement  
                • Productivity uplift  
                • Quality & SLA improvement  
                """)

            with c3:
                st.markdown("### 🏢 Industries Catered")
                st.markdown("""
                • Manufacturing  
                • FMCG  
                • BFSI  
                • Logistics & Supply Chain  
                • Energy & Utilities  
                """)

        else:
            st.warning("No supported files found in folder.")

    else:
        st.error("Folder path does not exist.")

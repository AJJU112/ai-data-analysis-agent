import os
import pandas as pd
import numpy as np
import streamlit as st
import google.generativeai as genai

# -------------------------
# 🔹 API Key Setup
# -------------------------
FALLBACK_API_KEY = "AIzaSyD4H7pgR32yhGkMZrnLK65iKGC5t3Gv62w"  # Replace with your key if needed
api_key = os.getenv("GOOGLE_API_KEY", FALLBACK_API_KEY)
genai.configure(api_key=api_key)

# -------------------------
# 🔹 Page Config
# -------------------------
st.set_page_config(page_title="Gemini Data Analyst", layout="wide")
st.title("📊 Gemini-Powered Data Q&A - Ajay ")

# -------------------------
# 🔹 File Upload or Demo
# -------------------------
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)  # Reads full CSV
    else:
        df = pd.read_excel(uploaded_file)  # Reads full Excel
else:
    # Demo dataset if no file uploaded
    np.random.seed(42)
    data = {
        "OrderID": range(1, 101),
        "Product": np.random.choice(["Laptop", "Mobile", "Tablet", "Headphones", "Camera"], 100),
        "Category": np.random.choice(["Electronics", "Accessories", "Gadgets"], 100),
        "Sales": np.random.randint(500, 50000, size=100),
        "Quantity": np.random.randint(1, 10, size=100),
        "Region": np.random.choice(["North", "South", "East", "West"], 100),
        "Date": pd.date_range(start="2023-01-01", periods=100, freq="D")
    }
    df = pd.DataFrame(data)
    st.info("Using demo dataset.")

# -------------------------
# 🔹 Filters
# -------------------------
with st.expander("🔍 Filter Data"):
    # Date filter
    if "Date" in df.columns:
        start_date = st.date_input("Start Date", df["Date"].min())
        end_date = st.date_input("End Date", df["Date"].max())
        df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

    # Category filter
    if "Category" in df.columns:
        selected_categories = st.multiselect("Select Categories", df["Category"].unique())
        if selected_categories:
            df = df[df["Category"].isin(selected_categories)]

    # Numeric range filter for Sales
    if "Sales" in df.columns:
        min_sales, max_sales = st.slider(
            "Select Sales Range",
            int(df["Sales"].min()),
            int(df["Sales"].max()),
            (int(df["Sales"].min()), int(df["Sales"].max()))
        )
        df = df[(df["Sales"] >= min_sales) & (df["Sales"] <= max_sales)]

# -------------------------
# 🔹 Show filtered data
# -------------------------
st.subheader("📄 Filtered Data")
st.dataframe(df.head(20))  # Show first 20 for preview

# -------------------------
# 🔹 Ask Gemini
# -------------------------
def ask_gemini(question, full_df):
    # Send ALL filtered rows to Gemini
    prompt = f"""
    You are a skilled data analyst.
    Here is the dataset after filtering:
    {full_df.to_string(index=False)}
    Question: {question}
    Give a short, clear, and accurate answer based ONLY on this dataset.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

st.subheader("💬 Ask Gemini about your data")
question = st.text_input("Enter your question here")

if st.button("Get Answer"):
    if question.strip():
        answer = ask_gemini(question, df)  # Pass full DataFrame
        st.success(answer)
    else:
        st.warning("Please enter a question.")


import streamlit as st
import pandas as pd
import base64

def load_csv(file):
    """Load CSV file into DataFrame"""
    try:
        return pd.read_csv(file)
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None

def display_data(df, title=None):
    """Display DataFrame preview with optional title"""
    if title:
        st.subheader(title)
    st.dataframe(df.head())

def download_csv(df, filename):
    """Create download link for DataFrame as CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

def process_results(df, results, primary_column):
    """Process and format extraction results"""
    return pd.DataFrame({
        "Entity": df[primary_column],
        "Extracted_Information": results
    })

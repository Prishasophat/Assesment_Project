import streamlit as st
import pandas as pd
import json
import io

def export_data(df: pd.DataFrame, format_type: str) -> None:
    if format_type == "CSV":
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "extracted_data.csv",
            "text/csv"
        )
    elif format_type == "JSON":
        json_str = df.to_json(orient='records')
        st.download_button(
            "📥 Download JSON",
            json_str,
            "extracted_data.json",
            "application/json"
        )
    elif format_type == "Excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            "📥 Download Excel",
            buffer.getvalue(),
            "extracted_data.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

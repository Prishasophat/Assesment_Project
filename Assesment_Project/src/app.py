import streamlit as st
import pandas as pd
from utils.google_sheets import authenticate_google_sheets, get_sheet_data, write_to_sheet
from utils.data_processing import load_csv, display_data, download_csv
from dotenv import load_dotenv
import os
from groq import Groq
import json
from utils.ai_helpers import (
    extract_info_with_groq,
    enhance_prompt,
    batch_process_with_groq,
    format_extraction_prompt
)

# Configuration and Constants
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

QUERY_TEMPLATES = {
    "Basic Info": "Extract basic information about {company}",
    "Contact Details": "Get the email and address for {company}",
    "Full Analysis": "Provide a detailed analysis of {company} including contact info, main business areas, and key personnel",
    "Custom": "Custom prompt..."
}

DEFAULT_FIELDS = ["Email", "Address", "Phone", "Website", "Description"]
BATCH_SIZE = 10

def initialize_session_state():
    if 'extraction_history' not in st.session_state:
        st.session_state.extraction_history = []
    if 'custom_fields' not in st.session_state:
        st.session_state.custom_fields = []

def initialize_app():
    st.title("Advanced AI Data Extraction Tool")
    st.markdown("Upload your data and extract intelligent insights using AI.")

def handle_data_source():
    st.sidebar.header("Data Source")
    source_tabs = st.sidebar.radio("Choose Data Source", ["Upload CSV", "Google Sheets"])
    df, sheet_url, source_type = None, None, None

    if source_tabs == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], key="csv_uploader")
        if uploaded_file:
            df = load_csv(uploaded_file)
            source_type = "Upload CSV"

    elif source_tabs == "Google Sheets":
        sheet_url = st.text_input("Enter Google Sheet URL", key="sheet_url")
        if sheet_url:
            df = get_sheet_data(sheet_url)
            source_type = "Google Sheets"

    return df, source_type, sheet_url

def handle_column_selection(df):
    # This section handles the column selection, which is above the tabs
    st.sidebar.header("Column Selection")
    primary_columns = st.sidebar.multiselect(
        "Select Entity Columns",
        df.columns if df is not None else [],
        help="Select one or more columns to use as entities"
    )
    return primary_columns

def handle_sidebar_controls(df, primary_columns):
    # This section handles the prompt selection and column-based functionality
    prompt_tabs = st.sidebar.radio("Choose Prompt Type", ["Generate Prompt", "Custom Prompt"])

    if prompt_tabs == "Generate Prompt":
        prompt = handle_generate_prompt_sidebar(df, primary_columns)
    else:
        prompt = handle_custom_prompt_sidebar(df)

    return prompt

def handle_generate_prompt_sidebar(df, primary_columns):
    # Standard fields selection for Generate Prompt
    selected_fields = st.sidebar.multiselect(
        "Select fields to extract",
        DEFAULT_FIELDS,
        default=["Email", "Phone"],
        key="fields_select"
    )

    # Allow the user to add custom fields in "Generate Prompt"
    custom_field = st.sidebar.text_input("Add Custom Field", key="custom_field_input")
    if custom_field:
        if custom_field not in selected_fields:
            selected_fields.append(custom_field)
            st.session_state['custom_fields'].append(custom_field)  # Add to session state

    # Ensure that selected fields are not empty
    if not selected_fields:
        st.sidebar.warning("Please select at least one field to extract.")

    # Generate a simplified prompt with curly braces for placeholders
    if primary_columns and selected_fields:
        prompt = f"Get me the {', '.join([f'{{{field}}}' for field in selected_fields])} for {', '.join([f'{{{col}}}' for col in primary_columns])}."
    else:
        prompt = ""

    if st.sidebar.checkbox("Show Prompt Preview", key="generate_prompt_preview_checkbox"):
        st.sidebar.text_area("Generated Prompt", prompt, disabled=True, key="generate_prompt_preview")

    return prompt


def handle_custom_prompt_sidebar(df):
    # Custom prompt text area for user input
    available_columns = list(df.columns) if df is not None and len(df.columns) > 0 else []
    custom_prompt = st.text_area(
        "Write your custom prompt here:",
        value="Extract information about company {company_name} located in {location}.",
        height=150
    )

    if st.checkbox("Show Available Placeholders"):
        st.markdown("#### Available Column Placeholders")
        if available_columns:
            st.code(", ".join([f'{{{col}}}' for col in available_columns]))
        else:
            st.markdown("No columns available. Please upload data.")

    return custom_prompt

def process_data_with_advanced_features(df, prompt_template, columns):
    try:
        if not columns:
            st.error("Please select at least one column before processing")
            return None

        with st.spinner("Processing data..."):
            # Prepare data with column values
            processed_data = []
            for _, row in df.iterrows():
                data_dict = {col: row[col] for col in columns}
                processed_data.append(data_dict)

            # Process with enhanced prompt
            results = batch_process_with_groq(
                processed_data,
                prompt_template,
                columns
            )

            results_df = pd.DataFrame({
                "Entity": df[columns[0]] if columns else df.index,
                "Extracted_Information": results
            })
            return results_df

    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        return None

def display_results(results_df):
    st.success("Information successfully extracted!")

    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download CSV",
            results_df.to_csv(index=False),
            "extracted_data.csv",
            "text/csv",
            key="download_csv_button"
        )
    with col2:
        st.download_button(
            "📥 Download JSON",
            results_df.to_json(orient='records'),
            "extracted_data.json",
            "application/json",
            key="download_json_button"
        )

    st.subheader("Extracted Information")
    for idx, row in results_df.iterrows():
        with st.expander(f"📄 Results for :green[{row['Entity']}]", expanded=True):
            try:
                info = row['Extracted_Information']
                if isinstance(info, str):
                    # Clean up the extracted text
                    info = info.replace('{"extracted_text":"', '').rstrip('}')
                    # Split into sections if present
                    sections = info.split('\n\n')
                    for section in sections:
                        if section.strip():
                            st.write(section.strip())
                else:
                    # Handle structured data
                    for key, value in info.items():
                        st.markdown(f"**:green[{key}]:**")
                        st.write(value)
            except Exception as e:
                st.write(row['Extracted_Information'])

def main():
    initialize_session_state()

    # Title Section
    st.title("Advanced AI Data Extraction Tool")
    st.write("Upload your data and extract intelligent insights using AI.")

    # Data Loading Section
    df, source_type, sheet_url = handle_data_source()

    if df is not None:
        # Data Preview Section
        st.header("Preview of uploaded data")
        st.dataframe(df.head(), use_container_width=True)

        # Column Selection above the tabs
        primary_columns = handle_column_selection(df)

        # Processing Section
        prompt = handle_sidebar_controls(df, primary_columns)

        # Process Data Button
        if st.button("Process Data", key="process_data_button", use_container_width=True):
            if not primary_columns:
                st.error("Please select at least one column before processing")
            else:
                results_df = process_data_with_advanced_features(df, prompt, primary_columns)

                if results_df is not None:
                    display_results(results_df)

                    # Google Sheets Integration
                    if source_type == "Google Sheets":
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("Write to Google Sheet", key="write_to_sheets_button"):
                                write_to_sheet(results_df, sheet_url)
                                st.success("Results written to Google Sheet!")

    else:
        st.info("Please select a data source to proceed.")

if __name__ == "__main__":
    main()

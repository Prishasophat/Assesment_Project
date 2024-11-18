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
from utils.web_search import perform_web_search

# Configuration and Constants
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
serpapi_key = os.getenv("SERPAPI_KEY")
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
    if 'selected_fields' not in st.session_state:
        st.session_state.selected_fields = DEFAULT_FIELDS.copy()

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
    st.sidebar.header("Column Selection")
    primary_columns = st.sidebar.multiselect(
        "Select Entity Columns",
        df.columns if df is not None else [],
        help="Select one or more columns to use as entities"
    )
    return primary_columns

def handle_web_search_controls(df):
    st.sidebar.header("Web Search Settings")
    enable_web_search = st.sidebar.checkbox("Enable Web Search Enhancement")
    search_intensity = None
    search_columns = None
    
    if enable_web_search:
        search_intensity = st.sidebar.slider(
            "Search Intensity",
            min_value=1,
            max_value=10,
            value=5,
            help="Higher values will perform more detailed web searches"
        )
        
        search_columns = st.sidebar.multiselect(
            "Select Columns for Web Search",
            df.columns if df is not None else [],
            help="Select specific columns to focus the web search on"
        )
    
    return enable_web_search, search_intensity, search_columns

def handle_generate_prompt_sidebar(df, primary_columns):
    # Combined field selection including both default and custom fields
    selected_fields = st.sidebar.multiselect(
        "Select fields to extract",
        st.session_state.selected_fields,
        default=st.session_state.selected_fields,
        key="fields_select"
    )

    # Update the session state with the current selection
    st.session_state.selected_fields = selected_fields

    if not selected_fields:
        st.sidebar.warning("Please select at least one field to extract.")

    # Text input for new custom field (moved after "Select fields to extract")
    new_custom_field = st.sidebar.text_input("Add new field", key="new_custom_field")
    add_field = st.sidebar.button("Add Field")

    if add_field and new_custom_field and new_custom_field not in st.session_state.selected_fields:
        st.session_state.selected_fields.append(new_custom_field)

    if primary_columns and selected_fields:
        prompt = f"Get me the {', '.join([f'{{{field}}}' for field in selected_fields])} for {', '.join([f'{{{col}}}' for col in primary_columns])}."
    else:
        prompt = ""

    if st.sidebar.checkbox("Show Prompt Preview", key="generate_prompt_preview_checkbox"):
        st.sidebar.text_area("Generated Prompt", prompt, disabled=True, key="generate_prompt_preview")

    return prompt

def handle_sidebar_controls(df, primary_columns):
    prompt_tabs = st.sidebar.radio("Choose Prompt Type", ["Generate Prompt", "Custom Prompt"])

    if prompt_tabs == "Generate Prompt":
        prompt = handle_generate_prompt_sidebar(df, primary_columns)
    else:
        prompt = handle_custom_prompt_sidebar(df)

    return prompt

def handle_custom_prompt_sidebar(df):
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

def process_data_with_advanced_features(df, prompt_template, columns, enable_web_search=False, search_intensity=5, search_columns=None):
    try:
        if not columns:
            st.error("Please select at least one column before processing")
            return None

        with st.spinner("Processing data..."):
            processed_data = []
            for _, row in df.iterrows():
                data_dict = {col: row[col] for col in columns}
                
                # Enhance with web search if enabled
                if enable_web_search and serpapi_key:
                    # Use selected search columns if specified, otherwise use primary columns
                    columns_to_search = search_columns if search_columns else columns
                    search_query = " ".join([str(row[col]) for col in columns_to_search])
                    web_results = perform_web_search(search_query, serpapi_key)
                    # Adjust search depth based on intensity
                    web_context = web_results.get('organic_results', [])[:search_intensity]
                    data_dict['web_context'] = web_context
                
                processed_data.append(data_dict)

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
                    info = info.replace('{"extracted_text":"', '').rstrip('}')
                    sections = info.split('\n\n')
                    for section in sections:
                        if section.strip():
                            st.write(section.strip())
                else:
                    for key, value in info.items():
                        st.markdown(f"**:green[{key}]:**")
                        st.write(value)
            except Exception as e:
                st.write(row['Extracted_Information'])

def main():
    initialize_session_state()

    st.title("Advanced AI Data Extraction Tool")
    st.write("Upload your data and extract intelligent insights using AI.")

    df, source_type, sheet_url = handle_data_source()

    if df is not None:
        st.header("Preview of uploaded data")
        st.dataframe(df.head(), use_container_width=True)

        primary_columns = handle_column_selection(df)
        
        # Add web search controls with column selection
        enable_web_search, search_intensity, search_columns = handle_web_search_controls(df)

        prompt = handle_sidebar_controls(df, primary_columns)

        if st.button("Process Data", key="process_data_button", use_container_width=True):
            if not primary_columns:
                st.error("Please select at least one column before processing")
            else:
                results_df = process_data_with_advanced_features(
                    df, 
                    prompt, 
                    primary_columns,
                    enable_web_search,
                    search_intensity,
                    search_columns
                )

                if results_df is not None:
                    display_results(results_df)

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

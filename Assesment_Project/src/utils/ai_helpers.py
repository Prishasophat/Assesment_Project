from groq import Groq
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import json

GROQ_MODEL = "llama3-70b-8192"
MAX_RETRIES = 3

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=10))
def extract_info_with_groq(data_row, prompt_template, column_names=None):
    """Extract information using Groq API with retry mechanism"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=groq_api_key)

    # Process input data
    if isinstance(data_row, list):
        if column_names is None:
            raise ValueError("column_names must be provided for CSV data")
        data_row = dict(zip(column_names, data_row))

    if isinstance(data_row, dict):
        for column_name, value in data_row.items():
            placeholder = f"{{{column_name}}}"
            prompt_template = prompt_template.replace(placeholder, str(value))
    else:
        raise ValueError("data_row should be a dictionary or a list.")

    # Make API call
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt_template,
        }],
        model=GROQ_MODEL,
    )

    return chat_completion.choices[0].message.content

def format_extraction_prompt(entity, fields):
    """Format prompt based on selected fields"""
    field_list = ", ".join(fields)
    return f"For {entity}, please extract the following information: {field_list}"

def enhance_prompt(prompt_template, context=None, examples=None):
    """Enhances the prompt with context and examples"""
    enhanced_prompt = prompt_template
    
    if context:
        enhanced_prompt = f"Context: {context}\n\n{enhanced_prompt}"
    
    if examples:
        examples_text = "\n".join(f"Example {i+1}: {ex}" for i, ex in enumerate(examples))
        enhanced_prompt = f"{enhanced_prompt}\n\nHere are some examples:\n{examples_text}"
    
    return enhanced_prompt

def batch_process_with_groq(data_rows, prompt_template, column_names):
    results = []
    for row in data_rows:
        try:
            extracted_info = extract_info_with_groq(row, prompt_template, column_names)
            # Ensure the response is properly formatted
            if isinstance(extracted_info, str):
                try:
                    json.loads(extracted_info)
                except:
                    # If not valid JSON, structure it as a simple object
                    extracted_info = {"extracted_text": extracted_info}
            results.append(extracted_info)
        except Exception as e:
            results.append({"error": str(e)})
    return results

# 📊 AI Assessment Project

![GitHub Stars](https://img.shields.io/github/stars/Prishasophat/Assesment_Project)
![GitHub Forks](https://img.shields.io/github/forks/Prishasophat/Assesment_Project)
![License](https://img.shields.io/github/license/Prishasophat/Assesment_Project)

> **Transform your data effortlessly with AI-powered tools.**

---

## 📚 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

---

## 📖 Overview
The **AI Assessment Project** is an intuitive application designed to process datasets from CSV files or Google Sheets. It enables users to analyze data with ease and generate customized prompts for AI-based insights.

---

## ✨ Features
- 📂 Upload CSV files effortlessly.
- 🌐 Link and process Google Sheets in real-time.
- 🔍 Preview datasets with a clean and responsive UI.
- ✏️ Generate prompts or create custom prompts for analysis.
- 🛠️ Export processed data in JSON or CSV format.

---

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Virtual Environment (recommended)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Prishasophat/Assesment_Project.git
   cd Assesment_Project

2. Create and Activate a virtual Enviornment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate

3. Install dependencies:
   ```bash
   pip install -r requirements.txt

## ⚙️ Setup
1. Set up environment variables: Create a .env file in the root directory:    

       touch .env
   
   Add the following keys to the .env file:
   
   ```makefile
   GROQ_API_KEY=your_groq_api_key_here
   GOOGLE_APPLICATION_CREDENTIALS=path_to_your_credentials.json
3. Google Sheets Credentials: 
  Download your credentials.json from the Google Cloud Console.
  Save it in the utils/ folder.
4. Securing Sensitive Files:

   -Add the following files to your .gitignore:
   ```bash
   utils/client-search.json
   utils/create-41115-xxxx.json
   utils/credentials.json
   .env
## 🚀 Usage
1. Run the application:
   ```
   streamlit run app.py
2. Navigate to http://localhost:8501 in your browser.
3. Steps to Use:
  - Upload a CSV or connect to a Google Sheet.
  - Select columns and generate custom prompts.
  - Process data and download the extracted information.

## 🎥 Demo
[Add a YouTube or GIF link demonstrating your project.]

## 🧰 Technologies Used
- Frontend: Streamlit
- AI Backend: Groq
- Google Sheets API: For seamless data integration
- Python Libraries:
    - pandas for data manipulation
    - dotenv for environment variable management
    - json for structured data handling

## 📂Folder Structure

```plaintext
Assesment_Project/
├── app.py               # Main application file
├── utils/
│   ├── google_sheets.py # Google Sheets API helper functions
│   ├── data_processing.py # Data processing utilities
│   ├── ai_helpers.py    # AI prompt processing functions
│   └── client-search.json
│   └── create-41115...json
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (ignored in Git)
├── README.md            # Project documentation







   

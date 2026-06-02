# Education Regulation Impact Analyzer (ERIA)

ERIA is a Streamlit-based analytics dashboard for educational regulations, circulars, and policy documents.
It is designed to help institutions translate dense legislative text into actionable insights, risk indicators, and stakeholder impact summaries.

## Project Structure

- `Home.py` - Main Streamlit landing page with project overview and feature description.
- `pages/ImpactAnalyzer.py` - Secondary Streamlit page for premium document analysis using Google Gemini.
- `Education Regulation Impact Analyzer (ERIA).docx` - Project documentation or proposal.

## Features

- Clean dashboard layout using Streamlit and custom UI styling.
- Document ingestion for PDF circulars.
- Integration with Google Gemini AI for structured document analysis.
- Extraction of policy metrics, stakeholder impacts, risk assessment, and timeline insights.

## Requirements

- Python 3.10+ or compatible Python environment.
- `streamlit`
- `pandas`
- `google-genai` (Google Gemini client library)

You can install all dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install streamlit pandas google-genai
```

3. Set your Google Gemini API key in the environment or enter it in the app sidebar:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

## Running the App

From the project root, run:

```bash
streamlit run Home.py
```

Then open the local Streamlit URL shown in the terminal.

## Usage

- `Home.py` provides an overview of ERIA and its analytics capabilities.
- `pages/ImpactAnalyzer.py` lets you upload a PDF circular and analyze it with Gemini.
- If the API key is not set, the sidebar will prompt you to enter it.

## Notes

- The current app expects uploaded documents in PDF format.
- Gemini integration is required for the premium analysis workflow.
- You may customize the dashboard styling and analysis prompt in `pages/ImpactAnalyzer.py`.

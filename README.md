# GRC Risk Advisor Bot

A one-page Streamlit app that ingests raw audit notes or questionnaire data, calls the OpenAI API,
and returns a structured summary of compliance gaps mapped to insurance-relevant controls.

## Quick start
1. Fork or clone this repo.
2. Fill in your `.env` or set `OPENAI_API_KEY` in your environment.
3. Run locally:

   ```bash
   pip install -r requirements.txt
   streamlit run app.py

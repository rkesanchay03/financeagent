# llm_analyzer.py - Final Version with Intent Classification

import requests
import os
import json
from dotenv import load_dotenv
from stock_fetcher import fetch_detailed_stock_data
from datetime import datetime

# --- Initialization ---
load_dotenv()
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
API_URL = "https://api.perplexity.ai/chat/completions"

if not PERPLEXITY_API_KEY:
    raise ValueError("PERPLEXITY_API_KEY not found. Please set it in your .env file.")

def _call_perplexity_api(prompt, system_message):
    """A centralized helper function to make API calls to Perplexity."""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"API Call Error: {e}")
        return "Sorry, there was an error communicating with the AI. Please try again."

# --- New Function: Intent Classification ---
def classify_intent(question, stock_context):
    stock_suspect = (
        "." in question
        and (question.strip().upper().endswith(".NS") or question.strip().upper().endswith(".BSE"))
        and len(question.strip()) <= 15
    )
    if stock_suspect:
        return "new_report"
    """Uses the LLM to classify the user's intent."""
    context_exists = "Yes" if stock_context else "No"

    system_message = """
    You are an expert at classifying user intent in a financial chatbot.
    Based on the user's question and whether a stock context exists, classify the intent.
    Respond with ONLY ONE of the following three words:
    - `new_report`: If the user is asking for a report on a specific stock ticker.
    - `follow_up`: If the user is asking a question related to the existing stock context.
    - `general_query`: For all other questions, including general financial topics or market trends.
    """

    prompt = f"""
    Stock context exists: {context_exists}
    User question: "{question}"

    Classification:
    """

    intent = _call_perplexity_api(prompt, system_message).strip().lower()

    # Fallback for safety
    if intent not in ['new_report', 'follow_up', 'general_query']:
        return 'general_query'

    return intent

# --- New Function: General Questions ---


def answer_general_question(question):
    """
    Answers any finance question, focusing on Indian markets where relevant.
    """
    prompt = f"""
    As a knowledgeable finance assistant, answer the following user question clearly and concisely. 
    Wherever possible, focus your answer, examples, and context on the Indian markets.

    Question: "{question}"

    Current date: {datetime.now().strftime('%A, %B %d, %Y, %I:%M %p %Z')}
    """
    system_message = "You are a helpful finance expert for all experience levels. Emphasize Indian market relevance whenever possible."
    return _call_perplexity_api(prompt, system_message)


# --- Report Generation ---
def generate_report(symbol):
    print(f"Generating report for {symbol}...")
    data = fetch_detailed_stock_data(symbol)
    if data.get("error"):
        return data["error"], None
    data_json_string = json.dumps(data, indent=2)
    prompt = f"""
    Generate a financial report for the stock: {symbol}, using this JSON data:
    ```
    {data_json_string}
    ```
    **Report Structure:**

        1. **Company Profile & Business Summary**
        - Brief overview of the company's core business, sector, and market positioning. Highlight any recent business developments or changes if present.

        2. **Current Market Performance**
        - Summarize the latest price data (current, open/close, high/low, 52-week range, volume).
        - If available, comment on recent price trends, volatility, and how the stock performed relative to major indices (e.g., NIFTY, SENSEX) or its sector in recent weeks.

        3. **Financial Health & Key Ratios**
        - Analyze profitability, growth, margins, and solvency using available ratios.
        - Give context (“above/below sector average” if possible) and mention any notable trends or changes over recent quarters or years.

        4. **Analyst Consensus & Market Sentiment**
        - Present analyst recommendations and summarize the overall market sentiment (bullish/bearish/neutral).
        - If analyst data is missing, suggest why (e.g., limited coverage, recent listing) and advise on alternative research.

        5. **Recent News & Notable Events**
        - Summarize top news headlines impacting this company (mergers, earnings, regulatory changes, leadership shifts, etc.).
        - Assess whether recent news is likely to be a positive, negative, or neutral catalyst.

        6. **Comparative & Peer Insights**
        - If applicable, compare the company’s financials, performance, or valuation with industry peers.
        - Highlight what sets this company apart (strengths, weaknesses, opportunities, threats).

        7. **AI-Powered Synthesis & Forward-Looking Insights**
        - Summarize investment positives (e.g., strong balance sheet, growth drivers, industry leadership) and key risks (e.g., high leverage, regulatory headwinds).
        - If data allows, offer AI-driven observations on recent trends, potential inflection points, or red flags to monitor.
        - Optionally, suggest key questions an investor should consider based on the data.

        8. **Disclaimer**
        - End with: 'This report is AI-generated and not financial advice.'

        - Today’s date: {datetime.now().strftime('%A, %B %d, %Y, %I:%M %p %Z')}
    """
    report_text = _call_perplexity_api(prompt, "You are an expert financial analyst AI.")
    return report_text, data

def generate_follow_up_answer(question, context):
    print(f"Generating follow-up answer for question: '{question}'")
    context_json_string = json.dumps(context, indent=2)
    prompt = f"""
    You are a helpful financial AI assistant. You have already provided a report on {context['symbol']}.
    The user is now asking a follow-up question.

    **Reference Data:**
    ```
    {context_json_string}
    ```

    **User's Follow-up Question:** "{question}"

    Answer the user's question directly and concisely based primarily on the provided data.
    """
    answer_text = _call_perplexity_api(prompt, "You are a helpful AI assistant answering follow-up financial questions.")
    return answer_text

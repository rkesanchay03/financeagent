# llm_analyzer.py - Final Version with Intent Classification

import requests
import os
import json
from dotenv import load_dotenv
from stock_fetcher import fetch_detailed_stock_data

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
    """Answers a general financial question."""
    system_message = "You are a helpful and knowledgeable financial expert AI. Explain complex topics simply."
    return _call_perplexity_api(question, system_message)

# --- (The rest of your functions remain largely the same) ---
def generate_report(symbol):
    print(f"Generating report for {symbol}...")
    data = fetch_detailed_stock_data(symbol)
    if data.get("error"):
        return data["error"], None
    data_json_string = json.dumps(data, indent=2)
    prompt = f"""
    Generate a  financial report for the stock: {symbol}, using this JSON data:
    ```
    {data_json_string}
    ```
    **Report Structure:**
    1.  **Company Profile & Business Summary** 
    2.  **Current Market Performance**
    3.  **Financial Health & Key Ratios**
    4.  **Analyst Consensus**
    5.  **Recent News Summary**
    6.  **AI-Powered Synthesis & Verdict**
    End with the disclaimer: 'This report is AI-generated and not financial advice.'
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


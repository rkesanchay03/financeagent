import streamlit as st
from llm_analyzer import (
    classify_intent,
    generate_report,
    generate_follow_up_answer,
    answer_general_question,
)

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Finance Agent",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded",
)


# --- Sidebar with Branding, Info & Links ---
with st.sidebar:
    st.markdown(
        """
        <h1 style='text-align:center;color:#00E5FF;'>📊 <span style='color:#00B8D4'>AI Finance Agent</span></h1>
        """,
        unsafe_allow_html=True,
    )
    st.write(
        "Welcome to your AI-powered assistant for Indian markets. Powered by <b>Perplexity AI</b>, <b>yfinance</b>, <b>Finnhub</b>, and <b>Streamlit</b>.",
        unsafe_allow_html=True,
    )
    st.divider()
    st.success(
        "**How to use:**\n"
        "- Type a stock symbol: `RELIANCE.NS`\n"
        "- Ask: `What is its P/E ratio?`\n"
        "- Try a finance question: `What is an ETF?`",
        icon="💡"
    )
    st.warning("AI-generated. Not financial advice.", icon="⚠️")
    st.write("---")
    st.markdown(
        "<small>v1.2 by <a href='https://yourportfolio.example' target='_blank'>Sanchay</a></small>",
        unsafe_allow_html=True,
    )

# --- Welcome Banner in main container ---
st.markdown(
    """
    <div style='background: #121212; border-radius: 8px; padding: 1.25em 1em 0.1em 1em; margin-bottom: 1.6em;'>
        <h2 style='color:#00E5FF; margin-bottom:0;font-size:2em;'>📈 Welcome to Your AI Finance Agent</h2>
        <p style='font-size:1.12em; color:#7FDBFF;margin-bottom:0;font-size:1.2em;'>Ask for reports, ratios, news, finance concepts, or market trends—just like chatting with a finance expert.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Chat History & Smart Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hello! How can I help you with your financial questions today?",
        }
    ]
if "stock_context" not in st.session_state:
    st.session_state.stock_context = None

# --- Render the chat "bubbles" with the requested color codes ---
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(
            f"<div style='background:#12163C; border-radius:10px; padding:1em; margin-top:0.4em; margin-bottom:0.8em; color:#FFFFFF;font-size:1.2em;'><b>🤖 Finance Agent:</b> {message['content']}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background:#D2F1F5; border-radius:10px; padding:1em; margin:0.4em 0 0.8em 30%; text-align:right; color:#004B57;font-size:1.2em;'><b>🧑‍💼 You:</b> {message['content']}</div>",
            unsafe_allow_html=True,
        )

st.write("")  # Keeps scroll to bottom

# --- Chat Input & Main Logic ---
prompt = st.chat_input("💡 Ask about a stock, a finance term, or the market...")

def is_probably_stock_symbol(text):
    if not text:  # Covers None and empty string
        return False
    t = text.strip().upper()
    return (t.endswith('.NS') or t.endswith('.BSE')) and (2 < len(t) <= 12)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.markdown(
        f"<div style='background:#D2F1F5; border-radius:10px; padding:1em; margin:0.4em 0 0.8em 30%; text-align:right; color:#004B57;font-size:1.2em;'><b>You:</b> {prompt}</div>",
        unsafe_allow_html=True,
    ):
        pass

    with st.spinner("Thinking..."):
        try:
            # Always check first if the prompt is likely a stock symbol
            if is_probably_stock_symbol(prompt):
                intent = "new_report"
            else:
                intent = classify_intent(prompt, st.session_state.stock_context)
            
            response = ""
            if intent == "new_report":
                response, data = generate_report(prompt)
                if data and "error" not in data:
                    st.session_state.stock_context = data
                else:
                    st.session_state.stock_context = None
            elif intent == "follow_up" and st.session_state.stock_context:
                response = generate_follow_up_answer(
                    prompt, st.session_state.stock_context
                )
            else:
                response = answer_general_question(prompt)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(
                f"<div style='background:#12163C; border-radius:10px; padding:1em; margin-top:0.4em; margin-bottom:0.8em; color:#FFFFFF;font-size:1.2em;'><b>🤖 Finance Agent:</b> {response}</div>",
                unsafe_allow_html=True,
            )
        except Exception as e:
            error_message = f"Sorry, an unexpected error occurred: <code>{e}</code>"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            st.markdown(
                f"<div style='background:#fdeaea; border-radius:10px; padding:1em; margin-top:0.4em; color:#b00020;'><b>❌ Error:</b> {error_message}</div>",
                unsafe_allow_html=True,
            )

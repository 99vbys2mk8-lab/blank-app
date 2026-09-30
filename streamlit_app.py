import json
import os
import streamlit as st
import urllib.parse

# PWA meta tags and configuration for iOS "Add to Home Screen" support
st.set_page_config(
    page_title="Jarvis Shopper",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inject custom PWA meta tags into the HTML header for iOS home screen support
st.markdown(
    """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Jarvis Shopper">
    <link rel="apple-touch-icon" href="https://imgur.com/3Z5V8p3.png">
    """,
    unsafe_allow_html=True,
)

# File-based memory setup
MEMORY_FILE = "jarvis_shop_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_memory(history):
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

st.title("🛍️ Jarvis Product Scout")
st.write("Your personal shopping assistant. Ask me to find the best gear, parts, or products.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# User input handling
if prompt := st.chat_input("What are you looking for today? (e.g., 'Find me the best oil filter for a GR86')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Intelligent Product Recommendation Logic
    query_lower = prompt.lower()
    
    if any(keyword in query_lower for keyword in ["find", "best", "buy", "filter", "oil", "part", "search", "recommend"]):
        encoded_query = urllib.parse.quote(prompt)
        google_shopping_url = f"https://www.google.com/search?tbm=shop&q={encoded_query}"
        amazon_url = f"https://www.amazon.com/s?k={encoded_query}"
        
        response_text = f"""At your service, sir. Here are the top recommendations based on your request for **"{prompt}"**:

### 🏆 Top Recommendations & Breakdown

1. **OEM / Factory Specification**
   - **Why it's the best:** Ensures absolute compatibility, factory warranty compliance, and precise engineering tolerances without aftermarket guesswork.
   - **Check availability:** [Google Shopping Search]({google_shopping_url}) | [Amazon Search]({amazon_url})

2. **High-Performance Aftermarket Variant**
   - **Why it's the best:** Often upgraded with superior materials (like synthetic filtration media or higher flow rates) designed for intensive use or track conditions.
   - **Check availability:** [Google Shopping Search]({google_shopping_url})

### 💡 Quick Advice
Always verify part numbers or model specifications against your specific year and trim before pulling the trigger. Let me know if you want me to look up alternative brands or specs!"""
    else:
        response_text = f"Analyzing your request: '{prompt}'. To look up products, try phrasing your prompt with words like 'Find the best...' or 'Search for...'"

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text, unsafe_allow_html=True)

    # Save updated history to file
    save_memory(st.session_state.messages)

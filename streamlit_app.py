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
if prompt := st.chat_input("What are you looking for today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Universal Product Scout Logic (Triggers on any query)
    encoded_query = urllib.parse.quote(prompt)
    google_shopping_url = f"https://www.google.com/search?tbm=shop&q={encoded_query}"
    amazon_url = f"https://www.amazon.com/s?k={encoded_query}"
    
    # Custom intelligence injection for specific car parts or general requests
    if "brake" in prompt.lower() or "pad" in prompt.lower():
        breakdown_text = """### 🏆 Top Recommendations & Breakdown
1. **OEM / Street Performance Compound**
   - **Why it's the best:** Offers balanced initial bite, low dust, and reliable cold-stopping power for daily driving without squealing.
   - **Check availability:** [Google Shopping]({google_shopping_url}) | [Amazon]({amazon_url})

2. **Track-Day / High-Friction Compound (e.g., EBC Redstuff/Yellowstuff or Project Mu)**
   - **Why it's the best:** Higher temperature threshold and aggressive bite designed to prevent brake fade under heavy canyon carving or track sessions.
   - **Check availability:** [Google Shopping Search]({google_shopping_url})"""
    else:
        breakdown_text = f"""### 🏆 Top Recommendations & Breakdown
1. **Top-Rated Performance Pick**
   - **Why it's the best:** Balances superior material quality, reliability, and user ratings for maximum value.
   - **Check availability:** [Google Shopping]({google_shopping_url}) | [Amazon]({amazon_url})

2. **OEM Factory Standard**
   - **Why it's the best:** Direct manufacturer fitment with zero modification required and guaranteed factory compatibility.
   - **Check availability:** [Google Shopping Search]({google_shopping_url})"""

    response_text = f"""At your service, sir. Here is the breakdown for **"{prompt}"**:

{breakdown_text}

### 💡 Quick Advice
Always cross-reference part numbers with your specific vehicle year and trim. Click the links above to view live pricing and options!"""

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text, unsafe_allow_html=True)

    # Save updated history to file
    save_memory(st.session_state.messages)

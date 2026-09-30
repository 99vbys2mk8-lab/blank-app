import json
import os
import streamlit as st

# PWA meta tags and configuration for iOS "Add to Home Screen" support
st.set_page_config(
    page_title="Jarvis",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inject custom PWA meta tags into the HTML header for iOS home screen support
st.markdown(
    """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Jarvis">
    <link rel="apple-touch-icon" href="https://imgur.com/3Z5V8p3.png">
    """,
    unsafe_allow_html=True,
)

# File-based memory setup
MEMORY_FILE = "jarvis_memory.json"


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


st.title("🤖 Jarvis Command Center")
st.write(
    "Your persistent mobile assistant. Add this app to your iOS Home Screen"
    " for quick access."
)

# Initialize chat history
if "messages" not in st.session_state:
  st.session_state.messages = load_memory()

# Display chat history
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User input handling
if prompt := st.chat_input("What would you like, sir?"):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Generate intelligent assistant response
  response = f"At your service, sir. I have logged your command: '{prompt}'. All systems are fully operational."
  st.session_state.messages.append({"role": "assistant", "content": response})

  with st.chat_message("assistant"):
    st.markdown(response)

  # Save updated history to file
  save_memory(st.session_state.messages)

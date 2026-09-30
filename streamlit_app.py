import json
import os
import streamlit as st
import requests

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
st.write("Your persistent mobile assistant with research & generation capabilities.")

# Sidebar for API keys if needed
with st.sidebar:
    st.subheader("Configuration")
    api_key = st.text_input("OpenRouter / API Key (Optional)", type="password")
    st.write("Enter your API key to enable live, unrestricted model routing.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image_url" in message and message["image_url"]:
            try:
                st.image(message["image_url"])
            except Exception:
                st.write("*(Image preview unavailable)*")

# User input handling
if prompt := st.chat_input("What would you like, sir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if the user is asking for an image generation
    if prompt.lower().startswith(("image:", "generate:", "draw:", "create image:")):
        image_prompt = prompt.split(":", 1)[1].strip() if ":" in prompt else prompt
        response_text = f"Generating visual asset for: '{image_prompt}'"
        
        # Use Pollinations direct image URL format with width/height parameters for stability
        safe_prompt = requests.utils.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text, 
            "image_url": image_url
        })
        
        with st.chat_message("assistant"):
            st.markdown(response_text)
            st.image(image_url)
    else:
        # Standard research/text response handling
        if api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "deepseek/deepseek-chat", 
                    "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                }
                res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                data = res.json()
                response_text = data["choices"][0]["message"]["content"]
            except Exception as e:
                response_text = f"Error connecting to API gateway: {str(e)}"
        else:
            if "gr86" in prompt.lower():
                response_text = "Regarding the Toyota GR86 filter: Common OEM and aftermarket options include the Toyota OEM oil filter (Suits FA24 engine, part # SU003-04702) or K&N PS-7035 / HKS hybrid filters for improved flow."
            else:
                response_text = f"Analyzing query: '{prompt}'. To unlock full live model inference and deep research, add your OpenRouter API key in the sidebar, or generate images by typing 'generate: [your idea]'."

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)

    # Save updated history to file
    save_memory(st.session_state.messages)

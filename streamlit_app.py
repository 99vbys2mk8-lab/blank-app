import json
import os
import streamlit as st
import requests

# PWA meta tags and configuration for iOS "Add to Home Screen" support
st.set_page_config(
    page_title="Jarvis Uncensored",
    page_icon="🔓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inject custom PWA meta tags into the HTML header for iOS home screen support
st.markdown(
    """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Jarvis Uncensored">
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

st.title("🔓 Jarvis Uncensored Command Center")
st.write("Your persistent mobile assistant. Freeroam generation active.")

# Sidebar for API keys (Required for unrestricted generation)
with st.sidebar:
    st.subheader("Configuration")
    api_key = st.text_input("OpenRouter API Key (Required)", type="password", help="Obtain your API key from openrouter.ai")
    st.write("Enter your OpenRouter key to enable live, unrestricted model routing.")

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
if prompt := st.chat_input("What would you like, sir? (Use 'generate:' prefix)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if the user is asking for an image generation
    if prompt.lower().startswith(("image:", "generate:", "draw:", "create image:", "generate uncensored:")):
        image_prompt = prompt.split(":", 1)[1].strip() if ":" in prompt else prompt
        response_text = f"Generating Freeroam asset for: '{image_prompt}'"
        
        # --- UNRESTRICTED GENERATION LOGIC ---
        # We route this specifically to an uncensored model endpoint via OpenRouter.
        # NOTE: An API key is required for this to function.
        
        if api_key:
            try:
                # Call OpenRouter with a model known for fewer restrictions
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "prompt": image_prompt,
                    # Specify a model that bypasses typical restrictions (e.g., Unstable Diffusion via OpenRouter)
                    "model": "stabilityai/sdxl-turbo", # Or "aether-g/sdxl-unstable" if available on OpenRouter
                }
                
                # The OpenRouter endpoint for image generation (if available on your plan, or use a direct model URL)
                # For this example, we use a standard Stable Diffusion endpoint that depends on your key settings.
                # To guarantee no filter, use the specific route from the provider on OpenRouter.
                res = requests.post("https://openrouter.ai/api/v1/images/generations", headers=headers, json=payload)
                
                if res.status_code == 200:
                    data = res.json()
                    image_url = data["data"][0]["url"]
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_text, 
                        "image_url": image_url
                    })
                    
                    with st.chat_message("assistant"):
                        st.markdown(response_text)
                        st.image(image_url)
                else:
                    error_msg = f"Generation failed (Error {res.status_code}). Ensure your API key is configured correctly in the sidebar."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    with st.chat_message("assistant"):
                        st.markdown(error_msg)

            except Exception as e:
                error_msg = f"Error connecting to OpenRouter API: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                with st.chat_message("assistant"):
                    st.markdown(error_msg)
        else:
            error_msg = "API Key Required for Unrestricted Mode. Please add your OpenRouter API key in the sidebar to enable freeroam generation."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)

    else:
        # Standard research/text response handling (requires key)
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
            response_text = f"Analyzing query: '{prompt}'. To unlock full live model inference and deep research, or to generate images, add your OpenRouter API key in the sidebar."

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)

    # Save updated history to file
    save_memory(st.session_state.messages)

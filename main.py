import streamlit as st
import os
from litellm import completion
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the Streamlit app
st.title("Multi-LLM Chat Application")

# Initialize session state if not already done
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Get API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Allow manual entry if environment variables aren't set
if not openai_api_key:
    openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
if not gemini_api_key:
    gemini_api_key = st.text_input("Enter your Google Gemini API Key:", type="password")

# Set up the sidebar
st.sidebar.title("Settings")

# Create fields for system prompt and user prompt
system_prompt = st.sidebar.text_area("System Prompt (instructions for the AI):", 
    value="You are a helpful assistant. Answer the user's question concisely and accurately.")

# Create a model selector
st.sidebar.subheader("Select LLMs")
use_chatgpt = st.sidebar.checkbox("ChatGPT (GPT-4o)", value=True)
use_gemini = st.sidebar.checkbox("Google Gemini", value=True)

# Main chat interface
st.subheader("Chat")

# Display chat history
for entry in st.session_state.chat_history:
    if entry["role"] == "user":
        st.chat_message("user").write(entry["content"])
    elif entry["role"] == "ChatGPT":
        st.chat_message("assistant", avatar="🔵").write(entry["content"])
    elif entry["role"] == "Gemini":
        st.chat_message("assistant", avatar="🟢").write(entry["content"])

# Get user input
user_input = st.chat_input("Type your message here...")

# Process user input
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    
    # Check if at least one LLM is selected
    if not (use_chatgpt or use_gemini):
        st.warning("Please select at least one LLM model.")
    else:
        messages = [{"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": user_input}]
        
        # Get ChatGPT response if selected and API key provided
        if use_chatgpt and openai_api_key:
            try:
                with st.spinner("ChatGPT is thinking..."):
                    gpt_response = completion(
                        model="gpt-4o", 
                        messages=messages, 
                        api_key=openai_api_key
                    )
                    gpt_content = gpt_response.choices[0].message.content
                    st.session_state.chat_history.append({"role": "ChatGPT", "content": gpt_content})
                    st.chat_message("assistant", avatar="🔵").write(gpt_content)
            except Exception as e:
                st.error(f"Error with ChatGPT: {str(e)}")
        
        # Get Gemini response if selected and API key provided
        if use_gemini and gemini_api_key:
            try:
                with st.spinner("Gemini is thinking..."):
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    gemini_messages = [{"role": "user", "parts": [system_prompt + "\n\n" + user_input]}]
                    gemini_response = model.generate_content(gemini_messages)
                    gemini_content = gemini_response.text
                    st.session_state.chat_history.append({"role": "Gemini", "content": gemini_content})
                    st.chat_message("assistant", avatar="🟢").write(gemini_content)
            except Exception as e:
                st.error(f"Error with Gemini: {str(e)}")

# Add information about the app
st.sidebar.title("About this app")

st.sidebar.write(
    "This app allows you to interact with multiple Language Models (LLMs) "
    "and compare their responses."
)

st.sidebar.subheader("Key features:")
st.sidebar.markdown(
    """
    - Select between ChatGPT and Google Gemini (or both)
    - Customize the system prompt to guide AI responses
    - View responses in a chat-like interface
    - Compare how different models respond to the same prompts
    """
)

# Add a clear button to reset the chat
if st.sidebar.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()
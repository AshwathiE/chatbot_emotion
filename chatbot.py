import streamlit as st
import os
from groq import Groq
import pyttsx3

# Set page title
st.set_page_config(page_title="🦙💬 Llama 3 Chatbot (Groq Edition)")

# Sidebar UI
with st.sidebar:
    st.title('🦙💬 Llama 3 Chatbot (Groq)')
    st.write('This chatbot uses Meta’s Llama 3 model served through Groq API.')
    if 'GROQ_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        groq_api = st.secrets['GROQ_API_KEY']
    else:
        groq_api = st.text_input('Enter Groq API key:', type='password')
        if not groq_api.startswith('gsk_'):
            st.warning('Please enter a valid Groq API key!', icon='⚠️')
        else:
            st.success('Proceed to enter your prompt message!', icon='👉')
    os.environ['GROQ_API_KEY'] = groq_api

    st.subheader('Model and Parameters')
    selected_model = st.selectbox('Choose a Llama3 model', ['llama3-8b-8192', 'llama3-70b-8192'], key='selected_model')
    temperature = st.slider('temperature', min_value=0.01, max_value=1.0, value=0.2, step=0.01)
    top_p = st.slider('top_p', min_value=0.01, max_value=1.0, value=0.95, step=0.01)
    st.markdown('[🔗 Groq API Docs](https://console.groq.com/docs)')

    st.subheader('Recent Topics')
    if "messages" in st.session_state:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                # Extract topic: first sentence or up to 30 chars
                topic = msg["content"].split(".\n")[0].split(". ")[0].split("\n")[0].strip()
                if not topic:
                    topic = msg["content"][:30]
                if len(topic) > 30:
                    topic = topic[:30] + '…'
                st.markdown(f"🔎 {topic}")

    st.subheader('Chatbot Sentiment')
    sentiment = st.selectbox('Choose a sentiment/personality:', ['Friendly', 'Mentor', 'Sarcastic'], index=0)

    voice_gender = st.radio('Voice Gender', ['Male', 'Female'], index=0)

# Initialize Groq client
client = Groq(api_key=os.environ['GROQ_API_KEY'])

# Session state messages
if "messages" not in st.session_state:
    # Set system prompt based on sentiment
    system_prompts = {
        'Friendly': "You are a helpful, friendly, and positive AI assistant. Respond in a warm and approachable manner.",
        'Mentor': "You are a wise mentor. Respond with guidance, encouragement, and constructive advice.",
        'Sarcastic': "You are a witty, sarcastic AI. Respond with clever, dry humor, but still answer the question."
    }
    st.session_state.messages = [{
        "role": "system",
        "content": system_prompts.get(sentiment, system_prompts['Friendly'])
    }, {"role": "assistant", "content": "How may I assist you today?"}]

# If sentiment changes, update system prompt
if 'last_sentiment' not in st.session_state:
    st.session_state.last_sentiment = sentiment
if sentiment != st.session_state.last_sentiment:
    system_prompts = {
        'Friendly': "You are a helpful, friendly, and positive AI assistant. Respond in a warm and approachable manner.",
        'Mentor': "You are a wise mentor. Respond with guidance, encouragement, and constructive advice.",
        'Sarcastic': "You are a witty, sarcastic AI. Respond with clever, dry humor, but still answer the question."
    }
    # Replace or update the system message
    st.session_state.messages[0] = {
        "role": "system",
        "content": system_prompts.get(sentiment, system_prompts['Friendly'])
    }
    st.session_state.last_sentiment = sentiment

# Display chat
st.subheader('Chat History')
if st.button('🧹 Clear Chat History'):
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Clear history button
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button("🧹 Clear Chat", on_click=clear_chat_history)

# Generate response from Groq
def generate_groq_response():
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    response = client.chat.completions.create(
        model=selected_model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=1024
    )
    return response.choices[0].message.content

def speak_text(text, gender='Male'):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Select voice by gender
    if gender == 'Female':
        for v in voices:
            if 'female' in v.name.lower() or v.gender == 'VoiceGenderFemale':
                engine.setProperty('voice', v.id)
                break
    else:
        for v in voices:
            if 'male' in v.name.lower() or v.gender == 'VoiceGenderMale':
                engine.setProperty('voice', v.id)
                break
    engine.say(text)
    engine.runAndWait()

# Chat input
if prompt := st.chat_input(disabled=not groq_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Respond with Groq model
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            full_response = generate_groq_response()
            st.markdown(full_response)
            # Voice output
            speak_text(full_response, gender=voice_gender)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
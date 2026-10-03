import streamlit as st
import asyncio
from agent import agent  # استدعاء الـ Agent المباشر

st.set_page_config(page_title="AI Agent Demo", page_icon="🤖")
st.title("🤖 Chatbot Demo")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اكتب استفسارك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير..."):
            try:
                # تشغيل الـ Agent المباشر
                response = asyncio.run(agent.run(prompt))
                bot_response = response.data
            except Exception as e:
                bot_response = f"حدث خطأ: {e}"
            
            st.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
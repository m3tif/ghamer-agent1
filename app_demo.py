import streamlit as st
from agent import get_agent_response

# إعدادات الواجهة
st.set_page_config(page_title="Ghamer AI Agent", page_icon="🤖")
st.title("🤖 Chatbot Demo - Ghamer Agency")

# تخزين وسجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال السؤال من المستخدم
if prompt := st.chat_input("اكتب استفسارك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد الرد من الـ Agent
    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير..."):
            bot_response = get_agent_response(prompt)
            st.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})

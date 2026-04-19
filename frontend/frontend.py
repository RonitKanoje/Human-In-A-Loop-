# frontend.py
import sys
import os
import streamlit as st  

# Force Python to include project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="Stock AI Assistant", layout="centered")



import streamlit as st
from backend.chatbot import run_chat


st.title("📈 Stock AI Assistant (LangGraph + HITL)")

# -------------------
# Session State
# -------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None

# -------------------
# Display Chat History
# -------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------
# User Input
# -------------------
user_input = st.chat_input("Ask about stocks...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    result = run_chat(user_input)

    # Check interrupt
    interrupts = result.get("__interrupt__", [])

    if interrupts:
        st.session_state.pending_interrupt = interrupts[0].value

    else:
        response = result["messages"][-1].content

        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.write(response)

# -------------------
# HANDLE HUMAN APPROVAL (HITL)
# -------------------
if st.session_state.pending_interrupt:
    st.warning(st.session_state.pending_interrupt)

    col1, col2 = st.columns(2)

    if col1.button("✅ Yes"):
        result = run_chat(None, resume="yes")

        response = result["messages"][-1].content

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.pending_interrupt = None
        st.rerun()

    if col2.button("❌ No"):
        result = run_chat(None, resume="no")

        response = result["messages"][-1].content

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.pending_interrupt = None
        st.rerun()  
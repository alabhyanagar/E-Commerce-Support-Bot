# app.py - HelloQ AI Support Assistant Streamlit Web Interface
import streamlit as st
from agent import HelloQSupportAgent

# Page Configuration
st.set_page_config(
    page_title="HelloQ AI Support Assistant",
    page_icon="🌈",
    layout="centered"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #E91E63;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">HelloQ Support Assistant 🌈</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Inclusive LGBTQIA+ Platform Support & Account Concierge</div>', unsafe_allow_html=True)

# Initialize Session State
if "agent" not in st.session_state:
    st.session_state.agent = HelloQSupportAgent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your HelloQ Support Assistant. How can I help you today with your account, perks, or privacy settings?"
        }
    ]

# Sidebar Controls
st.sidebar.header("Demo User Session")
selected_user = st.sidebar.selectbox(
    "Active Account:",
    options=["user_101", "user_102"],
    format_func=lambda x: "user_101 (Alex Taylor - Gold Tier)" if x == "user_101" else "user_102 (Jordan Smith - Free Tier)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Quick Prompt Ideas:**")
if st.sidebar.button("Restore Super Likes"):
    st.session_state.prompt_input = "My Super Likes didn't refresh today after my renewal. Can you fix this?"

if st.sidebar.button("Enable Discreet Mode"):
    st.session_state.prompt_input = "How do I turn on Discreet Mode and mask my app icon?"

if st.sidebar.button("Pronoun Settings"):
    st.session_state.prompt_input = "How many pronouns can I display on my profile?"

# Handle sidebar button click prompt insertion
prompt_to_submit = None
if "prompt_input" in st.session_state and st.session_state.prompt_input:
    prompt_to_submit = st.session_state.prompt_input
    del st.session_state["prompt_input"]

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Handling via Chat Box or Sidebar Shortcuts
user_input = st.chat_input("Ask a question about HelloQ...")

# Determine effective prompt
effective_prompt = prompt_to_submit or user_input

if effective_prompt:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": effective_prompt})
    with st.chat_message("user"):
        st.markdown(effective_prompt)

    # Generate Agent Response
    with st.chat_message("assistant"):
        with st.spinner("Consulting HelloQ services & knowledge base..."):
            response_text = st.session_state.agent.chat(effective_prompt, user_id=selected_user)
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
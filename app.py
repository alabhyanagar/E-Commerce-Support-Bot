"""
app.py - Streamlit Web UI for E-Commerce AI Customer Support
Provides chat interface, quick demo buttons, order lookup tools, and sidebar tools.
"""

import streamlit as st
import mock_db
# Import your agent module (Ensure agent.py is updated in your project)
from agent import process_user_message

# Page Configuration
st.set_page_config(
    page_title="E-Commerce Support Assistant",
    page_icon="🛒",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E88E5; }
    .sub-title { font-size: 1rem; color: #555555; margin-bottom: 20px; }
    .stChatMessage { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
# ---------------------------------------------------------------------------
# INITIALIZE PROCESSING STATE
# ---------------------------------------------------------------------------
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! 👋 I'm your E-Commerce AI Support Assistant. How can I help you today? You can ask me to track orders, check returns policy, search products, or raise support tickets!"
        }
    ]

if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = "user_101"

# ---------------------------------------------------------------------------
# SIDEBAR DASHBOARD
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🛍️ Customer Portal")
    st.caption("E-Commerce Assistant Controls & Utilities")
    
    # Active User Simulator
    st.subheader("👤 Demo User Profile")
    user_choice = st.selectbox(
        "Active Customer Account:",
        ["user_101 (Alabhya)", "user_102 (Priya)"]
    )
    st.session_state.current_user_id = "user_101" if "user_101" in user_choice else "user_102"
    
    st.divider()

    # Quick Orders Overview
    st.subheader("📦 Your Recent Orders")
    user_orders = {
        oid: details for oid, details in mock_db.MOCK_ORDERS.items() 
        if details["user_id"] == st.session_state.current_user_id
    }
    
    for oid, details in user_orders.items():
        with st.expander(f"{oid} - {details['product_name'][:20]}..."):
            st.write(f"**Status:** {details['status']}")
            st.write(f"**Price:** {details['price']}")
            if "expected_delivery" in details:
                st.write(f"**Delivery:** {details['expected_delivery']}")

    st.divider()

# Sample Quick Prompts Macro Buttons (Disabled while processing)
    st.subheader("🚀 Quick Test Prompts")
    
    if st.button("📦 Track Order ORD1001", disabled=st.session_state.is_processing):
        st.session_state.prompt_input = "Can you give me the latest tracking status for my order ORD1001?"
        
    if st.button("⚠️ Damaged Item / Ticket", disabled=st.session_state.is_processing):
        st.session_state.prompt_input = "I received order ORD1002 with a damaged box. Please raise a ticket."

    if st.button("🔄 Return Policy Query", disabled=st.session_state.is_processing):
        st.session_state.prompt_input = "What is your return policy for electronics and how many days do I have?"

    if st.button("🔍 Search Headphones", disabled=st.session_state.is_processing):
        st.session_state.prompt_input = "Do you have any wireless noise-cancelling headphones in stock under ₹5000?"

    if st.button("🗑️ Clear Chat History", disabled=st.session_state.is_processing):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chat history cleared! How can I assist you today?"
            }
        ]
        st.rerun()

# ---------------------------------------------------------------------------
# MAIN CHAT INTERFACE
# ---------------------------------------------------------------------------
st.markdown("<div class='main-title'>🛒 E-Commerce Customer Support Agent</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Ask about order tracking, return & refund policies, warranties, or search product inventory.</div>", unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------------------------
# MAIN CHAT INPUT & PROCESSING LOGIC
# ---------------------------------------------------------------------------
# Check for quick prompt trigger from sidebar
if "prompt_input" in st.session_state and st.session_state.prompt_input:
    if not st.session_state.is_processing:
        st.session_state.pending_prompt = st.session_state.prompt_input
        st.session_state.prompt_input = None
        st.session_state.is_processing = True
        st.rerun()

# Chat input is disabled while is_processing is True
user_prompt = st.chat_input(
    "Type your question here (e.g., 'Track order ORD1001')...", 
    disabled=st.session_state.is_processing
)

# If user typed something and hit enter
if user_prompt and not st.session_state.is_processing:
    st.session_state.pending_prompt = user_prompt
    st.session_state.is_processing = True
    st.rerun()  # Instantly locks input box and refreshes UI before processing

# EXECUTION BLOCK (Runs safely while input is locked)
# EXECUTION BLOCK in app.py
if st.session_state.pending_prompt:
    current_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None  # Clear pending prompt

    # 1. Append user message to history first so Gemini sees it
    st.session_state.messages.append({"role": "user", "content": current_prompt})
    with st.chat_message("user"):
        st.markdown(current_prompt)

    # 2. Generate & Display Assistant Response (Passing full message history)
    with st.chat_message("assistant"):
        with st.spinner("Searching store database and policies..."):
            try:
                response_text = process_user_message(
                    messages=st.session_state.messages,
                    user_id=st.session_state.current_user_id
                )
            except Exception as e:
                response_text = f"⚠️ **An error occurred:** {str(e)}"
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # 3. Unlock system and refresh UI
    st.session_state.is_processing = False
    st.rerun()
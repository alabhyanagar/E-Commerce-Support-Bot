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

    # Sample Quick Prompts Macro Buttons
    st.subheader("🚀 Quick Test Prompts")
    
    if st.button("📦 Track Order ORD1001"):
        st.session_state.prompt_input = "Can you give me the latest tracking status for my order ORD1001?"
        
    if st.button("⚠️ Damaged Item / Ticket"):
        st.session_state.prompt_input = "I received order ORD1002 with a damaged box. Please raise a ticket."

    if st.button("🔄 Return Policy Query"):
        st.session_state.prompt_input = "What is your return policy for electronics and how many days do I have?"

    if st.button("🔍 Search Headphones"):
        st.session_state.prompt_input = "Do you have any wireless noise-cancelling headphones in stock under ₹5000?"

    if st.button("🗑️ Clear Chat History"):
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

# Handle Quick Prompt Input from Sidebar Buttons
user_prompt = st.chat_input("Type your question here (e.g., 'Track order ORD1001')...")
if "prompt_input" in st.session_state and st.session_state.prompt_input:
    user_prompt = st.session_state.prompt_input
    st.session_state.prompt_input = None  # Reset trigger

# Process User Input
if user_prompt:
    # Display User Message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate & Display Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Searching store database and policies..."):
            try:
                response_text = process_user_message(
                    user_message=user_prompt,
                    user_id=st.session_state.current_user_id
                )
            except Exception as e:
                response_text = f"⚠️ **An error occurred:** {str(e)}"
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
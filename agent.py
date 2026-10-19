"""
agent.py - Gemini Agent & Tool Execution for E-Commerce Support Bot
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import mock_db
import rag_engine

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """
You are the official E-Commerce Customer Support AI Concierge.
You assist customers with order tracking, support tickets, product searches, and return policies.

CRITICAL BEHAVIOR:
- Maintain full conversational memory. If the user previously mentioned an Order ID (like ORD1001), remember it across subsequent turns.
- Customers can ONLY look up their own orders and tickets. 
- If a user asks about returns, warranties, or shipping timelines, query the knowledge base first using `search_knowledge_base`.
"""

def search_knowledge_base(query: str) -> str:
    """Searches store policies using ChromaDB RAG."""
    try:
        results = rag_engine.query_rag(query)
        return results if results else "No specific policy document found."
    except Exception as e:
        return f"Error: {str(e)}"

def process_user_message(messages: list, user_id: str) -> str:
    """Processes the full conversation history, maintaining memory and secure tool bindings."""
    
    # Define secure tool wrappers capturing the current user_id
    def secure_get_order_details(order_id: str):
        """Retrieves tracking status for an order ID belonging to the current user."""
        return mock_db.get_order_details(order_id=order_id, user_id=user_id)

    def secure_raise_support_ticket(order_id: str, issue_description: str):
        """Raises a support ticket for an order belonging to the current user."""
        return mock_db.raise_support_ticket(user_id=user_id, order_id=order_id, issue_description=issue_description)

    def secure_get_ticket_status(ticket_id: str):
        """Checks status of a support ticket belonging to the current user."""
        return mock_db.get_ticket_status(ticket_id=ticket_id, user_id=user_id)

    tools_list = [
        secure_get_order_details,
        secure_raise_support_ticket,
        secure_get_ticket_status,
        mock_db.search_products,
        search_knowledge_base
    ]

    # Format Streamlit message history into Gemini's expected role/parts structure
    formatted_contents = []
    
    # Prepend active customer context into the system instruction or first prompt context
    for i, msg in enumerate(messages):
        role = "user" if msg["role"] == "user" else "model"
        text = msg["content"]
        
        # If it's the very first user message, tag the active customer ID for background context
        if i == 0 and role == "user":
            text = f"[Active Customer ID: {user_id}]\n{text}"
            
        formatted_contents.append({
            "role": role,
            "parts": [{"text": text}]
        })

    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=formatted_contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools_list,
            temperature=0.3,
        )
    )
    
    return response.text
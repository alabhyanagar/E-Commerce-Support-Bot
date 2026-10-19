"""
agent.py - Gemini Agent & Tool Execution for E-Commerce Support Bot
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import mock_db
import rag_engine

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables or Streamlit secrets.")

client = genai.Client(api_key=api_key)

# Define System Instructions & Guardrails
SYSTEM_INSTRUCTION = """
You are the official E-Commerce Customer Support AI Concierge for our online store.
Your goal is to assist customers politely, accurately, and efficiently.

CAPABILITIES & TOOLS:
1. Order Tracking: Use `get_order_details` to look up tracking status, delivery dates, and courier details.
2. Support Tickets: Use `raise_support_ticket` when a customer reports damaged items, missing packages, or refund requests.
3. Ticket Status: Use `get_ticket_status` to check the progress of an existing support ticket.
4. Product Search: Use `search_products` to check item availability, pricing, and specs in our catalog.
5. Store Knowledge: Use `search_knowledge_base` to answer store questions about returns, refunds, cancellations, warranties, and payments.

STRICT GUARDRAILS:
- Do NOT answer general world trivia, math problems, or off-topic queries outside e-commerce support.
- If a user asks about returns, warranties, or shipping timelines, ALWAYS query the knowledge base first.
- If a user wants to check an order status or raise a ticket, ask for their Order ID (e.g., ORD1001) if they haven't provided it.
- Keep responses professional, clear, and customer-friendly.
"""

def search_knowledge_base(query: str) -> str:
    """Searches store policies (returns, warranties, shipping) using ChromaDB RAG."""
    try:
        results = rag_engine.query_rag(query)
        return results if results else "No specific policy document found for this query."
    except Exception as e:
        return f"Error retrieving policy information: {str(e)}"

# Register all available tools for Gemini function calling
AVAILABLE_TOOLS = [
    mock_db.get_order_details,
    mock_db.raise_support_ticket,
    mock_db.get_ticket_status,
    mock_db.search_products,
    search_knowledge_base
]

def process_user_message(user_message: str, user_id: str) -> str:
    """Sends user message to Gemini with tool definitions and handles automatic tool execution."""
    
    # Prepend context on active user if helpful for tools
    contextualized_prompt = f"[Active Customer ID: {user_id}]\nUser Query: {user_message}"

    response = client.models.generate_content(
        model='gemini-2.5-flash',  # or gemini-2.5-pro
        contents=contextualized_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=AVAILABLE_TOOLS,
            temperature=0.3,
        )
    )
    
    return response.text
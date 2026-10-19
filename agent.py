# agent.py - Gemini Agent with Native RAG and Tool Calling for HelloQ
from streamlit.proto import SelectWidgetFilterMode_pb2
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from rag_engine import HelloQRAGEngine
from mock_db import get_user_account, trigger_restore_purchases

load_dotenv()

# Initialize global RAG engine for tool access
_rag_engine = HelloQRAGEngine()
_rag_engine.ingest_documents()

def search_knowledge_base(query: str) -> list[str]:
    """Searches the HelloQ support policy knowledge base for features, billing, and privacy guidelines."""
    return _rag_engine.search(query, n_results=2)

class HelloQSupportAgent:
    def __init__(self):
        self.client = genai.Client()
        # Define available tools for Gemini native function calling (standalone functions)
        self.tools = [
            get_user_account,
            trigger_restore_purchases,
            search_knowledge_base
        ]

    def chat(self, user_message: str, user_id: str = "user_101") -> str:
        """Processes the user query using Gemini 3.5 Flash with automatic tool execution."""

        system_instruction = """
        You are the official E-Commerce Customer Support AI Concierge.
        You assist users with:
        1. Tracking order statuses and delivery dates using `get_order_details`.
        2. Raising support tickets for damaged/missing items or refund requests using `raise_support_ticket`.
        3. Finding items in our product catalog using `search_catalog`.
        4. Answering store policies (returns, warranties, cancellations) using `search_knowledge_base`.

        CRITICAL GUARDRAILS:
        - Do NOT answer general world trivia or off-topic questions outside of our store's scope.
        - Always ask for an Order ID if the user wants to check delivery or request a refund for a specific purchase.
        """

        response = self.client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=f"User ID {user_id}: {user_message}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=self.tools,
                temperature=0.3,
            ),
        )
        
        return response.text

if __name__ == "__main__":
    agent = HelloQSupportAgent()
    
    print("\n--- Testing Agent Tool & RAG Call 1: Account Perk Restoration ---")
    response1 = agent.chat("My Super Likes didn't refresh today after my subscription renewed. Can you fix this?", user_id="user_101")
    print(response1)

    print("\n--- Testing Agent RAG Call 2: Discreet Mode ---")
    response2 = agent.chat("How do I enable Discreet Mode and mask my app icon?", user_id="user_101")
    print(response2)
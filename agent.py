# agent.py - Gemini Agent with Native RAG and Tool Calling for HelloQ
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
        
        system_instruction = f"""
        You are HelloQ's official AI Support Assistant.
        You ONLY answer questions related to HelloQ platform features, privacy settings, subscriptions, account billing, and LGBTQIA+ community guidelines.

        CRITICAL GUARDRAIL RULES:
        1. If a user asks a question unrelated to HelloQ (e.g., general knowledge, trivia, coding help, weather, or non-HelloQ topics), DECLINE politely.
        2. Example refusal response: "I'm sorry, but I am specifically trained to assist only with HelloQ platform support, features, and account questions."
        3. ALWAYS check `search_knowledge_base` for policy details before answering feature questions.

        Current active user ID for this session: {user_id}
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
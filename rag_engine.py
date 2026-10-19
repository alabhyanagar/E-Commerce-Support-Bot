# rag_engine.py - ChromaDB RAG Vector Store Manager
import os
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()

class HelloQRAGEngine:
    def __init__(self, persist_directory="./chroma_db"):
        # Initialize ChromaDB client (local persistent storage)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "helloq_support_docs"
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        
        # Initialize Google GenAI client for embeddings
        self.genai_client = genai.Client()

    def ingest_documents(self, data_dir="data"):
        """Reads text files from the data directory and loads them into ChromaDB if empty."""
        if self.collection.count() > 0:
            print("Vector collection already populated. Skipping ingestion.")
            return

        documents = []
        metadatas = []
        ids = []

        if not os.path.exists(data_dir):
            print(f"Data directory '{data_dir}' not found.")
            return

        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Simple paragraph/section-based chunking split by double newlines
                    chunks = content.split("\n\n")
                    for i, chunk in enumerate(chunks):
                        if chunk.strip():
                            documents.append(chunk.strip())
                            metadatas.append({"source": filename})
                            ids.append(f"{filename}_chunk_{i}")

        if documents:
            # Generate embeddings using Google GenAI embedding model
            # Using text-embedding-001 for vector generation
            embeddings = []
            for doc in documents:
                response = self.genai_client.models.embed_content(
                    model="models/gemini-embedding-001",
                    contents=doc
                )
                embeddings.append(response.embeddings[0].values)

            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully ingested {len(documents)} document chunks into ChromaDB.")
        else:
            print("No valid documents found to ingest.")

    def search(self, query: str, n_results: int = 2) -> list[str]:
        """Performs semantic similarity search against the knowledge base."""
        # Embed the query
        query_response = self.genai_client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=query
        )
        query_embedding = query_response.embeddings[0].values

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Extract document text chunks from results
        retrieved_texts = results.get("documents", [[]])[0]
        return retrieved_texts

if __name__ == "__main__":
    # Test runner for RAG engine
    rag = HelloQRAGEngine()
    rag.ingest_documents()
    print("Test Search Result for 'Discreet Mode':")
    print(rag.search("what is ghost mode?"))
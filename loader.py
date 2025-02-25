# loader.py
import os
import logging
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Constants
INDEX_NAME = "test"
EMBEDDING_DIMENSION = 768

# Configure logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def load_env_vars():
    load_dotenv()
    pine_key = os.getenv("PINECONE_API_KEY")
    if not pine_key:
        logging.error("Pinecone API key not found in environment variables")
        raise ValueError("Pinecone API key not found in environment variables")
    return pine_key

def initialize_pinecone(api_key):
    print("Initializing Pinecone...")
    pc = Pinecone(api_key=api_key)
    return pc

def setup_pinecone_index(pc, index_name=INDEX_NAME):
    try:
        print(f"Checking if Pinecone index '{index_name}' exists...")
        pc.describe_index(index_name)
    except Exception:
        print(f"Index '{index_name}' not found. Creating a new index...")
        pc.create_index(
            name=index_name,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print(f"Index '{index_name}' created successfully.")

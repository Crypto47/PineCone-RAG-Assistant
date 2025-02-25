# chunker.py
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import csv_loader


# Constants for chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 250

def load_documents_pdf(file_path):
    print(f"Loading PDF file: {file_path}...")
    loader = PyPDFLoader(file_path)
    start_time = time.time()
    pages = loader.load()
    print(f"Loaded {len(pages)} pages in {time.time() - start_time:.2f} seconds.")
    return pages

def load_documents_csv(file_path):
    print(f"Loading CSV file: {file_path}...")
    loader = csv_loader.CSVLoader(file_path)
    start_time = time.time()
    pages = loader.load()
    print(f"Loaded {len(pages)} pages in {time.time() - start_time:.2f} seconds.")
    return pages

def split_documents(pages):
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False
    )
    start_time = time.time()
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks in {time.time() - start_time:.2f} seconds.")
    return chunks

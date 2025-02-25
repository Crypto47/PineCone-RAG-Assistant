# uploader.py
import time
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore

def create_embeddings(chunks, embedding_model):
    print("Creating embeddings for chunks...")
    embeddings = OllamaEmbeddings(model=embedding_model)
    start_time = time.time()
    # Create embeddings for each chunk's content
    vectors = embeddings.embed_documents([chunk.page_content for chunk in chunks])
    print(f"Created {len(vectors)} embeddings in {time.time() - start_time:.2f} seconds.")
    return vectors, embeddings

def create_embeddings_first_100(chunks, embedding_model):
    """
    Creates embeddings only for the first 100 document chunks.
    If there are fewer than 100 chunks, it will create embeddings for all available chunks.
    Returns the embeddings, the vector results, and the limited list of chunks.
    """
    limited_chunks = chunks[:100]
    print("Creating embeddings for the first 100 chunks...")
    embeddings = OllamaEmbeddings(model=embedding_model)
    start_time = time.time()
    vectors = embeddings.embed_documents([chunk.page_content for chunk in limited_chunks])
    print(f"Created {len(vectors)} embeddings in {time.time() - start_time:.2f} seconds.")
    return vectors, embeddings, limited_chunks


def upload_to_vector_store(pc, index_name, embeddings, chunks):
    print("Uploading documents to Pinecone Vector Store...")
    vector_store = PineconeVectorStore(index=pc.Index(index_name), embedding=embeddings)
    ids = [str(i) for i in range(1, len(chunks) + 1)]
    start_time = time.time()
    vector_store.add_documents(documents=chunks, ids=ids)
    print(f"Uploaded {len(chunks)} documents in {time.time() - start_time:.2f} seconds.")
    return vector_store


def upload_first_100_to_vector_store(pc, index_name, embeddings, chunks):
    """
    Uploads only the first 100 document chunks (and their embeddings) to the Pinecone Vector Store.
    If there are fewer than 100 chunks, it will upload all available chunks.
    """
    limited_chunks = chunks[:100]  # Select only the first 100 chunks
    print("Uploading the first 100 documents to Pinecone Vector Store...")
    vector_store = PineconeVectorStore(index=pc.Index(index_name), embedding=embeddings)
    ids = [str(i) for i in range(1, len(limited_chunks) + 1)]
    start_time = time.time()
    vector_store.add_documents(documents=limited_chunks, ids=ids)
    print(f"Uploaded {len(limited_chunks)} documents in {time.time() - start_time:.2f} seconds.")
    return vector_store
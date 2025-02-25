import os
import time
import tempfile
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.memory import buffer
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone, ServerlessSpec
from loader import load_env_vars, initialize_pinecone, setup_pinecone_index, INDEX_NAME

CHUNK_SIZE = 500
CHUNK_OVERLAP = 250
EMBEDDING_DIMENSION = 768
LLM_MODEL = "deepseek-r1:1.5b"
TEMPERATURE = 0.4

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str

pine_key = load_env_vars()
pc = initialize_pinecone(pine_key)
setup_pinecone_index(pc, INDEX_NAME)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
my_index = pc.Index(INDEX_NAME)
vector_store = PineconeVectorStore(index=my_index, embedding=embeddings)
memory = buffer.ConversationBufferMemory(return_messages=True)

def generate_rag_response(vector_store, embeddings, query, memory):
    embedded_query = embeddings.embed_query(query)
    results = vector_store._similarity_search_with_relevance_scores(query=query, k=5)
    rag_response = "\n".join(
        f"Context Chunk {idx + 1} (Relevance Score: {score:.2f}):\n{chunk.page_content}\n"
        for idx, (chunk, score) in enumerate(results)
    )
    history = "\n".join([msg.content for msg in memory.chat_memory.messages])
    prompt = ("You are an intelligent, helpful AI assistant using retrieval-augmented generation (RAG). "
              "Carefully analyze the retrieved context and conversation history to provide an accurate response.\n\n"
              f"Retrieved Context:\n{rag_response}\n\n"
              f"Conversation History:\n{history}\n\n"
              f"User Query: {query}\n\n"
              "Provide a comprehensive and precise response.")
    llm = ChatOllama(model=LLM_MODEL, temperature=TEMPERATURE)
    response = llm.invoke(prompt)
    filtered_content = response.content.split('\n\n', 1)[-1].strip()
    return filtered_content

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    query = request.message
    if not query.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        rag_response = generate_rag_response(vector_store, embeddings, query, memory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
    return {"response": rag_response}

def load_documents(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return pages

def split_documents(pages):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, length_function=len, is_separator_regex=False)
    chunks = splitter.split_documents(pages)
    return chunks

def create_embeddings(chunks, embedding_model):
    embs = OllamaEmbeddings(model=embedding_model)
    vectors = embs.embed_documents([chunk.page_content for chunk in chunks])
    return vectors, embs

def upload_to_vector_store(pc, index_name, embeddings, chunks):
    vs = PineconeVectorStore(index=pc.Index(index_name), embedding=embeddings)
    texts = [chunk.page_content for chunk in chunks]
    ids = [str(i) for i in range(1, len(texts) + 1)]
    vs.add_documents(documents=chunks, ids=ids)
    return vs

@app.post("/upload")
async def upload_endpoint(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    pages = load_documents(tmp_path)
    os.remove(tmp_path)
    chunks = split_documents(pages)
    _, embs = create_embeddings(chunks, "nomic-embed-text")
    upload_to_vector_store(pc, INDEX_NAME, embs, chunks)
    return {"detail": f"Uploaded {len(chunks)} documents."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

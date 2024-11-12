# rest_service.py

import os
import faiss
import pickle
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.faiss import FaissVectorStore
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import numpy as np

# Initialize FastAPI app
app = FastAPI()

# Load environment variables from a .env file
load_dotenv()
EMBED_DIMENSION = 512
Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimensions=EMBED_DIMENSION)

# Paths
EMBEDDINGS_PATH = 'vectore_store/embeddings_data.pkl'
FAISS_INDEX_PATH = 'vectore_store/faiss_index.faiss'

# Load embeddings and faiss index
def load_embeddings():
    with open(EMBEDDINGS_PATH, 'rb') as f:
        nodes = pickle.load(f)
    faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    return faiss_index, nodes

faiss_index, nodes = load_embeddings()
vector_store = FaissVectorStore(faiss_index=faiss_index)
vector_store_index = VectorStoreIndex(nodes)

# Создаём движок для запросов
query_engine = vector_store_index.as_query_engine(similarity_top_k=2)

# Request model
class QueryRequest(BaseModel):
    idea: str

# Function to find the most similar text in loaded embeddings
def find_most_similar_text(query_embedding):
    # Поиск ближайшего соседа в Faiss индексе
    distances, indices = faiss_index.search(np.array([query_embedding]).astype('float32'), 1)
    closest_index = indices[0][0]
    
    # Возвращаем наиболее подходящий текст из сохранённых узлов
    closest_text = nodes[closest_index].text  # Предполагается, что 'text' содержит текст строки
    return closest_text

# Endpoint to process the query and return the most similar text
@app.post("/similar")
async def ask_question(request: QueryRequest):
    question = request.idea
    
    # Получаем эмбеддинг запроса
    query_embedding = OpenAIEmbedding(model="text-embedding-3-small", dimensions=512).get_text_embedding(question)
    response = query_engine.query(question)
    
    # Находим наиболее похожий текст
    closest_text = find_most_similar_text(query_embedding)
    
    # Формируем ответ с текстом
    answer = {
        "answer": response.response,
        "csv_data": closest_text
    }

    return answer

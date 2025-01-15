# rest_service.py
from typing import Dict

import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel

from embedding_service import EmbeddingService

# Initialize FastAPI app
app = FastAPI()

# Load environment variables from a .env file
load_dotenv()
EMBED_DIMENSION = 512

Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimensions=EMBED_DIMENSION)


# Request model
class QueryRequest(BaseModel):
    idea: str


class BodyInsertIntoIndex(BaseModel):
    row: dict


EMBEDDINGS_PATH = 'vectore_store/embeddings_data.pkl'
FAISS_INDEX_PATH = 'vectore_store/faiss_index.faiss'

emb_service = EmbeddingService(FAISS_INDEX_PATH, EMBEDDINGS_PATH)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/healthcheck")
def read_root():
    return {"HackDB": "v.0.0.1"}


@app.post("/similar")
async def ask_question(request: QueryRequest):
    question = request.idea

    # Получаем эмбеддинг запроса
    query_embedding = OpenAIEmbedding(model="text-embedding-3-small", dimensions=512).get_text_embedding(question)
    response = emb_service.query_engine.query(question)

    # Находим наиболее похожий текст
    closest_text = emb_service.find_most_similar_text(query_embedding)

    # Формируем ответ с текстом
    answer = {
        "response_text": response.response,
        "csv_data": closest_text
    }

    return answer


@app.post("/insert_into_index")
async def insert_into_index(new_doc: BodyInsertIntoIndex):
    emb_service.insert_new_doc(new_doc.row)

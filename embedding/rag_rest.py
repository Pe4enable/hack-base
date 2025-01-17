# rest_service.py
from typing import Dict
from typing import List

import boto3
import json
import numpy as np
import psycopg2
import os
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
    request: str


class BodyInsertIntoIndex(BaseModel):
    row: dict

class DataItem(BaseModel):
    id: str
    hackathon: str 
    title: str
    link:str
    live_demo:str
    source_code:str
    video: str
    winner: str
    short: str
    merged_column: str

class DataList(BaseModel):
    data: List[DataItem]




EMBEDDINGS_PATH = 'vectore_store/embeddings_data.pkl'
FAISS_INDEX_PATH = 'vectore_store/faiss_index.faiss'

PIPELINE_STORAGE = 'pipeline_storage/docstore.json'
PIPELINE_STORAGE_CACHE = 'pipeline_storage/llama_cache'

# Метод для скачивания файла из Spaces Object Storage Digital Ocean
def download_file_from_spaces():
    try:
        # Создаем клиента Spaces
        session = boto3.session.Session()
        client = session.client('s3',
                        region_name=os.getenv("DO_BACKET_REGION_NAME"),
                        endpoint_url=os.getenv("DO_BACKET_URL"),
                        aws_access_key_id=os.getenv("DO_BACKET_KEY_ID"),
                        aws_secret_access_key=os.getenv("DO_BACKET_API_KEY"))

        # Скачиваем файл
        client.download_file(Bucket=os.getenv("DO_BACKET_NAME"), Key=EMBEDDINGS_PATH, Filename=EMBEDDINGS_PATH)
        client.download_file(Bucket=os.getenv("DO_BACKET_NAME"), Key=FAISS_INDEX_PATH, Filename=FAISS_INDEX_PATH)

        client.download_file(Bucket=os.getenv("DO_BACKET_NAME"), Key=PIPELINE_STORAGE, Filename=PIPELINE_STORAGE)
        client.download_file(Bucket=os.getenv("DO_BACKET_NAME"), Key=PIPELINE_STORAGE_CACHE, Filename=PIPELINE_STORAGE_CACHE)
        print("download")
    except Exception as e:
        raise RuntimeError(f"Ошибка при скачивании файлов: {e}")

emb_service = EmbeddingService(FAISS_INDEX_PATH, EMBEDDINGS_PATH)

# Метод для обновления файла в Spaces Object Storage Digital Ocean
def upload_file_to_spaces():
    try:
       # Создаем клиента Spaces
        session = boto3.session.Session()
        client = session.client('s3',
                        region_name=os.getenv("DO_BACKET_REGION_NAME"),
                        endpoint_url=os.getenv("DO_BACKET_URL"),
                        aws_access_key_id=os.getenv("DO_BACKET_KEY_ID"),
                        aws_secret_access_key=os.getenv("DO_BACKET_API_KEY"))

        # Загружаем файл
        client.upload_file(Filename=EMBEDDINGS_PATH, Bucket=os.getenv("DO_BACKET_NAME"), Key=EMBEDDINGS_PATH)
        client.upload_file(Filename=FAISS_INDEX_PATH, Bucket=os.getenv("DO_BACKET_NAME"), Key=FAISS_INDEX_PATH)

        client.upload_file(Filename=PIPELINE_STORAGE, Bucket=os.getenv("DO_BACKET_NAME"), Key=PIPELINE_STORAGE)
        client.upload_file(Filename=PIPELINE_STORAGE_CACHE, Bucket=os.getenv("DO_BACKET_NAME"), Key=PIPELINE_STORAGE_CACHE)
        print(f"Файлы успешно загружен в DO")
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке файла: {e}")


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/healthcheck")
def healthcheck():
    return {"HackDB": "v.0.0.1"}


@app.post("/search")
async def ask_question(request: QueryRequest):
    question = request.request

    # Получаем эмбеддинг запроса
    query_embedding = OpenAIEmbedding(model="text-embedding-3-small", dimensions=512).get_text_embedding(question)
    #response = emb_service.query_engine.query(question)

    # Находим наиболее похожий текст
    closest_text = emb_service.find_most_similar_text(query_embedding)

    # Формируем ответ с текстом
    # answer = {
    #     "response_text": response.response,
    #     "csv_data": closest_text
    # }

    #return answer

    #todo сделать подгрузку описаний проектов из бд по id
    #data_list_dict = json.loads(closest_text)
        
    # Создаем объект DataList из списка словарей
    return closest_text #DataList(data=[DataItem(**item) for item in data_list_dict])


@app.post("/insert_into_index")
async def insert_into_index(new_doc: BodyInsertIntoIndex):
    emb_service.insert_new_doc(new_doc.row)

@app.post("/data")
async def add_data(data_list: DataList):
    for item in data_list.data:
        # Преобразуем каждый элемент в строку
        item_str = f"id: {item.id}, hackathon: {item.hackathon}, title: {item.title}, link: {item.link}, " \
                   f"live_demo: {item.live_demo}, source_code: {item.source_code}, video: {item.video}, " \
                   f"winner: {item.winner}, short: {item.short}, merged_column: {item.merged_column}"
        
        # todo добавлять в бд
        # Вызываем метод insert_new_doc
        emb_service.insert_new_doc(item_str)
    upload_file_to_spaces()
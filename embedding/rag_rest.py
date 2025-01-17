# rest_service.py
from typing import Dict
from typing import List

import boto3
import json
import numpy as np
import psycopg2
import uuid
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
    id: uuid.UUID
    hackathon: str
    title: str
    source_link:str
    live_demo_link:str
    source_code_link:str
    video_link: str
    winner: str
    short_desc: str
    description: str
    merged_column: str

class DataList(BaseModel):
    data: List[DataItem]


EMBEDDINGS_PATH = 'vectore_store/embeddings_data.pkl'
FAISS_INDEX_PATH = 'vectore_store/faiss_index.faiss'

PIPELINE_STORAGE = 'pipeline_storage/docstore.json'
PIPELINE_STORAGE_CACHE = 'pipeline_storage/llama_cache'

#todo выделить в отдельный файл
def init_client():
    session = boto3.session.Session()
    return session.client('s3',
                        region_name=os.getenv("DO_BACKET_REGION_NAME"),
                        endpoint_url=os.getenv("DO_BACKET_URL"),
                        aws_access_key_id=os.getenv("DO_BACKET_KEY_ID"),
                        aws_secret_access_key=os.getenv("DO_BACKET_API_KEY"))

client = init_client()

@app.get("/api/do/download")
# Метод для скачивания файла из Spaces Object Storage Digital Ocean
def download_file_from_spaces():
    try:
        # Скачиваем файл
        client.download_file(Bucket=os.getenv("DO_BACKET_NAME"), Key=EMBEDDINGS_PATH, Filename=EMBEDDINGS_PATH)
        client.download_file(Bucket=os.getenv("DO_BACKET_NAME"), Key=FAISS_INDEX_PATH, Filename=FAISS_INDEX_PATH)

        client.download_file(Bucket=os.getenv("DO_BACKET_NAME"), Key=PIPELINE_STORAGE, Filename=PIPELINE_STORAGE)
        client.download_file(Bucket=os.getenv("DO_BACKET_NAME"), Key=PIPELINE_STORAGE_CACHE, Filename=PIPELINE_STORAGE_CACHE)
        print("Файлы успешно скачаны с DO")
    except Exception as e:
        raise RuntimeError(f"Ошибка при скачивании файлов: {e}")

emb_service = EmbeddingService(FAISS_INDEX_PATH, EMBEDDINGS_PATH)

@app.get("/api/do/upload")
# Метод для обновления файла в Spaces Object Storage Digital Ocean
#todo пока ошибка
def upload_file_to_spaces():
    try:
        # Загружаем файл
        client.upload_file(Filename=EMBEDDINGS_PATH, Bucket=os.getenv("DO_BACKET_NAME"), Key=EMBEDDINGS_PATH)
        client.upload_file(Filename=FAISS_INDEX_PATH, Bucket=os.getenv("DO_BACKET_NAME"), Key=FAISS_INDEX_PATH)

        client.upload_file(Filename=PIPELINE_STORAGE, Bucket=os.getenv("DO_BACKET_NAME"), Key=PIPELINE_STORAGE)
        client.upload_file(Filename=PIPELINE_STORAGE_CACHE, Bucket=os.getenv("DO_BACKET_NAME"), Key=PIPELINE_STORAGE_CACHE)
        print(f"Файлы успешно загружен в DO")
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке файла: {e}")

#todo выделить в отдельный файл
conn = psycopg2.connect(database=os.getenv("POSTGRESQL_DB_NAME"),
                        host=os.getenv("POSTGRESQL_HOST"),
                        user=os.getenv("POSTGRESQL_USER"),
                        password=os.getenv("POSTGRESQL_PASSWORD"),
                        port=os.getenv("POSTGRESQL_PORT"))

def init_db():
    conn = psycopg2.connect(database=os.getenv("POSTGRESQL_DB_NAME"),
                        host=os.getenv("POSTGRESQL_HOST"),
                        user=os.getenv("POSTGRESQL_USER"),
                        password=os.getenv("POSTGRESQL_PASSWORD"),
                        port=os.getenv("POSTGRESQL_PORT"))
    
    return conn.cursor()
    
def commit_changes():
    conn.commit()

def get_submissions_all():
    try:
        cursor = init_db()
        cursor.execute("SELECT * FROM public.\"Submissions\"")
        all_submissions=cursor.fetchall()
        return all_submissions
    except Exception as e:
        raise RuntimeError(f"Ошибка при get_all_submissions : {e}")


def get_submissions_by_ids(ids: List[str]):
    try:
        cursor = init_db()
        delimiter = "," # Define a delimiter
        ids_str = delimiter.join(ids)
        cursor.execute(f"SELECT * FROM public.\"Submissions\" WHERE Id IN {ids_str}")
        submissions=cursor.fetchall()
        return submissions
    except Exception as e:
        raise RuntimeError(f"Ошибка при get_submissions_by_ids : {e}")

#todo пока ошибка
def add_submission(item: DataItem):
    try:
        cursor = init_db()
        cursor.execute(f"INSERT INTO public.\"Submissions\" ( \
                       hackathon, \
                       title, \
                       source_link, \
                       live_demo_link, \
                       source_code_link,  \
                       video_link, \
                       winner, \
                       short_desc, \
                       description, \
                       merged_column) VALUES( \
                       \"{item.hackathon}\", \
                       \"{item.title}\", \
                       \"{item.source_link}\", \
                       \"{item.live_demo_link}\", \
                       \"{item.source_code_link}\", \
                       \"{item.video_link}\", \
                       \"{item.winner}\", \
                       \"{item.short_desc}\", \
                       \"{item.description}\", \
                       \"{item.merged_column}\" \
                       )")

        commit_changes()
    except Exception as e:
        raise RuntimeError(f"Ошибка при add_submission : {e}")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/healthcheck")
def healthcheck():
    return {"HackDB": "v.0.0.1"}

def string_to_datalist(closest_text: str) -> DataList:
    try:
        # Разбиваем строку на элементы по двойному переносу строки
        items = closest_text.strip().split('\n\n')
        
        # Преобразуем каждый элемент в словарь и создаем объект DataItem
        data_items = []
        for item in items:
            item_dict = {}
            for line in item.split('\n'):
                key, value = line.split(': ', 1)
                item_dict[key.strip()] = value.strip()
            data_items.append(DataItem(**item_dict))
        
        # Возвращаем объект DataList
        return DataList(data=data_items)
    except Exception as e:
        raise ValueError(f"Ошибка при преобразовании строки в DataList: {e}")

@app.post("/api/search")
async def ask_question(request: QueryRequest):
    question = request.request

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
    #todo чтото не мапится никак
    #return string_to_datalist(closest_text) 


@app.post("/api/insert_into_index")
async def insert_into_index(new_doc: BodyInsertIntoIndex):
    emb_service.insert_new_doc(new_doc.row)

@app.post("/api/submissions")
async def add_data(data_list: DataList):
    for item in data_list.data:
        # Преобразуем каждый элемент в строку
        item_str = f"id: {item.id}, hackathon: {item.hackathon}, title: {item.title}, source_link: {item.source_link}, " \
                   f"live_demo_link: {item.live_demo_link}, source_code_link: {item.source_code_link}, video_link: {item.video_link}, " \
                   f"winner: {item.winner}, short_desc: {item.short_desc}, description: {item.description}, merged_column: {item.merged_column}"
        
        add_submission(item)
        # Вызываем метод insert_new_doc
        # emb_service.insert_new_doc(item_str)
   # upload_file_to_spaces()

@app.get("/api/submissions/all")
async def get_data_all():
    return get_submissions_all()

@app.get("/api/submissions")
async def get_data_by_ids(ids: List[str]):
    return get_submissions_by_ids(ids)


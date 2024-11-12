from flask import Flask, request, jsonify
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.ingestion import IngestionPipeline

import os

# Инициализация Flask приложения
app = Flask(__name__)

# Задаем API-ключ (лучше хранить его в переменной окружения для безопасности)
API_KEY = os.getenv("API_KEY", "your_api_key_here")

# Функция для проверки API-ключа
def check_api_key():
    key = request.headers.get("x-api-key")
    return key == API_KEY

# Инициализация моделей и хранилищ (настраиваем ваши компоненты Llama Index)
llm = OpenAI(api_key="openai_api_key")
embedding = OpenAIEmbedding(api_key="openai_api_key")
vector_store = FaissVectorStore(embedding=embedding)

# Эндпоинт для обработки вопросов
@app.route('/ask', methods=['POST'])
def ask_question():
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    question = data.get("question")
    
    # Здесь может быть вызов вашего кода для обработки запроса и получения ответа
    response = llm.answer(question)  # Примерный вызов для получения ответа от LLM
    
    return jsonify({"answer": response})

# Запуск Flask-приложения
if __name__ == '__main__':
    app.run(port=5000, debug=True)

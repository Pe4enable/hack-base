# calculate_embeddings.py
import os
import faiss
import pickle
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.ingestion import IngestionPipeline
from dotenv import load_dotenv
from llama_index.readers.file import PagedCSVReader

# Load environment variables from a .env file
load_dotenv()

# Set the OpenAI API key environment variable
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

# LlamaIndex global settings for llm and embeddings
EMBED_DIMENSION = 512
Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimensions=EMBED_DIMENSION)

# Путь для сохранения эмбеддингов
EMBEDDINGS_PATH = 'embeddings_data.pkl'
FAISS_INDEX_PATH = 'faiss_index.faiss'

# Функция для сохранения эмбеддингов
def save_embeddings(faiss_index, nodes):
    with open(EMBEDDINGS_PATH, 'wb') as f:
        pickle.dump(nodes, f)
    faiss.write_index(faiss_index, FAISS_INDEX_PATH)

# Читаем CSV
csv_reader = PagedCSVReader()
reader = SimpleDirectoryReader(
    input_files=['first_30_rows.csv'],
    file_extractor={".csv": csv_reader}
)

docs = reader.load_data()

# Faiss vector store setup
faiss_index = faiss.IndexFlatL2(EMBED_DIMENSION)
vector_store = FaissVectorStore(faiss_index=faiss_index)

# Создаём pipeline для обработки документов
pipeline = IngestionPipeline(
    vector_store=vector_store,
    documents=docs
)

# Прогоняем pipeline и получаем векторы
nodes = pipeline.run()

# Сохраняем эмбеддинги и FAISS индекс
save_embeddings(faiss_index, nodes)

print("Эмбеддинги и FAISS индекс успешно сохранены.")

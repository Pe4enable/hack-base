# calculate_embeddings.py
import os
import pickle

import faiss
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import PagedCSVReader
from llama_index.vector_stores.faiss import FaissVectorStore

# Load environment variables from a .env file
load_dotenv()

# Set the OpenAI API key environment variable
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

# LlamaIndex global settings for llm and embeddings
EMBED_DIMENSION = 512
Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimensions=EMBED_DIMENSION)

# Путь для сохранения эмбеддингов
EMBEDDINGS_PATH = 'vectore_store/embeddings_data_full.pkl'
FAISS_INDEX_PATH = 'vectore_store/faiss_index_full.faiss'
CSV_FILE = 'data/first_30_rows.csv'


# Функция для сохранения эмбеддингов
def save_embeddings(faiss_index, nodes):
    with open(EMBEDDINGS_PATH, 'wb') as f:
        pickle.dump(nodes, f)
    faiss.write_index(faiss_index, FAISS_INDEX_PATH)


# Читаем CSV
csv_reader = PagedCSVReader()
reader = SimpleDirectoryReader(
    input_files=[CSV_FILE],
    file_extractor={".csv": csv_reader}
)

docs = reader.load_data()
# print(str(docs[0]), type(docs[0]), docs[0].extra_info)

# Faiss vector store setup
faiss_index = faiss.IndexFlatL2(EMBED_DIMENSION)
vector_store = FaissVectorStore(faiss_index=faiss_index)

# Создаём pipeline для обработки документов
pipeline = IngestionPipeline(
    vector_store=vector_store,
    documents=docs,
    docstore=SimpleDocumentStore()
)

# Прогоняем pipeline и получаем векторы
nodes = pipeline.run()

# Сохраняем эмбеддинги и FAISS индекс
save_embeddings(faiss_index, nodes)

print("Эмбеддинги и FAISS индекс успешно сохранены.")

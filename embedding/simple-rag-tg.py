from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.file import PagedCSVReader
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import VectorStoreIndex
import faiss
import os
import pandas as pd
from dotenv import load_dotenv


# Load environment variables from a .env file
load_dotenv()

# Set the OpenAI API key environment variable
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

# LlamaIndex settings for llm and embeddings
EMBED_DIMENSION = 512
Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimensions=EMBED_DIMENSION)

# Faiss vector store setup
faiss_index = faiss.IndexFlatL2(EMBED_DIMENSION)
vector_store = FaissVectorStore(faiss_index=faiss_index)

# Simple CSV reader for documents
csv_reader = PagedCSVReader()
reader = SimpleDirectoryReader(
    input_files=['first_30_rows.csv'],
    file_extractor={".csv": csv_reader}
)

docs = reader.load_data()
pipeline = IngestionPipeline(
    vector_store=vector_store,
    documents=docs
)

nodes = pipeline.run()
vector_store_index = VectorStoreIndex(nodes)
query_engine = vector_store_index.as_query_engine(similarity_top_k=2)

# Function to handle user queries
async def handle_query(update: Update, context):
    user_input = update.message.text
    response = query_engine.query(user_input)
    await update.message.reply_text(response.response)

# Main function to run the bot
if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # Handle commands
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Handle text messages
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query)
    application.add_handler(message_handler)

    # Start the bot
    application.run_polling()

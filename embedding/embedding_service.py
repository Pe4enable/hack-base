import pickle
from typing import Dict

import faiss
import numpy as np
from llama_index.core import VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline, DocstoreStrategy
from llama_index.core.schema import Document
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.faiss import FaissVectorStore


class EmbeddingService:
    def __init__(self, faiss_index_path, embeddings_path):
        self.faiss_index_path = faiss_index_path
        self.embeddings_path = embeddings_path
        self.faiss_index, self.nodes = self.load_embeddings()
        self.query_engine = self.load_query_engine()
        self.pipeline = self.load_pipeline()

    def load_embeddings(self):
        with open(self.embeddings_path, 'rb') as f:
            nodes = pickle.load(f)
        faiss_index = faiss.read_index(self.faiss_index_path)
        return faiss_index, nodes

    def load_query_engine(self):
        # vector_store = FaissVectorStore(faiss_index=faiss_index)
        vector_store_index = VectorStoreIndex(self.nodes)

        # Создаём движок для запросов
        query_engine = vector_store_index.as_query_engine(similarity_top_k=2)
        return query_engine

    def load_pipeline(self):
        vector_store = FaissVectorStore(faiss_index=self.faiss_index)
        pipeline = IngestionPipeline(vector_store=vector_store, docstore=SimpleDocumentStore(),
                                     docstore_strategy=DocstoreStrategy.DUPLICATES_ONLY)
        pipeline.load("./pipeline_storage")
        return pipeline

    def insert_new_doc(self, row: Dict):
        metadata = {}
        for k, doc in self.pipeline.docstore.docs.items():
            metadata = doc.metadata
        new_doc = Document(
            text="\n".join(
                f"{k.strip()}: {str(v).strip()}" for k, v in row.items()
            ),
            extra_info=metadata,
        )
        self.pipeline.run(documents=[new_doc])
        self._update()
        self._save_data()

    def save_embeddings(self):
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(self.nodes, f)
        faiss.write_index(self.faiss_index, self.faiss_index_path)

    def _save_data(self):
        self.save_embeddings()
        self.pipeline.persist("./pipeline_storage")

    def find_most_similar_text(self, query_embedding):
        # Поиск ближайшего соседа в Faiss индексе
        distances, indices = self.faiss_index.search(np.array([query_embedding]).astype('float32'), 1)
        closest_index = indices[0][0]

        # Возвращаем наиболее подходящий текст из сохранённых узлов
        closest_text = self.nodes[closest_index].text  # Предполагается, что 'text' содержит текст строки

        #todo возвращать список похожих проектов, а не только первый. в идел просто список id, вынести процент в env

        return closest_text
        
        

    def _update(self):
        self.nodes = list(self.pipeline.docstore.docs.values())
        self.query_engine = self.load_query_engine()

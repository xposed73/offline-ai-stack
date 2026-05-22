import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.qdrant import QdrantVectorStore

from app.config.settings import settings
from app.core.logging import logger
from app.qdrant.client import QdrantManager

class RAGPipeline:
    """Core Retrieval Augmented Generation (RAG) pipeline utilizing LlamaIndex, Ollama, and Qdrant."""

    def __init__(self, collection_name: Optional[str] = None) -> None:
        self.collection_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.qdrant_manager = QdrantManager()
        self._init_llamaindex()

    def _init_llamaindex(self) -> None:
        """Initializes Ollama LLM and Embeddings global settings in LlamaIndex."""
        logger.info("Initializing LlamaIndex Ollama services...")
        
        # Configure LLM
        Settings.llm = Ollama(
            model=settings.LLM_MODEL,
            base_url=settings.OLLAMA_HOST,
            request_timeout=120.0
        )
        
        # Configure Embeddings Model
        Settings.embed_model = OllamaEmbedding(
            model_name=settings.EMBEDDING_MODEL,
            base_url=settings.OLLAMA_HOST,
            request_timeout=60.0
        )
        
        # We also customize chunk size and overlap for high-quality RAG
        Settings.chunk_size = 512
        Settings.chunk_overlap = 50

    def _get_vector_store_index(self) -> Optional[VectorStoreIndex]:
        """Connects to the Qdrant Vector Store and builds the VectorStoreIndex wrapper."""
        if not self.qdrant_manager.is_healthy():
            logger.error("Qdrant daemon is offline. Cannot initialize vector store index.")
            return None
            
        # Ensure collection exists
        success = self.qdrant_manager.ensure_collection(self.collection_name, settings.EMBEDDING_MODEL)
        if not success:
            logger.error("Failed to prepare Qdrant collection index.")
            return None
            
        # Instantiate Vector Store
        qclient = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        vector_store = QdrantVectorStore(client=qclient, collection_name=self.collection_name)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Load from store
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        return index

    def ingest_file(self, file_path: Path) -> int:
        """Ingests a single document file (PDF, TXT, MD) into the Qdrant index. Returns number of ingested nodes."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Ingesting file: {file_path.name}...")
        try:
            # Use LlamaIndex SimpleDirectoryReader for a single file
            reader = SimpleDirectoryReader(input_files=[str(file_path)])
            documents = reader.load_data()
            
            if not documents:
                logger.warning(f"No content extracted from file: {file_path}")
                return 0
                
            index = self._get_vector_store_index()
            if not index:
                raise RuntimeError("Could not initialize vector index for insertion.")
                
            # Ingest/Insert into index
            for doc in documents:
                # Store original filename as metadata
                doc.metadata["file_name"] = file_path.name
                doc.metadata["file_path"] = str(file_path)
                index.insert(doc)
                
            node_count = len(documents)
            logger.info(f"Successfully ingested and indexed {node_count} pages/chunks from {file_path.name}")
            return node_count
        except Exception as e:
            logger.error(f"Failed to ingest file '{file_path}': {e}")
            raise e

    def ingest_directory(self, directory_path: Path) -> int:
        """Ingests all documents within a folder recursively. Returns total ingested node count."""
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        logger.info(f"Ingesting directory: {directory_path}...")
        try:
            # Recursively load documents
            reader = SimpleDirectoryReader(input_dir=str(directory_path), recursive=True)
            documents = reader.load_data()
            
            if not documents:
                logger.warning(f"No documents discovered in directory: {directory_path}")
                return 0
                
            index = self._get_vector_store_index()
            if not index:
                raise RuntimeError("Could not initialize vector index for insertion.")
                
            # Index all documents
            for doc in documents:
                index.insert(doc)
                
            node_count = len(documents)
            logger.info(f"Successfully ingested and indexed {node_count} nodes from directory {directory_path}")
            return node_count
        except Exception as e:
            logger.error(f"Failed to ingest directory '{directory_path}': {e}")
            raise e

    def query(self, query_str: str, system_prompt: Optional[str] = None) -> str:
        """Queries the vector index and returns a context-augmented LLM answer."""
        index = self._get_vector_store_index()
        if not index:
            return "Error: Qdrant or LlamaIndex RAG pipeline is not initialized."
            
        try:
            # Build LlamaIndex query engine
            # Standard German-language optimization support can be injected here
            default_system = (
                "You are a helpful, production-grade local AI Assistant. "
                "Answer the user query based ONLY on the provided context. If the answer cannot be determined "
                "from the context, say 'I don't have enough local context to answer this.' rather than making it up. "
            )
            
            # Append future German language optimization prompt if specified
            if system_prompt:
                default_system += "\n" + system_prompt
                
            query_engine = index.as_query_engine(
                similarity_top_k=4,
                system_prompt=default_system
            )
            
            logger.info(f"Running LLM Query: '{query_str}'")
            response = query_engine.query(query_str)
            return str(response)
        except Exception as e:
            logger.error(f"Error querying RAG pipeline: {e}")
            return f"Error executing query: {str(e)}"

    def semantic_search(self, query_str: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves raw matching text nodes and similarity scores without running LLM completion."""
        index = self._get_vector_store_index()
        if not index:
            return []
            
        try:
            # Build retriever from vector index
            retriever = index.as_retriever(similarity_top_k=limit)
            nodes = retriever.retrieve(query_str)
            
            results = []
            for node_with_score in nodes:
                node = node_with_score.node
                results.append({
                    "id": node.node_id,
                    "text": node.text,
                    "score": float(node_with_score.score) if node_with_score.score else 0.0,
                    "metadata": node.metadata
                })
            return results
        except Exception as e:
            logger.error(f"Error during semantic search: {e}")
            return []

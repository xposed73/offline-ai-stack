from typing import List, Dict, Any, Optional
import httpx
from qdrant_client import QdrantClient as OriginalQdrantClient
from qdrant_client.http import models as qmodels
from app.config.settings import settings
from app.core.logging import logger

class QdrantManager:
    """Manages Qdrant vector database interactions, collection creation, and state."""

    def __init__(self) -> None:
        self.host = settings.QDRANT_HOST
        self.port = settings.QDRANT_PORT
        self.client: Optional[OriginalQdrantClient] = None
        self._init_client()

    def _init_client(self) -> None:
        """Initializes the Qdrant Client."""
        try:
            self.client = OriginalQdrantClient(host=self.host, port=self.port, timeout=5.0)
        except Exception as e:
            logger.error(f"Failed to create Qdrant client: {e}")
            self.client = None

    def is_healthy(self) -> bool:
        """Pings Qdrant to confirm gRPC and HTTP health status."""
        if not self.client:
            return False
        try:
            # Simple status check
            collections = self.client.get_collections()
            return collections is not None
        except Exception:
            return False

    def auto_detect_embedding_dimension(self, model_name: str) -> int:
        """Pings Ollama with a test query to measure the dimension size of the embedding model."""
        try:
            payload = {
                "model": model_name,
                "prompt": "test"
            }
            # Directly hit the Ollama embedding endpoint
            url = f"{settings.OLLAMA_HOST}/api/embeddings"
            response = httpx.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                vector = response.json().get("embedding", [])
                if vector:
                    logger.info(f"Auto-detected dimension size for model '{model_name}': {len(vector)}")
                    return len(vector)
            
            # Fallback values for common embedding models
            if "nomic" in model_name:
                return 768
            if "bge" in model_name:
                return 1024
            if "minilm" in model_name:
                return 384
                
            logger.warning(f"Unable to auto-detect dimensions for '{model_name}'. Defaulting to 768.")
            return 768
        except Exception as e:
            logger.warning(f"Error auto-detecting dimensions: {e}. Defaulting to 768.")
            return 768

    def ensure_collection(self, collection_name: str, embedding_model: str) -> bool:
        """Creates a vector search collection if it doesn't already exist in Qdrant."""
        if not self.is_healthy():
            logger.error("Qdrant is not running. Cannot check or create collection.")
            return False

        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            for col in collections.collections:
                if col.name == collection_name:
                    logger.debug(f"Qdrant collection '{collection_name}' already exists.")
                    return True

            # If not found, dynamically detect vector dimension
            dimension = self.auto_detect_embedding_dimension(embedding_model)
            
            logger.info(f"Creating Qdrant collection '{collection_name}' with {dimension} dimensions...")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=dimension,
                    distance=qmodels.Distance.COSINE
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection '{collection_name}': {e}")
            return False

    def list_collections(self) -> List[str]:
        """Lists names of all active collections."""
        if not self.is_healthy():
            return []
        try:
            result = self.client.get_collections()
            return [col.name for col in result.collections]
        except Exception as e:
            logger.error(f"Failed to list Qdrant collections: {e}")
            return []

    def get_collection_count(self, collection_name: str) -> int:
        """Returns the number of indexed points (vectors) in a collection."""
        if not self.is_healthy():
            return 0
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return info.points_count or 0
        except Exception as e:
            # If the collection doesn't exist or other API error, return 0
            logger.debug(f"Could not retrieve count for '{collection_name}' (collection might not exist yet): {e}")
            return 0

    def delete_collection(self, collection_name: str) -> bool:
        """Deletes an entire collection index from Qdrant."""
        if not self.is_healthy():
            return False
        try:
            logger.warning(f"Deleting Qdrant collection '{collection_name}'...")
            self.client.delete_collection(collection_name=collection_name)
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            return False

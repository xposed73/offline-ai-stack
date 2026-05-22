import httpx
from typing import List
from app.config.settings import settings
from app.core.logging import logger

class EmbeddingGenerator:
    """Utility service to generate vector embeddings directly using the Ollama API."""

    def __init__(self) -> None:
        self.host = settings.OLLAMA_HOST
        self.model = settings.EMBEDDING_MODEL

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a numerical vector embedding for a single string block."""
        try:
            url = f"{self.host}/api/embeddings"
            payload = {
                "model": self.model,
                "prompt": text
            }
            response = httpx.post(url, json=payload, timeout=20.0)
            if response.status_code == 200:
                return response.json().get("embedding", [])
            
            logger.error(f"Ollama embedding request failed with code {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates list of embeddings for a batch list of string texts."""
        results = []
        for i, text in enumerate(texts):
            emb = self.generate_embedding(text)
            if emb:
                results.append(emb)
            else:
                logger.warning(f"Failed to get embedding for batch item {i}")
        return results

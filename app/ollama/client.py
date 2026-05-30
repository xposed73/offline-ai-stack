import json
from typing import List, Dict, Any, Optional
import httpx
from app.config.settings import settings
from app.core.logging import logger
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

class OllamaClient:
    """HTTP Client to interact with the local Ollama API for model management and simple inference."""

    def __init__(self) -> None:
        self.host = settings.OLLAMA_HOST

    def is_healthy(self) -> bool:
        """Pings the Ollama service endpoint to check if it's active."""
        try:
            response = httpx.get(f"{self.host}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def list_local_models(self) -> List[str]:
        """Lists names of all downloaded models currently available in Ollama."""
        if not self.is_healthy():
            logger.warning("Ollama is not running. Unable to fetch downloaded models.")
            return []
            
        try:
            response = httpx.get(f"{self.host}/api/tags", timeout=5.0)
            if response.status_code != 200:
                return []
                
            data = response.json()
            models = data.get("models", [])
            # Return names, e.g. ["llama3:latest", "nomic-embed-text:latest"]
            return [m["name"] for m in models]
        except Exception as e:
            logger.error(f"Failed to list local models: {e}")
            return []

    def is_model_available(self, model_name: str) -> bool:
        """Checks if a specific model (or its variation) is present locally."""
        local_models = self.list_local_models()
        # Handle exact match and extension-less matches
        # E.g., 'llama3' should match 'llama3:latest' or 'llama3:8b' if it's in the list
        for model in local_models:
            if model == model_name or model.split(":")[0] == model_name.split(":")[0]:
                return True
        return False

    def pull_model(self, model_name: str) -> bool:
        """Pulls a model from the Ollama library, showing a live download progress bar in the CLI."""
        if not self.is_healthy():
            logger.error("Ollama is not running. Cannot pull models.")
            return False

        if self.is_model_available(model_name):
            logger.info(f"Model '{model_name}' is already downloaded. Skipping pull.")
            return True

        logger.info(f"Initiating download of model '{model_name}' via Ollama...")

        # Setup Rich progress UI
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            transient=True
        ) as progress:
            task = progress.add_task(f"Downloading {model_name}...", total=100)
            
            try:
                # Use httpx streaming to process line-delimited JSON chunks
                url = f"{self.host}/api/pull"
                payload = {"name": model_name, "stream": True}
                
                # We need a large timeout for model downloads
                with httpx.stream("POST", url, json=payload, timeout=3600.0) as response:
                    if response.status_code != 200:
                        logger.error(f"Ollama returned HTTP {response.status_code} during model pull.")
                        return False
                        
                    for line in response.iter_lines():
                        if not line:
                            continue
                            
                        chunk = json.loads(line)
                        status = chunk.get("status", "")
                        
                        # Ollama sends progress chunks
                        total = chunk.get("total", 0)
                        completed = chunk.get("completed", 0)
                        
                        if total > 0:
                            progress.update(
                                task, 
                                total=total, 
                                completed=completed, 
                                description=f"Ollama: Downloading {model_name}"
                            )
                        else:
                            # Standard text status (e.g. 'verifying sha256', 'success')
                            progress.update(task, description=f"Ollama: {status}")

                logger.info(f"Model '{model_name}' pulled successfully.")
                return True
                
            except Exception as e:
                logger.error(f"Failed to pull model '{model_name}': {e}")
                return False

    def generate_completion(self, prompt: str, model: str = "tinyllama") -> Optional[str]:
        """Runs a fast text completion API test (for verification of inference)."""
        if not self.is_healthy():
            return None
            
        try:
            url = f"{self.host}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            response = httpx.post(url, json=payload, timeout=60.0)
            if response.status_code == 200:
                return response.json().get("response")
            return None
        except Exception as e:
            logger.error(f"Error during Ollama test generation: {e}")
            return None

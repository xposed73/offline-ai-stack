import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import docker
from docker.models.containers import Container
from docker.errors import ImageNotFound, NotFound, APIError
from app.config.settings import settings
from app.core.logging import logger
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

class ServiceStatus(BaseModel):
    """Pydantic model representing a service's runtime status."""
    name: str
    container_id: Optional[str] = None
    status: str  # "running", "stopped", "missing", "error"
    port: int
    image: str
    error_message: Optional[str] = None

class DockerOrchestrator:
    """Manages the deployment and lifecycle of the Docker containers for the stack."""
    
    def __init__(self) -> None:
        self.network_name = settings.DOCKER_NETWORK
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to connect to Docker daemon: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Returns True if the Docker client is active and communicating with dockerd."""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def _ensure_network(self) -> None:
        """Creates a dedicated Docker bridge network if it doesn't already exist."""
        if not self.is_available():
            raise RuntimeError("Docker daemon is unavailable.")
            
        try:
            self.client.networks.get(self.network_name)
            logger.debug(f"Docker bridge network '{self.network_name}' already exists.")
        except NotFound:
            logger.info(f"Creating custom Docker bridge network '{self.network_name}'...")
            self.client.networks.create(
                self.network_name,
                driver="bridge",
                attachable=True
            )

    def _get_ollama_docker_url(self) -> str:
        """Adapts Ollama host url for docker containers so they can reach the host service."""
        url = settings.OLLAMA_HOST
        # If running on localhost or 127.0.0.1, we map it to host.docker.internal
        if "localhost" in url:
            return url.replace("localhost", "host.docker.internal")
        if "127.0.0.1" in url:
            return url.replace("127.0.0.1", "host.docker.internal")
        return url

    def get_services_definitions(self) -> List[Dict[str, Any]]:
        """Defines Qdrant, OpenWebUI, XTTS, and n8n container specs."""
        ollama_url = self._get_ollama_docker_url()
        
        return [
            {
                "name": "qdrant",
                "image": "qdrant/qdrant:latest",
                "ports": {
                    "6333/tcp": settings.QDRANT_PORT,
                    "6334/tcp": settings.QDRANT_GRPC_PORT
                },
                "volumes": {
                    str(settings.qdrant_path): {"bind": "/qdrant/storage", "mode": "rw"}
                },
                "environment": {},
                "extra_hosts": {"host.docker.internal": "host-gateway"}
            },
            {
                "name": "open-webui",
                "image": "ghcr.io/open-webui/open-webui:main",
                "ports": {
                    "8080/tcp": settings.OPENWEBUI_PORT
                },
                "volumes": {
                    str(settings.openwebui_path): {"bind": "/app/backend/data", "mode": "rw"}
                },
                "environment": {
                    "OLLAMA_BASE_URL": ollama_url,
                    "WEBUI_AUTH": "false",
                    "AUDIO_TTS_ENGINE": "openai",
                    "AUDIO_TTS_API_BASE_URL": "http://xtts:8020/v1",
                    "AUDIO_TTS_API_KEY": "dummy",
                    "AUDIO_TTS_MODEL": "tts-1",
                    "AUDIO_TTS_VOICE": "de_voice.wav"
                },
                "extra_hosts": {"host.docker.internal": "host-gateway"}
            },
            {
                "name": "xtts",
                "image": "ghcr.io/coqui-ai/xtts-api-server:latest",
                "ports": {
                    "8020/tcp": settings.XTTS_PORT
                },
                "volumes": {
                    str(settings.xtts_path): {"bind": "/root/.local/share/tts", "mode": "rw"}
                },
                "environment": {
                    "COQUI_TOS_AGREED": "1"
                },
                "extra_hosts": {"host.docker.internal": "host-gateway"},
                "device_requests": [
                    docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
                ]
            },
            {
                "name": "n8n",
                "image": "docker.n8n.io/n8nio/n8n:latest",
                "ports": {
                    "5678/tcp": settings.N8N_PORT
                },
                "volumes": {
                    str(settings.n8n_path): {"bind": "/home/node/.n8n", "mode": "rw"}
                },
                "environment": {
                    "N8N_ENCRYPTION_KEY": "offline_ai_stack_secure_key_1337",
                    "N8N_DIAGNOSTICS_ENABLED": "false",
                    "N8N_METRICS_ENABLED": "false"
                },
                "extra_hosts": {"host.docker.internal": "host-gateway"}
            }
        ]

    def pull_image_with_progress(self, image_name: str) -> None:
        """Pulls an image from registry, displaying progress in the CLI console."""
        if not self.is_available():
            raise RuntimeError("Docker is unavailable.")

        try:
            # First check if the image is already pulled to skip downloads
            self.client.images.get(image_name)
            logger.debug(f"Image '{image_name}' is already cached locally. Skipping pull.")
            return
        except ImageNotFound:
            pass

        logger.info(f"Image '{image_name}' not found locally. Starting download...")
        
        # Display progress using Rich
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            transient=True
        ) as progress:
            task = progress.add_task(f"Pulling {image_name}...", total=100)
            
            try:
                # Docker API pull returns generator of download chunks
                for chunk in self.client.api.pull(image_name, stream=True, decode=True):
                    status = chunk.get("status", "")
                    progress.update(task, description=f"Pulling {image_name}: {status}")
                    # Estimate progression roughly from output
                    if "Downloading" in status or "Extracting" in status:
                        progress.advance(task, 0.5)
            except Exception as e:
                logger.error(f"Failed to pull image {image_name}: {e}")
                raise e

    def get_status(self) -> List[ServiceStatus]:
        """Inspects all stack containers and returns their current state."""
        results = []
        if not self.is_available():
            # Return empty or all-missing status with error
            for spec in self.get_services_definitions():
                results.append(ServiceStatus(
                    name=spec["name"],
                    status="error",
                    port=list(spec["ports"].values())[0],
                    image=spec["image"],
                    error_message="Docker daemon is not running."
                ))
            return results

        for spec in self.get_services_definitions():
            name = spec["name"]
            image = spec["image"]
            port = list(spec["ports"].values())[0]
            
            try:
                container: Container = self.client.containers.get(name)
                state = container.attrs.get("State", {})
                status = state.get("Status", "stopped")
                
                results.append(ServiceStatus(
                    name=name,
                    container_id=container.short_id,
                    status="running" if status == "running" else "stopped",
                    port=port,
                    image=image
                ))
            except NotFound:
                results.append(ServiceStatus(
                    name=name,
                    status="missing",
                    port=port,
                    image=image
                ))
            except APIError as e:
                results.append(ServiceStatus(
                    name=name,
                    status="error",
                    port=port,
                    image=image,
                    error_message=str(e)
                ))

        return results

    def start_stack(self) -> List[ServiceStatus]:
        """Deploys custom network, pulls required images, and starts all containers."""
        if not self.is_available():
            raise RuntimeError("Cannot start the stack. Docker is not running.")

        # Ensure network is configured
        self._ensure_network()
        
        specs = self.get_services_definitions()
        
        for spec in specs:
            name = spec["name"]
            image = spec["image"]
            
            # Pull image
            self.pull_image_with_progress(image)
            
            # Stop & remove container if running to avoid conflicts
            try:
                existing: Container = self.client.containers.get(name)
                logger.info(f"Removing pre-existing container '{name}' to ensure clean deployment...")
                existing.stop(timeout=5)
                existing.remove(force=True)
            except NotFound:
                pass
            
            # Run container
            logger.info(f"Starting container '{name}' on port {list(spec['ports'].values())[0]}...")
            
            run_kwargs = {
                "image": image,
                "name": name,
                "detach": True,
                "ports": spec["ports"],
                "volumes": spec["volumes"],
                "environment": spec["environment"],
                "extra_hosts": spec["extra_hosts"],
                "network": self.network_name,
                "restart_policy": {"Name": "always"}
            }
            
            if "device_requests" in spec:
                run_kwargs["device_requests"] = spec["device_requests"]
                
            try:
                self.client.containers.run(**run_kwargs)
            except Exception as e:
                # If GPU reservation fails, fallback to CPU
                if "device_requests" in run_kwargs and ("gpu" in str(e).lower() or "device" in str(e).lower()):
                    logger.warning(f"Failed to start container '{name}' with GPU reservation. Retrying in CPU fallback mode. Error: {e}")
                    del run_kwargs["device_requests"]
                    self.client.containers.run(**run_kwargs)
                else:
                    raise e
            
        logger.info("All containers initialized successfully.")
        # Pause slightly to allow startup
        time.sleep(2)
        return self.get_status()

    def stop_stack(self) -> List[ServiceStatus]:
        """Stops all running stack containers."""
        if not self.is_available():
            raise RuntimeError("Docker is unavailable.")

        specs = self.get_services_definitions()
        for spec in specs:
            name = spec["name"]
            try:
                container: Container = self.client.containers.get(name)
                if container.status == "running":
                    logger.info(f"Stopping container '{name}'...")
                    container.stop(timeout=10)
            except NotFound:
                pass
            except Exception as e:
                logger.warning(f"Error trying to stop container '{name}': {e}")
                
        logger.info("All containers stopped.")
        return self.get_status()

    def destroy_stack(self) -> None:
        """Stops and completely removes all containers, including clean removal of bridge networks."""
        if not self.is_available():
            raise RuntimeError("Docker is unavailable.")

        specs = self.get_services_definitions()
        for spec in specs:
            name = spec["name"]
            try:
                container: Container = self.client.containers.get(name)
                logger.info(f"Force removing container '{name}'...")
                container.remove(force=True)
            except NotFound:
                pass
            except Exception as e:
                logger.warning(f"Error removing container '{name}': {e}")

        # Clean bridge network
        try:
            network = self.client.networks.get(self.network_name)
            logger.info(f"Removing Docker bridge network '{self.network_name}'...")
            network.remove()
        except NotFound:
            pass
        except Exception as e:
            logger.warning(f"Error removing network '{self.network_name}': {e}")

        logger.info("Docker Stack cleanup complete.")

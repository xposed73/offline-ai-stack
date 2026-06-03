import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import docker
from docker.models.containers import Container
from docker.errors import ImageNotFound, NotFound, APIError
from app.config.settings import settings, BASE_DIR
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
        
        services = [
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
            }
        ]

        # Determine Kokoro Image - We always use the custom ONNX container which supports both English and German.
        kokoro_image = "kokoro-german-onnx:latest"
            
        if settings.ENABLE_TTS:
            kokoro_spec = {
                "name": "kokoro",
                "image": kokoro_image,
                "ports": {
                    "8881/tcp" if "onnx" in kokoro_image else "8880/tcp": settings.KOKORO_PORT
                },
                "volumes": {
                    str(settings.kokoro_path): {"bind": "/app/voices", "mode": "rw"}
                },
                "environment": {},
                "extra_hosts": {"host.docker.internal": "host-gateway"}
            }
            if "onnx" in kokoro_image:
                # Mount the German text rules script needed by the ONNX normalizer
                rules_path = (BASE_DIR / "app/docker/kokoro_german_onnx/german_text_rules.py").resolve()
                kokoro_spec["volumes"][str(rules_path)] = {"bind": "/app/german_text_rules.py", "mode": "ro"}
                
                default_voice = "martin" if getattr(settings, "APP_LANGUAGE", "en").lower() == "de" else "af_sky"
                default_lang = "de" if getattr(settings, "APP_LANGUAGE", "en").lower() == "de" else "en-us"

                # Add ONNX performance environment variables
                kokoro_spec["environment"] = {
                    "KOKORO_ONNX_THREADS": "2",
                    "KOKORO_ONNX_INTRA_OP_THREADS": "2",
                    "KOKORO_ONNX_INTER_OP_THREADS": "1",
                    "KOKORO_ONNX_EXECUTION_MODE": "sequential",
                    "KOKORO_ONNX_GRAPH_OPT": "all",
                    "KOKORO_ONNX_SPEED": "1.125",
                    "KOKORO_ONNX_TRIM": "true",
                    "KOKORO_ONNX_VOICE": default_voice,
                    "KOKORO_ONNX_LANG": default_lang,
                    "OMP_NUM_THREADS": "2",
                    "OPENBLAS_NUM_THREADS": "2",
                    "MKL_NUM_THREADS": "2",
                    "NUMEXPR_NUM_THREADS": "2",
                    "OMP_WAIT_POLICY": "PASSIVE",
                    "KOKORO_PAUSE_DURATION": "0.25",
                    "KOKORO_WORKERS": "2",
                    "KOKORO_ONNX_ALLOW_SPINNING": "0"
                }
            if "gpu" in kokoro_image.lower():
                kokoro_spec["device_requests"] = [
                    docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
                ]
            services.append(kokoro_spec)

        kokoro_internal_port = "8881" if "onnx" in kokoro_image.lower() else "8880"

        llm_model = settings.LLM_MODEL
        default_models = f"{llm_model};{llm_model}:latest" if ":" not in llm_model else llm_model

        # Configure OpenWebUI environment settings (with optional TTS parameters)
        webui_env = {
            "OLLAMA_BASE_URL": ollama_url,
            "WEBUI_AUTH": "true" if settings.OPENWEBUI_AUTH else "false",
            "ENABLE_PERSISTENT_CONFIG": "false",
            "DEFAULT_MODELS": default_models,
        }
        
        # Inject German language mode
        if getattr(settings, "APP_LANGUAGE", "en").lower() == "de":
            webui_env["DEFAULT_SYSTEM_PROMPT"] = "Bitte antworte immer auf Deutsch und formuliere die Sätze präzise."
            webui_env["DEFAULT_LOCALE"] = "de-DE"
            
        if settings.ENABLE_TTS:
            tts_voice = settings.KOKORO_VOICE
            # Kokoro v0.3.0 does not ship with a native German voice out-of-the-box in this image.
            # Using the default voice (e.g. af_bella) to prevent 400 Bad Request API crashes.
            if getattr(settings, "APP_LANGUAGE", "en").lower() == "de" and tts_voice.startswith(("af_", "am_", "bf_", "bm_", "df_")):
                tts_voice = "martin"  # Use the German ONNX voice
            elif getattr(settings, "APP_LANGUAGE", "en").lower() == "en" and tts_voice == "martin":
                tts_voice = "af_sky"  # Use the default English ONNX voice
                
            webui_env.update({
                "AUDIO_TTS_ENGINE": "openai",
                "AUDIO_TTS_OPENAI_API_BASE_URL": f"http://kokoro:{kokoro_internal_port}/v1",
                "AUDIO_TTS_OPENAI_API_KEY": "not-needed",
                "AUDIO_TTS_MODEL": settings.KOKORO_MODEL,
                "AUDIO_TTS_VOICE": tts_voice
            })

        if settings.ENABLE_STT:
            webui_env.update({
                "AUDIO_STT_ENGINE": "openai",
                "AUDIO_STT_OPENAI_API_BASE_URL": f"http://host.docker.internal:{settings.APP_PORT}/v1",
                "AUDIO_STT_OPENAI_API_KEY": "offline-ai-stack",
                "AUDIO_STT_MODEL": settings.WHISPER_MODEL
            })

        services.append({
            "name": "open-webui",
            "image": settings.OPENWEBUI_IMAGE,
            "ports": {
                "8080/tcp": settings.OPENWEBUI_PORT
            },
            "volumes": {
                str(settings.openwebui_path): {"bind": "/app/backend/data", "mode": "rw"}
            },
            "environment": webui_env,
            "extra_hosts": {"host.docker.internal": "host-gateway"}
        })



        services.append({
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
        })
        
        return services

    def pull_image_with_progress(self, image_name: str) -> None:
        """Pulls an image from registry (or builds from local source if available), displaying progress in the CLI console."""
        if not self.is_available():
            raise RuntimeError("Docker is unavailable.")

        try:
            # First check if the image is already pulled to skip downloads
            self.client.images.get(image_name)
            logger.debug(f"Image '{image_name}' is already cached locally. Skipping pull.")
            return
        except ImageNotFound:
            pass

        # If it's the Kokoro image and the cloned source folder exists, build it locally
        if image_name == settings.KOKORO_IMAGE and (BASE_DIR / "Kokoro-FastAPI").exists():
            logger.info(f"Image '{image_name}' not found locally. Building from local Kokoro-FastAPI source...")
            build_path = str((BASE_DIR / "Kokoro-FastAPI").resolve())
            dockerfile = "docker/cpu/Dockerfile.optimized"
        elif image_name == "kokoro-german-onnx:latest" and (BASE_DIR / "app/docker/kokoro_german_onnx/onnx-docker/Dockerfile").exists():
            logger.info(f"Image '{image_name}' not found locally. Building custom German/English ONNX Kokoro image...")
            # Auto-download any missing model weights/voices before building
            onnx_dir = BASE_DIR / "app/docker/kokoro_german_onnx"
            models_to_download = {
                "kokoro-martin.onnx": "https://huggingface.co/Godelaune/Kokoro-82M-ONNX-German-Martin/resolve/main/kokoro-martin.onnx",
                "voices-martin.npz": "https://huggingface.co/Godelaune/Kokoro-82M-ONNX-German-Martin/resolve/main/voices-martin.npz",
                "kokoro-v0_19.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx",
                "voices.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin"
            }
            import urllib.request
            for filename, url in models_to_download.items():
                filepath = onnx_dir / filename
                if not filepath.exists():
                    logger.info(f"Auto-downloading required TTS model file: {filename}...")
                    try:
                        temp_filepath = filepath.with_suffix(".tmp")
                        urllib.request.urlretrieve(url, temp_filepath)
                        temp_filepath.rename(filepath)
                        logger.info(f"Successfully downloaded {filename}.")
                    except Exception as download_error:
                        logger.error(f"Failed to auto-download {filename}: {download_error}")
                        raise download_error
            build_path = str((BASE_DIR / "app/docker/kokoro_german_onnx").resolve())
            dockerfile = "onnx-docker/Dockerfile"
        else:
            build_path = None

        if build_path:
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    transient=True
                ) as progress:
                    task = progress.add_task(f"Building {image_name} from source...", total=None)
                    for log in self.client.api.build(
                        path=build_path,
                        dockerfile=dockerfile,
                        tag=image_name,
                        rm=True,
                        decode=True
                    ):
                        if "stream" in log:
                            log_msg = log["stream"].strip()
                            if log_msg:
                                progress.update(task, description=f"Building: {log_msg}")
                logger.info(f"Successfully built and tagged '{image_name}' from local source.")
                return
            except Exception as e:
                logger.warning(f"Failed to build image {image_name} from local source: {e}. Falling back to pull...")

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
                    # If this is the kokoro container, switch image to CPU version
                    if name == "kokoro":
                        run_kwargs["image"] = "ghcr.io/remsky/kokoro-fastapi-cpu:latest"
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

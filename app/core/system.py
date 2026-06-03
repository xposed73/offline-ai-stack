import shutil
import subprocess
import sys
import platform
import psutil
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import docker
import httpx
from app.config.settings import settings
from app.core.logging import logger

class GPUInfo(BaseModel):
    """Pydantic model representing GPU capabilities."""
    detected: bool = False
    name: Optional[str] = None
    vram_mb: Optional[int] = None
    driver_version: Optional[str] = None

class SystemReport(BaseModel):
    """System specifications and requirements checklist."""
    os_name: str
    os_version: str
    cpu_count: int
    ram_gb: float
    disk_free_gb: float
    gpu: GPUInfo
    docker_installed: bool
    docker_running: bool
    ollama_running: bool
    requirements_met: bool
    warnings: list[str] = Field(default_factory=list)

def detect_gpu() -> GPUInfo:
    """Detects GPU details. Supports NVIDIA (via nvidia-smi) and Apple Silicon/macOS graphics."""
    # 1. Try NVIDIA GPU (Windows/Linux)
    try:
        # Query: name, memory.total, driver_version
        cmd = ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        
        output = result.stdout.strip()
        if output:
            # Parse output line (handles multi-GPU by taking the first one for simplicity)
            lines = output.split("\n")
            first_gpu = lines[0].split(",")
            
            name = first_gpu[0].strip()
            vram_mb = int(first_gpu[1].strip())
            driver = first_gpu[2].strip()
            
            return GPUInfo(
                detected=True,
                name=name,
                vram_mb=vram_mb,
                driver_version=driver
            )
    except (subprocess.SubprocessError, FileNotFoundError, IndexError, ValueError):
        pass

    # 2. Try Windows PowerShell fallback for NVIDIA GPUs if nvidia-smi failed (e.g. permission issues)
    if platform.system() == "Windows":
        try:
            cmd = ["powershell", "-Command", "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterCompatibility, AdapterRAM, DriverVersion | ConvertTo-Json"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            if res.stdout.strip():
                import json
                gpus = json.loads(res.stdout)
                # If there's only one GPU, it might not be a list in JSON, wrap it
                if not isinstance(gpus, list):
                    gpus = [gpus]
                
                for g in gpus:
                    compat = str(g.get("AdapterCompatibility", "")).lower()
                    name = str(g.get("Name", "")).lower()
                    if "nvidia" in compat or "nvidia" in name:
                        gpu_name = g.get("Name", "NVIDIA GPU")
                        ram_bytes = g.get("AdapterRAM", 0)
                        if ram_bytes:
                            if ram_bytes < 0:
                                ram_bytes = ram_bytes + 2**32
                            vram_mb = int(ram_bytes / (1024 * 1024))
                        else:
                            vram_mb = 0
                        driver = g.get("DriverVersion", "Unknown")
                        return GPUInfo(
                            detected=True,
                            name=gpu_name,
                            vram_mb=vram_mb,
                            driver_version=driver
                        )
        except Exception:
            pass

    # 2. Try macOS (Darwin) GPU detection
    if platform.system() == "Darwin":
        try:
            # Query system_profiler for Displays/Graphics info
            result = subprocess.run(["system_profiler", "SPDisplaysDataType"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            output = result.stdout
            
            # Find Chipset Model
            chipset = None
            for line in output.split("\n"):
                if "Chipset Model:" in line:
                    chipset = line.split(":", 1)[1].strip()
                    break
            
            if chipset:
                # On Apple Silicon, memory is Unified. We can get system RAM size for info.
                is_apple_silicon = "Apple" in chipset or platform.machine() == "arm64"
                vram_mb = None
                if is_apple_silicon:
                    # Let's get system memory and report it as unified memory in MB
                    ram_bytes = psutil.virtual_memory().total
                    vram_mb = int(ram_bytes / (1024 * 1024)) # MB of unified memory
                
                return GPUInfo(
                    detected=True,
                    name=chipset,
                    vram_mb=vram_mb,
                    driver_version="Metal Support"
                )
        except (subprocess.SubprocessError, FileNotFoundError, IndexError, ValueError):
            pass

    return GPUInfo(detected=False)

def verify_docker() -> Tuple[bool, bool]:
    """Verifies if Docker is installed and running on the host system."""
    docker_installed = shutil.which("docker") is not None
    docker_running = False
    
    if docker_installed:
        try:
            client = docker.from_env()
            client.ping()
            docker_running = True
        except Exception:
            # Installed but not running
            pass
            
    return docker_installed, docker_running

def verify_ollama() -> bool:
    """Verifies if Ollama is running and accessible via its HTTP API."""
    try:
        # Ping the Ollama API version endpoint
        url = f"{settings.OLLAMA_HOST}/api/tags"
        response = httpx.get(url, timeout=2.0)
        return response.status_code == 200
    except (httpx.RequestError, Exception):
        return False

def generate_system_report() -> SystemReport:
    """Gathers resources information and returns a system status report."""
    os_name = platform.system()
    os_version = platform.release()
    cpu_count = psutil.cpu_count(logical=True) or 1
    ram_bytes = psutil.virtual_memory().total
    ram_gb = round(ram_bytes / (1024 ** 3), 2)
    
    # Disk space check in workspace folder
    total, used, free = shutil.disk_usage(settings.data_path.parent)
    disk_free_gb = round(free / (1024 ** 3), 2)
    
    gpu = detect_gpu()
    docker_installed, docker_running = verify_docker()
    ollama_running = verify_ollama()
    
    warnings = []
    requirements_met = True
    
    # Validations
    if ram_gb < 8.0:
        requirements_met = False
        warnings.append(f"Insufficient RAM: {ram_gb}GB. A minimum of 8GB is required, 16GB+ is recommended.")
    elif ram_gb < 16.0:
        warnings.append(f"Modest RAM detected: {ram_gb}GB. High parameter models may run slowly or encounter out-of-memory errors.")
        
    if cpu_count < 4:
        warnings.append(f"Low CPU core count: {cpu_count} cores. 4+ logical cores are recommended.")
        
    if disk_free_gb < 20.0:
        requirements_met = False
        warnings.append(f"Low free disk space: {disk_free_gb}GB available. At least 20GB of free space is needed for images and models.")
        
    if not gpu.detected:
        if os_name == "Darwin":
            warnings.append("No Apple Silicon or supported GPU detected. Ollama will fall back to CPU, which will be significantly slower.")
        else:
            warnings.append("No NVIDIA GPU was detected. Inference will run strictly on CPU, which will be significantly slower.")
    elif gpu.vram_mb and gpu.vram_mb < 6000:
        if os_name == "Darwin":
            warnings.append(f"Low unified system memory detected ({ram_gb} GB). Recommend at least 16GB of Unified Memory for comfortable local running.")
        else:
            warnings.append(f"Low GPU VRAM detected ({gpu.vram_mb} MB). Recommend at least 6GB (6144 MB) of VRAM for comfortable local LLM running.")
        
    if not docker_installed:
        requirements_met = False
        warnings.append("Docker is not installed or not in the system PATH. Docker is required to deploy Qdrant, OpenWebUI, and n8n.")
    elif not docker_running:
        requirements_met = False
        warnings.append("Docker is installed, but the daemon is not running. Please start Docker Desktop or the dockerd service.")
        
    if not ollama_running:
        warnings.append("Ollama is not running. Please launch Ollama to enable local AI inference.")
        
    return SystemReport(
        os_name=os_name,
        os_version=os_version,
        cpu_count=cpu_count,
        ram_gb=ram_gb,
        disk_free_gb=disk_free_gb,
        gpu=gpu,
        docker_installed=docker_installed,
        docker_running=docker_running,
        ollama_running=ollama_running,
        requirements_met=requirements_met,
        warnings=warnings
    )

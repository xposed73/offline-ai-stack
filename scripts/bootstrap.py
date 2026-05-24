#!/usr/bin/env python3
"""
Offline AI Stack - Automated macOS/Linux Bootstrap Script

This script completely automates the installation, virtualenv creation,
dependency resolution (via Astral uv), and local environment configuration.
It uses a two-phase execution:
1. Setup Python, uv, and dependencies (without rich).
2. Re-executes itself inside the virtual environment to display rich output,
   clone Kokoro-FastAPI, build its Docker container, and show the summary.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import urllib.request

def check_python_version():
    """Ensure basic Python 3 is used for bootstrapping."""
    if sys.version_info < (3, 7):
        print("\033[1;31m  [Error] Python version must be at least 3.7 to run this bootstrap script.\033[0m")
        sys.exit(1)

def ensure_uv():
    """Checks for uv in PATH and installs it if missing."""
    uv_path = shutil.which("uv")
    if uv_path:
        return uv_path
        
    print("\033[1;34m  -> 'uv' was not found in system PATH. Attempting automated installation...\033[0m")
    
    # Try downloading the install script
    try:
        req = urllib.request.Request("https://astral.sh/uv/install.sh")
        with urllib.request.urlopen(req) as response:
            script = response.read()
            
        process = subprocess.Popen(["sh"], stdin=subprocess.PIPE)
        process.communicate(input=script)
        
        if process.returncode != 0:
            raise RuntimeError("Installation script failed")
            
        # Update path for current execution
        os.environ["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{os.path.expanduser('~/.cargo/bin')}:{os.environ.get('PATH', '')}"
        
        uv_path = shutil.which("uv")
        if not uv_path:
            raise RuntimeError("uv still not in PATH after installation")
            
        print("\033[1;32m  -> 'uv' successfully installed!\033[0m")
        return uv_path
    except Exception as e:
        print("\033[1;31m  [Error] Automated installation of 'uv' failed.\033[0m")
        print(f"\033[1;37m  Error details: {e}\033[0m")
        print("\033[1;37m  Please install 'uv' manually from https://github.com/astral-sh/uv and run this script again.\033[0m")
        sys.exit(1)

def create_venv_and_install(uv_path):
    """Creates .venv and installs dependencies via uv."""
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        print("\033[1;33m[3/5] Creating Python Virtual Environment (.venv)...\033[0m")
        subprocess.run([uv_path, "venv", "--python", "3.11"], check=True)
        print("\033[1;32m  -> Virtual environment created successfully.\033[0m")
    else:
        print("\033[1;37m  -> Virtual environment already exists. Skipping creation.\033[0m")

    print("\033[1;33m[4/5] Resolving and Installing Dependencies...\033[0m")
    
    # Try online install first
    res = subprocess.run([uv_path, "pip", "install", "-e", "."], cwd=os.getcwd())
    if res.returncode == 0:
        print("\033[1;32m  -> Project packages installed successfully in editable development mode.\033[0m")
    else:
        print("\033[1;33m  -> Network install failed, attempting offline fallback...\033[0m")
        res_offline = subprocess.run([uv_path, "pip", "install", "--offline", "-e", "."], cwd=os.getcwd())
        if res_offline.returncode == 0:
            print("\033[1;33m  -> Project packages installed successfully (OFFLINE MODE).\033[0m")
        else:
            print("\033[1;31m  [Error] Failed to install dependencies.\033[0m")
            print("\033[1;37m  Please ensure you have an internet connection for the first run, or the packages are cached.\033[0m")
            sys.exit(1)

def phase_one():
    """Phase 1: Ensure system prerequisites, install uv, create venv, and install python dependencies."""
    print("\033[1;36m==========================================================\033[0m")
    print("\033[1;32m          OFFLINE AI STACK - MAC/LINUX BOOTSTRAP          \033[0m")
    print("\033[1;36m==========================================================\033[0m")
    
    print("\033[1;33m[1/5] Verifying Python Installation...\033[0m")
    check_python_version()
    print(f"\033[1;37m  -> Found Python: {sys.version.split(' ')[0]}\033[0m")
    
    print("\033[1;33m[2/5] Verifying Astral 'uv' Package Manager...\033[0m")
    uv_path = ensure_uv()
    
    create_venv_and_install(uv_path)
    
    # Restart the script using the new virtual environment python
    venv_python = os.path.join(".venv", "bin", "python")
    if not os.path.exists(venv_python):
        print("\033[1;31m  [Error] Failed to locate virtual environment Python interpreter.\033[0m")
        sys.exit(1)
        
    os.execv(venv_python, [venv_python, __file__, "--phase-two"])

def clone_and_build_kokoro(console):
    """Clones Kokoro-FastAPI and builds the docker container using the rich library."""
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    import docker
    import dotenv

    env_config = dotenv.dotenv_values(".env")
    app_language = env_config.get("APP_LANGUAGE", "en").lower()

    if app_language == "de":
        console.print("[bold yellow][6/6] Setting up Kokoro-German (TTS)...[/bold yellow]")
        image_name = "kokoro-german:latest"
        build_path = "app/docker/kokoro_german"
        dockerfile = "Dockerfile"
    else:
        console.print("[bold yellow][6/6] Setting up Kokoro-FastAPI (TTS)...[/bold yellow]")
        
        kokoro_dir = Path("Kokoro-FastAPI")
        if not kokoro_dir.exists():
            console.print("[blue]  -> Cloning Kokoro-FastAPI repository...[/blue]")
            res = subprocess.run(["git", "clone", "https://github.com/remsky/Kokoro-FastAPI.git"], capture_output=True, text=True)
            if res.returncode != 0:
                console.print(f"[bold red]  [Error] Failed to clone repository: {res.stderr}[/bold red]")
                return
            console.print("[bold green]  -> Repository cloned successfully.[/bold green]")
        else:
            console.print("[dim]  -> Kokoro-FastAPI repository already exists.[/dim]")
            
        image_name = "ghcr.io/remsky/kokoro-fastapi-cpu:v0.3.0"
        build_path = "Kokoro-FastAPI"
        dockerfile = "docker/cpu/Dockerfile.optimized"

    try:
        client = docker.from_env()
    except Exception as e:
        console.print(f"[bold red]  [Error] Docker is not available. Ensure Docker Desktop is running: {e}[/bold red]")
        return

    try:
        client.images.get(image_name)
        console.print(f"[dim]  -> Image '{image_name}' is already cached locally. Skipping build.[/dim]")
    except docker.errors.ImageNotFound:
        console.print(f"[blue]  -> Building Docker container '{image_name}' (this may take a while)...[/blue]")
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                transient=True
            ) as progress:
                task = progress.add_task(f"Building {image_name} from source...", total=None)
                for log in client.api.build(
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
            console.print(f"[bold green]  -> Successfully built and tagged '{image_name}'![/bold green]")
        except Exception as e:
            console.print(f"[bold red]  [Error] Failed to build container: {e}[/bold red]")

def phase_two():
    """Phase 2: Use Rich to bootstrap the .env, build Kokoro, and show the final summary."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    
    console.print("[bold yellow][5/6] Checking Configuration Environment Settings...[/bold yellow]")
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists():
        if env_example_path.exists():
            shutil.copy(".env.example", ".env")
            console.print("[bold green]  -> Created default configuration '.env' from '.env.example'.[/bold green]")
        else:
            console.print("[bold red]  [Error] '.env.example' missing. Cannot create '.env'.[/bold red]")
    else:
        console.print("[dim]  -> Pre-existing configuration '.env' detected. Keeping unchanged.[/dim]")
        
    clone_and_build_kokoro(console)
    
    # Success Overview
    console.print()
    
    banner_text = Text()
    banner_text.append("🚀 STACK IS NOW ONLINE AND READY FOR USE! 🚀\n\n", style="bold green")
    banner_text.append("To execute local CLI workflows, run the following command:\n", style="white")
    banner_text.append("  .venv/bin/offline-ai system-check\n\n", style="bold cyan")
    banner_text.append("To launch Docker containers and pull local LLMs:\n", style="white")
    banner_text.append("  .venv/bin/offline-ai start\n\n", style="bold cyan")
    banner_text.append("To launch the background REST FastAPI web server:\n", style="white")
    banner_text.append("  .venv/bin/offline-ai serve\n\n", style="bold cyan")
    banner_text.append("Enjoy your fully private local AI stack!", style="bold green")
    
    console.print(Panel(banner_text, border_style="bold green", title="OFFLINE AI STACK PROVISIONED SUCCESSFULLY!", expand=False))

if __name__ == "__main__":
    # If the phase-two argument is present, we are already inside the virtual environment
    if "--phase-two" in sys.argv:
        phase_two()
    else:
        # Check if we're inexplicably already running inside a fully installed venv (user manually sourced)
        try:
            import rich
            import docker
            # We are in the venv and have rich/docker! Run phase one fast then phase two
            phase_one()
        except ImportError:
            # First execution
            phase_one()

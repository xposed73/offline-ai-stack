import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
import argparse
from pathlib import Path
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.utils.dashboard import get_dashboard_html

# Core Stack Imports
from app.config.settings import settings
from app.core.logging import logger, setup_logger
from app.core.system import generate_system_report
from app.docker.orchestrator import DockerOrchestrator
from app.ollama.client import OllamaClient
from app.qdrant.client import QdrantManager
from app.rag.pipeline import RAGPipeline
from app.openwebui import OpenWebUIManager
from app.n8n import N8NManager
from app.models.schemas import (
    IngestFileRequest,
    IngestFolderRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
    SearchResultNode
)

# Rich terminal components
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# ==========================================
# FastAPI Application Definition
# ==========================================
app = FastAPI(
    title="Offline AI Stack API",
    description="REST API for local technical RAG and system orchestration.",
    version="0.1.0"
)

# Configure CORS for local development integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def get_control_panel():
    """Serves the beautiful interactive Web Control Panel."""
    return get_dashboard_html()

@app.get("/status", tags=["System"])
def get_api_status():
    """Returns the full runtime status of host resources, Docker stack, and Ollama."""
    try:
        report = generate_system_report()
        docker_orc = DockerOrchestrator()
        docker_status = docker_orc.get_status() if docker_orc.is_available() else []
        
        ollama_cli = OllamaClient()
        ollama_models = ollama_cli.list_local_models() if ollama_cli.is_healthy() else []
        
        qdrant_mgr = QdrantManager()
        qdrant_collections = qdrant_mgr.list_collections() if qdrant_mgr.is_healthy() else []
        
        openwebui_mgr = OpenWebUIManager()
        n8n_mgr = N8NManager()
        
        return {
            "status": "healthy",
            "host_resources": {
                "os": f"{report.os_name} {report.os_version}",
                "cpu_cores": report.cpu_count,
                "ram_gb": report.ram_gb,
                "disk_free_gb": report.disk_free_gb,
                "gpu": report.gpu.model_dump()
            },
            "docker_services": [s.model_dump() for s in docker_status],
            "ollama": {
                "running": report.ollama_running,
                "host": settings.OLLAMA_HOST,
                "active_models": ollama_models
            },
            "qdrant": {
                "running": qdrant_mgr.is_healthy(),
                "collections": qdrant_collections
            },
            "openwebui": {
                "running": openwebui_mgr.is_healthy(),
                "url": openwebui_mgr.get_web_url()
            },
            "n8n": {
                "running": n8n_mgr.is_healthy(),
                "url": n8n_mgr.get_web_url()
            }
        }
    except Exception as e:
        logger.error(f"Error compiling REST status payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile system health: {str(e)}"
        )

@app.post("/ingest/file", response_model=IngestResponse, tags=["RAG Ingestion"])
def api_ingest_file(req: IngestFileRequest):
    """Ingests a single local document file (PDF, TXT, MD) into the Qdrant index."""
    try:
        path = Path(req.file_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Specified file path does not exist: {req.file_path}"
            )
            
        pipeline = RAGPipeline(collection_name=req.collection_name)
        count = pipeline.ingest_file(path)
        
        return IngestResponse(
            success=True,
            nodes_ingested=count,
            message=f"Successfully ingested {count} nodes from {path.name}"
        )
    except Exception as e:
        logger.error(f"REST Ingestion failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/ingest/folder", response_model=IngestResponse, tags=["RAG Ingestion"])
def api_ingest_folder(req: IngestFolderRequest):
    """Recursively ingests all supported documents in a folder."""
    try:
        path = Path(req.folder_path)
        if not path.exists() or not path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Specified folder path does not exist or is not a directory: {req.folder_path}"
            )
            
        pipeline = RAGPipeline(collection_name=req.collection_name)
        count = pipeline.ingest_directory(path)
        
        return IngestResponse(
            success=True,
            nodes_ingested=count,
            message=f"Successfully ingested {count} nodes from folder '{path.name}'"
        )
    except Exception as e:
        logger.error(f"REST Folder Ingestion failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/query", response_model=QueryResponse, tags=["RAG Query"])
def api_query_rag(req: QueryRequest):
    """Retrieves document chunks from Qdrant and returns a local LLM response."""
    try:
        pipeline = RAGPipeline(collection_name=req.collection_name)
        answer = pipeline.query(req.prompt, system_prompt=req.system_prompt)
        
        return QueryResponse(
            answer=answer,
            collection=pipeline.collection_name,
            model_used=settings.LLM_MODEL
        )
    except Exception as e:
        logger.error(f"REST Query failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/search", response_model=SearchResponse, tags=["RAG Query"])
def api_semantic_search(req: SearchRequest):
    """Performs raw semantic matching against the vector store, bypassing the LLM."""
    try:
        pipeline = RAGPipeline(collection_name=req.collection_name)
        nodes = pipeline.semantic_search(req.query, limit=req.limit)
        
        results = [
            SearchResultNode(
                node_id=n["id"],
                text=n["text"],
                score=n["score"],
                metadata=n["metadata"]
            )
            for n in nodes
        ]
        
        return SearchResponse(
            query=req.query,
            results=results
        )
    except Exception as e:
        logger.error(f"REST Search failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================
# Rich Terminal CLI Actions
# ==========================================

def draw_banner() -> None:
    """Renders a beautiful modern header inside the terminal."""
    banner_text = Text()
    banner_text.append(" ██████╗ ███████╗███████╗██╗     ██╗███╗   ██╗███████╗\n", style="bold cyan")
    banner_text.append("██╔═══██╗██╔════╝██╔════╝██║     ██║████╗  ██║██╔════╝\n", style="bold cyan")
    banner_text.append("██║   ██║█████╗  █████╗  ██║     ██║██╔██╗ ██║█████╗  \n", style="bold blue")
    banner_text.append("██║   ██║██╔══╝  ██╔══╝  ██║     ██║██║╚██╗██║██╔══╝  \n", style="bold blue")
    banner_text.append("╚██████╔╝██║     ██║     ███████╗██║██║ ╚████║███████╗\n", style="bold magenta")
    banner_text.append(" ╚═════╝ ╚═╝     ╚═╝     ╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝\n", style="bold magenta")
    banner_text.append("             LOCAL AI & RAG STACK ORCHESTRATOR        ", style="italic bold white")
    
    console.print(Panel(banner_text, border_style="bold magenta", expand=False))

def cli_system_check() -> None:
    """CLI operation: runs local hardware resource requirements checking."""
    draw_banner()
    console.print("[bold yellow]Initiating Host & Software Verification Check...[/bold yellow]\n")
    
    report = generate_system_report()
    
    # 1. System Table
    table = Table(title="Hardware & System Resources Status", header_style="bold cyan", border_style="dim")
    table.add_column("Parameter", style="bold")
    table.add_column("Value", style="white")
    table.add_column("Status", style="bold")
    
    # OS
    table.add_row("Operating System", f"{report.os_name} ({report.os_version})", "[green]OK[/green]" if report.os_name in ["Windows", "Linux", "Darwin"] else "[yellow]Warn[/yellow]")
    # CPU
    cpu_status = "[green]OK[/green]" if report.cpu_count >= 4 else "[yellow]Warn[/yellow]"
    table.add_row("CPU Cores", f"{report.cpu_count} logical cores", cpu_status)
    # RAM
    ram_status = "[green]OK[/green]" if report.ram_gb >= 16.0 else ("[yellow]OK (Min met)[/yellow]" if report.ram_gb >= 8.0 else "[red]Failure[/red]")
    table.add_row("System RAM", f"{report.ram_gb:.2f} GB", ram_status)
    # Disk Space
    disk_status = "[green]OK[/green]" if report.disk_free_gb >= 20.0 else "[red]Low Space[/red]"
    table.add_row("Free Disk Space", f"{report.disk_free_gb:.2f} GB", disk_status)
    
    console.print(table)
    console.print()

    # 2. GPU Table
    gpu_table = Table(title="Graphics Processing Unit (Inference Core)", header_style="bold magenta", border_style="dim")
    gpu_table.add_column("GPU Parameter", style="bold")
    gpu_table.add_column("Details", style="white")
    
    if report.gpu.detected:
        if "Metal" in str(report.gpu.driver_version):
            gpu_table.add_row("Apple GPU Found", "[green]Yes[/green]")
            gpu_table.add_row("Device Name", str(report.gpu.name))
            gpu_table.add_row("Unified Memory", f"{report.gpu.vram_mb} MB" if report.gpu.vram_mb else "N/A")
            gpu_table.add_row("Acceleration API", "Metal")
        else:
            gpu_table.add_row("NVIDIA GPU Found", "[green]Yes[/green]")
            gpu_table.add_row("Device Name", str(report.gpu.name))
            gpu_table.add_row("Dedicated VRAM", f"{report.gpu.vram_mb} MB")
            gpu_table.add_row("Driver Version", str(report.gpu.driver_version))
    else:
        gpu_table.add_row("GPU Found", "[red]No[/red]")
        gpu_table.add_row("Note", "CPU-only fallback mode. Large models will feel sluggish.")
        
    console.print(gpu_table)
    console.print()

    # 3. Docker and Ollama health
    soft_table = Table(title="Dependency Check", header_style="bold green", border_style="dim")
    soft_table.add_column("Software Service", style="bold")
    soft_table.add_column("Availability", style="white")
    
    soft_table.add_row("Docker CLI Tool", "[green]Installed[/green]" if report.docker_installed else "[red]Not found[/red]")
    soft_table.add_row("Docker Daemon Running", "[green]Yes[/green]" if report.docker_running else "[red]No[/red]")
    soft_table.add_row("Ollama API Connectivity", "[green]Healthy[/green]" if report.ollama_running else "[yellow]Offline / Not started[/yellow]")
    
    console.print(soft_table)
    console.print()

    # Final decision panel
    if report.requirements_met:
        console.print(Panel("[bold green]SUCCESS: System requirements validated successfully. Your environment is ready to start the AI Stack.[/bold green]", border_style="green"))
    else:
        console.print(Panel("[bold red]CRITICAL: Environment check failed. Review warnings below before running the stack.[/bold red]", border_style="red"))
        
    if report.warnings:
        console.print("[bold yellow]Warnings / System Recommendations:[/bold yellow]")
        for w in report.warnings:
            console.print(f" ⚠️  [yellow]{w}[/yellow]")
        console.print()

def cli_start() -> None:
    """CLI operation: provisions network, pulls images, launches Docker stack, and pulls Ollama models."""
    draw_banner()
    console.print("[bold green]Initializing local Offline AI Stack...[/bold green]\n")
    
    # 1. Start containers
    orc = DockerOrchestrator()
    if not orc.is_available():
        console.print("[bold red]Error: Docker is not running. Please start Docker Desktop first![/bold red]")
        sys.exit(1)
        
    console.print("[yellow]Deploying container stack...[/yellow]")
    status_list = orc.start_stack()
    
    # Print status table
    table = Table(title="Docker Services Health", header_style="bold green", border_style="dim")
    table.add_column("Container", style="bold")
    table.add_column("Image", style="dim")
    table.add_column("External Port", style="white")
    table.add_column("Status", style="bold")
    
    for s in status_list:
        status_color = "green" if s.status == "running" else "red"
        table.add_row(
            s.name,
            s.image,
            str(s.port),
            f"[{status_color}]{s.status.upper()}[/{status_color}]"
        )
    console.print(table)
    console.print()

    # 2. Verify Ollama & Pull Models
    ollama_cli = OllamaClient()
    if not ollama_cli.is_healthy():
        console.print("[bold yellow]Ollama not running. Attempting connection check...[/bold yellow]")
        console.print("Please make sure Ollama is launched (by clicking Ollama taskbar app or running 'ollama serve').")
        return
        
    console.print(f"[yellow]Verifying model availability (LLM: '{settings.LLM_MODEL}', Embedding: '{settings.EMBEDDING_MODEL}')...[/yellow]")
    
    # Pull embedding model
    embedding_success = ollama_cli.pull_model(settings.EMBEDDING_MODEL)
    # Pull LLM model
    llm_success = ollama_cli.pull_model(settings.LLM_MODEL)
    
    if embedding_success and llm_success:
        console.print(Panel(
            f"[bold green]STACK ONLINE AND OPERATIONAL![/bold green]\n\n"
            f"🔗 [bold cyan]FastAPI Server:[/bold cyan] http://localhost:{settings.APP_PORT}\n"
            f"🔗 [bold cyan]OpenWebUI:[/bold cyan] http://localhost:{settings.OPENWEBUI_PORT}\n"
            f"🔗 [bold cyan]n8n Automations:[/bold cyan] http://localhost:{settings.N8N_PORT}\n"
            f"🔗 [bold cyan]Qdrant Vector DB:[/bold cyan] http://localhost:{settings.QDRANT_PORT}\n\n"
            f"All data volumes are mounted locally. You can use OpenWebUI directly or execute Python queries.",
            border_style="green",
            title="Local AI Environment"
        ))
    else:
        console.print(Panel("[bold yellow]Stack containers started, but failed to complete pulling Ollama models. Please pull them manually using:\n  ollama pull nomic-embed-text\n  ollama pull tinyllama[/bold yellow]", border_style="yellow"))

def cli_stop() -> None:
    """CLI operation: stops all stack containers."""
    draw_banner()
    orc = DockerOrchestrator()
    if not orc.is_available():
        console.print("[bold red]Docker daemon is offline.[/bold red]")
        sys.exit(1)
        
    console.print("[yellow]Stopping Offline AI Stack Docker containers...[/yellow]")
    orc.stop_stack()
    console.print("[bold green]Stack stopped successfully.[/bold green]")

def cli_status() -> None:
    """CLI operation: prints service status dashboard."""
    draw_banner()
    
    # Docker
    orc = DockerOrchestrator()
    docker_ok = orc.is_available()
    status_list = orc.get_status() if docker_ok else []
    
    table = Table(title="Docker Services Health", header_style="bold blue", border_style="dim")
    table.add_column("Container", style="bold")
    table.add_column("Mapped Port", style="white")
    table.add_column("Status", style="bold")
    
    for s in status_list:
        status_color = "green" if s.status == "running" else "red"
        table.add_row(s.name, str(s.port), f"[{status_color}]{s.status.upper()}[/{status_color}]")
        
    console.print(table)
    console.print()

    # Ollama
    ollama_cli = OllamaClient()
    ollama_healthy = ollama_cli.is_healthy()
    models = ollama_cli.list_local_models() if ollama_healthy else []
    
    ollama_panel_text = f"Status: {'[bold green]HEALTHY[/bold green]' if ollama_healthy else '[bold red]OFFLINE[/bold red]'}\n"
    ollama_panel_text += f"Host: {settings.OLLAMA_HOST}\n"
    if models:
        ollama_panel_text += f"Downloaded Models: {', '.join(models)}"
    else:
        ollama_panel_text += "Downloaded Models: None (or Ollama unreachable)"
        
    console.print(Panel(ollama_panel_text, title="Ollama Service Overview", border_style="magenta"))
    
    # Qdrant Info
    qdrant_mgr = QdrantManager()
    qdrant_healthy = qdrant_mgr.is_healthy()
    collections = qdrant_mgr.list_collections() if qdrant_healthy else []
    
    q_text = f"Status: {'[bold green]HEALTHY[/bold green]' if qdrant_healthy else '[bold red]OFFLINE[/bold red]'}\n"
    if qdrant_healthy:
        q_text += "Collections Discovery:\n"
        if collections:
            for col in collections:
                count = qdrant_mgr.get_collection_count(col)
                q_text += f"  - [cyan]{col}[/cyan] ({count} vectors indexed)\n"
        else:
            q_text += "  - No collections found. Run an ingestion script first."
            
    console.print(Panel(q_text, title="Qdrant Database Index Status", border_style="green"))

def cli_ingest_file(file_path_str: str) -> None:
    """CLI operation: parses and indexes a single local document file."""
    path = Path(file_path_str)
    if not path.exists():
        console.print(f"[bold red]Error: Specified file path does not exist: {file_path_str}[/bold red]")
        sys.exit(1)
        
    console.print(f"[yellow]Ingesting document {path.name} into offline Qdrant collection...[/yellow]")
    try:
        pipeline = RAGPipeline()
        count = pipeline.ingest_file(path)
        console.print(Panel(f"[bold green]INGESTION COMPLETE![/bold green]\n\nSuccessfully split, embedded, and indexed [bold cyan]{count}[/bold cyan] nodes into Qdrant collection '[magenta]{pipeline.collection_name}[/magenta]'.", border_style="green"))
    except Exception as e:
        console.print(f"[bold red]Ingestion failed: {e}[/bold red]")

def cli_ingest_folder(folder_path_str: str) -> None:
    """CLI operation: recursively indexes an entire folder structure."""
    path = Path(folder_path_str)
    if not path.exists() or not path.is_dir():
        console.print(f"[bold red]Error: Specified path is not a folder: {folder_path_str}[/bold red]")
        sys.exit(1)
        
    console.print(f"[yellow]Scanning and indexing directory '{path.name}' recursively...[/yellow]")
    try:
        pipeline = RAGPipeline()
        count = pipeline.ingest_directory(path)
        console.print(Panel(f"[bold green]INGESTION COMPLETE![/bold green]\n\nSuccessfully indexed [bold cyan]{count}[/bold cyan] chunks from folder '{path.name}' into vector database.", border_style="green"))
    except Exception as e:
        console.print(f"[bold red]Folder ingestion failed: {e}[/bold red]")

def cli_query(query_str: str, german_mode: bool = False) -> None:
    """CLI operation: queries the vector database and outputs augmented answer."""
    console.print(f"[yellow]Retrieving context and formulating local RAG answer...[/yellow]")
    
    sys_prompt = None
    if german_mode or getattr(settings, "APP_LANGUAGE", "en").lower() == "de":
        sys_prompt = "Optimierung: Bitte antworte immer auf Deutsch und formuliere die Sätze präzise und professionell."
        
    try:
        pipeline = RAGPipeline()
        # Retrieve sources first to present them cleanly
        sources = pipeline.semantic_search(query_str, limit=3)
        answer = pipeline.query(query_str, system_prompt=sys_prompt)
        
        console.print(Panel(answer, title="Augmented Local LLM Response", border_style="bold cyan"))
        
        # Output context bibliography
        if sources:
            console.print("\n[bold dim]Retrieved Sources & Context Metadata:[/bold dim]")
            for i, src in enumerate(sources):
                score_pct = src["score"] * 100
                doc_name = src["metadata"].get("file_name", "unknown")
                console.print(f" [{i+1}] [cyan]{doc_name}[/cyan] (similarity: {score_pct:.1f}%)")
                snippet = src["text"].replace("\n", " ").strip()
                if len(snippet) > 120:
                    snippet = snippet[:120] + "..."
                console.print(f"     [dim]\"{snippet}\"[/dim]")
            console.print()
    except Exception as e:
        console.print(f"[bold red]Query failed: {e}[/bold red]")

def main() -> None:
    """Main CLI program router."""
    parser = argparse.ArgumentParser(description="Offline AI Stack Orchestration CLI")
    subparsers = parser.add_subparsers(dest="command", help="Orchestrator Actions")

    # system-check
    subparsers.add_parser("system-check", help="Verify hardware resources, Docker running state, and Ollama connectivity")
    # start
    subparsers.add_parser("start", help="Provision custom network, pull images, launch containers, and pull models")
    # stop
    subparsers.add_parser("stop", help="Stop all active containers in the stack")
    # status
    subparsers.add_parser("status", help="Generate dashboard report of running services and qdrant indexes")
    
    # ingest-file
    file_parser = subparsers.add_parser("ingest-file", help="Ingest a single document file (PDF, TXT, MD)")
    file_parser.add_argument("path", type=str, help="Absolute or relative path to file")
    
    # ingest-folder
    folder_parser = subparsers.add_parser("ingest-folder", help="Recursively ingest an entire folder of files")
    folder_parser.add_argument("path", type=str, help="Absolute or relative path to directory")
    
    # query
    query_parser = subparsers.add_parser("query", help="Ask a question using the RAG augmented engine")
    query_parser.add_argument("prompt", type=str, help="The prompt to search and formulate answer for")
    query_parser.add_argument("--de", action="store_true", help="German language optimization override")

    # serve
    subparsers.add_parser("serve", help="Launch the high-performance FastAPI web server")

    args = parser.parse_args()

    # Route subcommands
    if args.command == "system-check":
        cli_system_check()
    elif args.command == "start":
        cli_start()
    elif args.command == "stop":
        cli_stop()
    elif args.command == "status":
        cli_status()
    elif args.command == "ingest-file":
        cli_ingest_file(args.path)
    elif args.command == "ingest-folder":
        cli_ingest_folder(args.path)
    elif args.command == "query":
        cli_query(args.prompt, german_mode=args.de)
    elif args.command == "serve":
        draw_banner()
        console.print(f"[bold green]Launching high-performance REST API Server...[/bold green]")
        console.print(f"🔗 Documentation available at http://localhost:{settings.APP_PORT}/docs")
        console.print(f"🔗 Service endpoints base url http://localhost:{settings.APP_PORT}")
        uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
    else:
        # Default fallback: output help
        parser.print_help()

if __name__ == "__main__":
    main()

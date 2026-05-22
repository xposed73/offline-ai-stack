# Offline AI Stack 🚀

Offline AI Stack is a production-grade, modular, and fully private local AI ecosystem. It automates system requirement verification, detects host hardware capabilities (including NVIDIA GPU VRAM), launches containerized services (Qdrant vector database, OpenWebUI, and the n8n automation server), pulls LLMs, and deploys a clean **Retrieval-Augmented Generation (RAG)** pipeline.

---

## ━━━━━━━━━━━━━━━━━━
## 🌟 Core Features
## ━━━━━━━━━━━━━━━━━━

* **100% Air-Gapped / Private**: Zero API keys, zero cloud latency, and complete data boundaries.
* **Modern Package Manager**: Built specifically around Astral's ultra-fast `uv` toolchain instead of legacy pip paths.
* **Auto-GPU Verification**: Detects available NVIDIA CUDA cores and dedicates VRAM via automatic command-line parsing of `nvidia-smi`.
* **Robust Docker Orchestration**: Python SDK container lifecycle controller that deploys, monitors, and stops Qdrant, OpenWebUI, and n8n services on a custom virtual bridge network.
* **Automated Ollama Pipelines**: Streamlined streaming pulls for private embeddings (`nomic-embed-text`) and inference models (`llama3` or `mistral`) with active terminal progress bars.
* **Dynamic Dimension Auto-Detection**: Qdrant vector collections auto-configure their cosine distance coordinates by automatically querying the dimension payload of the downloaded embedding engine.
* **Enterprise Ingestion API**: Out-of-the-box support for single PDF documents, folder bulk indexing, semantic search queries, and custom system-level German language optimization flags.

---

## ━━━━━━━━━━━━━━━━━━
## 🛠️ Project Tech Stack
## ━━━━━━━━━━━━━━━━━━

* **Language**: Python 3.11 / 3.12
* **Package Manager**: Astral `uv`
* **Orchestrator**: Docker SDK for Python
* **LLM Engine**: Ollama
* **Vector DB**: Qdrant (Persistent Container)
* **Frontend UI**: OpenWebUI (Persistent Container)
* **Automations**: n8n Workflow Server (Persistent Container)
* **RAG Framework**: LlamaIndex Core (0.10.x)
* **API Service**: FastAPI + Uvicorn
* **Console UI**: Rich Terminal UI

---

## ━━━━━━━━━━━━━━━━━━
## 📁 Codebase Layout
## ━━━━━━━━━━━━━━━━━━

```
offline-ai-stack/
│
├── pyproject.toml              # Modern UV dependencies & CLI entrypoint mapper
├── README.md                   # System operations guide and manual
├── .env.example                # Sample environment config settings
├── setup.py                    # Legacy installation fallback
│
├── app/                        # Main Application Code
│   ├── main.py                 # Unified CLI Command Router & FastAPI Launcher
│   ├── config/                 # Pydantic Settings & storage directory managers
│   ├── core/                   # Hardware validators, GPU parsers & Rich loggers
│   ├── docker/                 # Container lifecycle orchestrators (Docker SDK)
│   ├── ollama/                 # Local Ollama HTTP API client & downloader
│   ├── rag/                    # LlamaIndex retrieval and ingestion pipelines
│   ├── qdrant/                 # Collection generators & auto-dimension solvers
│   ├── openwebui/              # Frontend connectivity checks
│   ├── n8n/                    # n8n webhook utilities
│   ├── embeddings/             # Standalone embedding creators
│   ├── models/                 # Request/Response validation schemas
│   └── utils/                  # Mock PDF creators & size calculators
│
├── scripts/
│   └── bootstrap.ps1           # Windows automated installer & UV compiler
│
├── docs/
│   └── architecture.md         # Network structures and topology maps
│
└── tests/
    ├── test_system.py          # OS & GPU check suites
    ├── test_docker.py          # Localhost mapping and network checkers
    └── test_rag.py             # Mock PDF & LlamaIndex test pipelines
```

---

## ━━━━━━━━━━━━━━━━━━
## 🚀 Guided Quickstart
## ━━━━━━━━━━━━━━━━━━

### Step 1: Automated Environment Setup
Open a **PowerShell** prompt in the workspace directory and execute the automated setup script. This script automatically checks your environment, installs Astral's `uv` package manager if missing, builds the virtualenv, maps editable paths, and configures default settings:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\scripts\bootstrap.ps1
```

### Step 2: Verify Host Requirements
Execute a resource analysis check to inspect RAM counts, disk boundaries, and confirm that your NVIDIA GPU card and Docker daemon are successfully recognized:

```powershell
.venv\Scripts\offline-ai system-check
```

### Step 3: Spin Up Stack Containers & Models
Launch the orchestration engine. This downloads and initializes the Docker containers (Qdrant, OpenWebUI, n8n), forms the custom network bridge, and programmatically pulls the correct private AI models inside Ollama:

```powershell
.venv\Scripts\offline-ai start
```

### Step 4: Access Local Interfaces
Once started successfully, visit the running dashboard interfaces:
* 🎛️ **OpenWebUI Chat Portal**: [http://localhost:3000](http://localhost:3000) (No login required by default)
* ⚙️ **n8n Automation Console**: [http://localhost:5678](http://localhost:5678)
* 🗄️ **Qdrant Vector Database Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## ━━━━━━━━━━━━━━━━━━
## 💻 Command Line Interface (CLI) Usage
## ━━━━━━━━━━━━━━━━━━

The stack provides an interactive Rich CLI to operate your offline pipeline directly from your shell:

### Check Environment Health
```powershell
.venv\Scripts\offline-ai status
```

### Ingest a Technical PDF Document
```powershell
.venv\Scripts\offline-ai ingest-file "C:\Users\root\Desktop\technical_specs.pdf"
```

### Ingest an Entire Folder Structure
```powershell
.venv\Scripts\offline-ai ingest-folder "C:\Users\root\Desktop\offline-ai-stack\data\ingest"
```

### Private RAG Inquiries (Inference & Document Context)
```powershell
.venv\Scripts\offline-ai query "What is the recommended RAM for deploying the vector store?"
```

### Query in German (German-Language System Prompts)
```powershell
.venv\Scripts\offline-ai query "Wie hoch sind die Mindestanforderungen für RAM?" --de
```

### Stop Running Containers
```powershell
.venv\Scripts\offline-ai stop
```

---

## ━━━━━━━━━━━━━━━━━━
## 🌐 REST API Endpoints
## ━━━━━━━━━━━━━━━━━━

Launch the high-performance FastAPI server to link third-party systems (like your n8n workflow server or a custom client application):

```powershell
.venv\Scripts\offline-ai serve
```

### API endpoints list:
* **`GET /status`**: Detailed health telemetry of CPU cores, GPU properties, Docker, and Qdrant points.
* **`POST /ingest/file`**: Send a local path string payload to index a single document:
  ```json
  { "file_path": "C:\\Users\\root\\Desktop\\guide.pdf" }
  ```
* **`POST /ingest/folder`**: Ingest an entire local directory:
  ```json
  { "folder_path": "C:\\Users\\root\\Desktop\\docs" }
  ```
* **`POST /query`**: Formulate private LLM questions:
  ```json
  {
    "prompt": "What are the Qdrant port configuration limits?",
    "system_prompt": "Answer in bullet points."
  }
  ```
* **`POST /search`**: Fetch raw vector text splits, scores, and parent bibliography metadata directly without invoking the LLM.

---

## ━━━━━━━━━━━━━━━━━━
## 🩺 Troubleshooting
## ━━━━━━━━━━━━━━━━━━

1. **"Ollama not running" Warning**:
   * If the client indicates Ollama is offline, assure Ollama is started on your taskbar or execute `ollama serve` in a background terminal.
2. **Docker Connection Failure**:
   * Make sure Docker Desktop is started. On Windows, verify that "Expose daemon on tcp://localhost:2375 without TLS" is toggled on if you are using specialized network bridges.
3. **GPU Acceleration Not Used**:
   * Run `nvidia-smi` inside your standard terminal. If it fails, install the latest NVIDIA Game Ready / Studio drivers from geforce.com to enable CUDA operations.
4. **Editable virtualenv issues**:
   * If files fail to import, run `uv pip install -e .` again to refresh package maps.

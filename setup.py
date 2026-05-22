from setuptools import setup, find_packages

setup(
    name="offline-ai-stack",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.28.0",
        "pydantic>=2.6.0",
        "pydantic-settings>=2.2.0",
        "docker>=7.0.0",
        "qdrant-client>=1.8.0",
        "llama-index-core>=0.10.0",
        "llama-index-vector-stores-qdrant>=0.1.0",
        "llama-index-embeddings-ollama>=0.1.0",
        "llama-index-llms-ollama>=0.1.0",
        "rich>=13.7.0",
        "pyyaml>=6.0.1",
        "httpx>=0.27.0",
        "psutil>=5.9.8",
        "pypdf>=4.1.0",
    ],
    entry_points={
        "console_scripts": [
            "offline-ai=app.main:main",
        ],
    },
)

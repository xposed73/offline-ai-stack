FROM ghcr.io/remsky/kokoro-fastapi-cpu:v0.3.0

USER root

# Install required system dependencies (espeak-ng is needed for text normalization)
RUN apt-get update && apt-get install -y git espeak-ng && rm -rf /var/lib/apt/lists/*

# Uninstall standard English Kokoro engine
RUN pip uninstall -y kokoro

# Clone and install the German fork of Kokoro
WORKDIR /app/kokoro_german
RUN git clone https://github.com/Thomcle/kokoro_german.git .
RUN pip install -e .

# Pre-download the German HuggingFace models to make the image fully offline capable
COPY download_weights.py /app/download_weights.py
RUN python /app/download_weights.py

# Switch back to the FastAPI working directory
WORKDIR /app

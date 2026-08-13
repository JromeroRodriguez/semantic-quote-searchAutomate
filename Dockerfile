# ============================================================
# Semantic Quote Search Engine — Dockerfile
# ============================================================
# Build:  docker build -t quote-search .
# Run:    docker run -p 8001:8000 --env-file .env quote-search
#
# IMPORTANT: Run this BEFORE building the image:
#   python scripts/build_index.py
# ============================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies for FAISS and torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---- Python dependencies (cached layer) ----
# Install CPU-only PyTorch first (the default wheel bundles ~3.5GB of
# CUDA/nvidia libraries that this CPU-only app never uses).
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Application code ----
COPY backend/ backend/
COPY scripts/ scripts/
COPY frontend/ frontend/
COPY .env.example .

# ---- Pre-built data (generate locally BEFORE docker build) ----
COPY data/quotes.json data/quotes.json
COPY data/quotes.index data/quotes.index
COPY data/metadata.json data/metadata.json

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

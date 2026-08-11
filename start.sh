#!/bin/bash
# ============================================================
# Semantic Quote Search Engine — Quick Start
# ============================================================
# Prerequisites: Docker must be running and user must be in docker group
#
# First time setup (if not in docker group):
#   sudo usermod -aG docker $USER
#   # Then log out and back in
#
# Build and run:
#   docker compose up --build
#
# Access:
#   http://localhost:8000
#
# Re-scrape quotes (optional, runs outside Docker):
#   .venv/bin/python scripts/scrape_quotes.py
#   .venv/bin/python scripts/build_index.py
# ============================================================

set -e

echo "Building Docker image..."
docker compose build

echo "Starting application..."
docker compose up

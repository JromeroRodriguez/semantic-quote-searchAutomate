"""FAISS vector retrieval service."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import faiss
import numpy as np

logger = logging.getLogger(__name__)


class FAISSService:
    """Loads the persisted FAISS index and performs candidate retrieval."""

    def __init__(self, index_path: Path, metadata_path: Path) -> None:
        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. "
                "Run 'python scripts/build_index.py' first."
            )
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found at {metadata_path}.")

        self._index = faiss.read_index(str(index_path))
        with metadata_path.open("r", encoding="utf-8") as fh:
            self._metadata: list[dict[str, Any]] = json.load(fh)

        if self._index.ntotal != len(self._metadata):
            raise ValueError(
                "Index/metadata mismatch: "
                f"index has {self._index.ntotal} vectors, "
                f"metadata has {len(self._metadata)} records."
            )
        logger.info(
            "loaded FAISS index (%s vectors, dim=%s)",
            self._index.ntotal,
            self._index.d,
        )

    @property
    def size(self) -> int:
        return self._index.ntotal

    def search(self, query_vector: np.ndarray, top_k: int) -> list[dict[str, Any]]:
        """Return the top-k candidates with quote_id and cosine distance."""
        top_k = min(top_k, self._index.ntotal)
        if top_k <= 0:
            return []

        vector = np.asarray([query_vector], dtype="float32")
        distances, indices = self._index.search(vector, top_k)
        return [
            {
                "quote_id": self._metadata[idx]["quote_id"],
                "distance": float(distances[0][pos]),
            }
            for pos, idx in enumerate(indices[0])
            if idx != -1
        ]

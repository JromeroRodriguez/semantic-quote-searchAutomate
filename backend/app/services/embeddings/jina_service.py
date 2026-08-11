"""Embedding service using sentence-transformers models."""

from __future__ import annotations

import logging

import numpy as np
import torch

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates embeddings for queries and passages using any sentence-transformers model."""

    def __init__(
        self,
        model_name: str,
        device: str | None = None,
        dtype: str = "float32",
    ) -> None:
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        model_kwargs: dict = {}
        if dtype == "bfloat16":
            model_kwargs["torch_dtype"] = torch.bfloat16
        elif dtype == "float16":
            model_kwargs["torch_dtype"] = torch.float16

        from sentence_transformers import SentenceTransformer

        logger.info("loading embedding model %s on %s", model_name, self._device)
        self._model = SentenceTransformer(
            model_name,
            device=self._device,
            model_kwargs=model_kwargs,
        )
        self._model.eval()
        self._dims = self._model.get_sentence_embedding_dimension()
        logger.info("embedding model ready (dim=%s)", self._dims)

    @property
    def dims(self) -> int:
        return self._dims

    def embed_passages(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        return self._model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

    def embed_query(self, text: str) -> np.ndarray:
        return self._model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

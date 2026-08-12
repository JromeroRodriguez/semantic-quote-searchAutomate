"""Service orchestrating the backed debate speaker feature using Ollama LLM with deterministic template fallback."""

from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any

from backend.app.core.config import get_settings
from backend.app.services.search.semantic_search_service import SemanticSearchService

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "I do not have sources in my database to debate this question."

PARAGRAPH_1_TEMPLATES = [
    (
        "Faced with the dilemma raised, documentary sources offer us an essential first line of analysis. "
        "In this regard, {author} forcefully maintains: \"{quote}\", establishing a fundamental starting point "
        "for understanding the nature of this discussion."
    ),
    (
        "Addressing this question requires looking beyond appearances and turning to the wisdom accumulated in the archive. "
        "As {author} states: \"{quote}\", this intellectual testimony illuminates the initial contours "
        "of the problem with notable precision."
    ),
    (
        "The question asked opens a deep debate upon which our database provides enlightening perspectives. "
        "In the words of {author}: \"{quote}\", a key dimension is revealed to us to decipher the heart of this conundrum."
    ),
]

PARAGRAPH_2_TEMPLATES = [
    (
        "However, the complexity of the debate expands when we incorporate other documented voices. "
        "In this sense, {author} provides a crucial perspective by stating: \"{quote}\", "
        "revealing that the resolution of this question demands balancing multiple nuances and arguments."
    ),
    (
        "On the other hand, the argumentative tension is enriched by considering a complementary view. "
        "As {author} reflects: \"{quote}\", consolidating the thesis that any rigorous reflection "
        "is supported by contrasted and diverse evidence."
    ),
    (
        "To close this dialectical analysis, it is essential to attend to the repercussions of another major contribution. "
        "As {author} reminds us: \"{quote}\", the richness of this debate lies precisely in the balanced confrontation "
        "of documented ideas."
    ),
]

SINGLE_QUOTE_TEMPLATES = [
    (
        "Along the same line of analysis, the previous contribution stands out, consolidating the central argument "
        "of the present debate and demonstrating the relevance and solidity of these reflections in addressing the complexity of the subject."
    ),
    (
        "Although we have a single direct source in this record, its argumentative weight is sufficient "
        "to support the exposed stance, inviting continuous meditation on the background of the matter."
    ),
]


class DebateService:
    """Orchestrates semantic search and dynamic essay synthesis using Ollama LLM

    with deterministic template fallback.
    """

    def __init__(self, search_service: SemanticSearchService) -> None:
        self._search_service = search_service

    def debate(self, query: str) -> dict[str, Any]:
        """Run semantic search for the query and synthesize a backed debate essay.

        Returns a dictionary with:
        - success: bool
        - essay: str (2 paragraphs or fallback message)
        - sources: list of dicts with id, quote, author
        """
        try:
            raw_results = self._search_service.search(query)
        except Exception as exc:
            logger.error("Debate search failed: %s", exc)
            return {
                "success": False,
                "essay": FALLBACK_MESSAGE,
                "sources": [],
            }

        if not raw_results:
            return {
                "success": False,
                "essay": FALLBACK_MESSAGE,
                "sources": [],
            }

        sources = [
            {
                "id": r["quote_id"],
                "quote": r["quote"],
                "author": r["author"],
            }
            for r in raw_results
        ]

        # 1. Try generating dynamic essay via local Ollama LLM
        essay = self._try_generate_ollama(query, sources)
        if essay:
            return {
                "success": True,
                "essay": essay,
                "sources": sources,
            }

        # 2. Fallback to deterministic templates if Ollama is unavailable
        essay = self._generate_template_essay(query, sources)
        return {
            "success": True,
            "essay": essay,
            "sources": sources,
        }

    def _try_generate_ollama(self, query: str, sources: list[dict[str, Any]]) -> str | None:
        settings = get_settings()
        if not settings.ollama_url:
            return None

        context = "\n".join([f'- "{s["quote"]}" by {s["author"]}' for s in sources[:3]])
        prompt = (
            f"You are a philosophical debate speaker. Write a concise, professional 2-paragraph essay addressing the question: '{query}'. "
            f"You must strictly ground your argument in and explicitly quote these database sources:\n{context}\n\n"
            f"Rules:\n1. Write exactly 2 paragraphs.\n2. Incorporate the provided quotes naturally.\n3. Do not invent external quotes or facts.\n\nEssay:"
        )

        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 250,
            },
        }

        try:
            req = urllib.request.Request(
                settings.ollama_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data.get("response", "").strip()
                if text:
                    logger.info("Generated essay via Ollama (%s)", settings.ollama_model)
                    return text
        except Exception as exc:
            logger.warning("Ollama unavailable or failed (%s). Falling back to templates.", exc)

        return None

    def _generate_template_essay(self, query: str, sources: list[dict[str, Any]]) -> str:
        q_hash = abs(hash(query))
        t1_idx = q_hash % len(PARAGRAPH_1_TEMPLATES)
        t2_idx = (q_hash // 7) % len(PARAGRAPH_2_TEMPLATES)

        quote_1 = sources[0]["quote"]
        author_1 = sources[0]["author"]

        p1 = PARAGRAPH_1_TEMPLATES[t1_idx].format(author=author_1, quote=quote_1)

        if len(sources) > 1:
            quote_2 = sources[1]["quote"]
            author_2 = sources[1]["author"]
            p2 = PARAGRAPH_2_TEMPLATES[t2_idx].format(author=author_2, quote=quote_2)
        else:
            s_idx = q_hash % len(SINGLE_QUOTE_TEMPLATES)
            p2 = SINGLE_QUOTE_TEMPLATES[s_idx]

        return f"{p1}\n\n{p2}"

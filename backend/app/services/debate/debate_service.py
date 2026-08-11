"""Service orchestrating the backed debate speaker feature with diverse templates."""

from __future__ import annotations

import logging
from typing import Any

from backend.app.services.search.semantic_search_service import SemanticSearchService

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "No dispongo de fuentes en mi base de datos para debatir sobre esta cuestión."

PARAGRAPH_1_TEMPLATES = [
    (
        "Frente al dilema planteado, las fuentes documentales nos ofrecen una primera línea de análisis esencial. "
        "Al respecto, {author} sostiene contundentemente: \"{quote}\", estableciendo un punto de partida fundamental "
        "para comprender la naturaleza de esta discusión."
    ),
    (
        "Abordar esta cuestión exige mirar más allá de las apariencias y acudir a la sabiduría acumulada en el archivo. "
        "Como manifiesta {author}: \"{quote}\", este testimonio intelectual ilumina los contornos iniciales "
        "del problema con notable precisión."
    ),
    (
        "La pregunta formulada abre un debate profundo sobre el cual nuestra base de datos aporta perspectivas esclarecedoras. "
        "En palabras de {author}: \"{quote}\", se nos revela una dimensión clave para descifrar el fondo de esta disyuntiva."
    ),
]

PARAGRAPH_2_TEMPLATES = [
    (
        "Sin embargo, la complejidad del debate se amplía cuando incorporamos otras voces documentadas. "
        "En este sentido, {author} aporta una perspectiva crucial al afirmar: \"{quote}\", "
        "revelando que la resolución de este interrogante demanda equilibrar múltiples matices y argumentos."
    ),
    (
        "Por otro lado, la tensión argumentativa se enriquece al considerar una visión complementaria. "
        "Como reflexiona {author}: \"{quote}\", consolidando la tesis de que toda reflexión rigurosa "
        "se sustenta en evidencias contrastadas y diversas."
    ),
    (
        "Para cerrar este análisis dialéctico, resulta indispensable atender a las repercusiones de otra gran aportación. "
        "Como nos recuerda {author}: \"{quote}\", la riqueza de este debate reside precisamente en la confrontación "
        "equilibrada de ideas documentadas."
    ),
]

SINGLE_QUOTE_TEMPLATES = [
    (
        "En la misma línea de análisis, se destaca la aportación anterior que consolida el argumento central "
        "del presente debate, mostrando la vigencia y solidez de estas reflexiones para abordar la complejidad del tema."
    ),
    (
        "Aunque disponemos de una única fuente directa en este registro, su peso argumental resulta suficiente "
        "para respaldar la postura expuesta, invitando a una meditación continua sobre el trasfondo del asunto."
    ),
]


class DebateService:
    """Orchestrates semantic search and diverse deterministic 2-paragraph essay synthesis

    grounded strictly in retrieved citations.
    """

    def __init__(self, search_service: SemanticSearchService) -> None:
        self._search_service = search_service

    def debate(self, query: str) -> dict[str, Any]:
        """Run semantic search for the query and synthesize a backed debate essay.

        Returns a dictionary with:
        - success: bool
        - essay: str (2 paragraphs or fallback message)
        - sources: list of dicts with quote_id, quote, author
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

        # Use query hash to deterministically select diverse templates to prevent redundancy
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

        essay = f"{p1}\n\n{p2}"

        return {
            "success": True,
            "essay": essay,
            "sources": sources,
        }

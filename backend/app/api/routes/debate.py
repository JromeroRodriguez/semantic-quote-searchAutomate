"""API route handlers for the debate feature."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from backend.app.schemas.debate import DebateRequest, DebateResponse
from backend.app.schemas.search import QuoteResult

router = APIRouter()


@router.post(
    "/debate",
    response_model=DebateResponse,
    summary="Generate a backed debate essay based on retrieved quotes",
)
def debate_endpoint(request: Request, body: DebateRequest) -> DebateResponse:
    """Run the backed debate speaker pipeline for a philosophical question."""
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    settings = request.app.state.settings
    if len(query) > settings.max_query_length:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long (max {settings.max_query_length} characters)",
        )

    debate_service = request.app.state.debate_service
    try:
        result = debate_service.debate(query)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=500,
            detail="Debate generation failed. Please try again.",
        ) from exc

    return DebateResponse(
        success=result["success"],
        essay=result["essay"],
        sources=[
            QuoteResult(id=s["id"], quote=s["quote"], author=s["author"])
            for s in result["sources"]
        ],
    )

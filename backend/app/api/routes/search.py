"""API route handlers."""

from fastapi import APIRouter, HTTPException, Request

from backend.app.schemas.search import QuoteResult, SearchRequest, SearchResponse

router = APIRouter()


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Find the 3 quotes most semantically relevant to a query",
)
def search_quotes(request: Request, body: SearchRequest) -> SearchResponse:
    """Run the semantic search pipeline for a free-text query."""
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    settings = request.app.state.settings
    if len(query) > settings.max_query_length:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long (max {settings.max_query_length} characters)",
        )

    service = request.app.state.search_service
    try:
        results = service.search(query)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=500,
            detail="Search failed. Please try again.",
        ) from exc

    return SearchResponse(
        results=[QuoteResult(id=r["quote_id"], quote=r["quote"], author=r["author"]) for r in results]
    )

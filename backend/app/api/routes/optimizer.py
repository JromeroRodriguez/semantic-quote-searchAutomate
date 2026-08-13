"""API route handler for the budget optimizer feature."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from backend.app.schemas.optimizer import OptimizerRequest, OptimizerResponse
from backend.app.services.optimizer.orchestrator import run_optimizer

router = APIRouter()


@router.post(
    "/optimizer/run",
    response_model=OptimizerResponse,
    summary="Run the budget optimizer on the quote dataset",
)
def run_optimizer_endpoint(request: Request, body: OptimizerRequest) -> OptimizerResponse:
    """Tokenize quotes, pack into optimal batches, return usage receipt."""
    settings = request.app.state.settings

    try:
        result = run_optimizer(
            quotes_path=settings.quotes_path,
            max_tokens=body.max_tokens,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=500,
            detail="Optimizer failed. Please try again.",
        ) from exc

    return OptimizerResponse(**result)

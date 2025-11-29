"""API routes for company context management."""

from typing import List, Any
from fastapi import APIRouter, HTTPException

from ..models import (
    CompanyContextCreate,
    CompanyContextUpdate,
    CompanyContextResponse,
)
from ..services.context_service import ContextService

router = APIRouter(prefix="/api/contexts", tags=["contexts"])


def get_db():
    """Dummy dependency for compatibility."""
    return None


@router.post("", response_model=CompanyContextResponse, status_code=201)
def create_context(
    context_data: CompanyContextCreate,
    db: Any = None
) -> CompanyContextResponse:
    """Create new company context."""
    context = ContextService.create_context(
        db=db,
        name=context_data.name,
        context_text=context_data.context_text,
        description=context_data.description
    )
    return CompanyContextResponse(
        id=context["id"],
        name=context["name"],
        context_text=context["context_text"],
        description=context["description"],
        created_at=context["created_at"].isoformat() if context["created_at"] else "",
        updated_at=context["updated_at"].isoformat() if context["updated_at"] else ""
    )


@router.get("", response_model=List[CompanyContextResponse])
def list_contexts(
    skip: int = 0,
    limit: int = 100,
    db: Any = None
) -> List[CompanyContextResponse]:
    """Get all company contexts."""
    contexts = ContextService.get_all_contexts(db, skip=skip, limit=limit)
    return [
        CompanyContextResponse(
            id=ctx["id"],
            name=ctx["name"],
            context_text=ctx["context_text"],
            description=ctx["description"],
            created_at=ctx["created_at"].isoformat() if ctx["created_at"] else "",
            updated_at=ctx["updated_at"].isoformat() if ctx["updated_at"] else ""
        )
        for ctx in contexts
    ]


@router.get("/{context_id}", response_model=CompanyContextResponse)
def get_context(
    context_id: int,
    db: Any = None
) -> CompanyContextResponse:
    """Get company context by ID."""
    context = ContextService.get_context(db, context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    
    return CompanyContextResponse(
        id=context["id"],
        name=context["name"],
        context_text=context["context_text"],
        description=context["description"],
        created_at=context["created_at"].isoformat() if context["created_at"] else "",
        updated_at=context["updated_at"].isoformat() if context["updated_at"] else ""
    )


@router.put("/{context_id}", response_model=CompanyContextResponse)
def update_context(
    context_id: int,
    context_data: CompanyContextUpdate,
    db: Any = None
) -> CompanyContextResponse:
    """Update company context."""
    context = ContextService.update_context(
        db=db,
        context_id=context_id,
        name=context_data.name,
        context_text=context_data.context_text,
        description=context_data.description
    )
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    
    return CompanyContextResponse(
        id=context["id"],
        name=context["name"],
        context_text=context["context_text"],
        description=context["description"],
        created_at=context["created_at"].isoformat() if context["created_at"] else "",
        updated_at=context["updated_at"].isoformat() if context["updated_at"] else ""
    )


@router.delete("/{context_id}", status_code=204)
def delete_context(
    context_id: int,
    db: Any = None
):
    """Delete company context."""
    success = ContextService.delete_context(db, context_id)
    if not success:
        raise HTTPException(status_code=404, detail="Context not found")


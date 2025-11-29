"""API routes for recipient name extraction."""

from fastapi import APIRouter
from pydantic import BaseModel

from ..services.recipient_extractor import extract_recipient_name, format_recipient_name, has_recipient_name

router = APIRouter(prefix="/api/recipient", tags=["recipient"])


class RecipientCheckRequest(BaseModel):
    source_subject: str
    source_body: str


class RecipientCheckResponse(BaseModel):
    has_name: bool
    recipient_name: str | None


@router.post("/check", response_model=RecipientCheckResponse)
def check_recipient_name(request: RecipientCheckRequest) -> RecipientCheckResponse:
    """Check if recipient name can be extracted from incoming email."""
    name = format_recipient_name(request.source_subject, request.source_body)
    return RecipientCheckResponse(
        has_name=name is not None,
        recipient_name=name
    )



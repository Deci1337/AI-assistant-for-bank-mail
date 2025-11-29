"""API routes for email thread management."""

from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.thread_service import ThreadService
from ..storage import storage

router = APIRouter(prefix="/api/threads", tags=["threads"])


def get_db():
    """Dummy dependency for compatibility."""
    return None


class ThreadCreate(BaseModel):
    """Request model for creating thread."""
    subject: str = Field(..., description="Тема переписки")
    company_context_id: Optional[int] = Field(None, description="ID корпоративного контекста")
    extra_directives: Optional[List[str]] = Field(None, description="Дополнительные указания для переписки")
    custom_prompt: Optional[str] = Field(None, description="Дополнительное описание задачи")


class ThreadUpdateDirectives(BaseModel):
    """Request model for updating thread directives."""
    extra_directives: Optional[List[str]] = Field(None, description="Дополнительные указания для переписки")
    custom_prompt: Optional[str] = Field(None, description="Дополнительное описание задачи")


@router.post("", response_model=dict, status_code=201)
def create_thread(
    thread_data: ThreadCreate,
    db: Any = None
) -> dict:
    """Create new email thread."""
    thread = ThreadService.create_thread(
        db=db,
        subject=thread_data.subject,
        company_context_id=thread_data.company_context_id,
        extra_directives=thread_data.extra_directives,
        custom_prompt=thread_data.custom_prompt
    )
    return {"id": thread["id"], "subject": thread["subject"], "created_at": thread["created_at"].isoformat()}


@router.get("/{thread_id}", response_model=dict)
def get_thread(
    thread_id: int,
    db: Any = None
) -> dict:
    """Get thread with all messages."""
    thread = ThreadService.get_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    messages = ThreadService.get_thread_history(db, thread_id)
    extra_directives, custom_prompt = ThreadService.get_thread_directives(thread)
    
    return {
        "id": thread["id"],
        "subject": thread["subject"],
        "company_context_id": thread.get("company_context_id"),
        "extra_directives": extra_directives,
        "custom_prompt": custom_prompt,
        "created_at": thread["created_at"].isoformat() if thread["created_at"] else None,
        "updated_at": thread["updated_at"].isoformat() if thread["updated_at"] else None,
        "messages": [
            {
                "id": msg["id"],
                "message_type": msg["message_type"],
                "subject": msg["subject"],
                "body": msg["body"],
                "sender_name": msg.get("sender_name"),
                "sender_position": msg.get("sender_position"),
                "created_at": msg["created_at"].isoformat() if msg["created_at"] else None,
            }
            for msg in messages
        ]
    }


@router.put("/{thread_id}/directives", response_model=dict)
def update_thread_directives(
    thread_id: int,
    directives_data: ThreadUpdateDirectives,
    db: Any = None
) -> dict:
    """Update thread directives."""
    print(f"[DEBUG] PUT /api/threads/{thread_id}/directives - extra_directives={directives_data.extra_directives}, custom_prompt={directives_data.custom_prompt}")
    thread = ThreadService.update_thread_directives(
        db=db,
        thread_id=thread_id,
        extra_directives=directives_data.extra_directives,
        custom_prompt=directives_data.custom_prompt
    )
    if not thread:
        print(f"[ERROR] Thread {thread_id} not found")
        raise HTTPException(status_code=404, detail="Thread not found")
    
    extra_directives, custom_prompt = ThreadService.get_thread_directives(thread)
    print(f"[DEBUG] Successfully updated thread {thread_id} - extra_directives={extra_directives}, custom_prompt={custom_prompt}")
    return {
        "id": thread["id"],
        "extra_directives": extra_directives,
        "custom_prompt": custom_prompt,
        "updated_at": thread["updated_at"].isoformat() if thread["updated_at"] else None,
    }


@router.get("", response_model=List[dict])
def list_threads(
    skip: int = 0,
    limit: int = 100,
    db: Any = None
) -> List[dict]:
    """Get all threads."""
    threads = storage.get_all_threads(skip, limit)
    return [
        {
            "id": thread["id"],
            "subject": thread["subject"],
            "company_context_id": thread.get("company_context_id"),
            "created_at": thread["created_at"].isoformat() if thread["created_at"] else None,
            "updated_at": thread["updated_at"].isoformat() if thread["updated_at"] else None,
            "message_count": len(storage.get_thread_messages(thread["id"])),
        }
        for thread in threads
    ]


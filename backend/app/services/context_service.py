"""Service for managing company context in memory."""

from typing import List, Optional, Any
from ..storage import storage


class ContextService:
    """Service for CRUD operations with company context."""
    
    @staticmethod
    def get_context(db: Any, context_id: int) -> Optional[dict]:
        """Get context by ID."""
        return storage.get_context(context_id)
    
    @staticmethod
    def get_all_contexts(db: Any, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all contexts with pagination."""
        return storage.get_all_contexts(skip, limit)
    
    @staticmethod
    def create_context(
        db: Any,
        name: str,
        context_text: str,
        description: Optional[str] = None
    ) -> dict:
        """Create new context."""
        return storage.create_context(name, context_text, description)
    
    @staticmethod
    def update_context(
        db: Any,
        context_id: int,
        name: Optional[str] = None,
        context_text: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[dict]:
        """Update existing context."""
        return storage.update_context(context_id, name, context_text, description)
    
    @staticmethod
    def delete_context(db: Any, context_id: int) -> bool:
        """Delete context by ID."""
        return storage.delete_context(context_id)
    
    @staticmethod
    def get_context_text(db: Any, context_id: int) -> Optional[str]:
        """Get context text by ID. Returns None if not found."""
        context = ContextService.get_context(db, context_id)
        return context["context_text"] if context else None


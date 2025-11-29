"""Service for managing email conversation threads."""

from typing import List, Optional, Any
from ..storage import storage


class ThreadService:
    """Service for CRUD operations with email threads."""
    
    @staticmethod
    def create_thread(
        db: Any,
        subject: str,
        company_context_id: Optional[int] = None,
        extra_directives: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None
    ) -> dict:
        """Create new email thread."""
        return storage.create_thread(subject, company_context_id, extra_directives, custom_prompt)
    
    @staticmethod
    def update_thread_directives(
        db: Any,
        thread_id: int,
        extra_directives: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None
    ) -> Optional[dict]:
        """Update thread directives."""
        print(f"[DEBUG] update_thread_directives called with thread_id={thread_id}, extra_directives={extra_directives}, custom_prompt={custom_prompt}")
        thread = storage.update_thread_directives(thread_id, extra_directives, custom_prompt)
        if not thread:
            print(f"[ERROR] Thread {thread_id} not found")
        else:
            print(f"[DEBUG] Thread updated: {thread}")
        return thread
    
    @staticmethod
    def get_thread_directives(thread: dict) -> tuple[Optional[List[str]], Optional[str]]:
        """Get thread directives."""
        return thread.get("extra_directives"), thread.get("custom_prompt")
    
    @staticmethod
    def get_thread(db: Any, thread_id: int) -> Optional[dict]:
        """Get thread by ID with messages."""
        return storage.get_thread(thread_id)
    
    @staticmethod
    def add_message(
        db: Any,
        thread_id: int,
        message_type: str,
        subject: str,
        body: str,
        sender_name: Optional[str] = None,
        sender_position: Optional[str] = None,
        generation_time_seconds: Optional[float] = None
    ) -> dict:
        """Add message to thread."""
        return storage.add_message(
            thread_id, message_type, subject, body, 
            sender_name, sender_position, generation_time_seconds
        )
    
    @staticmethod
    def get_thread_history(db: Any, thread_id: int) -> List[dict]:
        """Get all messages in thread ordered by creation time."""
        return storage.get_thread_messages(thread_id)
    
    @staticmethod
    def format_thread_history(messages: List[dict]) -> str:
        """Format thread history as text for context."""
        if not messages:
            return ""
        
        history_lines = ["История переписки:"]
        for msg in messages:
            msg_type = "Входящее письмо" if msg["message_type"] == "incoming" else "Исходящее письмо"
            sender_info = ""
            if msg.get("sender_name"):
                sender_info = f" от {msg['sender_name']}"
                if msg.get("sender_position"):
                    sender_info += f" ({msg['sender_position']})"
            
            history_lines.append(f"\n{msg_type}{sender_info}:")
            history_lines.append(f"Тема: {msg['subject']}")
            history_lines.append(f"Текст: {msg['body']}")
            history_lines.append("---")
        
        return "\n".join(history_lines)


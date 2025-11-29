"""In-memory storage for application data with mock analytics data."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class InMemoryStorage:
    """In-memory storage for all application data."""
    
    def __init__(self):
        self.contexts: Dict[int, dict] = {}
        self.threads: Dict[int, dict] = {}
        self.messages: Dict[int, dict] = {}
        self._context_counter = 1
        self._thread_counter = 1
        self._message_counter = 1
        
        self._init_mock_data()
    
    def _init_mock_data(self):
        """Initialize with mock data for analytics."""
        
        # Create mock contexts
        self.create_context(
            name="ПСБ Банк",
            context_text="Промсвязьбанк - крупный российский банк, предоставляющий широкий спектр финансовых услуг.",
            description="Основной контекст банка"
        )
        self.create_context(
            name="IT Департамент",
            context_text="IT отдел банка, отвечающий за техническую поддержку и разработку.",
            description="Контекст IT департамента"
        )
        self.create_context(
            name="Служба поддержки",
            context_text="Клиентская служба поддержки банка.",
            description="Контекст поддержки клиентов"
        )
        
        # Generate mock threads and messages for the last 30 days
        now = datetime.now()
        subjects = [
            "Вопрос по кредиту",
            "Открытие счета",
            "Техническая проблема с онлайн-банком",
            "Запрос выписки",
            "Изменение тарифного плана",
            "Блокировка карты",
            "Консультация по ипотеке",
            "Вопрос по переводу",
            "Настройка мобильного приложения",
            "Подключение SMS-информирования"
        ]
        
        for day in range(30):
            date = now - timedelta(days=day)
            num_threads = random.randint(2, 6)
            
            for _ in range(num_threads):
                thread = self.create_thread(
                    subject=random.choice(subjects),
                    company_context_id=random.choice([1, 2, 3, None])
                )
                thread_id = thread["id"]
                thread["created_at"] = date - timedelta(hours=random.randint(0, 23))
                thread["updated_at"] = thread["created_at"]
                
                # Add directives randomly
                if random.random() > 0.6:
                    thread["extra_directives"] = random.choice([
                        ["Деловой стиль"],
                        ["Краткий ответ"],
                        ["Деловой стиль", "С примерами"]
                    ])
                
                if random.random() > 0.7:
                    thread["custom_prompt"] = "Срочный запрос от VIP клиента"
                
                # Add 2-5 messages to each thread
                num_messages = random.randint(2, 5)
                for msg_idx in range(num_messages):
                    msg_type = "incoming" if msg_idx % 2 == 0 else "outgoing"
                    message = self.add_message(
                        thread_id=thread_id,
                        message_type=msg_type,
                        subject=thread["subject"],
                        body=f"Сообщение {msg_idx + 1} в переписке",
                        sender_name="Иван Петров" if msg_type == "incoming" else "Оператор Банка",
                        sender_position="Клиент" if msg_type == "incoming" else "Специалист поддержки",
                        generation_time_seconds=round(random.uniform(1.5, 4.5), 2) if msg_type == "outgoing" else None
                    )
                    message["created_at"] = thread["created_at"] + timedelta(minutes=msg_idx * 15)
        
        print(f"Mock data initialized: {len(self.contexts)} contexts, {len(self.threads)} threads, {len(self.messages)} messages")
    
    # Context methods
    def create_context(self, name: str, context_text: str, description: Optional[str] = None) -> dict:
        """Create new context."""
        context_id = self._context_counter
        self._context_counter += 1
        
        context = {
            "id": context_id,
            "name": name,
            "context_text": context_text,
            "description": description,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        self.contexts[context_id] = context
        return context
    
    def get_context(self, context_id: int) -> Optional[dict]:
        """Get context by ID."""
        return self.contexts.get(context_id)
    
    def get_all_contexts(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all contexts with pagination."""
        contexts = list(self.contexts.values())
        return contexts[skip:skip + limit]
    
    def update_context(self, context_id: int, name: Optional[str] = None, 
                      context_text: Optional[str] = None, description: Optional[str] = None) -> Optional[dict]:
        """Update context."""
        context = self.contexts.get(context_id)
        if not context:
            return None
        
        if name is not None:
            context["name"] = name
        if context_text is not None:
            context["context_text"] = context_text
        if description is not None:
            context["description"] = description
        context["updated_at"] = datetime.now()
        
        return context
    
    def delete_context(self, context_id: int) -> bool:
        """Delete context."""
        if context_id in self.contexts:
            del self.contexts[context_id]
            return True
        return False
    
    # Thread methods
    def create_thread(self, subject: str, company_context_id: Optional[int] = None,
                     extra_directives: Optional[List[str]] = None, 
                     custom_prompt: Optional[str] = None) -> dict:
        """Create new thread."""
        thread_id = self._thread_counter
        self._thread_counter += 1
        
        thread = {
            "id": thread_id,
            "subject": subject,
            "company_context_id": company_context_id,
            "extra_directives": extra_directives,
            "custom_prompt": custom_prompt,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        self.threads[thread_id] = thread
        return thread
    
    def get_thread(self, thread_id: int) -> Optional[dict]:
        """Get thread by ID."""
        return self.threads.get(thread_id)
    
    def get_all_threads(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get all threads with pagination."""
        threads = sorted(self.threads.values(), key=lambda x: x["updated_at"], reverse=True)
        return threads[skip:skip + limit]
    
    def update_thread_directives(self, thread_id: int, extra_directives: Optional[List[str]] = None,
                                custom_prompt: Optional[str] = None) -> Optional[dict]:
        """Update thread directives."""
        thread = self.threads.get(thread_id)
        if not thread:
            return None
        
        if extra_directives is not None:
            thread["extra_directives"] = extra_directives if extra_directives else None
        if custom_prompt is not None:
            thread["custom_prompt"] = custom_prompt.strip() if custom_prompt and custom_prompt.strip() else None
        thread["updated_at"] = datetime.now()
        
        return thread
    
    # Message methods
    def add_message(self, thread_id: int, message_type: str, subject: str, body: str,
                   sender_name: Optional[str] = None, sender_position: Optional[str] = None,
                   generation_time_seconds: Optional[float] = None) -> dict:
        """Add message to thread."""
        message_id = self._message_counter
        self._message_counter += 1
        
        message = {
            "id": message_id,
            "thread_id": thread_id,
            "message_type": message_type,
            "subject": subject,
            "body": body,
            "sender_name": sender_name,
            "sender_position": sender_position,
            "generation_time_seconds": generation_time_seconds,
            "created_at": datetime.now()
        }
        self.messages[message_id] = message
        
        # Update thread's updated_at
        thread = self.threads.get(thread_id)
        if thread:
            thread["updated_at"] = datetime.now()
        
        return message
    
    def get_thread_messages(self, thread_id: int) -> List[dict]:
        """Get all messages for a thread."""
        messages = [msg for msg in self.messages.values() if msg["thread_id"] == thread_id]
        return sorted(messages, key=lambda x: x["created_at"])
    
    def get_messages_in_period(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """Get messages created in specific period."""
        return [
            msg for msg in self.messages.values()
            if start_date <= msg["created_at"] <= end_date
        ]
    
    def get_threads_in_period(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """Get threads created in specific period."""
        return [
            thread for thread in self.threads.values()
            if start_date <= thread["created_at"] <= end_date
        ]


# Global storage instance
storage = InMemoryStorage()


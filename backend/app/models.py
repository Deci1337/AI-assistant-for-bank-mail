"""Pydantic models shared across the API."""

from typing import Literal, Optional, List

from pydantic import BaseModel, Field


Tone = Literal["formal", "neutral", "friendly"]
Purpose = Literal["response", "proposal", "notification", "refusal"]
Length = Literal["short", "medium", "long"]
Audience = Literal["colleague", "manager", "client", "partner", "regulator"]
AddressStyle = Literal["vy", "full_name"]
Urgency = Literal["low", "normal", "high"]
EmailCategory = Literal[
    "information_request",  # Запрос информации/документов
    "complaint",  # Официальная жалоба или претензия
    "regulatory_request",  # Регуляторный запрос
    "partnership_proposal",  # Партнёрское предложение
    "approval_request",  # Запрос на согласование
    "notification",  # Уведомление или информирование
    "other"  # Прочее
]


class EmailParameters(BaseModel):
    """High-level levers that shape the generated letter."""

    tone: Tone = "formal"
    purpose: Purpose = "response"
    length: Length = "medium"
    audience: Audience = "client"
    address_style: AddressStyle = "vy"
    include_formal_greetings: bool = True
    urgency: Urgency = "normal"
    include_corporate_phrases: bool = True
    include_greeting_and_signoff: bool = True
    extra_directives: Optional[list[str]] = Field(
        default=None,
        description="Additional free-form requirements merged into the prompt.",
    )


class EmailGenerationRequest(BaseModel):
    """Request payload for /emails/generate."""

    source_subject: str = Field(
        ..., description="Subject of the inbound letter or summary of request."
    )
    source_body: str = Field(
        ..., description="Original text or structured summary of the incoming letter."
    )
    company_context: Optional[str] = Field(
        default=None,
        description="Corporate facts/boilerplate that should remain stable across replies. If company_context_id is provided, this will be ignored.",
    )
    company_context_id: Optional[int] = Field(
        default=None,
        description="ID of company context from database. If provided, company_context will be loaded from DB.",
    )
    thread_id: Optional[int] = Field(
        default=None,
        description="ID переписки (thread). Если указан, история переписки будет автоматически добавлена в контекст.",
    )
    sender_first_name: Optional[str] = Field(
        default=None, description="Имя сотрудника, который подписывает письмо."
    )
    sender_last_name: Optional[str] = Field(
        default=None, description="Фамилия сотрудника, который подписывает письмо."
    )
    sender_middle_name: Optional[str] = Field(
        default=None, description="Отчество сотрудника, который подписывает письмо."
    )
    sender_position: Optional[str] = Field(
        default=None, description="Должность отправителя для блока подписи."
    )
    sender_phone_work: Optional[str] = Field(
        default=None, description="Рабочий телефон для подписи."
    )
    sender_phone_mobile: Optional[str] = Field(
        default=None, description="Мобильный телефон для подписи."
    )
    sender_email: Optional[str] = Field(
        default=None, description="Email для подписи."
    )
    sender_address: Optional[str] = Field(
        default=None, description="Адрес для подписи."
    )
    sender_hotline: Optional[str] = Field(
        default=None, description="Горячая линия для подписи."
    )
    sender_website: Optional[str] = Field(
        default=None, description="Сайт для подписи."
    )
    custom_prompt: Optional[str] = Field(
        default=None,
        description="Optional free-form task description appended to the generated prompt.",
    )
    parameters: EmailParameters = Field(
        default_factory=EmailParameters, description="Controls tone/style of the reply."
    )


class EmailAnalysisRequest(BaseModel):
    """Запрос на анализ входящего письма"""
    source_subject: str
    source_body: str
    company_context: str = ""


class EmailParametersResponse(BaseModel):
    """Ответ с автоматически определенными параметрами"""
    parameters: EmailParameters


class ExtractedInfo(BaseModel):
    """Извлеченная ключевая информация из письма"""
    request_essence: str = Field(..., description="Суть запроса и ожидания отправителя")
    contact_info: Optional[str] = Field(None, description="Контактные данные и реквизиты")
    regulatory_references: Optional[List[str]] = Field(None, description="Ссылки на нормативные акты")
    requirements: Optional[List[str]] = Field(None, description="Требования и ожидания отправителя")
    legal_risks: Optional[List[str]] = Field(None, description="Потенциальные юридические риски и ограничения")


class DetailedEmailAnalysis(BaseModel):
    """Расширенный анализ входящего письма"""
    category: EmailCategory = Field(..., description="Категория письма")
    parameters: EmailParameters = Field(..., description="Параметры для генерации ответа")
    extracted_info: ExtractedInfo = Field(..., description="Извлеченная ключевая информация")
    department: str = Field(..., description="Определенный отдел для маршрутизации")
    estimated_sla_days: int = Field(..., description="Расчетный срок ответа в рабочих днях")
    extracted_deadline_days: Optional[int] = Field(None, description="Извлеченный дедлайн из текста письма в рабочих днях, если указан")


class EmailGenerationResponse(BaseModel):
    """Returned to the caller after the LLM produces a draft."""

    subject: str
    body: str


class CompanyContextCreate(BaseModel):
    """Request model for creating company context."""
    name: str = Field(..., description="Название контекста")
    context_text: str = Field(..., description="Текст корпоративного контекста")
    description: Optional[str] = Field(None, description="Описание контекста")


class CompanyContextUpdate(BaseModel):
    """Request model for updating company context."""
    name: Optional[str] = Field(None, description="Название контекста")
    context_text: Optional[str] = Field(None, description="Текст корпоративного контекста")
    description: Optional[str] = Field(None, description="Описание контекста")


class CompanyContextResponse(BaseModel):
    """Response model for company context."""
    id: int
    name: str
    context_text: str
    description: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


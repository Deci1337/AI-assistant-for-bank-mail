"""API routes for email generation."""

from typing import Any
from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..models import (
    EmailGenerationRequest,
    EmailGenerationResponse,
    EmailAnalysisRequest,
    EmailParametersResponse,
    DetailedEmailAnalysis,
)
from ..services.yandex_gpt_client import YandexGPTService
from ..services.email_analyzer import EmailAnalyzer
from ..services.context_service import ContextService
from ..services.thread_service import ThreadService

router = APIRouter(prefix="/api/emails", tags=["emails"])


def get_db():
    """Dummy dependency for compatibility."""
    return None


def _get_service():
    """Get AI service based on configuration."""
    return YandexGPTService()


def _get_analyzer():
    """Get email analyzer service."""
    service = _get_service()
    return EmailAnalyzer(service)


@router.post("/generate", response_model=EmailGenerationResponse)
def generate_email(
    request: EmailGenerationRequest,
    db: Any = None
) -> EmailGenerationResponse:
    """Generate a professional email based on the request parameters."""
    print(f"[DEBUG] Received request - thread_id={request.thread_id}, extra_directives={request.parameters.extra_directives if request.parameters else None}, custom_prompt={request.custom_prompt}")
    # Load context from database if context_id is provided
    if request.company_context_id:
        context_text = ContextService.get_context_text(db, request.company_context_id)
        if not context_text:
            raise HTTPException(
                status_code=404,
                detail=f"Company context with ID {request.company_context_id} not found"
            )
        # Create a new request with loaded context, preserving all fields including parameters
        original_request = request
        request = EmailGenerationRequest(
            source_subject=original_request.source_subject,
            source_body=original_request.source_body,
            company_context=context_text,
            company_context_id=original_request.company_context_id,
            thread_id=original_request.thread_id,
            sender_first_name=original_request.sender_first_name,
            sender_last_name=original_request.sender_last_name,
            sender_middle_name=original_request.sender_middle_name,
            sender_position=original_request.sender_position,
            sender_phone_work=original_request.sender_phone_work,
            sender_phone_mobile=original_request.sender_phone_mobile,
            sender_email=original_request.sender_email,
            sender_address=original_request.sender_address,
            sender_hotline=original_request.sender_hotline,
            sender_website=original_request.sender_website,
            custom_prompt=original_request.custom_prompt,
            parameters=original_request.parameters
        )
    elif not request.company_context:
        raise HTTPException(
            status_code=400,
            detail="Either company_context or company_context_id must be provided"
        )
    
    # Handle thread history and directives
    thread_history = None
    thread_id = request.thread_id
    thread_extra_directives = None
    thread_custom_prompt = None
    
    has_extra_directives = request.parameters.extra_directives is not None if request.parameters else False
    print(f"[DEBUG] Processing thread_id={thread_id}, has_extra_directives={has_extra_directives}")
    if has_extra_directives and request.parameters:
        print(f"[DEBUG] extra_directives value: {request.parameters.extra_directives}")
    
    # If thread_id is provided, load history and directives
    if thread_id:
        thread = ThreadService.get_thread(db, thread_id)
        if not thread:
            raise HTTPException(
                status_code=404,
                detail=f"Thread with ID {thread_id} not found"
            )
        messages = ThreadService.get_thread_history(db, thread_id)
        thread_history = ThreadService.format_thread_history(messages)
        
        # Load directives from thread
        thread_extra_directives, thread_custom_prompt = ThreadService.get_thread_directives(thread)
        print(f"[DEBUG] Thread {thread_id} current directives - extra_directives: {thread_extra_directives}, custom_prompt: {thread_custom_prompt}")
        
        # Update thread directives if new ones provided (save to DB)
        update_needed = False
        new_extra_directives = thread_extra_directives
        new_custom_prompt = thread_custom_prompt
        
        # Check if extra_directives were provided (not None and not empty list)
        print(f"[DEBUG] Request extra_directives: {request.parameters.extra_directives}, type: {type(request.parameters.extra_directives)}")
        if request.parameters.extra_directives is not None:
            # Always update if it's a list (even if empty, to allow clearing)
            if isinstance(request.parameters.extra_directives, list):
                new_extra_directives = request.parameters.extra_directives if request.parameters.extra_directives else None
            update_needed = True
            print(f"[DEBUG] Updating extra_directives for thread {thread_id}: {new_extra_directives}")
        
        # Check if custom_prompt was provided (not None and not empty string)
        print(f"[DEBUG] Request custom_prompt: {request.custom_prompt}")
        if request.custom_prompt is not None:
            new_custom_prompt = request.custom_prompt
            update_needed = True
            print(f"[DEBUG] Updating custom_prompt for thread {thread_id}: {new_custom_prompt}")
        
        print(f"[DEBUG] Update needed: {update_needed}")
        if update_needed:
            print(f"[DEBUG] Calling update_thread_directives with extra_directives={new_extra_directives}, custom_prompt={new_custom_prompt}")
            updated_thread = ThreadService.update_thread_directives(
                db=db,
                thread_id=thread_id,
                extra_directives=new_extra_directives,
                custom_prompt=new_custom_prompt
            )
            if updated_thread:
                # Reload directives after update
                thread_extra_directives, thread_custom_prompt = ThreadService.get_thread_directives(updated_thread)
                print(f"[DEBUG] Successfully updated thread {thread_id} directives - extra_directives: {thread_extra_directives}, custom_prompt: {thread_custom_prompt}")
            else:
                print(f"[ERROR] Failed to update thread {thread_id} directives - update_thread_directives returned None")
        
        # Use thread directives if request doesn't have them
        if request.parameters.extra_directives is None and thread_extra_directives:
            request.parameters.extra_directives = thread_extra_directives
        if request.custom_prompt is None and thread_custom_prompt:
            request.custom_prompt = thread_custom_prompt
    
    # Save incoming message to thread
    if thread_id:
        sender_name = None
        if request.sender_first_name or request.sender_last_name:
            sender_name = f"{request.sender_first_name or ''} {request.sender_last_name or ''}".strip()
        
        ThreadService.add_message(
            db=db,
            thread_id=thread_id,
            message_type="incoming",
            subject=request.source_subject,
            body=request.source_body,
            sender_name=sender_name,
            sender_position=request.sender_position
        )
    
    # Extract recipient name from incoming email
    from ..services.recipient_extractor import extract_recipient_name, format_recipient_name
    recipient_name = format_recipient_name(request.source_subject, request.source_body)
    
    # Validate address_style - if full_name is selected but recipient data is not available, reset to "vy"
    if request.parameters.address_style == "full_name" and not recipient_name:
        request.parameters.address_style = "vy"
        print(f"[DEBUG] address_style reset from 'full_name' to 'vy' - recipient name not available")
    
    # Add recipient name to request if found
    if recipient_name:
        # Store recipient name in custom_prompt or create a new field
        recipient_info = f"Имя получателя (адресата): {recipient_name}"
        if request.custom_prompt:
            request.custom_prompt = f"{recipient_info}\n{request.custom_prompt}"
        else:
            request.custom_prompt = recipient_info
        print(f"[DEBUG] Extracted recipient name: {recipient_name}")
    
    # Measure generation time
    import time
    generation_start_time = time.time()
    
    service = _get_service()
    response = service.generate_letter(request, thread_history=thread_history, recipient_name=recipient_name)
    
    generation_time_seconds = time.time() - generation_start_time
    
    # Save generated response to thread
    if thread_id:
        sender_name = None
        if request.sender_first_name or request.sender_last_name:
            sender_name = f"{request.sender_first_name or ''} {request.sender_last_name or ''}".strip()
        
        ThreadService.add_message(
            db=db,
            thread_id=thread_id,
            message_type="outgoing",
            subject=response.subject,
            body=response.body,
            sender_name=sender_name,
            sender_position=request.sender_position,
            generation_time_seconds=generation_time_seconds
        )
    
    return response


@router.post("/analyze", response_model=EmailParametersResponse)
def analyze_email(request: EmailAnalysisRequest) -> EmailParametersResponse:
    """Analyze incoming email and automatically determine optimal parameters."""
    service = _get_service()
    
    params = service.analyze_email_parameters(
        subject=request.source_subject,
        body=request.source_body,
        company_context=request.company_context,
    )
    
    return EmailParametersResponse(parameters=params)


@router.post("/analyze-detailed", response_model=DetailedEmailAnalysis)
def analyze_email_detailed(request: EmailAnalysisRequest) -> DetailedEmailAnalysis:
    """Расширенный анализ входящего письма с извлечением ключевой информации."""
    try:
        # Валидация входных данных
        if not request.source_subject or not request.source_subject.strip():
            raise ValueError("Тема письма не может быть пустой")
        if not request.source_body or not request.source_body.strip():
            raise ValueError("Текст письма не может быть пустым")
        
        analyzer = _get_analyzer()
        
        return analyzer.analyze_email_detailed(
            subject=request.source_subject.strip(),
            body=request.source_body.strip(),
            company_context=request.company_context.strip() if request.company_context else "ПСБ банк",
        )
    except ValueError as e:
        # Ошибки валидации - возвращаем понятное сообщение
        import traceback
        error_details = traceback.format_exc()
        print(f"Ошибка валидации в analyze_email_detailed: {e}")
        print(error_details)
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Ошибки Yandex GPT API - возвращаем понятное сообщение
        import traceback
        error_details = traceback.format_exc()
        print(f"Ошибка Yandex GPT в analyze_email_detailed: {e}")
        print(error_details)
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Ошибка AI сервиса: {str(e)}")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Неожиданная ошибка в analyze_email_detailed: {e}")
        print(error_details)
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

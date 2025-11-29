"""YandexGPT API client using Responses API."""

from __future__ import annotations

import json
import re

import httpx

from ..config import get_settings
from ..models import EmailGenerationRequest, EmailGenerationResponse, EmailParameters
from .prompt_builder import build_messages
from .department_detector import detect_department_by_keywords, get_department_instruction


def _collapse_whitespace(value: str) -> str:
    """Replace escaped sequences and whitespace with single spaces."""
    normalized = value.replace("\\n", " ").replace("\\r", " ")
    return re.sub(r"\s+", " ", normalized).strip()


def _build_signature(req) -> str:
    """Формирует подпись из данных отправителя."""
    signature_parts = []
    
    # "С уважением,"
    signature_parts.append("С уважением,")
    
    # Фамилия
    if req.sender_last_name:
        signature_parts.append(req.sender_last_name)
    
    # Имя и отчество
    name_parts = []
    if req.sender_first_name:
        name_parts.append(req.sender_first_name)
    if req.sender_middle_name:
        name_parts.append(req.sender_middle_name)
    if name_parts:
        signature_parts.append(" ".join(name_parts))
        signature_parts.append("")  # Две пустые строки после имени
        signature_parts.append("")
    
    # Должность (разбиваем по словам "отдела", "управления", "департамента")
    if req.sender_position:
        position = req.sender_position
        position_lines = []
        
        # Разбиваем должность так, чтобы каждое ключевое слово было в конце строки
        # Пример: "Начальник отдела медиа продвижения управления маркетинговых коммуникаций департамента маркетинга"
        # Должно стать:
        # - "Начальник отдела"
        # - "медиа продвижения управления"
        # - "маркетинговых коммуникаций департамента"
        # - "маркетинга"
        
        keywords = ["отдела", "управления", "департамента"]
        words = position.split()
        current_line = []
        
        for word in words:
            current_line.append(word)
            # Проверяем, заканчивается ли текущее слово на ключевое слово
            current_text = " ".join(current_line)
            for keyword in keywords:
                if current_text.endswith(" " + keyword) or current_text == keyword:
                    position_lines.append(current_text)
                    current_line = []
                    break
        
        # Добавляем остаток, если есть
        if current_line:
            position_lines.append(" ".join(current_line))
        
        # Если разбиение не удалось, используем исходную должность
        if not position_lines:
            position_lines = [position]
        
        for line in position_lines:
            signature_parts.append(line)
        signature_parts.append("")  # Две пустые строки после должности
        signature_parts.append("")
    
    # Контактная информация
    # Рабочий телефон
    if req.sender_phone_work:
        signature_parts.append(req.sender_phone_work)
    
    # Мобильный телефон
    if req.sender_phone_mobile:
        signature_parts.append(req.sender_phone_mobile)
    
    # Email
    if req.sender_email:
        signature_parts.append(req.sender_email)
    
    # Адрес (разбиваем на две строки: до запятой перед "г." и после)
    if req.sender_address:
        address = req.sender_address
        if "," in address and "г." in address:
            # Находим позицию "г."
            g_pos = address.find("г.")
            if g_pos >= 0:
                # Ищем последнюю запятую перед "г."
                comma_before_g = address.rfind(",", 0, g_pos)
                if comma_before_g >= 0:
                    # Часть до запятой перед "г." включительно
                    part1 = address[:comma_before_g + 1].strip()
                    # Часть после запятой перед "г."
                    part2 = address[comma_before_g + 1:].strip()
                    signature_parts.append(part1)
                    if part2:
                        signature_parts.append(part2)
                else:
                    # Если запятой перед "г." нет, используем весь адрес
                    signature_parts.append(address)
            else:
                signature_parts.append(address)
        else:
            signature_parts.append(address)
        signature_parts.append("")  # Две пустые строки после адреса
        signature_parts.append("")
    
    # Горячая линия
    if req.sender_hotline:
        signature_parts.append(req.sender_hotline)
    
    # Сайт
    if req.sender_website:
        signature_parts.append(req.sender_website)
        # После сайта пустых строк нет (конец подписи)
    
    # Добавляем маркер для логотипа
    signature_parts.append("")
    signature_parts.append("[LOGO]")
    
    return "\n".join(signature_parts).rstrip()


def _remove_duplicate_signatures(body: str) -> str:
    """Удаляет дублирующиеся подписи в конце письма."""
    lines = body.split('\n')
    if len(lines) < 2:
        return body
    
    # Ищем блоки подписи (начинаются с "С уважением," или похожих фраз)
    signature_pattern = re.compile(r'^\s*(С уважением|С уважением,|С уважением:)', re.IGNORECASE)
    
    signature_indices = []
    for i, line in enumerate(lines):
        if signature_pattern.match(line.strip()):
            signature_indices.append(i)
    
    # Если найдено более одной подписи, удаляем все кроме последней
    if len(signature_indices) > 1:
        # Находим последний блок подписи (обычно 2-4 строки)
        last_idx = signature_indices[-1]
        # Определяем конец последнего блока подписи (обычно до 4 строк после "С уважением,")
        end_idx = min(last_idx + 4, len(lines))
        
        # Удаляем все предыдущие блоки подписей
        if last_idx > 0:
            prev_idx = signature_indices[-2]
            # Если предыдущая подпись близко к последней (в пределах 10 строк), удаляем её
            if last_idx - prev_idx <= 10:
                lines = lines[:prev_idx] + lines[last_idx:]
    
    return '\n'.join(lines).strip()


def _extract_subject_and_body(raw_text: str) -> tuple[str, str]:
    subject = "Заготовка ответа"
    body = raw_text.strip()

    subject_match = re.search(r"Тема:\s*(.+)", raw_text)
    if subject_match:
        subject = _collapse_whitespace(subject_match.group(1))

    if "Тело:" in raw_text:
        body = raw_text.split("Тело:", maxsplit=1)[1].strip()
    else:
        body = raw_text.strip()

    # Убираем строку "Направить в [отдел]" если она есть
    body = re.sub(r'\n?\s*Направить в .+?\n?$', '', body, flags=re.IGNORECASE | re.MULTILINE)
    body = re.sub(r'\n?\s*направить в .+?\n?$', '', body, flags=re.MULTILINE)

    # Удаляем дублирующиеся подписи
    body = _remove_duplicate_signatures(body)

    # Сохраняем переносы строк в теле письма (особенно для подписи)
    # Убираем множественные пробелы в строках, но сохраняем пустые строки для форматирования подписи
    lines = body.split('\n')
    cleaned_lines = []
    for line in lines:
        # Если строка пустая, сохраняем её как есть
        if not line.strip():
            cleaned_lines.append('')
        else:
            # Убираем множественные пробелы, но сохраняем строку
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            cleaned_lines.append(cleaned_line)
    
    # Убираем все ведущие пустые строки полностью (письмо должно начинаться сразу с текста)
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    
    body = '\n'.join(cleaned_lines)
    return subject, body


class YandexGPTService:
    """YandexGPT API client using Responses API."""

    def __init__(self, api_key: str | None = None, folder_id: str | None = None) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.yandex_api_key
        self._folder_id = folder_id or settings.yandex_folder_id
        self._model = settings.yandex_model
        self._api_url = "https://rest-assistant.api.cloud.yandex.net/v1/responses"

    def _make_request(self, messages: list[dict[str, str]], temperature: float = 0.4, response_format: dict | None = None) -> str:
        """Make request to YandexGPT Responses API."""
        system_message = None
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg["content"])

        instructions = system_message or "Ты полезный ассистент."
        input_text = "\n\n".join(user_messages)

        model_uri = f"gpt://{self._folder_id}/{self._model}"
        
        headers = {
            "Authorization": f"Api-Key {self._api_key}",
            "x-folder-id": self._folder_id,
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model_uri,
            "instructions": instructions,
            "input": input_text,
        }
        
        # Retry логика для обработки SSL ошибок
        max_retries = 3
        retry_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                # Настройка клиента с улучшенной обработкой SSL и таймаутов
                timeout = httpx.Timeout(90.0, connect=15.0, read=60.0)
                with httpx.Client(
                    timeout=timeout,
                    verify=True,
                    follow_redirects=True,
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                ) as client:
                    response = client.post(self._api_url, headers=headers, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    
                    if result.get("status") == "failed" or result.get("error"):
                        error_msg = result.get("error", {}).get("message", "Unknown error")
                        error_code = result.get("error", {}).get("code", "")
                        if "Failed to get model" in error_msg or error_code == "model_call_error":
                            raise RuntimeError(
                                f"Модель '{self._model}' недоступна в вашем каталоге. "
                                f"Проверьте:\n"
                                f"1. Что модель активирована в консоли Яндекс.Облака\n"
                                f"2. Что у вас есть доступ к модели в каталоге {self._folder_id}\n"
                                f"3. Попробуйте другую модель, например: qwen3-235b-a22b-fp8/latest или yandexgpt/latest"
                            )
                        raise RuntimeError(f"YandexGPT API error: {error_msg}")
                    
                    output_text = result.get("output_text")
                    if output_text:
                        return output_text.strip()
                    
                    output = result.get("output")
                    if output and isinstance(output, list):
                        texts = []
                        for msg in output:
                            if isinstance(msg, dict) and "content" in msg:
                                for content_item in msg["content"]:
                                    if isinstance(content_item, dict) and "text" in content_item:
                                        texts.append(content_item["text"])
                        if texts:
                            return "\n".join(texts).strip()
                    
                    text = result.get("text")
                    if text:
                        return str(text).strip()
                    
                    raise RuntimeError(f"Empty response from YandexGPT API. Full response: {result}")
                    
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                if attempt < max_retries - 1:
                    import time
                    print(f"[YandexGPT] Попытка {attempt + 1} не удалась: {e}. Повтор через {retry_delay} сек...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Экспоненциальная задержка
                    continue
                else:
                    raise RuntimeError(f"YandexGPT API connection error после {max_retries} попыток: {e}")
            except httpx.HTTPStatusError as e:
                error_detail = ""
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text
                raise RuntimeError(f"YandexGPT API HTTP error {e.response.status_code}: {error_detail}") from e
            except Exception as e:
                # Проверяем, является ли это SSL ошибкой
                error_str = str(e).lower()
                if "ssl" in error_str or "eof" in error_str or "protocol" in error_str:
                    if attempt < max_retries - 1:
                        import time
                        print(f"[YandexGPT] SSL ошибка на попытке {attempt + 1}: {e}. Повтор через {retry_delay} сек...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise RuntimeError(
                            f"YandexGPT API SSL error после {max_retries} попыток: {e}. "
                            f"Возможные причины: проблемы с сетью, прокси или SSL сертификатами."
                        ) from e
                raise RuntimeError(f"YandexGPT API error: {e}") from e

    def generate_letter(self, payload: EmailGenerationRequest, thread_history: str = None, recipient_name: str = None) -> EmailGenerationResponse:
        """Генерирует письмо на основе запроса. Использует кэширование для ускорения."""
        import hashlib
        import json
        
        # Try to get from cache
        from .cache_service import get_cache_service
        cache = get_cache_service()
        
        # Create hash of parameters for cache key
        params_dict = payload.parameters.model_dump() if payload.parameters else {}
        params_hash = hashlib.sha256(
            json.dumps(params_dict, sort_keys=True).encode('utf-8')
        ).hexdigest()[:16]
        
        # Check cache
        if cache.is_enabled():
            cached_result = cache.get_generation(
                payload.source_subject,
                payload.source_body,
                payload.company_context or "",
                params_hash,
                thread_history,
                payload.parameters.extra_directives if payload.parameters else None,
                payload.custom_prompt
            )
            if cached_result:
                return EmailGenerationResponse(**cached_result)
        
        # Определяем отдел банка на основе содержания письма
        department = detect_department_by_keywords(
            payload.source_subject,
            payload.source_body
        )
        
        # Формируем промпт с информацией об отделе и историей переписки
        messages = build_messages(payload, department=department, thread_history=thread_history, recipient_name=recipient_name)
        raw_text = self._make_request(messages, temperature=0.4)
        subject, body = _extract_subject_and_body(raw_text)

        # Вставляем подпись внутрь основного текста письма
        if (payload.sender_last_name or payload.sender_first_name or 
            payload.sender_position or payload.sender_email or 
            payload.sender_phone_work or payload.sender_phone_mobile):
            # Удаляем существующую подпись из body, если она есть
            signature_pattern = re.compile(r'^\s*(С уважением|С уважением,|С уважением:)', re.IGNORECASE | re.MULTILINE)
            
            lines = body.split('\n')
            last_signature_idx = None
            
            # Ищем подпись с конца
            for i in range(len(lines) - 1, -1, -1):
                if signature_pattern.match(lines[i].strip()):
                    last_signature_idx = i
                    break
            
            # Удаляем старую подпись, если найдена
            if last_signature_idx is not None:
                # Удаляем подпись и все пустые строки перед ней (но оставляем хотя бы одну, если есть текст)
                body_lines = lines[:last_signature_idx]
                # Убираем пустые строки в конце перед подписью
                while body_lines and not body_lines[-1].strip():
                    body_lines.pop()
                body = '\n'.join(body_lines).rstrip()
            
            # Формируем подпись
            signature = _build_signature(payload)
            
            # Вставляем подпись внутрь основного текста письма
            # Убираем лишние пробелы и пустые строки в конце основного текста
            body = body.rstrip()
            
            # Добавляем подпись как часть основного текста письма
            if body.strip():
                # Гарантируем ровно две пустые строки перед подписью для разделения
                # Убираем все пустые строки в конце и добавляем ровно две
                body = body.rstrip() + "\n\n" + signature
            else:
                body = signature

        result = EmailGenerationResponse(subject=subject, body=body)
        
        # Cache the result
        if cache.is_enabled():
            try:
                cache.set_generation(
                    payload.source_subject,
                    payload.source_body,
                    payload.company_context or "",
                    params_hash,
                    result.model_dump(),
                    thread_history,
                    payload.parameters.extra_directives if payload.parameters else None,
                    payload.custom_prompt
                )
            except Exception as e:
                print(f"[CACHE] Error caching generation result: {e}")
        
        return result

    def analyze_email_parameters(
        self, subject: str, body: str, company_context: str
    ) -> EmailParameters:
        """
        Анализирует входящее письмо и определяет оптимальные параметры для ответа.
        """
        analysis_prompt = f"""Проанализируй входящее письмо и определи оптимальные параметры для ответа.

Входящее письмо:
Тема: {subject}
Текст: {body}
Контекст компании: {company_context}

Верни ТОЛЬКО валидный JSON со следующими параметрами:
{{
  "tone": "formal",
  "purpose": "response",
  "length": "medium",
  "audience": "colleague",
  "urgency": "normal",
  "address_style": "vy",
  "include_formal_greetings": true,
  "include_greeting_and_signoff": true,
  "include_corporate_phrases": true
}}

Возможные значения:
- tone: "formal" | "neutral" | "friendly"
- purpose: "response" | "proposal" | "notification" | "refusal"
- length: "short" | "medium" | "long"
- audience: "colleague" | "manager" | "client" | "partner" | "regulator"
  * "client" - Клиент банка (получает услуги: кредиты, вклады, счета)
  * "partner" - Бизнес-партнер (сотрудничество на равных: интеграции, совместные проекты, B2B)
- urgency: "low" | "normal" | "high"
- address_style: "vy" | "ty" | "full_name"
"""

        try:
            raw_json = self._make_request(
                [
                    {
                        "role": "system",
                        "content": "Ты эксперт по деловой переписке. Отвечай только валидным JSON.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            if isinstance(raw_json, str):
                raw_json = raw_json.strip()
            else:
                raw_json = str(raw_json).strip()
            
            params_dict = json.loads(raw_json)
            return EmailParameters(**params_dict)

        except Exception as e:
            print(f"Ошибка анализа параметров: {e}")
            return EmailParameters(
                tone="formal",
                purpose="response",
                length="medium",
                audience="colleague",
                urgency="normal",
                address_style="vy",
                include_formal_greetings=True,
                include_greeting_and_signoff=True,
                include_corporate_phrases=True,
            )


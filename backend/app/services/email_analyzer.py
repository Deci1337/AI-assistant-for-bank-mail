"""Расширенный анализ входящих писем согласно ТЗ."""

from __future__ import annotations

import json
import re
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, cast

from pydantic import ValidationError

from ..models import (
    EmailParameters,
    DetailedEmailAnalysis,
    ExtractedInfo,
    EmailCategory,
)
from .department_detector import detect_department_by_keywords
from .category_detector import hybrid_category_detection, detect_category_by_keywords
from .yandex_gpt_client import YandexGPTService


class EmailAnalyzer:
    """Сервис для расширенного анализа входящих писем."""

    def __init__(self, yandex_service: YandexGPTService | None = None):
        self.yandex_service = yandex_service or YandexGPTService()

    def _extract_contact_info(self, text: str) -> str | None:
        """Извлекает контактные данные из текста."""
        patterns = [
            r'\b\d{10,11}\b',  # Телефоны
            r'\b[\w\.-]+@[\w\.-]+\.\w+\b',  # Email
            r'ИНН\s*:?\s*\d{10,12}',  # ИНН
            r'ОГРН\s*:?\s*\d{13,15}',  # ОГРН
            r'БИК\s*:?\s*\d{9}',  # БИК
        ]
        
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        
        return ", ".join(found) if found else None

    def _check_no_response_required(self, text: str) -> bool:
        """Проверяет, требуется ли ответ на письмо."""
        no_response_phrases = [
            "ответ не требуется",
            "ответ на настоящее уведомление не требуется",
            "ответ не обязателен",
            "уведомление",
            "информирование",
            "для сведения",
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in no_response_phrases)

    def _calculate_work_days_until_date(self, target_date: datetime) -> int:
        """Вычисляет количество рабочих дней до указанной даты."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        target = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if target <= today:
            return 1  # Если дата уже прошла, возвращаем 1 день
        
        work_days = 0
        current = today
        while current < target:
            # Пропускаем выходные (суббота=5, воскресенье=6)
            if current.weekday() < 5:
                work_days += 1
            current += timedelta(days=1)
        
        return max(1, work_days)  # Минимум 1 рабочий день

    def _extract_deadline_from_text(self, text: str) -> int | None:
        """Извлекает дедлайн из текста письма в рабочих днях."""
        text_lower = text.lower()
        
        # Проверяем, есть ли упоминание дедлайна или срока
        deadline_indicators = [
            "дедлайн",
            "срок",
            "в течение",
            "до",
            "не позднее",
            "в срок",
            "немедленно",
            "срочно",
        ]
        
        has_deadline_mention = any(indicator in text_lower for indicator in deadline_indicators)
        
        # Если нет упоминания дедлайна, возвращаем None
        if not has_deadline_mention:
            return None
        
        # ПРИОРИТЕТ 1: Сначала проверяем явные указания на количество рабочих дней
        # Это более точная информация, чем даты
        work_days_patterns = [
            (r'в течение (\d+)\s*рабочи[хм]\s*дн[еяй]', True),  # "в течение 10 рабочих дней" - ПРИОРИТЕТ
            (r'дедлайн[ае]?\s*:?\s*(\d+)\s*рабочи[хм]\s*дн[еяй]', True),  # "дедлайн 3 рабочих дня"
            (r'дедлайн[ае]?\s*:?\s*(\d+)\s*раб\.?\s*дн\.?', True),  # "дедлайн 3 раб. дн."
            (r'в течение (\d+)\s*раб\.?\s*дн\.?', True),  # "в течение 3 раб. дн."
            (r'(\d+)\s*рабочи[хм]\s*дн[еяй]', True),  # "10 рабочих дней"
            (r'(\d+)\s*раб\.?\s*дн\.?', True),  # "10 раб. дн."
        ]
        
        for pattern, is_work_days in work_days_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        continue
                    try:
                        days = int(match)
                        if 1 <= days <= 30:  # Разумные пределы
                            return days
                    except (ValueError, TypeError):
                        continue
        
        # ПРИОРИТЕТ 2: Проверяем другие паттерны с днями (не рабочие дни)
        days_patterns = [
            (r'дедлайн[ае]?\s*:?\s*(\d+)\s*дн[еяй]', False),  # "дедлайн 3 дня"
            (r'в течение (\d+)\s*дн[еяй]', False),  # "в течение 3 дней"
            (r'в течение (\d+)\s*дня', False),  # "в течение 3 дня"
            (r'в течение (\d+)\s*дней', False),  # "в течение 3 дней"
            (r'немедленно', True),  # "немедленно" = 1 день
            (r'срочно', True),  # "срочно" = 1 день
            (r'в кратчайшие сроки', True),  # "в кратчайшие сроки" = 1 день
        ]
        
        for pattern, is_work_days in days_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                if pattern in [r'немедленно', r'срочно', r'в кратчайшие сроки']:
                    return 1
                
                for match in matches:
                    if isinstance(match, tuple):
                        continue
                    try:
                        days = int(match)
                        if 1 <= days <= 30:  # Разумные пределы
                            # Если это не рабочие дни, конвертируем примерно (календарные дни * 0.7)
                            if not is_work_days:
                                days = max(1, int(days * 0.7))
                            return days
                    except (ValueError, TypeError):
                        continue
        
        # ПРИОРИТЕТ 3: Проверяем даты (если не нашли явное указание на дни)
        date_patterns = [
            r'до (\d{1,2})\.(\d{1,2})\.(\d{4})',  # "до 25.11.2025"
            r'в срок до (\d{1,2})\.(\d{1,2})\.(\d{4})',  # "в срок до 25.11.2025"
            r'не позднее (\d{1,2})\.(\d{1,2})\.(\d{4})',  # "не позднее 25.11.2025"
            r'дедлайн[ае]?\s*:?\s*(\d{1,2})\.(\d{1,2})\.(\d{4})',  # "дедлайн: 25.11.2025"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    day, month, year = map(int, match)
                    # Проверяем валидность даты
                    target_date = datetime(year, month, day)
                    work_days = self._calculate_work_days_until_date(target_date)
                    # Ограничиваем разумными пределами (1-30 рабочих дней)
                    if 1 <= work_days <= 30:
                        return work_days
                except (ValueError, TypeError):
                    continue
        
        return None

    def _calculate_sla_days(
        self, category: EmailCategory, urgency: str, audience: str, body: str, subject: str = ""
    ) -> int:
        """
        Вычисляет SLA в рабочих днях на основе категории, срочности и аудитории.
        
        Стандарты SLA:
        1. КРИТИЧЕСКИЙ (Внешние регуляторы & срочные дедлайны) - 1-5 рабочих дней
        2. ВЫСОКИЙ (Клиенты, партнёры, претензии) - 3 рабочих дня
        3. СРЕДНИЙ (Стратегические партнёрства & благотворительность) - 7-15 рабочих дней
        4. НИЗКИЙ / ИНФОРМАЦИОННЫЙ (Уведомления) - 1-2 дня
        """
        # 4. НИЗКИЙ / ИНФОРМАЦИОННЫЙ (Уведомления) - 1-2 дня
        if category == "notification":
            if self._check_no_response_required(body):
                return 0  # Ответ не требуется
            return 1  # Информационные уведомления - 1 день
        
        # 1. КРИТИЧЕСКИЙ (Внешние регуляторы & срочные дедлайны) - 1-5 рабочих дней
        if category == "regulatory_request" or audience == "regulator":
            # Для регуляторных запросов используем среднее значение 3 дня
            # Если есть извлеченный дедлайн, он будет показан отдельно
            return 3
        
        # 2. ВЫСОКИЙ (Клиенты, партнёры, претензии) - 3 рабочих дня
        if category == "complaint":
            return 3  # Претензии требуют расследования и юридического согласования
        
        # Если высокая срочность для клиентов или партнёров
        if urgency == "high" and (audience == "client" or audience == "partner"):
            return 3  # Высокий приоритет для клиентов и партнёров
        
        # Если запрос информации от клиента с высокой срочностью
        if category == "information_request" and urgency == "high" and audience == "client":
            return 3
        
        # 3. СРЕДНИЙ (Стратегические партнёрства & благотворительность) - 7-15 рабочих дней
        if category == "partnership_proposal":
            return 10  # Партнёрские предложения требуют согласования нескольких отделов
        
        if category == "approval_request":
            return 10  # Запросы на согласование требуют финансового анализа
        
        # Если партнёр с обычной срочностью
        if audience == "partner" and urgency == "normal":
            return 10  # Стратегические партнёрства
        
        # Если запрос информации от партнёра
        if category == "information_request" and audience == "partner":
            return 10
        
        # Для остальных случаев с обычной срочностью
        if urgency == "normal":
            if audience == "client":
                return 5  # Стандартный срок для клиентов
            return 7  # Стандартный срок для остальных
        
        # Если высокая срочность для остальных случаев
        if urgency == "high":
            return 3  # Высокий приоритет
        
        # Дефолтное значение
        return 5

    def analyze_email_detailed(
        self, subject: str, body: str, company_context: str
    ) -> DetailedEmailAnalysis:
        """
        Выполняет расширенный анализ входящего письма согласно ТЗ.
        Использует кэширование для ускорения повторных запросов.
        """
        # Try to get from cache
        from .cache_service import get_cache_service
        cache = get_cache_service()
        
        if cache.is_enabled():
            cached_result = cache.get_analysis(subject, body, company_context)
            if cached_result:
                try:
                    return DetailedEmailAnalysis(**cached_result)
                except Exception as e:
                    print(f"[CACHE] Error deserializing cached analysis: {e}")
        
        analysis_prompt = f"""Проанализируй входящее письмо и выполни комплексный анализ.

Входящее письмо:
Тема: {subject}
Текст: {body}
Контекст компании: {company_context}

Верни ТОЛЬКО валидный JSON со следующей структурой:
{{
  "category": "information_request",
  "parameters": {{
    "tone": "formal",
    "purpose": "response",
    "length": "medium",
    "audience": "client",
    "urgency": "normal",
    "address_style": "vy",
    "include_formal_greetings": true,
    "include_greeting_and_signoff": true,
    "include_corporate_phrases": true
  }},
  "extracted_info": {{
    "request_essence": "Краткое описание сути запроса и ожиданий отправителя",
    "contact_info": "Извлеченные контактные данные, если есть",
    "regulatory_references": ["Ссылка на нормативный акт 1", "Ссылка на нормативный акт 2"],
    "requirements": ["Требование 1", "Требование 2"],
    "legal_risks": ["Потенциальный риск 1", "Потенциальный риск 2"]
  }}
}}

КРИТИЧЕСКИ ВАЖНО - Определение категории (category):
- "complaint" - Официальная жалоба или претензия:
  * Содержит фразы: "нарушение", "требуем", "претензия", "жалоба", "недовольство", "грубое нарушение"
  * Упоминает нарушения условий договора, некачественное обслуживание, неправомерные действия
  * Требует разъяснений, возврата средств, компенсации
  * Примеры: "нарушение условий договора", "требуем возврата средств", "претензия по качеству услуг"
- "notification" - Используй ТОЛЬКО если письмо явно является уведомлением или информированием:
  * Содержит фразы: "уведомляем", "информируем", "доводим до сведения", "ответ не требуется"
  * Сообщает об изменениях, новых требованиях, обновлениях без запроса действий
  * Примеры: уведомления регулятора об изменениях нормативов, информирование о новых процедурах
- "regulatory_request" - Требования от надзорных органов (Банк России, ЦБ РФ) с нормативными основаниями, требующие действий
- "information_request" - Запрос информации/документов (справки, выписки, подтверждающие документы)
- "partnership_proposal" - Партнёрское предложение (коммерческие предложения, запросы на сотрудничество)
- "approval_request" - Запрос на согласование (необходимость утверждения документов, условий сделок)
- "other" - Прочее (используй только если ни одна категория не подходит)

Параметры (parameters):
- tone: "formal" | "neutral" | "friendly"
  * Для жалоб и претензий используй "formal"
- purpose: "response" | "proposal" | "notification" | "refusal"
  * Если category = "notification", то purpose должен быть "notification"
  * Если category = "complaint", то purpose должен быть "response" (это ответ на жалобу/претензию)
  * Для жалоб и претензий всегда используй "response"
- length: "short" | "medium" | "long"
- audience: "colleague" | "manager" | "client" | "partner" | "regulator"
  * КРИТИЧЕСКИ ВАЖНО - Различие между "client" и "partner":
    - "client" - Клиент банка: физическое или юридическое лицо, которое ПОЛУЧАЕТ УСЛУГИ банка:
      * Использует банковские продукты: кредиты, вклады, счета, карты, переводы
      * Обращается за обслуживанием, консультациями, справками
      * Имеет договорные отношения клиент-банк (клиент платит за услуги)
      * Примеры: запросы о кредите, открытие вклада, проблемы с картой, жалобы на обслуживание
    - "partner" - Бизнес-партнер: компания, с которой банк СОТРУДНИЧАЕТ НА РАВНЫХ:
      * Совместные проекты, интеграции, партнерские программы
      * B2B отношения, API интеграции, белый label решения
      * Коммерческие предложения о сотрудничестве, партнерстве
      * Примеры: предложения о партнерстве, запросы на интеграцию API, совместные маркетинговые программы
  * "regulator" - Если письмо от Банка России, ЦБ РФ, регулятора - используй "regulator"
  * "colleague" - Внутренняя переписка между сотрудниками банка
  * "manager" - Вышестоящее руководство
- urgency: "low" | "normal" | "high"
  * Если в письме указан конкретный дедлайн или фразы "немедленно", "срочно" - используй "high"
  * Для жалоб обычно "high" или "normal" в зависимости от тональности
- address_style: "vy" | "ty" | "full_name"

Извлеченная информация (extracted_info):
- request_essence: ОБЯЗАТЕЛЬНО заполни! Краткое описание сути письма:
  * Для уведомлений: опиши, о чем уведомляют и какие действия требуются (если требуются)
  * Для запросов: опиши суть запроса и ожидания отправителя
  * Для жалоб: опиши суть претензии
  * Будь конкретным и информативным (2-3 предложения)
- contact_info: Извлеченные контактные данные, реквизиты (если есть)
- regulatory_references: Массив ссылок на упомянутые нормативные акты (если есть)
  * Примеры: "Указание Банка России №58-У", "Федеральный закон №...", "Методические рекомендации №..."
- requirements: Массив требований и ожиданий отправителя (если есть)
  * Для уведомлений: какие действия требуются (например, "внести изменения в системы до 01.01.2026")
- legal_risks: Массив потенциальных юридических рисков и ограничений (если есть)

Важно:
- Если информации нет, используй null для опциональных полей или пустые массивы []
- Будь точным и конкретным в извлечении информации
- Для legal_risks укажи только реальные потенциальные проблемы
- request_essence ВСЕГДА должен быть заполнен - это критически важно для оператора
"""

        try:
            raw_json = self.yandex_service._make_request(
                [
                    {
                        "role": "system",
                        "content": (
                            "Ты эксперт по анализу деловой корреспонденции банка. "
                            "Отвечай только валидным JSON без дополнительных комментариев."
                        ),
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.3,
            )

            if isinstance(raw_json, str):
                raw_json = raw_json.strip()
                # Убираем markdown code blocks если есть
                if raw_json.startswith("```"):
                    raw_json = re.sub(r"^```(?:json)?\n", "", raw_json)
                    raw_json = re.sub(r"\n```$", "", raw_json)
                    raw_json = raw_json.strip()
            else:
                raw_json = str(raw_json).strip()

            # Пытаемся найти JSON в тексте, если он обернут в текст
            json_match = re.search(r'\{.*\}', raw_json, re.DOTALL)
            if json_match:
                raw_json = json_match.group(0)

            try:
                analysis_dict = json.loads(raw_json)
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")
                print(f"Сырой ответ: {raw_json[:500]}...")
                raise ValueError(f"Не удалось распарсить JSON ответ от ИИ: {e}")
            
            # Валидация обязательных полей
            if "category" not in analysis_dict:
                raise ValueError("Отсутствует поле category в ответе")
            if "parameters" not in analysis_dict:
                raise ValueError("Отсутствует поле parameters в ответе")
            if "extracted_info" not in analysis_dict:
                raise ValueError("Отсутствует поле extracted_info в ответе")
            
            # Гибридное определение категории: ИИ + взвешенные ключевые слова
            ai_category_str = analysis_dict.get("category", "other")
            # Валидация категории
            valid_categories = ["information_request", "complaint", "regulatory_request", 
                              "partnership_proposal", "approval_request", "notification", "other"]
            if ai_category_str not in valid_categories:
                print(f"Неизвестная категория от ИИ: {ai_category_str}, используем 'other'")
                ai_category_str = "other"
            
            ai_category: EmailCategory = ai_category_str  # type: ignore
            
            try:
                final_category = hybrid_category_detection(ai_category, subject, body)
            except Exception as e:
                print(f"Ошибка гибридного определения категории: {e}")
                final_category = ai_category
            
            # Обновляем категорию в словаре, если она изменилась
            if final_category != ai_category:
                analysis_dict["category"] = final_category
                print(f"Категория скорректирована: {ai_category} -> {final_category}")
            
            # Убеждаемся, что request_essence заполнен
            extracted_info_dict = analysis_dict.get("extracted_info", {})
            if not isinstance(extracted_info_dict, dict):
                extracted_info_dict = {}
            
            if not extracted_info_dict.get("request_essence") or not extracted_info_dict.get("request_essence", "").strip():
                # Генерируем суть запроса на основе категории и текста
                if final_category == "notification":
                    extracted_info_dict["request_essence"] = f"Уведомление: {subject}. Требуется ознакомление и учет информации."
                else:
                    extracted_info_dict["request_essence"] = f"Запрос по теме: {subject}. Требуется обработка и ответ."
            
            # Убеждаемся, что все опциональные поля имеют правильный тип
            if "regulatory_references" not in extracted_info_dict or not isinstance(extracted_info_dict.get("regulatory_references"), list):
                extracted_info_dict["regulatory_references"] = []
            if "requirements" not in extracted_info_dict or not isinstance(extracted_info_dict.get("requirements"), list):
                extracted_info_dict["requirements"] = []
            if "legal_risks" not in extracted_info_dict or not isinstance(extracted_info_dict.get("legal_risks"), list):
                extracted_info_dict["legal_risks"] = []

            # Определяем отдел
            department = detect_department_by_keywords(subject, body)

            # Извлекаем дедлайн из текста
            extracted_deadline = self._extract_deadline_from_text(f"{subject} {body}")
            
            # Вычисляем SLA
            category = final_category
            urgency = analysis_dict["parameters"]["urgency"]
            audience = analysis_dict["parameters"]["audience"]
            sla_days = self._calculate_sla_days(category, urgency, audience, body, subject)

            # Дополняем контактную информацию если не извлечена ИИ
            if not extracted_info_dict.get("contact_info"):
                contact_info = self._extract_contact_info(f"{subject} {body}")
                if contact_info:
                    extracted_info_dict["contact_info"] = contact_info

            try:
                # Валидация и создание параметров
                params_dict = analysis_dict.get("parameters", {})
                email_params = EmailParameters(**params_dict)
                
                # Валидация и создание extracted_info
                extracted_info_obj = ExtractedInfo(**extracted_info_dict)
                
                result = DetailedEmailAnalysis(
                    category=category,  # type: ignore
                    parameters=email_params,
                    extracted_info=extracted_info_obj,
                    department=department,
                    estimated_sla_days=sla_days,
                    extracted_deadline_days=extracted_deadline,
                )
                
                # Cache the result
                if cache.is_enabled():
                    try:
                        cache.set_analysis(
                            subject,
                            body,
                            company_context,
                            result.model_dump()
                        )
                    except Exception as e:
                        print(f"[CACHE] Error caching analysis result: {e}")
                
                return result
            except Exception as e:
                print(f"Ошибка создания DetailedEmailAnalysis: {e}")
                print(f"Параметры: {analysis_dict.get('parameters')}")
                print(f"Extracted info: {extracted_info_dict}")
                import traceback
                traceback.print_exc()
                raise

        except Exception as e:
            print(f"Ошибка расширенного анализа: {e}")
            import traceback
            traceback.print_exc()
            
            # Используем гибридный подход: взвешенные ключевые слова + базовый анализ ИИ
            keyword_category, keyword_confidence = detect_category_by_keywords(subject, body)
            
            # Fallback на базовый анализ
            basic_params = self.yandex_service.analyze_email_parameters(
                subject, body, company_context
            )
            
            # Определяем финальную категорию
            # Если ключевые слова дают высокую уверенность, используем их
            if keyword_confidence >= 0.3:
                final_category = keyword_category
            else:
                # Пытаемся определить по purpose из базового анализа
                purpose_to_category = {
                    "notification": "notification",
                    "response": "information_request",
                    "proposal": "partnership_proposal",
                    "refusal": "complaint",
                }
                final_category = purpose_to_category.get(basic_params.purpose, "other")
            
            department = detect_department_by_keywords(subject, body)
            sla_days = self._calculate_sla_days(final_category, basic_params.urgency, basic_params.audience, body, subject)
            
            # Извлекаем дедлайн из текста
            extracted_deadline = self._extract_deadline_from_text(f"{subject} {body}")
            
            # Генерируем базовую суть запроса
            if final_category == "notification":
                request_essence = f"Уведомление: {subject}. Требуется ознакомление с информацией."
            elif final_category == "regulatory_request":
                request_essence = f"Регуляторный запрос: {subject}. Требуется выполнение требований регулятора."
            elif final_category == "complaint":
                request_essence = f"Жалоба/претензия: {subject}. Требуется рассмотрение и ответ."
            else:
                request_essence = f"Запрос по теме: {subject}. Требуется обработка и ответ."

            return DetailedEmailAnalysis(
                category=final_category,  # type: ignore
                parameters=basic_params,
                extracted_info=ExtractedInfo(
                    request_essence=request_essence
                ),
                department=department,
                estimated_sla_days=sla_days,
                extracted_deadline_days=extracted_deadline,
            )


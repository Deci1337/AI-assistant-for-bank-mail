"""Гибридный детектор категории письма: ИИ + взвешенные ключевые слова."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from ..models import EmailCategory


# Взвешенные ключевые слова для категорий
CATEGORY_KEYWORDS: Dict[EmailCategory, List[Tuple[str, float]]] = {
    "notification": [
        # Высокий вес для явных индикаторов уведомлений
        ("уведомляем", 3.0),
        ("информируем", 3.0),
        ("доводим до сведения", 3.0),
        ("ответ не требуется", 5.0),
        ("ответ на настоящее уведомление не требуется", 5.0),
        ("для сведения", 2.5),
        ("к сведению", 2.5),
        ("информирование", 2.0),
        ("уведомление", 2.0),
        # Контекстные фразы
        ("изменения в методике", 2.0),
        ("вступают в силу", 1.5),
        ("с 01.01", 1.5),
        ("с 1 января", 1.5),
    ],
    "regulatory_request": [
        # Высокий вес для регуляторных запросов
        ("банк россии", 4.0),
        ("цб рф", 4.0),
        ("центральный банк", 4.0),
        ("регулятор", 3.0),
        ("надзорный орган", 3.0),
        ("требуем", 3.5),
        ("просим предоставить", 3.0),
        ("необходимо предоставить", 3.0),
        ("в срок до", 2.0),
        ("в течение", 2.0),
        ("указание банка россии", 3.5),
        ("распоряжение", 2.5),
        ("приказ", 2.5),
    ],
    "information_request": [
        ("запрос", 2.0),
        ("просим предоставить", 3.0),
        ("необходима информация", 3.0),
        ("требуется информация", 3.0),
        ("справка", 2.5),
        ("выписка", 2.5),
        ("документ", 1.5),
        ("подтверждающий документ", 3.0),
        ("копия документа", 2.0),
    ],
    "complaint": [
        ("жалоба", 4.0),
        ("претензия", 4.0),
        ("недовольство", 3.5),
        ("нарушение", 4.5),
        ("грубое нарушение", 5.0),
        ("нарушение условий договора", 5.0),
        ("некачественное обслуживание", 3.5),
        ("требуем", 3.5),
        ("требуем компенсацию", 4.0),
        ("требуем возврата", 4.0),
        ("требуем разъяснения", 3.5),
        ("возврат средств", 3.5),
        ("нарушены условия", 4.0),
        ("не соблюдены", 3.0),
        ("списаны без", 3.5),
        ("неправомерные действия", 4.0),
    ],
    "partnership_proposal": [
        ("партнерство", 3.5),
        ("сотрудничество", 3.0),
        ("коммерческое предложение", 4.0),
        ("предлагаем", 2.5),
        ("партнерская программа", 3.5),
        ("b2b", 2.0),
        ("b2b2c", 2.0),
        ("интеграция", 2.0),
        ("совместный проект", 3.0),
    ],
    "approval_request": [
        ("согласование", 3.5),
        ("утверждение", 3.5),
        ("просим согласовать", 4.0),
        ("требуется согласование", 3.5),
        ("на согласование", 3.0),
        ("на утверждение", 3.0),
        ("одобрение", 2.5),
    ],
}


def calculate_category_score(text: str, category: EmailCategory) -> float:
    """
    Вычисляет взвешенный score для категории на основе ключевых слов.
    
    Args:
        text: Текст для анализа (обычно subject + body)
        category: Категория для проверки
        
    Returns:
        Взвешенный score (чем выше, тем вероятнее категория)
    """
    text_lower = text.lower()
    score = 0.0
    
    keywords = CATEGORY_KEYWORDS.get(category, [])
    
    for keyword, weight in keywords:
        # Используем word boundary для точного совпадения
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
        score += matches * weight
    
    return score


def detect_category_by_keywords(subject: str, body: str) -> Tuple[EmailCategory, float]:
    """
    Определяет категорию письма на основе взвешенных ключевых слов.
    
    Returns:
        Tuple[category, confidence_score]
    """
    text = f"{subject} {body}"
    
    category_scores: Dict[EmailCategory, float] = {}
    
    for category in EmailCategory.__args__:  # type: ignore
        score = calculate_category_score(text, category)
        if score > 0:
            category_scores[category] = score
    
    if not category_scores:
        return ("other", 0.0)
    
    # Находим категорию с максимальным score
    best_category = max(category_scores.items(), key=lambda x: x[1])
    
    # Нормализуем confidence (максимальный score / сумма всех scores)
    total_score = sum(category_scores.values())
    confidence = best_category[1] / total_score if total_score > 0 else 0.0
    
    return (best_category[0], confidence)


def hybrid_category_detection(
    ai_category: EmailCategory,
    subject: str,
    body: str,
    confidence_threshold: float = 0.3
) -> EmailCategory:
    """
    Гибридный подход: комбинирует результат ИИ с анализом ключевых слов.
    
    Args:
        ai_category: Категория, определенная ИИ
        subject: Тема письма
        body: Текст письма
        confidence_threshold: Порог уверенности для переопределения категории
        
    Returns:
        Финальная категория
    """
    keyword_category, keyword_confidence = detect_category_by_keywords(subject, body)
    
    # Если ключевые слова дают высокую уверенность и она отличается от ИИ
    if keyword_confidence >= confidence_threshold and keyword_category != ai_category:
        # Проверяем, не является ли категория от ключевых слов более специфичной
        priority_categories = ["notification", "regulatory_request", "complaint"]
        
        # Если ключевые слова указывают на приоритетную категорию, используем её
        if keyword_category in priority_categories:
            return keyword_category
        
        # Если ИИ определил "other", а ключевые слова дают конкретную категорию
        if ai_category == "other" and keyword_category != "other":
            return keyword_category
    
    # В остальных случаях доверяем ИИ
    return ai_category


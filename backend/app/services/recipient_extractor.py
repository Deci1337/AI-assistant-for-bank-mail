"""Service for extracting recipient name from incoming email."""

import re
from typing import Optional, Tuple


def extract_recipient_name(subject: str, body: str) -> Optional[Tuple[str, str]]:
    """
    Извлекает имя и отчество/фамилию получателя из входящего письма.
    
    Returns:
        Tuple[str, str] | None: (first_name, last_name_or_patronymic) или None
    """
    # Паттерны для поиска имени в обращении
    # "Уважаемый Артем Евгеньевич", "Добрый день, Артем Евгеньевич", и т.д.
    patterns = [
        r'(?:Уважаемый|Добрый день|Здравствуйте|Привет)[,\s!]*([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)',
        r'([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)(?:[,\s]+(?:уважаемый|добрый|здравствуйте))',
        r'Обращаюсь к ([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)',
        # Просто имя и отчество/фамилия в начале письма
        r'^[^А-ЯЁ]*([А-ЯЁ][а-яё]{2,15})\s+([А-ЯЁ][а-яё]{3,20})[,\s!]',
    ]
    
    # Ищем в теме и теле письма
    text = f"{subject} {body}"
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            first_name = match.group(1).strip()
            second_part = match.group(2).strip()
            
            # Проверяем, что это похоже на имя (не слишком длинное, начинается с заглавной)
            # Исключаем слова, которые не являются именами
            excluded_words = ['банк', 'компания', 'организация', 'фирма', 'предприятие', 'учреждение']
            if (len(first_name) > 1 and len(first_name) < 20 and 
                len(second_part) > 1 and len(second_part) < 25 and
                first_name.lower() not in excluded_words and
                second_part.lower() not in excluded_words):
                return (first_name, second_part)
    
    # Также ищем в начале письма в формате "Имя Отчество" или "Имя Фамилия"
    # Обычно это в первых 300 символах
    beginning = text[:300]
    name_pattern = r'([А-ЯЁ][а-яё]{2,15})\s+([А-ЯЁ][а-яё]{3,20})'
    matches = re.finditer(name_pattern, beginning)
    for match in matches:
        first_name = match.group(1).strip()
        second_part = match.group(2).strip()
        # Проверяем, что это не часть подписи отправителя или служебной информации
        context_before = beginning[max(0, match.start()-20):match.start()].lower()
        context_after = beginning[match.end():min(len(beginning), match.end()+20)].lower()
        if ('с уважением' not in context_before and 
            'заместитель' not in context_before and
            'директор' not in context_before and
            'менеджер' not in context_before and
            first_name.lower() not in ['банк', 'компания', 'организация']):
            return (first_name, second_part)
    
    return None


def has_recipient_name(subject: str, body: str) -> bool:
    """Проверяет, есть ли имя получателя во входящем письме."""
    return extract_recipient_name(subject, body) is not None


def format_recipient_name(subject: str, body: str) -> Optional[str]:
    """Форматирует имя получателя для использования в обращении."""
    name_tuple = extract_recipient_name(subject, body)
    if name_tuple:
        return f"{name_tuple[0]} {name_tuple[1]}"
    return None


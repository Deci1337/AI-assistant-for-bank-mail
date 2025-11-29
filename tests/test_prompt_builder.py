from backend.app.models import EmailGenerationRequest, EmailParameters
from backend.app.services.prompt_builder import build_messages


def _make_request(custom_prompt: str | None = None, **param_overrides):
    params = EmailParameters(**param_overrides)
    return EmailGenerationRequest(
        source_subject="Запрос данных",
        source_body="Просим предоставить отчёт по портфелю до пятницы.",
        company_context="ПСБ банк. Используем строгий корпоративный стиль.",
        sender_first_name="Анна",
        sender_last_name="Иванова",
        sender_position="Руководитель отдела",
        custom_prompt=custom_prompt,
        parameters=params,
    )


def test_prompt_contains_all_parameter_flags():
    req = _make_request(
        tone="friendly",
        purpose="proposal",
        length="short",
        audience="manager",
        address_style="full_name",
        include_formal_greetings=False,
        include_greeting_and_signoff=False,
        urgency="high",
        include_corporate_phrases=False,
        extra_directives=["Используй маркеры для списка действий"],
    )

    messages = build_messages(req)
    user_prompt = messages[1]["content"]

    assert "Тон: friendly" in user_prompt
    assert "Цель: proposal" in user_prompt
    assert "Срочность: high" in user_prompt
    assert "Корпоративные фразы: избегать" in user_prompt
    assert "Используй маркеры" in user_prompt
    assert "ответ возвращай строго" in user_prompt.lower()


def test_prompt_references_source_letter_and_context():
    req = _make_request()
    user_prompt = build_messages(req)[1]["content"]

    assert "Запрос данных" in user_prompt
    assert "Просим предоставить отчёт" in user_prompt
    assert "ПСБ банк" in user_prompt
    assert "Данные подписанта" in user_prompt
    assert "- Имя: Анна" in user_prompt


def test_custom_prompt_section_is_included():
    req = _make_request(custom_prompt="Включи KPI и ссылки на приложения.")
    user_prompt = build_messages(req)[1]["content"]

    assert "Дополнительное описание задачи" in user_prompt
    assert "Включи KPI и ссылки" in user_prompt


def test_sender_block_omitted_when_no_data():
    req = EmailGenerationRequest(
        source_subject="Тема",
        source_body="Тело",
        company_context="Контекст",
        parameters=EmailParameters(),
    )
    user_prompt = build_messages(req)[1]["content"]

    assert "- Имя:" not in user_prompt


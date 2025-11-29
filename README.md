# BizMail AI Assistant

AI-ассистент для генерации корпоративных писем. Backend на FastAPI с интеграцией YandexGPT, Frontend на React.

## Быстрый старт

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env  # заполните YANDEX_API_KEY и YANDEX_FOLDER_ID
uvicorn backend.app.main:app --reload --port 8001
```

Документация доступна на `http://localhost:8001/api/docs`.

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:5500`

### Старый HTML фронтенд

Старый HTML файл `site.html` можно открыть напрямую в браузере или через Live Server.

## Проверка интеграции

```bash
PYTHONPATH=. pytest -q
```

## Пример запроса

- По умолчанию `custom_prompt` оставляйте пустым (`""` или просто не передавайте). Добавляйте текст только тогда, когда нужно явно описать задачу или цель письма.

```bash
curl -X POST http://localhost:8001/api/emails/generate \
  -H "Content-Type: application/json" \
  -d '{
        "source_subject":"Ответ ФНС",
        "source_body":"Напоминаем о необходимости отчета до 30 ноября.",
        "company_context":"ПАО Банк. Соблюдаем строгий деловой стиль.",
        "sender_first_name":"Анна",
        "sender_last_name":"Иванова",
        "sender_position":"Начальник управления комплаенса",
        "custom_prompt":"",
        "parameters":{
          "tone":"formal",
          "purpose":"response",
          "length":"short",
          "audience":"regulator",
          "address_style":"vy",
          "include_formal_greetings":true,
          "include_greeting_and_signoff":true,
          "urgency":"high",
          "include_corporate_phrases":true,
          "extra_directives":["Добавь блок со следующими шагами"]
        }
      }'
```

### Тестовые сценарии

1. **Ответ регулятору (высокая срочность)**  
   ```json
   {
     "source_subject": "Запрос ЦБ по отчётности",
     "source_body": "Прошу предоставить обновлённый отчёт по ликвидности до конца дня.",
     "company_context": "ПАО Банк. Соблюдаем строгий деловой стиль.",
     "sender_first_name": "Ирина",
     "sender_last_name": "Петрова",
     "sender_position": "Директор департамента отчётности",
     "custom_prompt": "",
     "parameters": {
       "tone": "formal",
       "purpose": "response",
       "length": "medium",
       "audience": "regulator",
       "address_style": "vy",
       "include_formal_greetings": true,
       "include_greeting_and_signoff": true,
       "urgency": "high",
       "include_corporate_phrases": true
     }
   }
   ```

2. **Коммерческое предложение партнёру**  
   ```json
   {
     "source_subject": "Совместная акция",
     "source_body": "Партнёр просит описать условия совместной программы лояльности.",
     "company_context": "ПАО Банк. Фокус на выгоде для клиента.",
     "sender_first_name": "Дмитрий",
     "sender_last_name": "Николаев",
     "sender_position": "Руководитель партнёрских программ",
     "custom_prompt": "Сделай акцент на совместной выгоде и мягко попроси фидбек до пятницы.",
     "parameters": {
       "tone": "friendly",
       "purpose": "proposal",
       "length": "medium",
       "audience": "partner",
       "address_style": "full_name",
       "include_formal_greetings": true,
       "include_greeting_and_signoff": true,
       "urgency": "normal",
       "include_corporate_phrases": false,
       "extra_directives": ["Добавь список следующих шагов"]
     }
   }
   ```

3. **Внутреннее уведомление команде**  
   ```json
   {
     "source_subject": "Перенос дедлайна",
     "source_body": "Нужно уведомить команду об изменении срока сдачи проекта на 5 декабря.",
     "company_context": "ПАО Банк. Команда разработки BizMail.",
     "sender_first_name": "Мария",
     "sender_last_name": "Семенова",
     "sender_position": "Тимлид BizMail",
     "custom_prompt": "",
     "parameters": {
       "tone": "neutral",
       "purpose": "notification",
       "length": "short",
       "audience": "colleague",
       "address_style": "vy",
       "include_formal_greetings": false,
       "include_greeting_and_signoff": true,
       "urgency": "normal",
       "include_corporate_phrases": false
     }
   }
   ```

## Структура

### Backend

- `backend/app/models.py` – Pydantic-модели и параметры тонкой настройки
- `backend/app/services/prompt_builder.py` – генерация промпта из параметров
- `backend/app/services/yandex_gpt_client.py` – вызов YandexGPT API и парсинг ответа
- `backend/app/services/department_detector.py` – автоматическое определение отдела банка
- `backend/app/api/routes.py` – REST-эндпоинты `/api/emails/generate` и `/api/emails/analyze`
- `tests/test_prompt_builder.py` – тесты

### Frontend

- `frontend/src/components/` – React компоненты
- `frontend/src/services/api.js` – API клиент
- `frontend/src/styles/` – CSS стили

## Особенности

- ✅ Автоматическое определение отдела банка на основе содержания письма
- ✅ AI анализ входящего письма для подбора оптимальных параметров
- ✅ Генерация писем с учетом корпоративного стиля
- ✅ Современный React интерфейс
- ✅ Интеграция с YandexGPT (Qwen 3 235B)


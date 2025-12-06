"""
Каталог услуг для телеграм-ботов с ИИ
Здесь указаны все возможные сервисы и их базовые цены
"""

# Базовая стоимость разработки
BASE_BOT_COST = 5000

# Каталог дополнительных услуг
ADDITIONAL_SERVICES = {
    # ИИ и машинное обучение (первые по важности)
    "chatgpt_integration": {
        "name": "Интеграция с ChatGPT API",
        "description": "Умные ответы на вопросы клиентов",
        "price": 2000,
        "category": "ai"
    },
    "advanced_prompt_engineering": {
        "name": "Продвинутый промт-инжиниринг",
        "description": "Создание специализированных промптов для вашей отрасли",
        "price": 8000,
        "category": "ai"
    },
    
    # Функции по возрастанию цены
    "telegram_channel": {
        "name": "Интеграция с Telegram каналом",
        "description": "Отправка заявок в общий канал/чат",
        "price": 1100,
        "category": "communications"
    },
    "email_notifications": {
        "name": "Email уведомления",
        "description": "Отправка уведомлений на email о новых заказах",
        "price": 800,
        "category": "communications"
    },
    "backup_system": {
        "name": "Система резервного копирования",
        "description": "Автоматическое резервное копирование данных",
        "price": 800,
        "category": "administration"
    },
    "trello": {
        "name": "Интеграция с Trello",
        "description": "Автоматическое создание карточек задач",
        "price": 900,
        "category": "integrations"
    },
    "google_sheets": {
        "name": "Интеграция с Google Sheets",
        "description": "Автоматическое сохранение данных в таблицы Google",
        "price": 1000,
        "category": "integrations"
    },
    "scheduler": {
        "name": "Планировщик задач",
        "description": "Автоматическое выполнение задач по расписанию",
        "price": 1000,
        "category": "special"
    },
    "file_storage": {
        "name": "Файловое хранилище",
        "description": "Безопасное хранение файлов клиентов",
        "price": 1200,
        "category": "special"
    },
    "notion": {
        "name": "Интеграция с Notion",
        "description": "Синхронизация с базой знаний Notion",
        "price": 1200,
        "category": "integrations"
    },
    "analytics_dashboard": {
        "name": "Аналитика и отчеты",
        "description": "Дашборд с метриками и статистикой",
        "price": 1200,
        "category": "analytics"
    },
    "sentiment_analysis": {
        "name": "Анализ настроения клиентов",
        "description": "Автоматический анализ тона сообщений",
        "price": 1500,
        "category": "ai"
    },
    "payment_systems": {
        "name": "Интеграция с платежными системами",
        "description": "Прием оплаты через ЮKassa, Сбербанк, QIWI",
        "price": 2500,
        "category": "payments"
    },
    "voice_messages": {
        "name": "Голосовые сообщения",
        "description": "Обработка и генерация голосовых сообщений",
        "price": 2500,
        "category": "special"
    },
    "webhook_integration": {
        "name": "Webhook интеграция",
        "description": "Отправка данных в ваши системы через webhook",
        "price": 2000,
        "category": "communications"
    },
    "admin_panel": {
        "name": "Админ-панель",
        "description": "Веб-интерфейс для управления ботом",
        "price": 2000,
        "category": "administration"
    },
    "crypto_payments": {
        "name": "Криптоплатежи",
        "description": "Прием оплаты в Bitcoin, Ethereum, USDT",
        "price": 3500,
        "category": "payments"
    }
}

# Категории услуг для группировки
SERVICE_CATEGORIES = {
    "integrations": "Интеграции с внешними сервисами",
    "payments": "Платежные системы",
    "ai": "ИИ и машинное обучение",
    "communications": "Коммуникации и уведомления",
    "analytics": "Аналитика и отчеты",
    "administration": "Администрирование и безопасность",
    "special": "Специальные функции"
}

def get_service_by_id(service_id: str):
    """Получить услугу по ID"""
    return ADDITIONAL_SERVICES.get(service_id)

def get_services_by_category(category: str):
    """Получить все услуги определенной категории"""
    return {k: v for k, v in ADDITIONAL_SERVICES.items() if v["category"] == category}

def get_all_services():
    """Получить все услуги"""
    return ADDITIONAL_SERVICES

def calculate_total_cost(selected_services: list):
    """Рассчитать общую стоимость с выбранными услугами"""
    total = BASE_BOT_COST
    selected = []
    
    for service_id in selected_services:
        if service_id in ADDITIONAL_SERVICES:
            service = ADDITIONAL_SERVICES[service_id]
            total += service["price"]
            selected.append(service)
    
    return total, selected


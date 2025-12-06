import logging
from openai import OpenAI
from typing import Dict, Any
from datetime import datetime
from ..config import CHATGPT_API_KEY

logger = logging.getLogger(__name__)

# Настройка OpenAI
client = OpenAI(api_key=CHATGPT_API_KEY)

async def generate_order_summary(user_data: Dict[str, Any]) -> str:
    """
    Генерирует умное summary заказа с помощью ChatGPT
    """
    try:
        company = user_data.get('company', 'Не указано')
        bot_purpose = user_data.get('bot_purpose', 'Не указано')
        contact_name = user_data.get('contact_name', 'Не указано')
        
        # Формируем промпт для ChatGPT
        prompt = f"""
Ты - опытный IT-консультант, который помогает клиентам заказывать телеграм-ботов. Общайся как живой человек, без формальностей.

Клиент {contact_name} из компании "{company}" хочет заказать бота для следующих целей: {bot_purpose}

Твоя задача:
1. Создать краткое, но информативное резюме их потребностей
2. Задать 2-3 уточняющих вопроса для лучшего понимания проекта
3. Показать, что ты понимаешь их бизнес

ВАЖНО:
- НЕ используй заголовки, нумерацию или формальные структуры
- НЕ говори "Компания "название"", а используй более естественные формулировки
- Пиши как живой консультант, который разговаривает с клиентом
- Будь дружелюбным, но профессиональным
- Используй русский язык и эмодзи для лучшего восприятия
- НЕ добавляй фразы типа "Жду вашего ответа" или "Ожидаю ответа"

Пример хорошего ответа:
"Привет, {contact_name}! 🌟

Отлично, понимаю вашу задачу! Вы хотите создать бота для автоматизации процесса работы с клиентами - сбора заявок, расчета стоимости и формирования резюме проектов.

У меня есть несколько вопросов для уточнения деталей:
• Какие именно данные нужно собирать у клиентов для расчета стоимости?
• Есть ли у вас уже готовые шаблоны для резюме заказов?
• Планируете ли интегрировать бота с другими системами?

Это поможет мне предложить оптимальное решение для вашего бизнеса! 🚀"
        """
        
        # Вызываем ChatGPT
        response = await _call_chatgpt(prompt)
        
        if response:
            logger.info(f"ChatGPT сгенерировал summary для {contact_name}")
            return response
        else:
            # Fallback на базовую версию
            return _generate_fallback_summary(user_data)
        
    except Exception as e:
        logger.error(f"Ошибка при генерации summary заказа: {e}")
        return _generate_fallback_summary(user_data)

async def _call_chatgpt(prompt: str) -> str:
    """
    Вызывает ChatGPT API
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - опытный IT-менеджер, который помогает клиентам заказывать телеграм-ботов. Отвечай кратко, профессионально и дружелюбно."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Ошибка при вызове ChatGPT: {e}")
        return None

def _generate_fallback_summary(user_data: Dict[str, Any]) -> str:
    """
    Fallback версия summary без ChatGPT
    """
    company = user_data.get('company', 'Не указано')
    bot_purpose = user_data.get('bot_purpose', 'Не указано')
    contact_name = user_data.get('contact_name', 'Не указано')
    
    return f"""
📋 **Резюме заказа**

👤 **{contact_name}**, спасибо за подробное описание!

🏢 **Ваша компания:** {company}
🎯 **Назначение бота:** {bot_purpose}

❓ **Уточняющие вопросы:**
• Какой объем заказов планируете обрабатывать в день?
• Нужна ли интеграция с вашими существующими системами?
• Какие дополнительные функции были бы полезны?

Готовы обсудить детали проекта?
    """.strip()

async def generate_cost_breakdown(user_data: Dict[str, Any]) -> str:
    """
    Генерирует разбивку стоимости базового бота
    """
    try:
        contact_name = user_data.get('contact_name', 'Клиент')
        
        cost_breakdown = f"""
💰 **Базовая стоимость разработки бота**

👤 **{contact_name}**, вот что входит в базовую стоимость **3000 рублей**:

🔧 **Основные компоненты:**
• Создание структуры бота на aiogram
• Настройка базовой логики и состояний
• Интеграция с Telegram Bot API
• Базовый интерфейс пользователя

📱 **Функциональность:**
• Обработка команд и сообщений
• Система состояний для диалогов
• Логирование действий пользователей
• Обработка ошибок

⚙️ **Техническая часть:**
• Развертывание на VPS-сервере
• Настройка SSL-сертификатов
• Мониторинг работы бота
• Резервное копирование

---
*Это базовая версия. Дополнительные функции оплачиваются отдельно.*
        """.strip()
        
        logger.info(f"Сгенерирована разбивка стоимости для {contact_name}")
        return cost_breakdown
        
    except Exception as e:
        logger.error(f"Ошибка при генерации разбивки стоимости: {e}")
        return "❌ Произошла ошибка при генерации стоимости. Попробуйте еще раз."

async def generate_recommendations(user_data: Dict[str, Any]) -> str:
    """
    Генерирует персонализированные рекомендации и итоговую стоимость
    """
    try:
        company = user_data.get('company', 'вашей компании')
        bot_purpose = user_data.get('bot_purpose', 'выполнять задачи')
        contact_name = user_data.get('contact_name', 'Клиент')
        
        # Анализируем назначение бота для рекомендаций
        bot_purpose_lower = bot_purpose.lower()
        
        # Определяем рекомендуемые сервисы на основе назначения
        recommended_services = []
        additional_cost = 0
        
        if any(word in bot_purpose_lower for word in ['заявк', 'заказ', 'покупк']):
            recommended_services.append("🛒 **Система заказов** - 2000₽")
            additional_cost += 2000
            recommended_services.append("💳 **Интеграция с платежными системами** - 1500₽")
            additional_cost += 1500
            
        if any(word in bot_purpose_lower for word in ['консульт', 'помощь', 'вопрос']):
            recommended_services.append("🤖 **Интеграция с ChatGPT API** - 3000₽")
            additional_cost += 3000
            recommended_services.append("📚 **База знаний и FAQ** - 1000₽")
            additional_cost += 1000
            
        if any(word in bot_purpose_lower for word in ['технич', 'проблем', 'поддерж']):
            recommended_services.append("🎫 **Система тикетов** - 2500₽")
            additional_cost += 2500
            recommended_services.append("📊 **Аналитика и отчеты** - 1500₽")
            additional_cost += 1500
            
        if any(word in bot_purpose_lower for word in ['автоматиз', 'процесс', 'бизнес']):
            recommended_services.append("📊 **Интеграция с Google Sheets** - 2000₽")
            additional_cost += 2000
            recommended_services.append("📧 **Интеграция с email-сервисами** - 1500₽")
            additional_cost += 1500
            
        # Базовые рекомендуемые сервисы для всех ботов
        if not recommended_services:
            recommended_services.extend([
                "📊 **Интеграция с Google Sheets** - 2000₽",
                "🤖 **Базовая интеграция с ИИ** - 2000₽",
                "📱 **Адаптивный интерфейс** - 1500₽"
            ])
            additional_cost += 5500
        
        # Добавляем базовую стоимость
        total_cost = 3000 + additional_cost
        
        recommendations = f"""
🎯 **Персонализированные рекомендации**

👤 **{contact_name}**, исходя из описания вашего бота, я рекомендую подключить следующие сервисы:

{chr(10).join(recommended_services)}

📋 **Итоговая стоимость:**
• Базовая разработка: **3000₽**
• Дополнительные сервисы: **{additional_cost}₽**
• **Итого: {total_cost}₽**

💡 **Почему именно эти сервисы?**
Ваш бот будет {bot_purpose.lower()}, поэтому дополнительные функции значительно улучшат его эффективность и удобство использования.

🚀 **Сроки разработки:** 7-14 дней
        """.strip()
        
        logger.info(f"Сгенерированы рекомендации для {contact_name} на сумму {total_cost}₽")
        return recommendations
        
    except Exception as e:
        logger.error(f"Ошибка при генерации рекомендаций: {e}")
        return "❌ Произошла ошибка при генерации рекомендаций. Попробуйте еще раз."

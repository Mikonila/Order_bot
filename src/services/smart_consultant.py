"""
Умный консультант для анализа диалога и подбора услуг
"""

import logging
from typing import Dict, Any, List, Tuple
from openai import OpenAI
from ..config import CHATGPT_API_KEY
from .services_catalog import get_all_services, calculate_total_cost, SERVICE_CATEGORIES

logger = logging.getLogger(__name__)

# Настройка OpenAI
client = OpenAI(api_key=CHATGPT_API_KEY)

class SmartConsultant:
    def __init__(self):
        self.services = get_all_services()
        self.categories = SERVICE_CATEGORIES
    
    async def analyze_conversation(self, user_data: Dict[str, Any]) -> str:
        """
        Анализирует всю собранную информацию и генерирует умный ответ
        """
        try:
            company = user_data.get('company', '')
            bot_purpose = user_data.get('bot_purpose', '')
            contact_name = user_data.get('contact_name', '')
            clarifications = user_data.get('clarifications', [])
            
            # Формируем промпт для анализа
            prompt = f"""
Ты - опытный консультант по телеграм-ботам. Проанализируй информацию клиента и задай 2-3 конкретных уточняющих вопроса.

Клиент: {contact_name}
Компания: {company}
Назначение бота: {bot_purpose}

Твоя задача:
1. Кратко резюмировать понимание задачи клиента (1-2 предложения)
2. Задать 2-3 конкретных вопроса для понимания технических потребностей
3. НЕ предлагай "связаться для обсуждения" - задавай конкретные вопросы прямо сейчас

Формат ответа:
"Привет, {contact_name}! 🌟 [Краткое резюме понимания задачи]

Уточню несколько деталей:
• [Конкретный вопрос 1]
• [Конкретный вопрос 2] 
• [Конкретный вопрос 3]

Это поможет мне предложить наилучшее решение для вашего бизнеса! 🚀"

Будь конкретным, дружелюбным и профессиональным. Используй эмодзи.
            """
            
            # Вызываем ChatGPT
            response = await self._call_chatgpt(prompt)
            
            if response:
                logger.info(f"ChatGPT проанализировал диалог для {contact_name}")
                return response
            else:
                return self._generate_fallback_analysis(user_data)
                
        except Exception as e:
            logger.error(f"Ошибка при анализе диалога: {e}")
            return self._generate_fallback_analysis(user_data)
    
    async def answer_general_question(self, message: str, user_data: Dict[str, Any] = None) -> str:
        """
        Отвечает на общие вопросы с учетом контекста, если есть
        """
        try:
            # Формируем промпт с учетом контекста
            if user_data and any(user_data.values()):
                context = f"""
Контекст клиента:
- Имя: {user_data.get('contact_name', 'Не указано')}
- Компания: {user_data.get('company', 'Не указано')}
- Назначение бота: {user_data.get('bot_purpose', 'Не указано')}
- Уточнения: {chr(10).join(f"• {clarification}" for clarification in user_data.get('clarifications', []))}

Вопрос клиента: {message}
                """
            else:
                context = f"""
Клиент задал общий вопрос: {message}

Ты - опытный IT-консультант по телеграм-ботам с ИИ.
                """
            
            prompt = f"""
{context}

Твоя задача:
1. Ответить на вопрос клиента профессионально и дружелюбно
2. Если есть контекст - использовать его для персонализированного ответа
3. Если вопрос касается услуг - объяснить их преимущества
4. Если вопрос технический - дать понятное объяснение
5. Быть полезным и информативным

ВАЖНО:
- Используй русский язык и эмодзи
- Будь конкретным и полезным
- Если не знаешь ответа - честно скажи об этом
- Предлагай связаться для детального обсуждения
            """
            
            # Вызываем ChatGPT
            response = await self._call_chatgpt(prompt)
            
            if response:
                logger.info(f"ChatGPT ответил на общий вопрос: {message[:50]}...")
                return response
            else:
                return self._generate_fallback_general_answer(message)
                
        except Exception as e:
            logger.error(f"Ошибка при ответе на общий вопрос: {e}")
            return self._generate_fallback_general_answer(message)
    
    async def recommend_services(self, user_data: Dict[str, Any]) -> Tuple[List[str], str]:
        """
        Рекомендует услуги на основе анализа диалога
        """
        try:
            # Анализируем текст для понимания потребностей
            analysis_text = f"""
            Компания: {user_data.get('company', '')}
            Назначение: {user_data.get('bot_purpose', '')}
            Уточнения: {' '.join(user_data.get('clarifications', []))}
            """
            
            # Формируем промпт для подбора услуг
            prompt = f"""
Ты - эксперт по подбору IT-услуг. Проанализируй потребности клиента и выбери релевантные услуги.

Информация о клиенте:
{analysis_text}

Доступные услуги (выбери только те, которые точно нужны):
{self._format_services_for_prompt()}

Твоя задача:
1. Проанализировать потребности клиента
2. Выбрать 3-7 наиболее релевантных услуг
3. Вернуть ТОЛЬКО список ID услуг через запятую, без объяснений

Пример ответа: google_sheets,payment_systems,analytics_dashboard
            """
            
            # Вызываем ChatGPT для подбора услуг
            response = await self._call_chatgpt(prompt)
            
            if response:
                # Парсим ответ и получаем список услуг
                service_ids = [s.strip() for s in response.split(',') if s.strip()]
                recommended_services = [s for s in service_ids if s in self.services]
                
                # Генерируем описание рекомендаций
                recommendations_text = await self._generate_recommendations_text(user_data, recommended_services)
                
                return recommended_services, recommendations_text
            else:
                # Fallback - базовые рекомендации
                fallback_services = ['google_sheets', 'telegram_channel', 'analytics_dashboard']
                fallback_text = self._generate_fallback_recommendations(user_data, fallback_services)
                return fallback_services, fallback_text
                
        except Exception as e:
            logger.error(f"Ошибка при подборе услуг: {e}")
            fallback_services = ['google_sheets', 'telegram_channel']
            fallback_text = self._generate_fallback_recommendations(user_data, fallback_services)
            return fallback_services, fallback_text
    
    async def generate_final_cost_breakdown(self, user_data: Dict[str, Any], selected_services: List[str]) -> str:
        """
        Генерирует финальную разбивку стоимости с выбранными услугами
        """
        try:
            contact_name = user_data.get('contact_name', 'Клиент')
            total_cost, services = calculate_total_cost(selected_services)
            
            # Группируем услуги по категориям
            categorized_services = {}
            for service in services:
                category = service['category']
                if category not in categorized_services:
                    categorized_services[category] = []
                categorized_services[category].append(service)
            
            # Формируем текст
            cost_text = f"""
💰 **Индивидуальная стоимость для {contact_name}**

💻 **Базовая разработка бота: 5000₽**
• Создание структуры и логики
• Настройка состояний и обработчиков  
• Интеграция с Telegram Bot API
• Развертывание на VPS-сервере
• Настройка SSL и мониторинга

🔧 **Рекомендуемые дополнения:**
"""
            
            for category, services_list in categorized_services.items():
                category_name = self.categories.get(category, category)
                cost_text += f"\n📋 **{category_name}:**\n"
                for service in services_list:
                    cost_text += f"• {service['name']} - {service['price']}₽\n"
            
            cost_text += f"""
💡 **Почему именно эти дополнения?**
Исходя из анализа вашего проекта, эти функции максимально подходят для ваших задач и значительно улучшат эффективность бота.

**Итого: {total_cost}₽**
            """.strip()
            
            return cost_text
            
        except Exception as e:
            logger.error(f"Ошибка при генерации стоимости: {e}")
            return "❌ Произошла ошибка при расчете стоимости. Попробуйте еще раз."
    
    def _format_services_for_prompt(self) -> str:
        """Форматирует услуги для промпта"""
        formatted = []
        for service_id, service in self.services.items():
            formatted.append(f"{service_id}: {service['name']} - {service['description']}")
        return '\n'.join(formatted)
    
    async def _generate_recommendations_text(self, user_data: Dict[str, Any], services: List[str]) -> str:
        """Генерирует текст рекомендаций"""
        contact_name = user_data.get('contact_name', 'Клиент')
        
        # Получаем информацию об услугах
        services_info = []
        for service_id in services:
            if service_id in self.services:
                service = self.services[service_id]
                services_info.append(f"• {service['name']} - {service['description']}")
        
        recommendations = f"""
🎯 **Персональные рекомендации для {contact_name}**

Исходя из анализа вашего проекта, я рекомендую следующие дополнения:

{chr(10).join(services_info)}

Эти функции идеально подходят для ваших задач и значительно улучшат эффективность бота! 🚀
        """.strip()
        
        return recommendations
    
    def _generate_fallback_recommendations(self, user_data: Dict[str, Any], services: List[str]) -> str:
        """Fallback рекомендации"""
        contact_name = user_data.get('contact_name', 'Клиент')
        
        services_info = []
        for service_id in services:
            if service_id in self.services:
                service = self.services[service_id]
                services_info.append(f"• {service['name']} - {service['description']}")
        
        return f"""
🎯 **Рекомендуемые дополнения для {contact_name}**

{chr(10).join(services_info)}

Эти базовые функции подойдут для большинства проектов! 🚀
        """.strip()
    
    async def _call_chatgpt(self, prompt: str) -> str:
        """Вызывает ChatGPT API"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты - опытный IT-консультант, который помогает клиентам заказывать телеграм-ботов. Отвечай кратко, профессионально и дружелюбно."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка при вызове ChatGPT: {e}")
            return None
    
    def _generate_fallback_analysis(self, user_data: Dict[str, Any]) -> str:
        """Fallback анализ"""
        contact_name = user_data.get('contact_name', 'Клиент')
        
        return f"""
Отлично, {contact_name}! Теперь я понимаю вашу задачу.

Для лучшего понимания ваших потребностей, у меня есть несколько вопросов:
• Планируете ли принимать оплату через бота?
• Нужны ли уведомления о новых заказах?
• Хотите ли отслеживать статистику по проектам?

Это поможет мне предложить оптимальный набор функций! 🚀
        """.strip()
    
    def _generate_fallback_general_answer(self, message: str) -> str:
        """Fallback ответ на общий вопрос"""
        return f"""
Спасибо за ваш вопрос! 🤖

К сожалению, сейчас у меня возникли технические сложности с обработкой вашего сообщения: "{message}"

Но я готов помочь! Для получения детальной консультации по телеграм-ботам с ИИ, используйте команду /start и мы создадим ваш проект с нуля.

Если у вас есть конкретные вопросы по технологиям или услугам, я постараюсь ответить на них! 🚀
        """.strip()

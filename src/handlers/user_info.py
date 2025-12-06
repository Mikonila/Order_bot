import logging
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, Any
from ..services.smart_consultant import SmartConsultant
from ..services.chat_logger import ChatLogger

router = Router()
logger = logging.getLogger(__name__)

# Инициализируем умного консультанта
consultant = SmartConsultant()

# Глобальная переменная для ChatLogger
chat_logger: ChatLogger = None

def set_chat_logger(logger_instance: ChatLogger):
    """Устанавливает экземпляр ChatLogger для логирования"""
    global chat_logger
    chat_logger = logger_instance

# Define states for collecting order information
class OrderStates(StatesGroup):
    waiting_for_company = State()
    waiting_for_bot_purpose = State()
    waiting_for_contact_name = State()
    waiting_for_clarifications = State()
    waiting_for_service_selection = State()
    waiting_for_additional_requests = State()
    waiting_for_final_decision = State()

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """Приветственное сообщение с кнопкой создания заказа"""
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    # Создаем клавиатуру с кнопкой
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Создать заказ", callback_data="create_order")]
    ])
    
    welcome_text = """
🤖 <b>Добро пожаловать в сервис разработки телеграм-ботов с ИИ!</b>

Мы создаем персональных ботов для вашего бизнеса, которые помогут:

📋 <b>Автоматизировать процессы:</b>
• Обработка заявок и заказов
• Консультации клиентов 24/7
• Прием платежей и оформление покупок
• Техническая поддержка

🤖 <b>Интегрировать ИИ-технологии:</b>
• Умные ответы на вопросы
• Анализ запросов клиентов
• Персонализированные рекомендации
• Автоматическое решение задач

⚡ <b>Повысить эффективность:</b>
• Сокращение времени обработки запросов
• Увеличение конверсии
• Улучшение качества обслуживания
• Снижение операционных расходов

Нажмите кнопку ниже, чтобы начать создание вашего бота:
    """.strip()
    
    response = await message.answer(welcome_text, parse_mode="HTML", reply_markup=keyboard)
    
    # Логируем ответ бота
    if chat_logger:
        await chat_logger.log_bot_response(welcome_text, message.from_user.first_name, message.from_user.id)

@router.message(Command("chatid"))
async def chat_id_handler(message: types.Message):
    """Показывает ID чата с детальной информацией о типе чата"""
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    chat_id = message.chat.id
    chat_type = message.chat.type
    user_id = message.from_user.id
    username = message.from_user.username or "Не указан"
    first_name = message.from_user.first_name or "Не указано"
    
    # Дополнительная информация для групповых чатов
    chat_title = getattr(message.chat, 'title', None)
    member_count = getattr(message.chat, 'member_count', None)
    
    info_text = f"""
🆔 <b>Информация о чате:</b>

📱 <b>Тип чата:</b> {chat_type}
💬 <b>ID чата:</b> <code>{chat_id}</code>
"""
    
    # Добавляем информацию специфичную для типа чата
    if chat_type == "private":
        info_text += f"""
👤 <b>ID пользователя:</b> <code>{user_id}</code>
👨‍💼 <b>Имя:</b> {first_name}
🔗 <b>Username:</b> @{username}
"""
    elif chat_type in ["group", "supergroup"]:
        info_text += f"""
👥 <b>Название группы:</b> {chat_title or "Не указано"}
📊 <b>Участников:</b> {member_count or "Неизвестно"}
👤 <b>Ваш ID:</b> <code>{user_id}</code>
👨‍💼 <b>Ваше имя:</b> {first_name}
🔗 <b>Ваш username:</b> @{username}

💡 <b>Используйте ID чата <code>{chat_id}</code> для отправки сообщений в эту группу!</b>
"""
    elif chat_type == "channel":
        info_text += f"""
📢 <b>Название канала:</b> {chat_title or "Не указано"}
👤 <b>Ваш ID:</b> {user_id}
👨‍💼 <b>Ваше имя:</b> {first_name}

💡 <b>Используйте ID канала <code>{chat_id}</code> для отправки сообщений в канал!</b>
"""
    
    info_text += """
💡 <b>Как использовать:</b>
• Для отправки сообщений в этот чат через API
• Для настройки уведомлений
• Для интеграции с внешними системами
    """.strip()
    
    response = await message.answer(info_text, parse_mode="HTML")
    
    # Логируем ответ бота
    if chat_logger:
        await chat_logger.log_bot_response(info_text, message.from_user.first_name, message.from_user.id)

@router.callback_query(F.data == "create_order")
async def create_order_handler(callback: types.CallbackQuery, state: FSMContext):
    """Начинаем создание заказа"""
    logger.info(f"Пользователь {callback.from_user.id} начал создание заказа")
    
    # Логируем нажатие кнопки
    if chat_logger:
        await chat_logger.log_callback_query(callback, "Создание заказа")
    
    await callback.message.edit_text("Отлично! Давайте создадим ваш персональный бот. 🚀")
    
    response_text = "🏢 <b>Расскажите о вашей компании</b>\n\nОпишите кратко:\n• Название компании\n• Сферу деятельности\n• Основные продукты или услуги\n\nЭто поможет нам лучше понять ваши потребности и предложить оптимальное решение."
    await callback.message.bot.send_message(callback.from_user.id, response_text, parse_mode="HTML")
    
    # Логируем ответ бота
    if chat_logger:
        await chat_logger.log_bot_response(response_text, callback.from_user.first_name, callback.from_user.id)
    
    await state.set_state(OrderStates.waiting_for_company)

@router.message(OrderStates.waiting_for_company)
async def company_handler(message: types.Message, state: FSMContext):
    """Обработка названия компании"""
    logger.info(f"Получено название компании: {message.text} от пользователя {message.from_user.id}")
    
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    await state.update_data(company=message.text)
    
    response_text = "🎯 <b>Опишите назначение вашего бота</b>\n\nРасскажите, какие задачи он должен решать. Например:\n• Обрабатывать заявки и заказы клиентов\n• Консультировать по продуктам и услугам\n• Решать технические проблемы и вопросы\n• Принимать платежи и оформлять покупки\n• Отвечать на часто задаваемые вопросы\n\nОпишите своими словами, что именно должен делать ваш бот!"
    await message.answer(response_text, parse_mode="HTML")
    
    # Логируем ответ бота
    if chat_logger:
        await chat_logger.log_bot_response(response_text, message.from_user.first_name, message.from_user.id)
    
    await state.set_state(OrderStates.waiting_for_bot_purpose)

@router.message(OrderStates.waiting_for_bot_purpose)
async def purpose_handler(message: types.Message, state: FSMContext):
    """Обработка назначения бота"""
    logger.info(f"Получено назначение бота: {message.text} от пользователя {message.from_user.id}")
    
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    await state.update_data(bot_purpose=message.text)
    
    response_text = "👤 <b>Как к вам обращаться?</b>\n\nУкажите ваше имя для дальнейшего общения и оформления заказа."
    await message.answer(response_text, parse_mode="HTML")
    
    # Логируем ответ бота
    if chat_logger:
        await chat_logger.log_bot_response(response_text, message.from_user.first_name, message.from_user.id)
    
    await state.set_state(OrderStates.waiting_for_contact_name)

@router.message(OrderStates.waiting_for_contact_name)
async def contact_name_handler(message: types.Message, state: FSMContext):
    """Обработка имени контакта"""
    logger.info(f"Получено имя контакта: {message.text} от пользователя {message.from_user.id}")
    
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    await state.update_data(contact_name=message.text)
    
    # Генерируем умный анализ от нейросети
    user_data = await state.get_data()
    analysis = await consultant.analyze_conversation(user_data)
    
    # Отправляем сообщение от нейросети без кнопок
    await message.answer(analysis, parse_mode="HTML")
    
    # Логируем ответ бота (анализ от нейросети)
    if chat_logger:
        await chat_logger.log_bot_response(analysis, message.from_user.first_name, message.from_user.id)
    
    # Переходим к сбору уточняющих вопросов
    await state.set_state(OrderStates.waiting_for_clarifications)

@router.message(OrderStates.waiting_for_clarifications)
async def clarifications_handler(message: types.Message, state: FSMContext):
    """Обработка ответов на уточняющие вопросы"""
    logger.info(f"Получен ответ на уточняющий вопрос: {message.text} от пользователя {message.from_user.id}")
    
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    # Сохраняем ответы на уточняющие вопросы
    current_data = await state.get_data()
    clarifications = current_data.get('clarifications', [])
    clarifications.append(message.text)
    await state.update_data(clarifications=clarifications)
    
    # Если это первый ответ, просим продолжить
    if len(clarifications) == 1:
        response_text = "Отлично! Есть ли еще что-то, что нужно уточнить для вашего проекта?"
        await message.answer(response_text, parse_mode="HTML")
        
        # Логируем ответ бота
        if chat_logger:
            await chat_logger.log_bot_response(response_text, message.from_user.first_name, message.from_user.id)
    else:
        # Анализируем все ответы и переходим к выбору сервисов
        response_text = "Спасибо за подробные ответы! Теперь давайте подберем оптимальный набор услуг для вашего бота. 📋"
        await message.answer(response_text, parse_mode="HTML")
        
        # Логируем ответ бота
        if chat_logger:
            await chat_logger.log_bot_response(response_text, message.from_user.first_name, message.from_user.id)
        
        # Переходим к выбору сервисов
        await state.set_state(OrderStates.waiting_for_service_selection)
        
        # Показываем доступные сервисы с кнопками
        await show_services_selection(message, state)

@router.callback_query(F.data == "place_order")
async def place_order_handler(callback: types.CallbackQuery, state: FSMContext):
    """Оформление заказа"""
    logger.info(f"Пользователь {callback.from_user.id} оформляет заказ")
    
    # Логируем нажатие кнопки
    if chat_logger:
        await chat_logger.log_callback_query(callback, "Оформление заказа")
    
    user_data = await state.get_data()
    recommended_services = user_data.get('recommended_services', [])
    
    # Показываем финальную стоимость
    cost_info = await consultant.generate_final_cost_breakdown(user_data, recommended_services)
    await callback.message.bot.send_message(callback.from_user.id, cost_info, parse_mode="HTML")
    
    # Логируем информацию о стоимости
    if chat_logger:
        await chat_logger.log_bot_response(cost_info, callback.from_user.first_name, callback.from_user.id)
    
    # Отправляем финальное сообщение
    final_message = """
🎉 <b>Заказ принят в работу!</b>

📞 <b>Свяжемся с вами в ближайшее время для уточнения деталей.</b>

📧 <b>Для связи:</b> @support_username
🌐 <b>Сайт:</b> example.com
⏰ <b>Время работы:</b> Пн-Пт, 9:00-18:00

Спасибо за доверие! 🚀
    """.strip()
    
    await callback.message.bot.send_message(callback.from_user.id, final_message, parse_mode="Markdown")
    
    # Логируем финальное сообщение
    if chat_logger:
        await chat_logger.log_bot_response(final_message, callback.from_user.first_name, callback.from_user.id)
    
    await state.clear()

@router.callback_query(F.data == "detailed_estimate")
async def detailed_estimate_handler(callback: types.CallbackQuery, state: FSMContext):
    """Детальная смета"""
    logger.info(f"Пользователь {callback.from_user.id} запросил детальную смету")
    
    # Логируем нажатие кнопки
    if chat_logger:
        await chat_logger.log_callback_query(callback, "Запрос детальной сметы")
    
    user_data = await state.get_data()
    recommended_services = user_data.get('recommended_services', [])
    
    # Показываем детальную стоимость
    cost_info = await consultant.generate_final_cost_breakdown(user_data, recommended_services)
    await callback.message.bot.send_message(callback.from_user.id, cost_info, parse_mode="HTML")
    
    # Логируем детальную смету
    if chat_logger:
        await chat_logger.log_bot_response(cost_info, callback.from_user.first_name, callback.from_user.id)
    
    # Создаем клавиатуру для оформления
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оформить заказ", callback_data="place_order")]
    ])
    
    final_message = "Готовы оформить заказ?"
    await callback.message.bot.send_message(callback.from_user.id, final_message, reply_markup=keyboard, parse_mode="HTML")
    
    # Логируем финальное сообщение
    if chat_logger:
        await chat_logger.log_bot_response(final_message, callback.from_user.first_name, callback.from_user.id)

@router.message(Command("status"))
async def status_handler(message: types.Message, state: FSMContext):
    """Показывает текущее состояние заказа"""
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    current_state = await state.get_state()
    user_data = await state.get_data()
    
    if not current_state:
        response_text = "Вы еще не начали создание заказа. Используйте /start для начала."
        await message.answer(response_text, parse_mode="Markdown")
        
        # Логируем ответ бота
        if chat_logger:
            await chat_logger.log_bot_response(response_text, message.from_user.first_name, message.from_user.id)
        return
    
    status_text = f"📊 <b>Статус заказа:</b>\n\n"
    
    if user_data.get('company'):
        status_text += f"🏢 <b>Компания:</b> {user_data['company']}\n"
    if user_data.get('bot_purpose'):
        status_text += f"🎯 <b>Назначение бота:</b> {user_data['bot_purpose']}\n"
    if user_data.get('contact_name'):
        status_text += f"👤 <b>Контакт:</b> {user_data['contact_name']}\n"
    
    if current_state == OrderStates.waiting_for_company.state:
        status_text += "\n⏳ <b>Ожидаю:</b> название компании"
    elif current_state == OrderStates.waiting_for_bot_purpose.state:
        status_text += "\n⏳ <b>Ожидаю:</b> описание функций бота"
    elif current_state == OrderStates.waiting_for_contact_name.state:
        status_text += "\n⏳ <b>Ожидаю:</b> ваше имя"
    elif current_state == OrderStates.waiting_for_clarifications.state:
        status_text += "\n⏳ <b>Ожидаю:</b> ответы на уточняющие вопросы"
    elif current_state == OrderStates.waiting_for_final_decision.state:
        status_text += "\n⏳ <b>Ожидаю:</b> решение по заказу"
    
    await message.answer(status_text, parse_mode="HTML")
    
    # Логируем ответ бота
    if chat_logger:
        await chat_logger.log_bot_response(status_text, message.from_user.first_name, message.from_user.id)

@router.message(Command("reset"))
async def reset_handler(message: types.Message, state: FSMContext):
    """Сбрасывает текущий заказ"""
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    await state.clear()
    response_text = "🔄 Заказ сброшен. Используйте /start для создания нового заказа."
    await message.answer(response_text, parse_mode="Markdown")
    
    # Логируем ответ бота
    if chat_logger:
        await chat_logger.log_bot_response(response_text, message.from_user.first_name, message.from_user.id)


@router.message(OrderStates.waiting_for_additional_requests)
async def additional_requests_handler(message: types.Message, state: FSMContext):
    """Обработка дополнительных пожеланий пользователя"""
    logger.info(f"=== additional_requests_handler вызван ===")
    logger.info(f"Получен ответ на вопрос о дополнительных пожеланиях: {message.text} от пользователя {message.from_user.id}")
    logger.info(f"Текущее состояние: {await state.get_state()}")
    logger.info(f"Тип сообщения: {type(message)}")
    logger.info(f"ID сообщения: {message.message_id}")
    logger.info(f"Дата сообщения: {message.date}")
    
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    user_data = await state.get_data()
    contact_name = user_data.get('contact_name', 'Клиент')
    logger.info(f"Контактное имя: {contact_name}")
    
    # Пересылаем сообщение вам (ID: 1339362869)
    logger.info(f"Пытаемся переслать сообщение на ID: 1339362869")
    
    # Формируем текст с полной информацией о пользователе
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    first_name = message.from_user.first_name or "без имени"
    last_name = message.from_user.last_name or ""
    
    forward_text = f"""🧑 <b>Новое сообщение от клиента:</b>

👤 <b>ID:</b> <code>{user_id}</code>
👤 <b>Username:</b> @{username}
👤 <b>Имя:</b> {first_name} {last_name}
👤 <b>Контакт:</b> {contact_name}

💬 <b>Сообщение:</b>
{message.text}"""
    
    # Отправляем сообщение (используем только message.bot для избежания дублирования)
    try:
        await message.bot.send_message(1339362869, forward_text, parse_mode="HTML")
        logger.info(f"✅ Сообщение переслано на ID: 1339362869 с полной информацией о пользователе")
    except Exception as e:
        logger.error(f"❌ Ошибка при пересылке: {e}")
        
        # Если не удалось отправить с Markdown, пробуем без него
        try:
            forward_text_plain = f"""🧑 Новое сообщение от клиента:

👤 ID: {user_id}
👤 Username: @{username}
👤 Имя: {first_name} {last_name}
👤 Контакт: {contact_name}

💬 Сообщение:
{message.text}"""
            await message.bot.send_message(1339362869, forward_text_plain)
            logger.info(f"✅ Сообщение переслано на ID: 1339362869 без Markdown")
        except Exception as e2:
            logger.error(f"❌ Ошибка при пересылке без Markdown: {e2}")
    
    # Сохраняем дополнительные пожелания
    await state.update_data(additional_requests=message.text)
    logger.info(f"Дополнительные пожелания сохранены: {message.text}")
    
    # Переходим к финальному этапу
    await state.set_state(OrderStates.waiting_for_final_decision)
    logger.info(f"Состояние изменено на: {await state.get_state()}")
    
    # Показываем финальные кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="pay_order")],
        [InlineKeyboardButton(text="❓ Связаться с программистом", callback_data="ask_programmer")]
    ])
    
    final_message = "Отлично! Теперь вы можете оплатить заказ или задать вопросы программисту."
    await message.answer(final_message, reply_markup=keyboard)
    logger.info(f"Финальные кнопки отправлены")
    
    # Логируем финальное сообщение
    if chat_logger:
        await chat_logger.log_bot_response(final_message, message.from_user.first_name, message.from_user.id)
    
    logger.info(f"=== additional_requests_handler завершен ===")


# Умный обработчик для всех текстовых сообщений с контекстом (только когда не в состоянии заказа)
@router.message(F.text)
async def smart_message_handler(message: types.Message, state: FSMContext):
    """Умный обработчик для всех текстовых сообщений с использованием ChatGPT"""
    # Проверяем, не находимся ли мы в процессе создания заказа
    current_state = await state.get_state()
    
    logger.info(f"smart_message_handler: получено сообщение от {message.from_user.id}, текущее состояние: {current_state}")
    
    # Если пользователь в процессе создания заказа, не обрабатываем здесь
    if current_state and current_state in [
        OrderStates.waiting_for_company.state,
        OrderStates.waiting_for_bot_purpose.state,
        OrderStates.waiting_for_contact_name.state,
        OrderStates.waiting_for_clarifications.state,
        OrderStates.waiting_for_service_selection.state,
        OrderStates.waiting_for_additional_requests.state,
        OrderStates.waiting_for_final_decision.state
    ]:
        # Пропускаем обработку - пусть FSM хендлеры обрабатывают
        logger.info(f"smart_message_handler: пропускаем обработку для состояния {current_state}")
        return
    
    logger.info(f"Получено текстовое сообщение: '{message.text}' от пользователя {message.from_user.id}")
    
    # Логируем сообщение пользователя
    if chat_logger:
        await chat_logger.log_user_message(message)
    
    # Получаем текущий контекст пользователя
    user_data = await state.get_data()
    
    # Используем ChatGPT для умного ответа с учетом контекста
    smart_response = await consultant.answer_general_question(message.text, user_data)
    
    # Отправляем ответ
    await message.answer(smart_response, parse_mode="HTML")
    
    # Логируем ответ бота
    if chat_logger:
        await chat_logger.log_bot_response(smart_response, message.from_user.first_name, message.from_user.id)

async def show_services_selection(message: types.Message, state: FSMContext):
    """Показывает доступные сервисы с кнопками для выбора"""
    from ..services.services_catalog import ADDITIONAL_SERVICES, BASE_BOT_COST, SERVICE_CATEGORIES
    
    # Создаем клавиатуру с сервисами
    keyboard_buttons = []
    
    # Добавляем кнопки для каждого сервиса
    for service_id, service in ADDITIONAL_SERVICES.items():
        button_text = f"{service['name']} - {service['price']}₽"
        keyboard_buttons.append([InlineKeyboardButton(
            text=button_text, 
            callback_data=f"select_service:{service_id}"
        )])
    
    # Добавляем кнопку "Продолжить"
    keyboard_buttons.append([InlineKeyboardButton(
        text="✅ Продолжить", 
        callback_data="continue_with_services"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    services_text = f"""
🔧 <b>Выберите дополнительные услуги для вашего бота:</b>

💻 <b>Базовая разработка: {BASE_BOT_COST}₽</b>
• Создание структуры и логики
• Настройка состояния и обработчиков
• Интеграция с Telegram Bot API
• Развертывание на VPS-сервере

📋 <b>Дополнительные услуги (выберите нужные):</b>
    """.strip()
    
    await message.answer(services_text, reply_markup=keyboard, parse_mode="HTML")
    
    # Логируем показ сервисов
    if chat_logger:
        await chat_logger.log_bot_response(services_text, message.from_user.first_name, message.from_user.id)

@router.callback_query(F.data.startswith("select_service:"))
async def service_selection_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора сервиса"""
    service_id = callback.data.split(":")[1]
    logger.info(f"Пользователь {callback.from_user.id} выбрал сервис: {service_id}")
    
    # Логируем выбор сервиса
    if chat_logger:
        await chat_logger.log_callback_query(callback, f"Выбор сервиса: {service_id}")
    
    # Получаем текущие выбранные сервисы
    user_data = await state.get_data()
    selected_services = user_data.get('selected_services', [])
    
    # Добавляем или убираем сервис
    if service_id in selected_services:
        selected_services.remove(service_id)
        await callback.answer(f"❌ Сервис убран из выбора")
        logger.info(f"Сервис {service_id} убран из выбора пользователя {callback.from_user.id}")
    else:
        selected_services.append(service_id)
        await callback.answer(f"✅ Сервис добавлен в выбор")
        logger.info(f"Сервис {service_id} добавлен в выбор пользователя {callback.from_user.id}")
    
    # Обновляем данные
    await state.update_data(selected_services=selected_services)
    
    # Обновляем текст кнопки
    from ..services.services_catalog import ADDITIONAL_SERVICES
    service = ADDITIONAL_SERVICES.get(service_id)
    if service:
        try:
            # Создаем новую клавиатуру с обновленными текстами
            new_keyboard_buttons = []
            
            # Проходим по всем сервисам и создаем кнопки заново
            for s_id, s_info in ADDITIONAL_SERVICES.items():
                if s_id in selected_services:
                    button_text = f"✅ {s_info['name']} - {s_info['price']}₽"
                else:
                    button_text = f"{s_info['name']} - {s_info['price']}₽"
                
                new_keyboard_buttons.append([InlineKeyboardButton(
                    text=button_text, 
                    callback_data=f"select_service:{s_id}"
                )])
            
            # Добавляем кнопку "Продолжить"
            new_keyboard_buttons.append([InlineKeyboardButton(
                text="✅ Продолжить", 
                callback_data="continue_with_services"
            )])
            
            new_keyboard = InlineKeyboardMarkup(inline_keyboard=new_keyboard_buttons)
            await callback.message.edit_reply_markup(reply_markup=new_keyboard)
        except Exception as e:
            logger.error(f"Ошибка при обновлении клавиатуры: {e}")
            # Просто отвечаем пользователю без обновления клавиатуры
            pass

@router.callback_query(F.data == "continue_with_services")
async def continue_with_services_handler(callback: types.CallbackQuery, state: FSMContext):
    """Продолжение после выбора сервисов"""
    # Логируем продолжение
    if chat_logger:
        await chat_logger.log_callback_query(callback, "Продолжение после выбора сервисов")
    
    user_data = await state.get_data()
    selected_services = user_data.get('selected_services', [])
    
    # Показываем выбранные сервисы и стоимость
    from ..services.services_catalog import calculate_total_cost, BASE_BOT_COST
    
    total_cost, services = calculate_total_cost(selected_services)
    
    # Формируем текст с выбранными сервисами
    services_text = f"""
💰 <b>Ваш выбор услуг:</b>

💻 <b>Базовая разработка: {BASE_BOT_COST}₽</b>
• Создание структуры и логики
• Настройка состояний и обработчиков
• Интеграция с Telegram Bot API
• Развертывание на VPS-сервере
"""
    
    if services:
        services_text += "\n🔧 <b>Выбранные дополнения:</b>\n"
        for service in services:
            services_text += f"• {service['name']} - {service['price']}₽\n"
    
    services_text += f"\n💵 <b>Итого: {total_cost}₽</b>"
    
    await callback.message.bot.send_message(callback.from_user.id, services_text, parse_mode="HTML")
    
    # Логируем информацию о выбранных сервисах
    if chat_logger:
        await chat_logger.log_bot_response(services_text, callback.from_user.first_name, callback.from_user.id)
    
    # Переходим к вопросу о дополнительных пожеланиях
    await state.set_state(OrderStates.waiting_for_additional_requests)
    logger.info(f"Пользователь {callback.from_user.id} переведен в состояние waiting_for_additional_requests")
    
    # Проверяем, что состояние действительно установилось
    current_state = await state.get_state()
    logger.info(f"Проверка состояния после set_state: {current_state}")
    
    additional_question = "Отлично! Есть ли что-то еще, что бы вы хотели добавить в бота?"
    await callback.message.bot.send_message(callback.from_user.id, additional_question, parse_mode="HTML")
    logger.info(f"Вопрос о дополнительных пожеланиях отправлен")
    
    # Логируем вопрос о дополнительных пожеланиях
    if chat_logger:
        await chat_logger.log_bot_response(additional_question, callback.from_user.first_name, callback.from_user.id)

@router.callback_query(F.data == "pay_order")
async def pay_order_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработка оплаты заказа"""
    # Логируем нажатие кнопки
    if chat_logger:
        await chat_logger.log_callback_query(callback, "Оплата заказа")
    
    # Реквизиты для оплаты
    payment_message = """
💳 <b>Оплата заказа</b>

Оплатить можно на реквизиты Т-банка, Сбербанка, Freedom Finance, Paypal, также принимается оплата криптовалютой. Свяжитесь со мной для получения реквизитов и обсуждения деталей.


🔗 <b>Telegram:</b> @helionstudio
📧 <b>Email для связи:</b> helionstudio20@protonmail.com
    """.strip()
    
    await callback.answer("💳 Отправляю информацию об оплате...")
    await callback.message.bot.send_message(callback.from_user.id, payment_message, parse_mode="HTML")
    
    # Логируем сообщение об оплате
    if chat_logger:
        await chat_logger.log_bot_response(payment_message, callback.from_user.first_name, callback.from_user.id)
    
    await state.clear()

@router.callback_query(F.data == "ask_programmer")
async def ask_programmer_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработка вопроса программисту"""
    # Логируем нажатие кнопки
    if chat_logger:
        await chat_logger.log_callback_query(callback, "Вопрос программисту")
    
    programmer_message = """
❓ <b>Вопрос программисту</b>

👨‍💻 <b>Свяжитесь с программистом:</b>
🔗 <b>Telegram:</b> @helionstudio
📧 <b>Email:</b> helionstudio20@protonmail.com

Он ответит на все ваши технические вопросы! 🚀
    """.strip()
    
    await callback.answer("❓ Отправляю контакты программиста...")
    await callback.message.bot.send_message(callback.from_user.id, programmer_message, parse_mode="HTML")
    
    # Логируем сообщение о связи с программистом
    if chat_logger:
        await chat_logger.log_bot_response(programmer_message, callback.from_user.first_name, callback.from_user.id)
    
    await state.clear()
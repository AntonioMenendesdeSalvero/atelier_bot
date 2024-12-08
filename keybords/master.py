from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models import get_all_services


def get_master_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='➕ Додати клієнта')],
            [KeyboardButton(text='📄 Переглянути записи')],
            [KeyboardButton(text='Внести суму доходу')]
        ],
        resize_keyboard=True
    )


def generate_services_keyboard():
    """Генерує клавіатуру з доступними послугами."""
    services = get_all_services()  # Отримує список послуг із бази даних

    if not services:
        # Якщо послуг немає, повертаємо повідомлення
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Список порожній", callback_data="empty")]]
        )

    # Генеруємо список кнопок для послуг
    keyboard = [
        [InlineKeyboardButton(text=service['name'], callback_data=f"service_{service['id']}")]
        for service in services
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

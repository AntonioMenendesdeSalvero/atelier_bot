from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router


def get_client_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📒 Записатися на прийом")],
            [KeyboardButton(text="👨‍💼 Переглянути профіль майстра")],
            [KeyboardButton(text="🔍 Переглянути прайс-лист")],  # Додана кнопка для прайс-листа
        ],
        resize_keyboard=True
    )


router = Router()


def generate_service_buttons(services):
    """
    Генерує інлайн-кнопки з послугами.
    :param services: Список послуг (кожна послуга — це словник з ключами 'name' та 'id').
    :return: Об'єкт InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardMarkup()
    for service in services:
        button = InlineKeyboardButton(
            text=service['name'],  # Назва послуги
            callback_data=f"service:{service['id']}"  # Унікальний ідентифікатор послуги
        )
        keyboard.add(button)
    return keyboard

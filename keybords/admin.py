from db.models import get_all_masters
from db.models import get_all_services
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='➕ Додати майстра')],
            [KeyboardButton(text='📄 Список майстрів')],
            [KeyboardButton(text='❌ Видалити майстра')],
            [KeyboardButton(text='📥 Додати послугу')],
            [KeyboardButton(text='📥 Видалити послугу')],
            [KeyboardButton(text='Зробити розсилку')],
            [KeyboardButton(text='📊 Сформувати звіт')],
            [KeyboardButton(text='☑️ Скачати базу')]
        ],
        resize_keyboard=True
    )


# Сформувати звіт
# генератор клавіатури майстрів
def generate_masters_keyboard():
    masters = get_all_masters()  # Отримуємо список майстрів із бази

    if not masters:
        # Якщо майстрів немає, створюємо клавіатуру з повідомленням "Список порожній"
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Список порожній")]],
            resize_keyboard=True
        )

    # Створюємо клавіатуру з іменами майстрів
    keyboard = [
        [KeyboardButton(text=master["name"])] for master in masters
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


# генератор клавіатури послуг

def generate_services_keyboard():
    services = get_all_services()  # Отримуємо список послуг із бази

    if not services:
        # Якщо послуг немає, створюємо клавіатуру з повідомленням "Список порожній"
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Список порожній")]],
            resize_keyboard=True
        )

    # Створюємо клавіатуру з назвами послуг
    keyboard = [
        [KeyboardButton(text=service["name"])] for service in services
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

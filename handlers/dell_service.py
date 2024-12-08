from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db.models import get_all_services, delete_service
from config import ADMIN_IDS

router = Router()


def generate_services_keyboard():
    """Генерує клавіатуру з усіма доступними послугами."""
    services = get_all_services()
    if not services:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Список порожній")]],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=service['name'])] for service in services],
        resize_keyboard=True
    )


@router.message(F.text == "📥 Видалити послугу")
async def delete_service_start(message: types.Message):
    """Надсилає список послуг для видалення."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас немає прав адміністратора!!.")
        return

    keyboard = generate_services_keyboard()
    await message.answer("Оберіть послугу, яку хочете видалити:", reply_markup=keyboard)


@router.message(F.text.in_([service['name'] for service in get_all_services()]))
async def process_delete_service(message: types.Message):
    """Обробляє вибір послуги для видалення."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас немає прав адміністратора!!.")
        return

    service_name = message.text.strip()  # Назва послуги, яку потрібно видалити
    if delete_service(service_name):
        await message.answer(f"Послугу '{service_name}' успішно видалено.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Послугу '{service_name}' не знайдено в базі.", reply_markup=ReplyKeyboardRemove())

    # Надсилаємо оновлений список послуг
    keyboard = generate_services_keyboard()
    await message.answer("Оновлений список послуг:", reply_markup=keyboard)

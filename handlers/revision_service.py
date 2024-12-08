from aiogram import Router, types, F
import sqlite3
from config import DATABASE_PATH

router = Router()


def format_service_list(services):
    """Форматує список послуг у гарний текст."""
    formatted_services = []
    for service in services:
        formatted_services.append(
            f"🛠 <b>{service['name']}</b>\n"
            f"💵 <i>Ціна:</i> {service['price']} грн\n"
            f"📝 <i>Опис:</i> {service['description']}\n"
            f"-----------------------------------"
        )
    return "\n\n".join(formatted_services)


def get_all_services():
    """Отримує всі послуги з бази даних."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT name, price, description FROM services")
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання послуг: {e}")


@router.message(F.text == "🔍 Переглянути прайс-лист")
async def view_price_list(message: types.Message):
    """Відправляє клієнту прайс-лист із усіма послугами."""
    try:
        services = get_all_services()  # Отримуємо всі послуги

        if not services:
            await message.answer("Список послуг порожній.")
            return

        # Форматуємо список послуг
        response = "\n\n".join(
            [
                f"🛠 <b>{service['name']}</b>\n"
                f"💵 <b>Ціна:</b> {service['price']} грн\n"
                f"📄 <b>Опис:</b> {service['description']}"
                for service in services
            ]
        )
        await message.answer(f"<b>Наш прайс-лист:</b>\n\n{response}", parse_mode="HTML")
    except RuntimeError as e:
        await message.answer(f"Сталася помилка: {e}")

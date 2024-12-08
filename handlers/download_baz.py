from aiogram import Router, types, F
from config import ADMIN_IDS
from db.db_utils import export_client_records_to_excel

import os

router = Router()


@router.message(F.text == "☑️ Скачати базу")
async def handle_download_database(message: types.Message):
    """Обробляє запит на скачування бази даних."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас немає прав для цієї дії.")
        return

    try:
        # Шлях до тимчасового файлу
        file_path = "client_records.xlsx"
        export_client_records_to_excel(file_path)

        # Надсилаємо файл адміністратору
        await message.answer_document(document=types.FSInputFile(file_path))

        # Видаляємо файл після відправлення
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"Помилка при експорті бази даних: {e}")

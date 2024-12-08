from aiogram import Router, types, F
from keybords.admin import generate_masters_keyboard
from db.models import get_master_by_name
from config import ADMIN_IDS

router = Router()


# Перегляд списку майстрів
@router.message(F.text == "📄 Список майстрів")
async def list_masters(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Оберіть майстра зі списку:", reply_markup=generate_masters_keyboard())
    else:
        await message.answer("У вас немає прав для цієї дії.")


@router.message(F.text == "👨‍💼 Переглянути профіль майстра")
async def list_masters(message: types.Message):
    await message.answer("Оберіть майстра зі списку:", reply_markup=generate_masters_keyboard())


# Перегляд профілю майстра
@router.message(lambda msg: get_master_by_name(msg.text))
async def view_master_profile(message: types.Message):
    master = get_master_by_name(message.text)

    if master:
        await message.answer_photo(
            photo=master['photo'],
            caption=f"👤 **Ім'я:** {master['name']}\n\n"
                    f"📋 **Опис:** {master['description']}"
        )
    else:
        await message.answer("Майстра з таким ім'ям не знайдено.")

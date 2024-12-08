from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from db.db_utils import delete_master
from keybords.admin import get_admin_keyboard
from states.del_master import DellMasterState
from db.models import get_master_data_for_del

router = Router()


# Кнопка для початку видалення майстра
@router.message(F.text == "❌ Видалити майстра")
async def delete_master_start(message: types.Message, state: FSMContext):
    await message.answer("Надішліть ID майстра, якого потрібно видалити:")
    await state.set_state(DellMasterState.waiting_for_delete_id)  # Перехід до стану видалення


# Обробка ID майстра для видалення
@router.message(DellMasterState.waiting_for_delete_id)
async def process_delete_master_id(message: types.Message, state: FSMContext):
    try:
        master_id = int(message.text)  # Отримуємо ID майстра
        # Логування ID
        print(f"Отриманий ID: {master_id}")

        # Перевірка наявності майстра з таким ID в базі
        master = get_master_data_for_del(master_id)

        if master:
            # Логування успішного пошуку майстра
            print(f"Знайдено майстра: {master}")
            # Видалення майстра
            delete_master(master_id)
            await message.answer(f"Майстра з ID {master_id} успішно видалено!", reply_markup=get_admin_keyboard())
        else:
            # Логування, що майстра не знайдено
            print(f"Майстра з ID {master_id} не знайдено")
            await message.answer(f"Майстра з ID {master_id} немає в списку зареєстрованих.",
                                 reply_markup=get_admin_keyboard())

        await state.clear()  # Очистити стан після операції
    except ValueError:
        await message.answer("Будь ласка, введіть числовий ID.")

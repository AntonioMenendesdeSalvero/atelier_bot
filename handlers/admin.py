from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keybords.admin import get_admin_keyboard
from states.add_master import AddMasterState
from db.db_utils import add_master

router = Router()


@router.message(F.text == "➕ Додати майстра")
async def add_master_start(message: types.Message, state: FSMContext):
    """Початок процесу додавання майстра."""
    await message.answer("Надішліть ID майстра:")
    await state.set_state(AddMasterState.waiting_for_id)


@router.message(AddMasterState.waiting_for_id)
async def process_master_id(message: types.Message, state: FSMContext):
    """Обробка ID майстра."""
    try:
        master_id = int(message.text.strip())
        # Зберігаємо ID у стані
        await state.update_data(master_id=master_id)
        await message.answer("Введіть ім'я майстра:")
        await state.set_state(AddMasterState.waiting_for_name)
    except ValueError:
        await message.answer("Будь ласка, введіть числовий ID.")


@router.message(AddMasterState.waiting_for_name)
async def process_master_name(message: types.Message, state: FSMContext):
    """Обробка імені майстра."""
    name = message.text.strip()
    await state.update_data(name=name)
    await message.answer("Надішліть фото майстра.")
    await state.set_state(AddMasterState.waiting_for_photo)


@router.message(AddMasterState.waiting_for_photo, F.photo)
async def process_master_photo(message: types.Message, state: FSMContext):
    """Обробка фото майстра."""
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await message.answer("Напишіть опис майстра:")
    await state.set_state(AddMasterState.waiting_for_description)


@router.message(AddMasterState.waiting_for_photo)
async def handle_invalid_photo(message: types.Message):
    """Обробка помилкового типу даних замість фото."""
    await message.answer("Будь ласка, надішліть фото.")


@router.message(AddMasterState.waiting_for_description)
async def process_master_description(message: types.Message, state: FSMContext):
    """Завершення додавання майстра."""
    data = await state.get_data()
    try:
        # Додаємо майстра до бази
        add_master(
            master_id=data['master_id'],
            name=data['name'],
            photo=data['photo'],
            description=message.text.strip()
        )
        await message.answer("Майстра успішно додано!", reply_markup=get_admin_keyboard())
        await state.clear()
    except Exception as e:
        await message.answer(f"Помилка під час додавання майстра: {e}")

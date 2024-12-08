from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from states.add_client import AddClientState
from db.db_utils import add_client
from db.models import get_all_services_for_m, get_master_data_for_id_mast

router = Router()


def is_master(user_id: int) -> bool:
    """Перевіряє, чи є користувач майстром."""
    master_data = get_master_data_for_id_mast(user_id)
    return bool(master_data)  # Повертає True, якщо користувач є майстром


def generate_master_services_keyboard():
    """Генерує клавіатуру з усіма доступними послугами для клієнта."""
    services = get_all_services_for_m()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=service['name'],
                                  callback_data=f"master_service_{service['id']}")]
            for service in services
        ]
    )


@router.message(F.text == "➕ Додати клієнта")
async def add_client_start(message: types.Message, state: FSMContext):
    """Початок додавання клієнта."""
    # Генеруємо клавіатуру для майстра
    keyboard = generate_master_services_keyboard()
    await message.answer("Оберіть послугу для клієнта:", reply_markup=keyboard)
    await state.set_state(AddClientState.waiting_for_service)


@router.callback_query(F.data.startswith("master_service_"))
async def process_master_service_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обробляє вибір послуги майстром."""
    try:
        # Перевіряємо формат callback_data
        data_parts = callback.data.split("_")
        if len(data_parts) != 3 or data_parts[0] != "master" or data_parts[1] != "service":
            await callback.answer("Невірний формат callback_data.", show_alert=True)
            return

        # Отримуємо ID послуги
        service_id = int(data_parts[2])
        await state.update_data(service_id=service_id)

        # Переходимо до наступного кроку
        await callback.message.edit_text("Введіть дату у форматі dd.mm.yy (наприклад, 12.10.2024):")
        await state.set_state(AddClientState.waiting_for_date)
        await callback.answer()
    except ValueError:
        await callback.answer("Сталася помилка під час обробки вибору послуги.", show_alert=True)
        print("Помилка обробки callback_data:", callback.data)


@router.message(AddClientState.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    """Зберігає дату та запитує час."""
    date = message.text.strip()
    await state.update_data(date=date)
    await message.answer("Введіть час у форматі hh:mm (наприклад, 12:00):")
    await state.set_state(AddClientState.waiting_for_time)


@router.message(AddClientState.waiting_for_time)
async def process_time(message: types.Message, state: FSMContext):
    """Зберігає час та запитує ім’я клієнта."""
    time = message.text.strip()
    await state.update_data(time=time)
    await message.answer("Введіть ім’я клієнта:")
    await state.set_state(AddClientState.waiting_for_name)


@router.message(AddClientState.waiting_for_name)
async def process_client_name(message: types.Message, state: FSMContext):
    """Зберігає ім’я клієнта та запитує телефон."""
    name = message.text.strip()
    await state.update_data(name=name)
    await message.answer("Введіть номер телефону клієнта:")
    await state.set_state(AddClientState.waiting_for_phone)


@router.message(AddClientState.waiting_for_phone)
async def process_client_phone(message: types.Message, state: FSMContext):
    """Зберігає всі дані та додає клієнта до бази."""
    phone = message.text.strip()
    data = await state.get_data()
    try:
        # Додаємо клієнта в базу
        add_client(
            name=data['name'],
            phone=phone,
            service_id=data['service_id'],
            date=data['date'],
            time=data['time'],
            master_id=message.from_user.id  # Додаємо ID майстра
        )
        await message.answer("Клієнта успішно додано!")
        await state.clear()
    except Exception as e:
        await message.answer(f"Помилка: {e}")

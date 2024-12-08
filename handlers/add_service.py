from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states.add_service import AddServiceState
from db.models import add_service, init_services_db

router = Router()
init_services_db()


# Початок додавання послуги
@router.message(F.text == "📥 Додати послугу")
async def add_service_start(message: types.Message, state: FSMContext):
    """Запитує назву послуги."""
    await message.answer("Введіть назву послуги:")
    await state.set_state(AddServiceState.waiting_for_service_name)


# Запит ціни послуги
@router.message(AddServiceState.waiting_for_service_name)
async def process_service_name(message: types.Message, state: FSMContext):
    """Зберігає назву послуги та запитує ціну."""
    service_name = message.text.strip()
    await state.update_data(service_name=service_name)
    await message.answer("Введіть ціну послуги:")
    await state.set_state(AddServiceState.waiting_for_service_price)


# Запит опису послуги
@router.message(AddServiceState.waiting_for_service_price)
async def process_service_price(message: types.Message, state: FSMContext):
    """Зберігає ціну послуги та запитує опис."""
    try:
        service_price = float(message.text.strip())
        await state.update_data(service_price=service_price)
        await message.answer("Введіть опис послуги:")
        await state.set_state(AddServiceState.waiting_for_service_description)
    except ValueError:
        await message.answer("Будь ласка, введіть коректну числову ціну.")


# Завершення додавання послуги
@router.message(AddServiceState.waiting_for_service_description)
async def process_service_description(message: types.Message, state: FSMContext):
    """Зберігає опис послуги та додає її до бази даних."""
    service_description = message.text.strip()
    data = await state.get_data()

    # Отримання даних із стану
    service_name = data.get("service_name")
    service_price = data.get("service_price")

    # Додавання до бази даних
    add_service(service_name, service_price, service_description)
    await message.answer(f"Послуга '{service_name}' успішно додана!")
    await state.clear()

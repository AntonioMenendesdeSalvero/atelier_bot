from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from db.models import get_records_by_date

router = Router()


class ViewRecordsState(StatesGroup):
    waiting_for_date = State()


@router.message(F.text == "📄 Переглянути записи")
async def view_records_start(message: types.Message, state: FSMContext):
    """
    Початок процесу перегляду записів.
    Запитує дату у форматі dd.mm.yy.
    """
    await message.answer("Введіть дату у форматі dd.mm.yy (наприклад, 12.10.2024):")
    await state.set_state(ViewRecordsState.waiting_for_date)


@router.message(ViewRecordsState.waiting_for_date)
async def process_view_records_date(message: types.Message, state: FSMContext):
    """
    Отримує записи на вказану дату.
    """
    date = message.text.strip()
    master_id = message.from_user.id  # ID майстра
    try:
        # Отримуємо всі записи для вказаного майстра та дати
        records = get_records_by_date(master_id, date)
        if not records:
            await message.answer("На цю дату немає записів.")
        else:
            # Формуємо повідомлення зі списком записів
            response = "\n\n".join(
                [
                    f"Клієнт: {record['name']}\n"
                    f"Телефон: {record['phone']}\n"
                    f"Час: {record['time']}\n"
                    f"Послуга: {record['service_name']}"
                    for record in records
                ]
            )
            await message.answer(f"Записи на {date}:\n\n{response}")
    except Exception as e:
        await message.answer(f"Помилка: {e}")
        print(f"Помилка у view_records: {e}")  # Логування помилки
    finally:
        await state.clear()

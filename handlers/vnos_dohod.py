from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from db.db_utils import add_income_record

router = Router()


class AddIncomeState(StatesGroup):
    waiting_for_date = State()
    waiting_for_income = State()


@router.message(F.text == "Внести суму доходу")
async def start_add_income(message: types.Message, state: FSMContext):
    """Початок процесу додавання доходу."""
    await message.answer("Вкажіть дату у форматі dd.mm.yyyy (наприклад, 12.12.2024):")
    await state.set_state(AddIncomeState.waiting_for_date)


@router.message(AddIncomeState.waiting_for_date)
async def add_income_date(message: types.Message, state: FSMContext):
    """Обробка введеної дати."""
    try:
        date = message.text.strip()
        await state.update_data(date=date)
        await message.answer("Вкажіть суму доходу за цей день:")
        await state.set_state(AddIncomeState.waiting_for_income)
    except ValueError:
        await message.answer("Некоректний формат дати. Спробуйте ще раз.")


@router.message(AddIncomeState.waiting_for_income)
async def add_income_value(message: types.Message, state: FSMContext):
    """Обробка введеної суми доходу."""
    try:
        income = float(message.text.strip())
        data = await state.get_data()
        date = data["date"]
        master_id = message.from_user.id  # ID майстра

        # Додаємо запис до бази
        add_income_record(master_id, date, income)

        await message.answer("Дохід успішно внесено!")
        await state.clear()
    except ValueError:
        await message.answer("Некоректний формат суми. Вкажіть число.")
    except Exception as e:
        await message.answer(f"Помилка: {e}")

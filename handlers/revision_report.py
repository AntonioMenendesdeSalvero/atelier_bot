from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from db.db_utils import calculate_income_for_period

router = Router()


class ReportIncomeState(StatesGroup):
    waiting_for_date_range = State()


@router.message(F.text == "📊 Сформувати звіт")
async def start_report(message: types.Message, state: FSMContext):
    """Початок формування звіту."""
    await message.answer("Вкажіть період у форматі dd.mm.yyyy - dd.mm.yyyy:")
    await state.set_state(ReportIncomeState.waiting_for_date_range)


@router.message(ReportIncomeState.waiting_for_date_range)
async def process_date_range(message: types.Message, state: FSMContext):
    """Формування звіту за вказаний період."""
    try:
        date_range = message.text.strip()
        start_date, end_date = map(str.strip, date_range.split("-"))

        # Розрахунок суми доходу
        total_income = calculate_income_for_period(start_date, end_date)

        await message.answer(
            f"Звіт за період {start_date} - {end_date}:\n"
            f"💵 Загальна сума доходу: {total_income} грн"
        )
        await state.clear()
    except ValueError:
        await message.answer("Некоректний формат дати. Спробуйте ще раз.")
    except Exception as e:
        await message.answer(f"Сталася помилка: {e}")

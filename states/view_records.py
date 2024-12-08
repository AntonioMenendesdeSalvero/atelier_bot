from aiogram.fsm.state import StatesGroup, State


class ViewRecordsState(StatesGroup):
    waiting_for_date = State()

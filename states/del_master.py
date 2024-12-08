from aiogram.fsm.state import StatesGroup, State


class DellMasterState(StatesGroup):
    waiting_for_delete_id = State()
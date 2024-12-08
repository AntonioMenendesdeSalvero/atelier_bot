from aiogram.fsm.state import StatesGroup, State

class AddMasterState(StatesGroup):
    waiting_for_id = State()
    waiting_for_name = State()
    waiting_for_photo = State()
    waiting_for_description = State()
    waiting_for_delete_id = State()

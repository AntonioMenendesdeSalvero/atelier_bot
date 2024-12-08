from aiogram.fsm.state import StatesGroup, State

class AddServiceState(StatesGroup):
    waiting_for_service_name = State()
    waiting_for_service_price = State()
    waiting_for_service_description = State()
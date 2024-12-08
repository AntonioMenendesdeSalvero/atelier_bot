from aiogram.fsm.state import StatesGroup, State



class ClientBookingState(StatesGroup):
    """Стани для запису клієнта."""
    waiting_for_service = State()
    waiting_for_master = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_contact = State()

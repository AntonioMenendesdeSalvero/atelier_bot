from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from config import ADMIN_IDS
from db.models import get_all_chat_ids

router = Router()


class BroadcastState(StatesGroup):
    waiting_for_broadcast_message = State()


@router.message(F.text == "Зробити розсилку")
async def start_broadcast(message: types.Message, state: FSMContext):
    """Ініціює процес створення розсилки."""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас немає прав для цієї дії.")
        return

    await message.answer("Надішліть повідомлення, яке потрібно розіслати.")
    await state.set_state(BroadcastState.waiting_for_broadcast_message)


@router.message(BroadcastState.waiting_for_broadcast_message)
async def handle_broadcast_message(message: types.Message, state: FSMContext):
    """Обробляє повідомлення для розсилки."""
    broadcast_message = message

    # Отримуємо всі ID чатів із бази
    chat_ids = get_all_chat_ids()

    success_count = 0
    fail_count = 0

    for chat_id in chat_ids:
        try:
            await message.bot.send_message(chat_id=chat_id, text=broadcast_message.text, parse_mode="HTML")
            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f"Помилка під час відправки до {chat_id}: {e}")

    await message.answer(f"Розсилка завершена!\nУспішно: {success_count}, Не вдалося: {fail_count}.")
    await state.clear()

from datetime import datetime, timedelta
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from db.models import get_master_data_for_del  # Функція для отримання списку послуг
from keybords.admin import get_admin_keyboard
from keybords.common import get_client_keyboard
from keybords.master import get_master_keyboard
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states.client_booking import ClientBookingState
from db.models import get_all_services, get_all_masters, get_service_name
from db.db_utils import add_client_record

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    """Обробка команди /start."""
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer("Привіт, адміністраторе! Оберіть дію:", reply_markup=get_admin_keyboard())
    elif get_master_data_for_del(user_id):
        await message.answer("Привіт, майстре! Ось ваші доступні дії:", reply_markup=get_master_keyboard())
    else:
        await message.answer("Привіт! Ви у вітальному повідомленні. Оберіть дію:", reply_markup=get_client_keyboard())


def generate_client_services_keyboard():
    """Генерує клавіатуру з усіма доступними послугами для клієнта."""
    services = get_all_services()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=service['name'], callback_data=f"client_service_{service['id']}")]
            for service in services
        ]
    )


@router.message(F.text == "📒 Записатися на прийом")
async def start_booking(message: types.Message, state: FSMContext):
    """Початок процесу запису клієнта."""
    # Генеруємо клавіатуру для клієнта
    keyboard = generate_client_services_keyboard()
    await message.answer("Оберіть послугу:", reply_markup=keyboard)
    await state.set_state(ClientBookingState.waiting_for_service)


def generate_masters_keyboard():
    """Генерує клавіатуру з усіма майстрами."""
    masters = get_all_masters()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=master['name'], callback_data=f"master_{master['id']}")]
            for master in masters
        ]
    )


@router.callback_query(F.data.startswith("client_service_"))
async def process_client_service_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обробляє вибір послуги клієнтом."""
    try:
        service_id = int(callback.data.split("_")[2])  # Отримуємо ID послуги
        await state.update_data(service_id=service_id)
        keyboard = generate_masters_keyboard()
        await callback.message.edit_text("Оберіть майстра:", reply_markup=keyboard)
        await state.set_state(ClientBookingState.waiting_for_master)
        await callback.answer()
    except (ValueError, IndexError) as e:
        await callback.answer("Сталася помилка під час обробки вибору послуги.")


def generate_dates_keyboard():
    """Генерує інлайн клавіатуру з датами на 7 днів вперед."""
    keyboard = []

    # Додаємо дати на 7 днів вперед
    today = datetime.now()
    for i in range(7):
        date = today + timedelta(days=i)
        date_text = date.strftime("%d.%m.%Y")
        keyboard.append([InlineKeyboardButton(text=date_text, callback_data=f"date_{date_text}")])

    # Додаємо кнопку для вибору іншої дати
    # keyboard.append([InlineKeyboardButton(text="Обрати іншу дату", callback_data="custom_date")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data.startswith("master_"))
async def process_master_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обробляє вибір майстра та запитує дату."""
    # Отримуємо ID майстра з callback_data
    master_record_id = int(callback.data.split("_")[1])  # Це поле `id`, а не `master_id`

    # Шукаємо майстра за ID в результатах get_all_masters()
    all_masters = get_all_masters()
    master = next((m for m in all_masters if m["id"] == master_record_id), None)

    if not master:
        await callback.answer("Майстра не знайдено!", show_alert=True)
        return

    master_id = master['master_id']  # Беремо `master_id` для Telegram
    print(f"Збережений master_id: {master_id} (з callback_data)")

    # Зберігаємо ID майстра у стан
    await state.update_data(master_id=master_id)

    # Генеруємо клавіатуру з датами
    keyboard = generate_dates_keyboard()
    await callback.message.edit_text("Оберіть дату:", reply_markup=keyboard)
    await state.set_state(ClientBookingState.waiting_for_date)
    await callback.answer()


def generate_times_keyboard():
    """Генерує клавіатуру з часом (09:00 до 18:00)."""
    times = [f"{hour}:00" for hour in range(9, 19)]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=time, callback_data=f"time_{time}")] for time in times
        ]
    )


@router.callback_query(F.data.startswith("date_"))
async def process_date_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обробляє вибір дати."""
    date = callback.data.split("_")[1]  # Отримуємо дату
    await state.update_data(date=date)
    keyboard = generate_times_keyboard()
    await callback.message.edit_text("Оберіть час:", reply_markup=keyboard)
    await state.set_state(ClientBookingState.waiting_for_time)
    await callback.answer()


@router.callback_query(F.data.startswith("time_"))
async def process_time_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обробляє вибір часу."""
    time = callback.data.split("_")[1]  # Отримуємо час
    await state.update_data(time=time)
    await callback.message.edit_text("Натисніть 'Поділитися контактом', щоб завершити запис.")
    await callback.message.answer("Натисніть кнопку, щоб поділитися своїм контактом.",
                                  reply_markup=types.ReplyKeyboardMarkup(
                                      keyboard=[
                                          [types.KeyboardButton(text="Поділитися контактом", request_contact=True)]
                                      ],
                                      resize_keyboard=True
                                  ))
    await state.set_state(ClientBookingState.waiting_for_contact)
    await callback.answer()


@router.message(ClientBookingState.waiting_for_contact, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    try:
        contact = message.contact
        user_id = contact.user_id
        if not user_id:
            await message.answer("Сталася помилка: не вдалося отримати ID користувача.")
            return

        data = await state.get_data()

        master_id = data.get("master_id")
        service_id = data.get("service_id")
        if not master_id or not service_id:
            await message.answer("Сталася помилка: не вдалося знайти майстра або послугу.")
            return

        # Надсилаємо майстру інформацію про запис із кнопкою
        await message.bot.send_message(
            chat_id=master_id,
            text=(
                f"Новий запис:\n"
                f"Ім'я: {contact.first_name}\n"
                f"Телефон: {contact.phone_number}\n"
                f"Дата: {data.get('date')}\n"
                f"Час: {data.get('time')}\n"
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Написати клієнту",
                            url=f"tg://user?id={contact.user_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Підтвердити запис",
                            callback_data=f"approve_booking|{contact.user_id}|{data.get('date')}|{data.get('time')}|{service_id}"
                        )
                    ]
                ]
            )
        )

        await message.answer("Ваші дані передані майстру. Очікуйте підтвердження.")
        await state.clear()
    except Exception as e:
        await message.answer(f"Сталася помилка: {e}")
        await state.clear()


@router.callback_query(F.data.startswith("approve_booking|"))
async def approve_booking(callback: types.CallbackQuery):
    """Підтверджує запис, додає до бази та повідомляє клієнта."""
    try:
        # Розбиваємо callback_data на частини
        parts = callback.data.split("|")
        if len(parts) != 5:
            await callback.answer("Сталася помилка: некоректні дані.", show_alert=True)
            return

        _, user_id, date, time, service_id = parts

        # Отримуємо ім'я клієнта з тексту повідомлення
        client_name = callback.message.text.split("\n")[1].split(": ")[1]
        master_id = callback.from_user.id  # ID майстра, який підтверджує запис

        # Отримуємо назву послуги
        service_name = get_service_name(int(service_id))

        if not service_name:
            await callback.answer("Сталася помилка: не вдалося знайти послугу.", show_alert=True)
            return

        # Додаємо запис до бази даних
        add_client_record(
            name=client_name,
            phone="Не вказано",
            service_id=int(service_id),
            date=date,
            time=time,
            master_id=master_id
        )

        # Відправляємо повідомлення клієнту
        await callback.message.bot.send_message(
            chat_id=int(user_id),
            text=(
                f"Ваш запис на {date}, {time} до ательє-салону «Успіх» підтверджено.\n"
                f"Чекаємо вас за адресою: Небесної Сотні 105 каб.409.\n"
                f"Контактний номер: 0931838307."
            )
        )

        # Оновлюємо текст заявки для майстра
        await callback.message.edit_text("Запис підтверджено.")
        await callback.answer("Запис підтверджено.")
    except Exception as e:
        await callback.answer(f"Сталася помилка: {e}", show_alert=True)

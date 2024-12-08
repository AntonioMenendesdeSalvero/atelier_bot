from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import (admin, common, saw_master, del_master, add_service,
                      dell_service, add_client_master, view_records, revision_service, revision_zvit,
                      vnos_dohod, download_baz, revision_report)
from db.models import init_clients_db, init_services_db
import logging
from db.db_utils import init_db, create_master_income_table
from db.models import init_interactions_table

# Ініціалізація таблиці interactions
init_interactions_table()

# Ініціалізація бази даних
init_db()
init_services_db()  # Ініціалізуємо таблицю послуг
init_clients_db()  # Ініціалізуємо таблицю клієнтів
create_master_income_table()  # створюємо таблицю майстрів

# Ініціалізація логування
logging.basicConfig(level=logging.INFO, filename='logs/bot.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Ініціалізація бази даних
init_db()

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Підключення роутерів
dp.include_router(add_client_master.router)  # додавання клієнта для майстра
dp.include_router(common.router)  # Загальні команди, наприклад, /start
dp.include_router(admin.router)  # Команди адміністратора
dp.include_router(saw_master.router)  # перегляд профілю
dp.include_router(del_master.router)  # видалити майстра
dp.include_router(add_service.router)  # додати послугу
dp.include_router(view_records.router)  # перегляд записів майстра
dp.include_router(dell_service.router)  # Видалення послуг
dp.include_router(revision_service.router)  # перегляд послуг
dp.include_router(revision_zvit.router)  # перегляд послуг
dp.include_router(revision_report.router)  # Додайте його до диспетчера
dp.include_router(vnos_dohod.router)  # Додайте його до диспетчера
dp.include_router(download_baz.router)  # Додайте його до диспетчера

if __name__ == "__main__":
    dp.run_polling(bot)

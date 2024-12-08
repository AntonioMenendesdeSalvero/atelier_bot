import sqlite3
from config import DATABASE_PATH
import logging
import pandas as pd

DATABASE_PATH = DATABASE_PATH  # Змініть на шлях до вашої бази даних


def get_connection():
    """Повертає об'єкт з'єднання з базою даних."""
    try:
        return sqlite3.connect(DATABASE_PATH)
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка підключення до бази даних: {e}")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Майстра успішно додано")


def add_master(master_id, name, photo, description):
    """Додає майстра до бази даних."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Перевіряємо, чи майстер уже існує
            cursor.execute("SELECT 1 FROM masters WHERE master_id = ?", (master_id,))
            if cursor.fetchone():
                raise ValueError("Майстер із таким ID уже існує.")
            # Додаємо нового майстра
            cursor.execute(
                "INSERT INTO masters (master_id, name, photo, description) VALUES (?, ?, ?, ?)",
                (master_id, name, photo, description)
            )
    except sqlite3.IntegrityError as e:
        raise ValueError("Помилка додавання майстра: " + str(e))


def get_masters(fields="name"):
    """Отримує список майстрів із бази даних."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        query = f"SELECT {fields} FROM masters"
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]


# функція для видалення майстра з бази
def delete_master(master_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM masters WHERE master_id = ?", (master_id,))
    conn.commit()
    conn.close()


def get_master_by_id(master_id: int):
    """
    Отримує дані майстра за його ID.
    :param master_id: ID майстра.
    :return: Дані майстра (dict) або None, якщо майстра немає в базі.
    """
    conn = sqlite3.connect("database.db")  # Замініть на шлях до вашої бази даних
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM masters WHERE id = ?", (master_id,))
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1]}
        return None
    finally:
        conn.close()


def is_master(user_id: int) -> bool:
    """
    Перевіряє, чи є користувач зареєстрованим майстром у базі даних.
    :param user_id: ID користувача.
    :return: True, якщо користувач є майстром, інакше False.
    """
    master = get_master_by_id(user_id)
    return master is not None


def add_client(name, phone, service_id, date, time, master_id):
    """Додає клієнта до бази з урахуванням ціни та назви послуги."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            # Отримуємо ціну та назву послуги
            cursor.execute("SELECT price, name FROM services WHERE id = ?", (service_id,))
            service_data = cursor.fetchone()
            if not service_data:
                raise RuntimeError("Не вдалося знайти послугу для обраного service_id.")

            service_price, service_name = service_data

            # Логування
            print(
                f"Додається запис: {name}, {phone}, {service_id}, {service_name}, {date}, {time}, {master_id}, {service_price}")

            # Додаємо клієнта до таблиці client_records
            cursor.execute('''
                INSERT INTO client_records (name, phone, service_id, service_name, date, time, master_id, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, service_id, service_name, date, time, master_id, service_price))
            conn.commit()

    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка додавання клієнта: {e}")


def debug_check_client_records():
    """Виводить усі записи з таблиці client_records для перевірки."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM client_records")
            rows = cursor.fetchall()
            print("Дані таблиці client_records:")
            for row in rows:
                print(row)
    except sqlite3.Error as e:
        print(f"Помилка читання таблиці client_records: {e}")


# debug_check_client_records()


def update_clients_table():
    """Оновлює структуру таблиці clients для додавання колонки master_id."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Створюємо нову таблицю з master_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                master_id INTEGER NOT NULL,
                FOREIGN KEY(service_id) REFERENCES services(id),
                FOREIGN KEY(master_id) REFERENCES masters(id)
            )
        ''')

        # Копіюємо дані зі старої таблиці, додаючи значення master_id = 0 (потім це можна оновити)
        cursor.execute('''
            INSERT INTO clients_new (id, name, phone, service_id, date, time, master_id)
            SELECT id, name, phone, service_id, date, time, 0 FROM clients
        ''')

        # Видаляємо стару таблицю
        cursor.execute('DROP TABLE clients')

        # Перейменовуємо нову таблицю на clients
        cursor.execute('ALTER TABLE clients_new RENAME TO clients')

        conn.commit()


def check_clients_table():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        print("Стовпці таблиці clients:")
        for column in columns:
            print(column)


def init_client_records_table():
    """Створює таблицю для записів клієнтів."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS client_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    master_id INTEGER NOT NULL
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка створення таблиці client_records: {e}")


def init_db():
    """Ініціалізує базу даних, створюючи необхідні таблиці."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Створення таблиці для записів клієнтів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS client_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    master_id INTEGER NOT NULL
                )
            ''')
            conn.commit()
    except Exception as e:
        raise RuntimeError(f"Помилка ініціалізації бази даних: {e}")


def add_client_record(name, phone, service_id, date, time, master_id):
    """Додає підтверджений запис клієнта до таблиці."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Отримання ціни послуги
            cursor.execute("SELECT price FROM services WHERE id = ?", (service_id,))
            service_price = cursor.fetchone()
            if not service_price:
                raise RuntimeError("Не вдалося знайти ціну для обраної послуги.")

            # Отримання назви послуги
            cursor.execute("SELECT name FROM services WHERE id = ?", (service_id,))
            service_name = cursor.fetchone()
            if not service_name:
                raise RuntimeError("Не вдалося знайти назву послуги.")

            # Додаємо запис
            cursor.execute('''
                INSERT INTO client_confirmed_records (name, phone, date, time, service_name, master_id, price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, date, time, service_name[0], master_id, service_price[0]))
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка додавання клієнта: {e}")


def create_master_income_table():
    """Створює таблицю для записів доходу майстрів, якщо вона не існує."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS master_income (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    master_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    income REAL NOT NULL,
                    FOREIGN KEY (master_id) REFERENCES masters(master_id)
                )
            """)
            conn.commit()
            print("Таблиця 'master_income' успішно створена.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка створення таблиці 'master_income': {e}")


# print(calculate_total_earnings('01.12.2024 - 31.12.2024'))
def add_income_record(master_id, date, income):
    """Додає запис про дохід у базу даних."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO master_income (master_id, date, income)
                VALUES (?, ?, ?)
            """, (master_id, date, income))
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка додавання доходу: {e}")


def calculate_income_for_period(start_date, end_date):
    """Розраховує загальний дохід за період."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(income)
                FROM master_income
                WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка розрахунку доходу: {e}")


def export_client_records_to_excel(file_path):
    """Експортує дані таблиці client_records у файл Excel."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            # Завантажуємо дані з таблиці client_records
            query = "SELECT * FROM client_records"
            df = pd.read_sql_query(query, conn)

            # Зберігаємо в Excel
            df.to_excel(file_path, index=False)
            print(f"Дані таблиці client_records успішно експортовані у файл: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Помилка експорту даних у Excel: {e}")

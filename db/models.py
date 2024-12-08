import sqlite3
from config import DATABASE_PATH


def get_connection():
    """Повертає підключення до бази даних."""
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    """Створює таблицю masters, якщо вона не існує."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS masters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,  -- Telegram ID майстра
                    name TEXT NOT NULL,                   -- Ім'я майстра
                    photo TEXT,                           -- Фото майстра
                    description TEXT                      -- Опис майстра
                )
            ''')
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка ініціалізації бази даних: {e}")


# з ним працювало
def get_all_masters():
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM masters")
            return [dict(master) for master in cursor.fetchall()]
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання майстрів: {e}")


# Отримання майстра за іменем
def get_master_by_name(name):
    """Повертає інформацію про майстра за його ім'ям."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM masters WHERE name = ?", (name,))
            master = cursor.fetchone()
            return dict(master) if master else None
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання майстра за ім'ям: {e}")


# Отримання майстра за ID
def get_master_data(master_id):
    """Повертає фото та опис майстра за його ID."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT photo, description FROM masters WHERE id = ?", (master_id,))
            master = cursor.fetchone()
            return {"photo": master[0], "description": master[1]} if master else None
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання даних майстра за ID: {e}")


# Функція для отримання майстра по master_id (який є унікальним)
def get_master_data_for_del(master_id):
    """Повертає фото та опис майстра за його master_id."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT photo, description FROM masters WHERE master_id = ?", (master_id,))
            master = cursor.fetchone()
            if master:
                return {"photo": master[0], "description": master[1]}
            else:
                return None
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання даних майстра за ID: {e}")


def delete_master(master_id):
    """Видаляє майстра за master_id."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM masters WHERE master_id = ?", (master_id,))
            conn.commit()
            return cursor.rowcount > 0  # True, якщо був видалений запис
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка видалення майстра: {e}")


def add_service(name, price, description):
    """Додає нову послугу до таблиці."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO services (name, price, description)
                VALUES (?, ?, ?)
            ''', (name, price, description))
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка додавання послуги: {e}")


def init_services_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )
        ''')
        conn.commit()


def get_services():
    """Отримати список послуг із бази даних."""
    connection = sqlite3.connect("atelier.db")
    cursor = connection.cursor()
    cursor.execute("SELECT name, price FROM services")  # Таблиця послуг
    services = [{"name": row[0], "price": row[1]} for row in cursor.fetchall()]
    connection.close()
    return services


def get_all_services():
    """Отримує список усіх доступних послуг."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM services")
        return [dict(service) for service in cursor.fetchall()]


def get_master_data_for_id_mast(master_id):
    """Перевіряє, чи є користувач майстром у базі."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM masters WHERE master_id = ?", (master_id,))
            return cursor.fetchone()  # Повертає запис про майстра або None
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання даних майстра: {e}")


def init_clients_db():
    """Ініціалізує таблицю clients, якщо вона ще не існує."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                master_id INTEGER NOT NULL,  -- Майстер, який створив запис
                FOREIGN KEY(service_id) REFERENCES services(id),
                FOREIGN KEY(master_id) REFERENCES masters(id)
            )
        ''')
        conn.commit()


def update_clients_table():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Створення нової таблиці з master_id
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

        # Копіювання даних із старої таблиці (заповнюємо master_id значенням за замовчуванням, наприклад, 0)
        cursor.execute('''
            INSERT INTO clients_new (id, name, phone, service_id, date, time, master_id)
            SELECT id, name, phone, service_id, date, time, 0 FROM clients
        ''')

        # Видалення старої таблиці
        cursor.execute('DROP TABLE clients')

        # Перейменування нової таблиці
        cursor.execute('ALTER TABLE clients_new RENAME TO clients')

        conn.commit()


def get_records_by_date(master_id, date):
    """
    Отримує всі записи (внесені вручну і підтверджені клієнтами) для конкретного майстра на певну дату,
    з інформацією про послуги.
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
            SELECT name, phone, time, service_name
            FROM client_records
            WHERE master_id = ? AND date = ?

            UNION ALL

            SELECT name, phone, time, service_name
            FROM client_confirmed_records
            WHERE master_id = ? AND date = ?

            UNION ALL

            SELECT clients.name, clients.phone, clients.time, services.name as service_name
            FROM clients
            JOIN services ON clients.service_id = services.id
            WHERE clients.master_id = ? AND clients.date = ?

            ORDER BY time
            """
            cursor.execute(query, (master_id, date, master_id, date, master_id, date))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання записів: {e}")


def delete_service(service_name: str) -> bool:
    """Видаляє послугу з бази за її назвою. Повертає True, якщо успішно, інакше False."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM services WHERE name = ?", (service_name,))
            conn.commit()
            return cursor.rowcount > 0  # Перевіряємо, чи була видалена хоча б одна послуга
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка видалення послуги: {e}")


def get_service_name(service_id):
    """Отримує назву послуги за її ID."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM services WHERE id = ?", (service_id,))
        result = cursor.fetchone()
        return result[0] if result else None


def get_all_services_for_m():
    """Отримує список усіх доступних послуг."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM services")
        return [dict(service) for service in cursor.fetchall()]


def get_all_services_rev():
    """Отримує всі послуги з бази даних."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT name, price, description FROM services")
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання послуг: {e}")


def add_client(name, phone, service_id, date, time, master_id):
    """Додає запис клієнта до таблиці."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Отримання ціни послуги
            cursor.execute("SELECT price FROM services WHERE id = ?", (service_id,))
            service_price = cursor.fetchone()
            if not service_price:
                raise RuntimeError("Не вдалося знайти ціну для обраної послуги.")

            # Додаємо запис
            cursor.execute('''
                INSERT INTO client_records (name, phone, service_id, date, time, master_id, price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, service_id, date, time, master_id, service_price[0]))
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка додавання клієнта: {e}")


def init_users_table():
    """Ініціалізує таблицю для збереження Telegram ID користувачів."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL UNIQUE
            )
        ''')
        conn.commit()


init_users_table()


def get_all_chat_ids():
    """
    Отримує список усіх chat_id, які взаємодіяли з ботом.
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT chat_id FROM interactions")  # Таблиця `interactions` має містити поле `chat_id`
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка отримання chat_id: {e}")


def save_chat_id(chat_id):
    """
    Зберігає chat_id у таблицю interactions.
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO interactions (chat_id)
                VALUES (?)
            ''', (chat_id,))
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка збереження chat_id: {e}")


def init_interactions_table():
    """
    Створює таблицю interactions для зберігання chat_id, якщо вона не існує.
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL UNIQUE,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Таблиця interactions успішно створена.")
    except sqlite3.Error as e:
        raise RuntimeError(f"Помилка створення таблиці interactions: {e}")

import logging
from typing import Optional, Dict

from asyncpg_lite import DatabaseManager
from sqlalchemy import BigInteger, Integer, Boolean, TIMESTAMP

USERS_TABLE = "users_reg"


class PostgresHandler:
    def __init__(
        self,
        deletion_password: str,
        db_url: Optional[str] = None,
        expire_on_commit: bool = True,
        echo: bool = False,
        log_level: int = logging.INFO,
        auth_params: Optional[Dict[str, str]] = None,
    ):
        self.pg_db = DatabaseManager(
            deletion_password, db_url, expire_on_commit, echo, log_level, auth_params
        )

    async def create_table_users(self, table_name=USERS_TABLE):
        async with self.pg_db as manager:
            columns = [
                {
                    "name": "user_id",
                    "type": BigInteger,
                    "options": {"primary_key": True, "autoincrement": False},
                },
                {"name": "subscribed", "type": Boolean},
                {"name": "progress", "type": Integer},
                {"name": "date_reg", "type": TIMESTAMP},
            ]

            await manager.create_table(table_name=table_name, columns=columns)

    async def get_user_data(self, user_id: int, table_name=USERS_TABLE):
        async with self.pg_db as manager:
            user_info = await manager.select_data(
                table_name=table_name, where_dict={"user_id": user_id}, one_dict=True
            )
            if user_info:
                return user_info
            else:
                return None

    async def insert_user(self, user_data: dict, table_name=USERS_TABLE):
        async with self.pg_db as manager:
            await manager.insert_data_with_update(
                table_name=table_name,
                records_data=user_data,
                conflict_column="user_id",
                update_on_conflict=False,
            )


# import sqlite3
# __DATABASE_NAME = "users.db"

# def create_connection():
#     """Создает подключение к базе данных SQLite."""
#     conn = None
#     try:
#         conn = sqlite3.connect(__DATABASE_NAME)
#     except sqlite3.Error as e:
#         print(f"Ошибка подключения к базе данных: {e}")
#     return conn

# def create_table():
#     """Создает таблицу users, если она не существует."""
#     conn = create_connection()
#     if conn is not None:
#         try:
#             cursor = conn.cursor()
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS users (
#                     user_id INTEGER PRIMARY KEY,
#                     subscribed INTEGER DEFAULT 0,
#                     progress INTEGER DEFAULT 0,
#                     time_preference TEXT DEFAULT '12:00'
#                 )
#             """)
#             conn.commit()
#         except sqlite3.Error as e:
#             print(f"Ошибка создания таблицы: {e}")
#         finally:
#             conn.close()

# def subscribe_user(user_id):
#     """Подписывает пользователя на рассылку."""
#     conn = create_connection()
#     if conn is not None:
#         try:
#             cursor = conn.cursor()
#             cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
#             cursor.execute("UPDATE users SET subscribed = 1 WHERE user_id = ?", (user_id,))
#             conn.commit()
#         except sqlite3.Error as e:
#             print(f"Ошибка подписки пользователя: {e}")
#         finally:
#             conn.close()

# def unsubscribe_user(user_id):
#     """Отписывает пользователя от рассылки."""
#     conn = create_connection()
#     if conn is not None:
#         try:
#             cursor = conn.cursor()
#             cursor.execute("UPDATE users SET subscribed = 0 WHERE user_id = ?", (user_id,))
#             conn.commit()
#         except sqlite3.Error as e:
#             print(f"Ошибка отписки пользователя: {e}")
#         finally:
#             conn.close()

# def is_user_subscribed(user_id):
#     """Проверяет, подписан ли пользователь на рассылку."""
#     conn = create_connection()
#     if conn is not None:
#         try:
#             cursor = conn.cursor()
#             cursor.execute("SELECT subscribed FROM users WHERE user_id = ?", (user_id,))
#             result = cursor.fetchone()
#             if result:
#                 return result[0] == 1
#             else:
#                 return False  # Пользователь не найден в базе данных
#         except sqlite3.Error as e:
#             print(f"Ошибка проверки подписки: {e}")
#             return False
#         finally:
#             conn.close()
#     return False

# def get_all_subscribed_users():
#     """Возвращает список user_id всех подписанных пользователей."""
#     conn = create_connection()
#     if conn is not None:
#         try:
#             cursor = conn.cursor()
#             cursor.execute("SELECT user_id FROM users WHERE subscribed = 1")
#             users = [row[0] for row in cursor.fetchall()]
#             return users
#         except sqlite3.Error as e:
#             print(f"Ошибка получения списка пользователей: {e}")
#             return []
#         finally:
#             conn.close()
#     return []

# def get_user_time_preference(user_id):
#     """Получает предпочтительное время рассылки для пользователя."""
#     conn = create_connection()
#     if conn is not None:
#         try:
#             cursor = conn.cursor()
#             cursor.execute("SELECT time_preference FROM users WHERE user_id = ?", (user_id,))
#             result = cursor.fetchone()
#             if result:
#                 return result[0]
#             else:
#                 return '09:00'  # Время по умолчанию
#         except sqlite3.Error as e:
#             print(f"Ошибка получения времени: {e}")
#             return '09:00'
#         finally:
#             conn.close()
#     return '09:00'

# def set_user_time_preference(user_id, time_preference):
#     """Устанавливает предпочтительное время рассылки для пользователя."""
#     conn = create_connection()
#     if conn is not None:
#         try:
#             cursor = conn.cursor()
#             cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
#             cursor.execute("UPDATE users SET time_preference = ? WHERE user_id = ?", (time_preference, user_id))
#             conn.commit()
#         except sqlite3.Error as e:
#             print(f"Ошибка установки времени: {e}")
#         finally:
#             conn.close()


# # Создаем таблицу при запуске
# create_table()

# if __name__ == '__main__':
#     # Пример использования
#     user_id = 12345
#     subscribe_user(user_id)
#     print(f"Пользователь {user_id} подписан: {is_user_subscribed(user_id)}")
#     print(f"Предпочтительное время пользователя {user_id}: {get_user_time_preference(user_id)}")
#     set_user_time_preference(user_id, "10:30")
#     print(f"Новое время пользователя {user_id}: {get_user_time_preference(user_id)}")
#     unsubscribe_user(user_id)
#     print(f"Пользователь {user_id} подписан: {is_user_subscribed(user_id)}")

import logging
from typing import Optional, Dict

from asyncpg_lite import DatabaseManager
from sqlalchemy import TEXT, BigInteger, Integer, Boolean, TIMESTAMP

USERS_TABLE = "users_reg"
CONTENT_TABLE = "content_reg"
ACTIVITIES_TABLE = "activities_reg"


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

    async def create_table_content(self, table_name=CONTENT_TABLE):
        async with self.pg_db as manager:
            columns = [
                {
                    "name": "content_id",
                    "type": BigInteger,
                    "options": {"primary_key": True, "autoincrement": True},
                },
                {"name": "day_id", "type": BigInteger},
                {"name": "text", "type": TEXT},
                {"name": "audio", "type": TEXT, "options": {"nullable": True}},
                {"name": "photo", "type": TEXT, "options": {"nullable": True}},
            ]
        await manager.create_table(table_name=table_name, columns=columns)

    async def create_table_activities(self, table_name=ACTIVITIES_TABLE):
        async with self.pg_db as manager:
            columns = [
                {
                    "name": "content_id",
                    "type": BigInteger,
                    "options": {"primary_key": True, "autoincrement": True},
                },
                {"name": "day_id", "type": BigInteger},
                {"name": "text", "type": TEXT},
                {"name": "audio", "type": TEXT, "options": {"nullable": True}},
                {"name": "photo", "type": TEXT, "options": {"nullable": True}},
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

    async def subscribe_user(
        self, user_id: int, need_subscribe: bool, table_name=USERS_TABLE
    ):
        async with self.pg_db as manager:
            await manager.insert_data_with_update(
                table_name=table_name,
                records_data={"user_id": user_id, "subscribed": need_subscribe},
                conflict_column="user_id",
                update_on_conflict=True,
            )

    async def remove_content(self, day: int, table_name=CONTENT_TABLE):
        async with self.pg_db as manager:
            await manager.delete_data(table_name=table_name, where_dict={"day_id": day})

    async def insert_content(self, content_data: dict, table_name=CONTENT_TABLE):
        async with self.pg_db as manager:
            await manager.insert_data_with_update(
                table_name=table_name,
                records_data=content_data,
                conflict_column="day_id",
                update_on_conflict=False,
            )

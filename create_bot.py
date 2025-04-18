import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv

from aiogram.fsm.storage.redis import RedisStorage

from db_handler.db_class import PostgresHandler

logger = logging.getLogger(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


pg_db = PostgresHandler(
    db_url=os.getenv("PG_LINK"), deletion_password=os.getenv("PG_ROOT_PASS")
)

storage = RedisStorage.from_url(os.getenv("REDIS_LINK"))

admins_var: str = os.getenv("ADMINS")
admins = set(
    [int(admin_id) for admin_id in admins_var.split(",")] if admins_var else []
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=storage)

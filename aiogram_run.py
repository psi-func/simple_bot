import asyncio
import aioschedule as schedule

from create_bot import bot, dp, pg_db
from handlers.start import start_router
from handlers.common import common_router

async def main():
    # TODO: add schedule
    try:
        await pg_db.create_table_users()

        dp.include_router(common_router)
        dp.include_router(start_router)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

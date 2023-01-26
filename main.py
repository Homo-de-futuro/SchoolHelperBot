from aiogram import executor

from handlers import user
from run_bot import dp, bot, scheduler
from SQL.db_start import sql_start


async def on_startup(_):
    print('---Start')
    sql_start()


if __name__ == '__main__':
    
    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
from handlers import (register_handler_add_post, register_handler_logout,
                      register_handlers_common, register_handlers_login, 
                      register_handlers_register, register_handlers_send_posts)
from aiogram import Bot, Dispatcher, executor
from data.db_session import global_init
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = ''

global_init("db/database.sqlite3")
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

if __name__ == '__main__':
    register_handlers_common(dp)
    register_handlers_register(dp)
    register_handlers_login(dp)
    register_handler_logout(dp)
    register_handlers_send_posts(dp)
    register_handler_add_post(dp)
    executor.start_polling(dp, skip_updates=True)

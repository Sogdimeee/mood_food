
import asyncio
import logging
from static.config import bot, dp
from commands.start import start_router
from commands.fsm import fsm_router

async def on_startup(dispatcher):

    print('Бот вышел в онлайн')


async def main():
    dp.include_router(start_router)
    dp.include_router(fsm_router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    dp.startup.register(on_startup)
    asyncio.run(main())
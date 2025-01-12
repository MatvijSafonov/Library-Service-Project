import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers.handlers import router
from conf.settings import setup_logging, bot


storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Function for setting commands
async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Start working with bot"),
        BotCommand(command="menu", description="Show menu"),
        BotCommand(command="reg", description="Register"),
        BotCommand(command="login", description="Login"),
        BotCommand(command="contacts", description="Contact information"),
        BotCommand(command="help", description="Get help"),
    ]
    await bot.set_my_commands(commands)


async def reset_bot(bot: Bot) -> None:
    # Delete webhook and clear updates queue
    await bot.delete_webhook(drop_pending_updates=True)
    # Delete bot commands
    await bot.delete_my_commands()
    # Clear FSM storage - using close instead of clear
    await storage.close()


async def main() -> None:
    try:
        dp.include_router(router)
        setup_logging()

        # First clear old updates
        await bot.delete_webhook(drop_pending_updates=True)

        # Set bot commands
        await set_commands(bot)

        # Start polling with ignored updates
        await dp.start_polling(bot, allowed_updates=[], skip_updates=True)
    finally:
        await reset_bot(bot)
        await storage.close()
        await bot.session.close()
        setup_logging()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        setup_logging()

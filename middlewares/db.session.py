from aiogram.types import TelegramObject


class DbSessionMiddleware:
    def __init__(self, session_generator):
        self.session_generator = session_generator

    async def __call__(self, handler, event: TelegramObject, data: dict):
        async with self.session_generator() as session:
            data["session"] = session
            return await handler(event, data)

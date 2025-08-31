from bot.main import main, dp, bot
import asyncio
from bot.utils import get_time

from bot.settings import (
    USE_WEBHOOK,
    WEB_SERVER_HOST,
    WEB_SERVER_PORT,
    WEBHOOK_PATH,
    WEBHOOK_SECRET,
)

if __name__ == "__main__":
    if not USE_WEBHOOK:
        asyncio.run(main())
    else:
        from aiohttp import web
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


        app = web.Application()

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET,
        )

        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        # async def cleanup(app):
        #     await shutdown()
            
        # app.on_cleanup.append(cleanup)

        try:
            web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
        except KeyboardInterrupt:
            print(f"{get_time()} - Received interrupt signal")
        # finally:
        #     loop = asyncio.get_event_loop()
        #     if not loop.is_closed():
        #         loop.run_until_complete(cleanup())
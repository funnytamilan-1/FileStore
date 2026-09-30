import asyncio
from bot import Bot
from config import settings
from web.server import create_server

async def main():
    bot=Bot(); await bot.initialize(); health=None
    try:
        await bot.start(); health=await create_server(bot,settings.port); await asyncio.Event().wait()
    finally:
        if health: await health.cleanup()
        try: await bot.stop()
        finally: await bot.close_services()

if __name__=="__main__": asyncio.run(main())

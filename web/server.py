import time
from aiohttp import web

async def create_server(bot,port:int):
    async def health(_): return web.json_response({"status":"ok","bot":"running","uptime":int(time.monotonic()-bot.started)})
    async def ping(_): return web.json_response({"status":"ok"})
    app=web.Application(); app.router.add_get("/",health); app.router.add_get("/health",health); app.router.add_get("/ping",ping)
    runner=web.AppRunner(app); await runner.setup(); await web.TCPSite(runner,"0.0.0.0",port).start(); return runner

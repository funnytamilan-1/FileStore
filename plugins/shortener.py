from helper.shortener import Shortener

async def shorten_link(client, url: str) -> str | None:
    if not client.shortener_enabled:
        return None
    try:
        return await Shortener(client.shortener_url, client.shortener_api).shorten(url)
    except Exception as exc:
        client.LOGGER(__name__, client.name).warning("shortener request failed: %s", exc)
        return None

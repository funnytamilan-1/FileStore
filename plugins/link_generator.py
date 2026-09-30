from pyrogram import Client,filters
from helper.shortener import Shortener

@Client.on_message(filters.command(["genlink","link"]) & filters.private)
async def genlink(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    reply=message.reply_to_message
    if not reply or not await client.db_channels.allowed(reply.chat.id): return await message.reply_text("Reply to a message in an enabled storage channel.")
    direct=f"https://t.me/{client.username}?start={client.payload_codec.encode('file',reply.chat.id,[reply.id])}"
    short=None
    if client.shortener_enabled and not (client.shortener_for_admins and message.from_user.id in client.admins):
        try: short=await Shortener(client.shortener_url,client.shortener_api).shorten(direct)
        except Exception as exc: client.LOGGER(__name__,client.name).warning("shortener failed: %s",exc)
    await message.reply_text("File Link\n\nDirect:\n"+direct+(f"\n\nShort:\n{short}" if short else ""),disable_web_page_preview=True)

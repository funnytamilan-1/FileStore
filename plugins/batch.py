from pyrogram import Client,filters
from config import settings
from helper.validators import ids_range
from helper.shortener import Shortener

@Client.on_message(filters.command("batch") & filters.private)
async def batch(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    args=message.command[1:]
    if len(args)==3:
        try: cid=int(args[0]); ids=ids_range(int(args[1]),int(args[2]),settings.batch_max)
        except (ValueError,TypeError): return await message.reply_text("Usage: /batch <channel_id> <start_id> <end_id>")
    elif message.reply_to_message: cid=message.reply_to_message.chat.id; ids=[message.reply_to_message.id]
    else: return await message.reply_text("Usage: /batch <channel_id> <start_id> <end_id>")
    if not await client.db_channels.allowed(cid): return await message.reply_text("Storage channel is not configured.")
    direct=f"https://t.me/{client.username}?start={client.payload_codec.encode('batch',cid,ids)}"; short=None
    if client.shortener_enabled and not (client.shortener_for_admins and message.from_user.id in client.admins):
        try: short=await Shortener(client.shortener_url,client.shortener_api).shorten(direct)
        except Exception as exc: client.LOGGER(__name__,client.name).warning("batch shortener failed: %s",exc)
    text=f"Batch Link\n\nDirect:\n{direct}"+(f"\n\nShort:\n{short}" if short else "")
    await message.reply_text(text,disable_web_page_preview=True)

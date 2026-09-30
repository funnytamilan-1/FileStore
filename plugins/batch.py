from pyrogram import Client,filters
from config import settings
from helper.validators import ids_range
from helper.shortener import Shortener

async def forwarded_source(message):
    if message.forward_from_chat and message.forward_from_message_id:
        return message.forward_from_chat.id, message.forward_from_message_id
    return None

async def make_link(client,message,cid,ids):
    direct=f"https://t.me/{client.username}?start={client.payload_codec.encode('batch',cid,ids)}"
    short=None
    if client.shortener_enabled and not (client.shortener_for_admins and message.from_user.id in client.admins):
        try: short=await Shortener(client.shortener_url,client.shortener_api).shorten(direct)
        except Exception as exc: client.LOGGER(__name__,client.name).warning("batch shortener failed: %s",exc)
    return "Batch Link\n\nDirect:\n"+direct+(f"\n\nShort:\n{short}" if short else "")

@Client.on_message(filters.command("batch") & filters.private)
async def batch(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    args=message.command[1:]
    if len(args)==3:
        try: cid=int(args[0]); ids=ids_range(int(args[1]),int(args[2]),settings.batch_max)
        except (ValueError,TypeError): return await message.reply_text("Usage: /batch <channel_id> <start_id> <end_id>")
        if not await client.db_channels.allowed(cid): return await message.reply_text("Storage channel is not configured.")
        return await message.reply_text(await make_link(client,message,cid,ids),disable_web_page_preview=True)

    await message.reply_text("Forward the first message from a configured storage channel within 60 seconds.")
    try:
        first=await client.listen(filters=filters.all,user_id=message.from_user.id,chat_id=message.chat.id,timeout=60)
        start=await forwarded_source(first)
        if not start: return await message.reply_text("Please forward a channel message, not a copied message.")
        cid,start_id=start
        if not await client.db_channels.allowed(cid): return await message.reply_text("That channel is not configured.")
        await message.reply_text("Now forward the last message from the same channel.")
        last=await client.listen(filters=filters.all,user_id=message.from_user.id,chat_id=message.chat.id,timeout=60)
        end=await forwarded_source(last)
        if not end or end[0]!=cid: return await message.reply_text("The second message must come from the same storage channel.")
        ids=ids_range(start_id,end[1],settings.batch_max)
        await message.reply_text(await make_link(client,message,cid,ids),disable_web_page_preview=True)
    except Exception:
        await message.reply_text("Batch creation timed out or failed. Try again.")

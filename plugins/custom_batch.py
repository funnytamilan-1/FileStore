from pyrogram import Client,filters
from config import settings
from helper.shortener import Shortener

def parse_ids(values):
    out=[]
    for value in values:
        if "-" in value[1:]:
            left,right=value.split("-",1); start,end=int(left),int(right); step=1 if end>=start else -1; out.extend(range(start,end+step,step))
        else: out.append(int(value))
    return list(dict.fromkeys(out))

@Client.on_message(filters.command("custom_batch") & filters.private)
async def custom_batch(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    args=message.command[1:]
    if len(args)<2: return await message.reply_text("Usage: /custom_batch <channel_id> <id|start-end> ...")
    try: cid=int(args[0]); ids=parse_ids(args[1:])
    except (ValueError,TypeError): return await message.reply_text("Invalid IDs.")
    if not ids or len(ids)>settings.batch_max or any(x<=0 for x in ids): return await message.reply_text("Invalid or oversized batch.")
    if not await client.db_channels.allowed(cid): return await message.reply_text("Storage channel is not configured.")
    direct=f"https://t.me/{client.username}?start={client.payload_codec.encode('custom',cid,ids)}"; short=None
    if client.shortener_enabled and not (client.shortener_for_admins and message.from_user.id in client.admins):
        try: short=await Shortener(client.shortener_url,client.shortener_api).shorten(direct)
        except Exception as exc: client.LOGGER(__name__,client.name).warning("custom batch shortener failed: %s",exc)
    text=f"Custom Batch\n\nDirect:\n{direct}"+(f"\n\nShort:\n{short}" if short else "")
    await message.reply_text(text,disable_web_page_preview=True)

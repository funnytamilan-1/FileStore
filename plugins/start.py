import asyncio
from pyrogram import Client,filters
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from pyrogram.errors import FloodWait
from config import settings

async def missing(app,user_id):
    out=[]
    for cid,data in app.fsub_channels.items():
        try:
            status=str((await app.get_chat_member(cid,user_id)).status).lower()
            if status.endswith("left") or status.endswith("kicked"): out.append(data)
        except Exception: out.append(data)
    return out

async def fsub_ui(message,app,items):
    rows=[]
    for item in items:
        link=item.get("invite_link") or item.get("username")
        if link:
            if not link.startswith("http"): link="https://t.me/"+link.lstrip("@")
            rows.append([InlineKeyboardButton("Join "+item.get("title","Channel"),url=link)])
    rows.append([InlineKeyboardButton("Check Subscription",callback_data="fsub:check")])
    await message.reply_text(app.messages.get("FSUB","Please join required channels."),reply_markup=InlineKeyboardMarkup(rows))

def register(app):
    pass

@Client.on_message(filters.command("start") & filters.private)
async def start(client,message):
    if not message.from_user: return
    await client.mongodb.user(message.from_user)
    if await client.mongodb.is_banned(message.from_user.id): return await message.reply_text("You are banned from using this bot.")
    if not await client.limiter.allow(message.from_user.id): return await message.reply_text("Too many requests. Try again later.")
    if len(message.command)==1:
        rows=[[InlineKeyboardButton("Help",callback_data="help"),InlineKeyboardButton("Premium",callback_data="myplan")],
              [InlineKeyboardButton("My Plan",callback_data="myplan"),InlineKeyboardButton("About",callback_data="about")]]
        if message.from_user.id in client.admins: rows.append([InlineKeyboardButton("Admin Panel",callback_data="admin")])
        text=client.messages.get("START",settings.start_message).format(mention=message.from_user.mention,first=message.from_user.first_name)
        photo=client.messages.get("START_PHOTO")
        if photo: return await message.reply_photo(photo,caption=text,reply_markup=InlineKeyboardMarkup(rows))
        return await message.reply_text(text,reply_markup=InlineKeyboardMarkup(rows))
    try: kind,cid,ids=client.payload_codec.decode(message.command[1])
    except ValueError: return await message.reply_text("Invalid or expired link.")
    if not await client.db_channels.allowed(cid): return await message.reply_text("Storage link is no longer active.")
    if client.fsub_enabled:
        needed=await missing(client,message.from_user.id)
        if needed: return await fsub_ui(message,client,needed)
    sent=[]
    for mid in ids:
        try:
            source=await client.get_messages(cid,mid)
            if source and not source.empty:
                sent.append(await source.copy(message.chat.id,protect_content=client.protect_content,
                                               reply_markup=None if client.disable_btn else source.reply_markup))
        except FloodWait as exc:
            await asyncio.sleep(exc.value)
        except Exception as exc:
            client.LOGGER(__name__,client.name).warning("delivery failed %s/%s: %s",cid,mid,exc)
    if not sent: return await message.reply_text("No available files were found.")
    if client.auto_delete_time:
        async def cleanup(ids_to_delete):
            await asyncio.sleep(client.auto_delete_time)
            for mid in ids_to_delete:
                try: await client.delete_messages(message.chat.id,mid)
                except Exception: pass
        task=asyncio.create_task(cleanup([x.id for x in sent])); client._tasks.add(task); task.add_done_callback(client._tasks.discard)


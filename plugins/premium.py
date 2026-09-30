from datetime import datetime,timedelta,timezone
from pyrogram import Client,filters

@Client.on_message(filters.command("addpremium") & filters.private)
async def addpremium(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)<2: return await message.reply_text("Usage: /addpremium <user_id> [days]")
    try: uid=int(message.command[1]); days=int(message.command[2]) if len(message.command)>2 else None
    except ValueError: return await message.reply_text("Invalid user ID or duration.")
    expiry=datetime.now(timezone.utc)+timedelta(days=days) if days else None
    await client.mongodb.add_premium(uid,expiry,message.from_user.id); await message.reply_text("Premium activated.")

@Client.on_message(filters.command(["remove_premium","removepremium","delpremium"]) & filters.private)
async def remove_premium(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)!=2: return await message.reply_text("Usage: /remove_premium <user_id>")
    try: uid=int(message.command[1])
    except ValueError: return await message.reply_text("Invalid user ID.")
    await client.mongodb.remove_premium(uid); await message.reply_text("Premium removed.")

@Client.on_message(filters.command(["myplan","profile"]) & filters.private)
async def myplan(client,message):
    await client.mongodb.user(message.from_user); premium=await client.mongodb.is_pro(message.from_user.id); expiry=await client.mongodb.get_expiry_date(message.from_user.id)
    if expiry and expiry.tzinfo is None: expiry=expiry.replace(tzinfo=timezone.utc)
    await message.reply_text(f"User ID: {message.from_user.id}\nPlan: {'Premium' if premium else 'Free'}\nExpiry: {expiry.isoformat() if expiry else ('Permanent' if premium else '—')}\nShortener: {'Bypassed' if premium and not client.shortener_for_premium else ('Enabled' if client.shortener_enabled else 'Disabled')}")

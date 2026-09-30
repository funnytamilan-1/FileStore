from pyrogram import Client,filters
from helper.shortener import Shortener

@Client.on_message(filters.command(["setshortener","setshortner"]) & filters.private)
async def setshortener(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)<3: return await message.reply_text("Usage: /setshortener <url> <api_key>")
    client.shortener_url=client.short_url=message.command[1].rstrip("/"); client.shortener_api=client.short_api=" ".join(message.command[2:])
    client.shortener_enabled=client.shortner_enabled=True
    await client.mongodb.set_setting("shortlink_enabled",True); await client.mongodb.set_setting("shortlink_url",client.shortener_url); await client.mongodb.set_setting("shortlink_api",client.shortener_api)
    await message.reply_text("Shortener enabled and saved.")

@Client.on_message(filters.command(["removeshortener","removeshortner"]) & filters.private)
async def removeshortener(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    client.shortener_enabled=client.shortner_enabled=False; await client.mongodb.set_setting("shortlink_enabled",False); await message.reply_text("Shortener disabled.")

@Client.on_message(filters.command(["shortener","shortner"]) & filters.private)
async def shortener_status(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    await message.reply_text(f"Shortener: {'enabled' if client.shortener_enabled else 'disabled'}\nURL: {client.shortener_url or 'not configured'}")

@Client.on_message(filters.command("count") & filters.private)
async def shortener_count(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    data=await client.mongodb.shortener_stats()
    await message.reply_text(f"Shortener clicks\n\nTotal: {data['total']}\nToday: {data['today']}\nUnique users: {data['unique']}\nSuccessful: {data['successful']}")

@Client.on_callback_query(filters.regex(r"^toggle_shortner$"))
async def toggle_shortner(client,query):
    if query.from_user.id not in client.admins: return await query.answer("Not authorized.",show_alert=True)
    client.shortener_enabled=client.shortner_enabled=not client.shortener_enabled; await client.mongodb.set_setting("shortlink_enabled",client.shortener_enabled); await query.answer("Updated")

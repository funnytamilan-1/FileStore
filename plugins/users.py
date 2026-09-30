from pyrogram import Client,filters
@Client.on_message(filters.command("users") & filters.private)
async def users(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    data=await client.mongodb.stats()
    await message.reply_text(f"Users: {data['users']}\nPremium: {data['premium']}\nBanned: {data['banned']}")
@Client.on_message(filters.command("help"))
async def help_command(client,message): await message.reply_text("Commands: /start /myplan /genlink /batch /custom_batch /help /about")
@Client.on_message(filters.command("about"))
async def about(client,message): await message.reply_text("Telegram FileStore + URL Shortener")

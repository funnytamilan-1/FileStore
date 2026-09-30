from pyrogram import Client,filters

@Client.on_message(filters.command("add_admin") & filters.private)
async def add_admin(client,message):
    if message.from_user.id!=client.owner: return await message.reply_text("Only the owner can manage admins.")
    if len(message.command)!=2: return await message.reply_text("Usage: /add_admin <user_id>")
    try: uid=int(message.command[1])
    except ValueError: return await message.reply_text("Invalid user ID.")
    await client.mongodb.add_admin(uid,message.from_user.id); client.admins.add(uid); await message.reply_text("Admin added.")

@Client.on_message(filters.command("deladmin") & filters.private)
async def deladmin(client,message):
    if message.from_user.id!=client.owner: return await message.reply_text("Only the owner can manage admins.")
    if len(message.command)!=2: return await message.reply_text("Usage: /deladmin <user_id>")
    try: uid=int(message.command[1])
    except ValueError: return await message.reply_text("Invalid user ID.")
    if uid==client.owner: return await message.reply_text("Owner cannot be removed.")
    await client.mongodb.remove_admin(uid); client.admins.discard(uid); await message.reply_text("Admin removed.")

@Client.on_message(filters.command("admins") & filters.private)
async def admins(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    await message.reply_text("Admins\n\n"+"\n".join(str(uid) for uid in sorted(client.admins)))

from pyrogram import Client,filters

@Client.on_message(filters.command("ban") & filters.private)
async def ban(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    try: uid=message.reply_to_message.from_user.id if message.reply_to_message else int(message.command[1])
    except (IndexError,ValueError,AttributeError): return await message.reply_text("Usage: /ban <user_id> or reply to a user.")
    if uid==client.owner: return await message.reply_text("The owner cannot be banned.")
    await client.mongodb.ban(uid); await message.reply_text("User banned.")

@Client.on_message(filters.command("unban") & filters.private)
async def unban(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)!=2: return await message.reply_text("Usage: /unban <user_id>")
    try: uid=int(message.command[1])
    except ValueError: return await message.reply_text("Invalid user ID.")
    await client.mongodb.unban(uid); await message.reply_text("User unbanned.")

@Client.on_message(filters.command("banlist") & filters.private)
async def banlist(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    rows=await client.mongodb.get_banned_users(1,50)
    await message.reply_text("Banned users\n\n"+("\n".join(str(x["user_id"]) for x in rows) or "Empty"))

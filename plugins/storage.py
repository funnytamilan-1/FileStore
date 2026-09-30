from pyrogram import Client,filters

@Client.on_message(filters.command("addstorage") & filters.private)
async def add_storage(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)!=2: return await message.reply_text("Usage: /addstorage <channel_id>")
    try:
        cid=int(message.command[1]); chat=await client.get_chat(cid); primary=not bool(await client.db_channels.primary())
        await client.db_channels.add(cid,chat.title or str(cid),chat.username,primary=primary,added_by=message.from_user.id)
        await message.reply_text("Storage channel added.")
    except Exception: await message.reply_text("Channel validation failed.")

@Client.on_message(filters.command("removestorage") & filters.private)
async def remove_storage(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)!=2: return await message.reply_text("Usage: /removestorage <channel_id>")
    try: await client.db_channels.remove(int(message.command[1])); await message.reply_text("Storage channel disabled.")
    except ValueError: await message.reply_text("Invalid channel ID.")

@Client.on_message(filters.command("storages") & filters.private)
async def storages(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    rows=await client.db_channels.all()
    await message.reply_text("Storage channels\n\n"+("\n".join(f"{x['channel_id']} — {x.get('title','Channel')} {'PRIMARY' if x.get('is_primary') else ''}" for x in rows) or "No storage channels configured."))

from pyrogram import Client,filters

@Client.on_message(filters.command("dlt_time") & filters.private)
async def dlt_time(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)!=2: return await message.reply_text("Usage: /dlt_time <seconds>")
    try: seconds=max(0,int(message.command[1]))
    except ValueError: return await message.reply_text("Invalid seconds.")
    client.auto_delete_time=client.auto_del=seconds; await client.mongodb.set_setting("auto_delete_time",seconds); await message.reply_text(f"Auto-delete: {seconds}s")

@Client.on_message(filters.command("check_dlt_time") & filters.private)
async def check_dlt_time(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    await message.reply_text(f"Auto-delete: {client.auto_delete_time}s")

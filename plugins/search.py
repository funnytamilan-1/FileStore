from pyrogram import Client,filters
@Client.on_message(filters.command("search") & filters.private)
async def search(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    query=" ".join(message.command[1:]).strip()
    if not query: return await message.reply_text("Usage: /search <filename or caption>")
    rows=await client.db.files.find({"$or":[{"filename":{"$regex":query,"$options":"i"}},{"caption":{"$regex":query,"$options":"i"}}]},{"channel_id":1,"message_id":1,"filename":1}).limit(20).to_list(length=20)
    await message.reply_text("Results\n\n"+("\n".join(f"{x['channel_id']}/{x['message_id']} — {x.get('filename','unknown')}" for x in rows) or "No matching files."))

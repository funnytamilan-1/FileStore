import time
import psutil
from pyrogram import Client,filters

@Client.on_message(filters.command("premium_users") & filters.private)
async def premium_users(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    rows=await client.mongodb.get_premium_users(page=1,page_size=50)
    await message.reply_text("💎 Premium users\n\n"+("\n".join(f"• `{x['user_id']}` — {x.get('premium_expiry') or 'Permanent'}" for x in rows) or "No active premium users."))

@Client.on_message(filters.command("delreq") & filters.private)
async def delreq(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    result=await client.db.join_requests.delete_many({"status":{"$in":["rejected","expired"]}})
    await message.reply_text(f"🧹 Removed {result.deleted_count} stale join-request records.")

@Client.on_message(filters.command("health") & filters.private)
async def health(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    process=psutil.Process()
    await message.reply_text(f"🩺 Uptime: {int(time.monotonic()-client.started)}s\nCPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%\nProcess RAM: {process.memory_info().rss/1048576:.1f} MB")

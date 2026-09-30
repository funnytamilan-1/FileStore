from pyrogram import Client,filters
import time,psutil

@Client.on_message(filters.command("stats") & filters.private)
async def stats(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    data=await client.mongodb.stats(); process=psutil.Process()
    await message.reply_text(f"Users: {data['users']}\nPremium: {data['premium']}\nBanned: {data['banned']}\nAdmins: {data['admins']}\nUptime: {int(time.monotonic()-client.started)}s\nCPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%\nDisk: {psutil.disk_usage('/').percent}%\nProcess RAM: {process.memory_info().rss/1048576:.1f} MB")

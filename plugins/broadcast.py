import asyncio
from datetime import datetime,timezone
from pyrogram import Client,filters
from pyrogram.errors import FloodWait,UserIsBlocked,UserDeactivated,PeerIdInvalid
from config import settings

async def deliver(source,client,user_id,retries=2):
    for attempt in range(retries+1):
        try: return await source.copy(user_id)
        except FloodWait as exc:
            if attempt>=retries: raise
            await asyncio.sleep(exc.value)

@Client.on_message(filters.command(["broadcast","dbroadcast","pbroadcast"]) & filters.private)
async def broadcast(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    source=message.reply_to_message
    if not source: return await message.reply_text("Reply to the message you want to broadcast.")
    progress=await message.reply_text("Broadcast started...")
    counts={"total":0,"successful":0,"blocked":0,"deleted":0,"failed":0,"floodwait":0}
    sem=asyncio.Semaphore(settings.broadcast_concurrency); lock=asyncio.Lock()
    async def one(uid):
        async with sem:
            try: await deliver(source,client,uid); counts["successful"]+=1
            except UserIsBlocked: counts["blocked"]+=1
            except UserDeactivated: counts["deleted"]+=1
            except FloodWait: counts["floodwait"]+=1
            except PeerIdInvalid: counts["failed"]+=1
            except Exception: counts["failed"]+=1
    tasks=[]
    async for row in client.db.users.find({},{"user_id":1}).batch_size(500):
        counts["total"]+=1; tasks.append(asyncio.create_task(one(row["user_id"])))
        if len(tasks)>=500:
            await asyncio.gather(*tasks,return_exceptions=True); tasks.clear()
            await progress.edit_text("Broadcasting...\n"+str(counts))
    if tasks: await asyncio.gather(*tasks,return_exceptions=True)
    await client.db.broadcasts.insert_one({"created_at":datetime.now(timezone.utc),"by":message.from_user.id,**counts})
    await progress.edit_text("Broadcast complete\n"+str(counts))

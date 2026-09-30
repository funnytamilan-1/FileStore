from pyrogram import Client,filters

@Client.on_message(filters.command("addchnl") & filters.private)
async def addchnl(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)<2: return await message.reply_text("Usage: /addchnl <channel_id> [invite_link] [request_join]")
    try: cid=int(message.command[1]); chat=await client.get_chat(cid)
    except Exception: return await message.reply_text("Channel validation failed.")
    invite=message.command[2] if len(message.command)>2 else chat.invite_link
    request_join=len(message.command)>3 and message.command[3].lower() in {"1","true","yes","request"}
    row={"channel_id":cid,"title":chat.title or str(cid),"username":chat.username,"invite_link":invite,"enabled":True,"request_join":request_join}
    await client.db.fsub_channels.update_one({"channel_id":cid},{"$set":row},upsert=True); client.fsub_channels[cid]=row; client.fsub_dict[cid]=[row["title"],invite,request_join,0]; client.fsub_enabled=True
    await client.mongodb.set_setting("fsub_enabled",True); await message.reply_text("ForceSub channel added.")

@Client.on_message(filters.command("delchnl") & filters.private)
async def delchnl(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    if len(message.command)!=2: return await message.reply_text("Usage: /delchnl <channel_id>")
    try: cid=int(message.command[1])
    except ValueError: return await message.reply_text("Invalid channel ID.")
    await client.db.fsub_channels.delete_one({"channel_id":cid}); client.fsub_channels.pop(cid,None); client.fsub_dict.pop(cid,None)
    client.fsub_enabled=bool(client.fsub_channels); await client.mongodb.set_setting("fsub_enabled",client.fsub_enabled); await message.reply_text("ForceSub channel removed.")

@Client.on_message(filters.command("listchnl") & filters.private)
async def listchnl(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    rows=await client.db.fsub_channels.find({"enabled":True}).to_list(length=100)
    await message.reply_text("ForceSub channels\n\n"+("\n".join(f"{x['channel_id']} — {x.get('title','Channel')}" for x in rows) or "None"))

@Client.on_message(filters.command("fsub_mode") & filters.private)
async def fsub_mode(client,message):
    if message.from_user.id not in client.admins: return await message.reply_text("Not authorized.")
    client.fsub_enabled=not client.fsub_enabled; await client.mongodb.set_setting("fsub_enabled",client.fsub_enabled); await message.reply_text(f"ForceSub: {'ON' if client.fsub_enabled else 'OFF'}")

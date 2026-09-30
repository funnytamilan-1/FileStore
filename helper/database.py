from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

class Database:
    def __init__(self,url:str,name:str):
        self.client=AsyncIOMotorClient(url,serverSelectionTimeoutMS=8000,connectTimeoutMS=8000)
        self.db=self.client[name]

    async def connect(self): await self.client.admin.command("ping")
    async def close(self): self.client.close()

    async def ensure_indexes(self):
        specs={
            "users":[("user_id",ASCENDING,True),("last_seen",DESCENDING,False)],
            "admins":[("user_id",ASCENDING,True)],
            "premium_users":[("user_id",ASCENDING,True),("premium_expiry",ASCENDING,False)],
            "banned_users":[("user_id",ASCENDING,True)],
            "storage_channels":[("channel_id",ASCENDING,True),("enabled",ASCENDING,False)],
            "fsub_channels":[("channel_id",ASCENDING,True),("enabled",ASCENDING,False)],
            "files":[("channel_id",ASCENDING,False),("message_id",ASCENDING,False),("filename",ASCENDING,False)],
            "shortener_clicks":[("user_id",ASCENDING,False),("created_at",DESCENDING,False),("payload",ASCENDING,False)],
            "broadcasts":[("created_at",DESCENDING,False)],
            "join_requests":[("user_id",ASCENDING,False),("channel_id",ASCENDING,False),("status",ASCENDING,False)]
        }
        for collection,items in specs.items():
            for field,direction,unique in items:
                try: await self.db[collection].create_index(field,direction=direction,unique=unique)
                except Exception:
                    if unique: await self.db[collection].create_index(field,direction=direction)

    async def indexes(self): await self.ensure_indexes()

    async def user(self,user):
        now=datetime.now(timezone.utc)
        await self.db.users.update_one(
            {"user_id":user.id},
            {"$set":{"username":user.username,"first_name":user.first_name or "","last_name":user.last_name or "","last_seen":now},
             "$setOnInsert":{"user_id":user.id,"joined_at":now,"is_banned":False,"is_premium":False,"premium_expiry":None}},
            upsert=True)
        return await self.db.users.find_one({"user_id":user.id}) or {}

    async def add_user(self,user_id:int,**fields):
        now=datetime.now(timezone.utc)
        await self.db.users.update_one({"user_id":int(user_id)},
            {"$setOnInsert":{"user_id":int(user_id),"joined_at":now,"is_banned":False,"is_premium":False,"premium_expiry":None},"$set":fields},upsert=True)

    async def get_user(self,user_id:int): return await self.db.users.find_one({"user_id":int(user_id)})
    async def update_user(self,user_id:int,**fields): await self.db.users.update_one({"user_id":int(user_id)},{"$set":fields},upsert=True)
    async def delete_user(self,user_id:int): await self.db.users.delete_one({"user_id":int(user_id)})
    async def present_user(self,user_id:int): return bool(await self.get_user(user_id))
    async def full_userbase(self): return [x["user_id"] async for x in self.db.users.find({},{"user_id":1})]

    async def get_all_users(self,page=1,page_size=100):
        skip=max(0,page-1)*page_size
        return [x async for x in self.db.users.find({},{"user_id":1,"username":1}).sort("user_id",ASCENDING).skip(skip).limit(page_size)]
    async def get_total_users(self): return await self.db.users.count_documents({})
    async def get_premium_users(self,page=1,page_size=100):
        await self.expire_premium(); skip=max(0,page-1)*page_size
        return [x async for x in self.db.users.find({"is_premium":True}).sort("user_id",ASCENDING).skip(skip).limit(page_size)]
    async def get_banned_users(self,page=1,page_size=100):
        skip=max(0,page-1)*page_size
        return [x async for x in self.db.users.find({"is_banned":True}).sort("user_id",ASCENDING).skip(skip).limit(page_size)]

    async def banned(self,uid:int): return bool(await self.db.users.find_one({"user_id":int(uid),"is_banned":True},{"_id":1}))
    async def is_banned(self,uid:int): return await self.banned(uid)
    async def ban(self,uid:int,reason=""):
        now=datetime.now(timezone.utc); uid=int(uid)
        await self.db.users.update_one({"user_id":uid},{"$set":{"is_banned":True}},upsert=True)
        await self.db.banned_users.update_one({"user_id":uid},{"$set":{"user_id":uid,"reason":reason,"created_at":now}},upsert=True)
    async def ban_user(self,uid:int): await self.ban(uid)
    async def unban(self,uid:int):
        uid=int(uid); await self.db.users.update_one({"user_id":uid},{"$set":{"is_banned":False}}); await self.db.banned_users.delete_one({"user_id":uid})
    async def unban_user(self,uid:int): await self.unban(uid)

    async def add_admin(self,uid:int,added_by:int):
        await self.db.admins.update_one({"user_id":int(uid)},{"$set":{"user_id":int(uid),"added_by":int(added_by),"created_at":datetime.now(timezone.utc)}},upsert=True)
    async def remove_admin(self,uid:int): await self.db.admins.delete_one({"user_id":int(uid)})
    async def get_admin_ids(self): return [int(x["user_id"]) async for x in self.db.admins.find({},{"user_id":1})]

    async def get_setting(self,key:str,default=None):
        row=await self.db.settings.find_one({"_id":key}); return default if not row else row.get("value",default)
    async def setting(self,key:str,default=None): return await self.get_setting(key,default)
    async def set_setting(self,key:str,value:Any): await self.db.settings.update_one({"_id":key},{"$set":{"value":value}},upsert=True)

    async def set_shortner_settings(self,values): await self.set_setting("shortener",values)
    async def get_shortner_settings(self): return dict(await self.get_setting("shortener",{}))
    async def update_shortner_setting(self,key,value):
        values=await self.get_shortner_settings(); values[key]=value; await self.set_shortner_settings(values)
    async def get_shortner_status(self): return bool(await self.get_setting("shortlink_enabled",True))
    async def set_shortner_status(self,enabled): await self.set_setting("shortlink_enabled",bool(enabled))

    async def add_premium(self,uid:int,expiry=None,added_by=None):
        uid=int(uid)
        await self.db.users.update_one({"user_id":uid},{"$set":{"is_premium":True,"premium_expiry":expiry}},upsert=True)
        await self.db.premium_users.update_one({"user_id":uid},{"$set":{"user_id":uid,"premium":True,"premium_expiry":expiry,"added_by":added_by,"created_at":datetime.now(timezone.utc)}},upsert=True)
    async def add_pro(self,uid:int,expiry_date=None): await self.add_premium(uid,expiry_date)
    async def remove_premium(self,uid:int):
        uid=int(uid); await self.db.users.update_one({"user_id":uid},{"$set":{"is_premium":False,"premium_expiry":None}}); await self.db.premium_users.delete_one({"user_id":uid})
    async def remove_pro(self,uid:int): await self.remove_premium(uid)
    async def expire_premium(self):
        now=datetime.now(timezone.utc)
        ids=[x["user_id"] async for x in self.db.users.find({"is_premium":True,"premium_expiry":{"$ne":None,"$lte":now}},{"user_id":1})]
        if ids:
            await self.db.users.update_many({"user_id":{"$in":ids}},{"$set":{"is_premium":False,"premium_expiry":None}})
            await self.db.premium_users.delete_many({"user_id":{"$in":ids}})
    async def is_pro(self,uid:int):
        await self.expire_premium(); return bool(await self.db.users.find_one({"user_id":int(uid),"is_premium":True},{"_id":1}))
    async def get_expiry_date(self,uid:int):
        row=await self.db.users.find_one({"user_id":int(uid)},{"premium_expiry":1}); return row.get("premium_expiry") if row else None
    async def get_pros_list(self): await self.expire_premium(); return [x["user_id"] async for x in self.db.users.find({"is_premium":True},{"user_id":1})]

    async def record_shortener_click(self,user_id:int,payload:str,shortener:str,successful_redirect:bool):
        now=datetime.now(timezone.utc); start=now.replace(hour=0,minute=0,second=0,microsecond=0)
        if await self.db.shortener_clicks.find_one({"user_id":int(user_id),"payload":payload,"created_at":{"$gte":start}}): return
        await self.db.shortener_clicks.insert_one({"user_id":int(user_id),"payload":payload,"created_at":now,"shortener":shortener,"click":1,"successful_redirect":bool(successful_redirect)})
    async def shortener_stats(self):
        start=datetime.now(timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0)
        return {"total":await self.db.shortener_clicks.count_documents({}),
                "today":await self.db.shortener_clicks.count_documents({"created_at":{"$gte":start}}),
                "unique":len(await self.db.shortener_clicks.distinct("user_id")),
                "successful":await self.db.shortener_clicks.count_documents({"successful_redirect":True})}
    async def stats(self):
        await self.expire_premium()
        return {"users":await self.db.users.count_documents({}),"premium":await self.db.users.count_documents({"is_premium":True}),
                "banned":await self.db.users.count_documents({"is_banned":True}),"admins":await self.db.admins.count_documents({})}

    async def set_channels(self,channels): await self.set_setting("request_channels",[int(x) for x in channels])
    async def get_channels(self): return list(await self.get_setting("request_channels",[]))
    async def set_fsub_channels(self,data): await self.set_setting("legacy_fsub_channels",data)
    async def get_fsub_channels(self): return dict(await self.get_setting("legacy_fsub_channels",{}))
    async def add_fsub_channel(self,cid,data):
        x=await self.get_fsub_channels(); x[str(cid)]=data; await self.set_fsub_channels(x)
    async def remove_fsub_channel(self,cid):
        x=await self.get_fsub_channels(); x.pop(str(cid),None); await self.set_fsub_channels(x)

MongoDB=Database

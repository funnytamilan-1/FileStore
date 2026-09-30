from datetime import datetime, timezone

class Channels:
    def __init__(self,db): self.db=db.db
    async def allowed(self,cid:int)->bool:
        return bool(await self.db.storage_channels.find_one({"channel_id":int(cid),"enabled":True}))
    async def add(self,cid:int,title="",username=None,primary=False,added_by=None):
        cid=int(cid)
        if primary: await self.db.storage_channels.update_many({},{"$set":{"is_primary":False}})
        await self.db.storage_channels.update_one({"channel_id":cid},{"$set":{"title":title,"username":username,"enabled":True,"is_primary":bool(primary),"added_by":added_by},"$setOnInsert":{"created_at":datetime.now(timezone.utc)}},upsert=True)
    async def remove(self,cid:int): await self.db.storage_channels.update_one({"channel_id":int(cid)},{"$set":{"enabled":False,"is_primary":False}})
    async def set_primary(self,cid:int):
        if not await self.allowed(cid): raise ValueError("storage channel is not enabled")
        await self.db.storage_channels.update_many({},{"$set":{"is_primary":False}})
        await self.db.storage_channels.update_one({"channel_id":int(cid)},{"$set":{"is_primary":True}})
    async def all(self,page=1,page_size=100):
        skip=max(0,page-1)*page_size
        return [x async for x in self.db.storage_channels.find({"enabled":True}).sort("created_at",1).skip(skip).limit(page_size)]
    async def primary(self): return await self.db.storage_channels.find_one({"enabled":True,"is_primary":True})

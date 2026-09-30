import time
from datetime import datetime
from pyrogram import Client
from config import LOGGER, MESSAGES, settings
from helper.database import Database
from helper.db_channels import Channels
from helper.rate_limit import RateLimiter

class Bot(Client):
    def __init__(self):
        super().__init__("filestore",api_id=settings.api_id,api_hash=settings.api_hash,
                         bot_token=settings.bot_token,workers=settings.workers,plugins={"root":"plugins"})
        self.name="filestore"; self.LOGGER=LOGGER; self.owner=settings.owner_id
        self.admins=set(settings.admins)|{self.owner}; self.mongodb=Database(settings.database_url,settings.database_name)
        self.db=self.mongodb.db; self.db_channels=Channels(self.mongodb); self.primary_db_channel=settings.channel_id
        self.fsub_channels={}; self.fsub_dict={}; self.fsub_enabled=False; self.req_channels=[]; self.req_fsub={}
        self.shortner_enabled=self.shortener_enabled=settings.shortlink_enabled
        self.short_url=self.shortener_url=settings.shortlink_url; self.short_api=self.shortener_api=settings.shortlink_api
        self.shortener_for_premium=settings.shortlink_for_premium; self.shortener_for_admins=settings.shortlink_for_admins
        self.tutorial_link=""; self.auto_del=self.auto_delete_time=settings.auto_delete_time
        self.protect=self.protect_content=settings.protect_content; self.disable_btn=False
        self.messages=MESSAGES; self.reply_text=MESSAGES["REPLY"]; self.uptime=datetime.now()
        self.started=time.monotonic(); self.db_channel=None; self.username=None; self._tasks=set()
        self.limiter=RateLimiter(settings.rate_limit,settings.rate_window)

    async def initialize(self):
        await self.mongodb.connect(); await self.mongodb.ensure_indexes()
        for uid in await self.mongodb.get_admin_ids(): self.admins.add(uid)
        if self.primary_db_channel:
            try:
                chat=await self.get_chat(self.primary_db_channel)
                await self.db_channels.add(self.primary_db_channel,chat.title or str(self.primary_db_channel),chat.username,primary=True,added_by=self.owner)
            except Exception as exc: self.LOGGER(__name__,self.name).warning("Primary storage validation failed: %s",exc)
        self.fsub_channels={x["channel_id"]:x async for x in self.db.fsub_channels.find({"enabled":True})}
        self.fsub_dict={cid:[x.get("title",str(cid)),x.get("invite_link"),x.get("request_join",False),0] for cid,x in self.fsub_channels.items()}
        self.req_channels=[cid for cid,x in self.fsub_channels.items() if x.get("request_join")]
        self.fsub_enabled=bool(await self.mongodb.get_setting("fsub_enabled",bool(self.fsub_channels)))
        self.shortener_enabled=bool(await self.mongodb.get_setting("shortlink_enabled",settings.shortlink_enabled)); self.shortner_enabled=self.shortener_enabled
        self.shortener_url=self.short_url=await self.mongodb.get_setting("shortlink_url",settings.shortlink_url)
        self.shortener_api=self.short_api=await self.mongodb.get_setting("shortlink_api",settings.shortlink_api)
        self.auto_delete_time=self.auto_del=int(await self.mongodb.get_setting("auto_delete_time",settings.auto_delete_time))
        self.protect_content=self.protect=bool(await self.mongodb.get_setting("protect_content",settings.protect_content))

    async def start(self):
        await super().start(); me=await self.get_me(); self.username=me.username; self.started=time.monotonic()
        await self._validate_storage_channels()
        try: await self.send_message(self.owner,f"✅ {me.first_name} is online.")
        except Exception: pass

    async def _validate_storage_channels(self):
        ids=[]
        if self.primary_db_channel: ids.append(self.primary_db_channel)
        async for row in self.db.storage_channels.find({"enabled":True}): ids.append(row["channel_id"])
        for cid in dict.fromkeys(ids):
            try:
                chat=await self.get_chat(cid)
                await self.db.storage_channels.update_one({"channel_id":cid},{"$set":{"title":chat.title or str(cid),"username":chat.username}},upsert=True)
                if cid==self.primary_db_channel: self.db_channel=chat
            except Exception as exc: self.LOGGER(__name__,self.name).warning("Storage %s unavailable: %s",cid,exc)

    async def stop(self,*args): await super().stop()

    async def close_services(self):
        await self.mongodb.close()

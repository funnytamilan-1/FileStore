import logging
import os
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1","true","yes","on"}

def env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)
    return default if value in (None, "") else int(value)

def env_ids(name: str) -> list[int]:
    return [int(x.strip()) for x in os.getenv(name, "").split(",") if x.strip()]

@dataclass(frozen=True, slots=True)
class Settings:
    api_id:int; api_hash:str; bot_token:str; owner_id:int; admins:tuple[int,...]
    database_url:str; database_name:str; channel_id:int|None; port:int
    protect_content:bool; shortlink_enabled:bool; shortlink_url:str; shortlink_api:str
    shortlink_for_premium:bool; shortlink_for_admins:bool; auto_delete_time:int
    workers:int; broadcast_concurrency:int; rate_limit:int; rate_window:int
    batch_max:int; payload_ttl:int; payload_secret:str; start_message:str; start_photo:str

def load_settings() -> Settings:
    required=("API_ID","API_HASH","BOT_TOKEN","OWNER_ID","DATABASE_URL","DATABASE_NAME")
    missing=[x for x in required if not os.getenv(x)]
    if missing: raise RuntimeError("Missing required environment variables: "+", ".join(missing))
    token=os.environ["BOT_TOKEN"]; channel=os.getenv("CHANNEL_ID","").strip()
    return Settings(
        int(os.environ["API_ID"]),os.environ["API_HASH"],token,int(os.environ["OWNER_ID"]),
        tuple(env_ids("ADMINS")),os.environ["DATABASE_URL"],os.environ["DATABASE_NAME"],
        int(channel) if channel else None,env_int("PORT",8080),env_bool("PROTECT_CONTENT",True),
        env_bool("SHORTLINK_ENABLED",True),os.getenv("SHORTLINK_URL","").strip(),os.getenv("SHORTLINK_API","").strip(),
        env_bool("SHORTENER_FOR_PREMIUM",False),env_bool("SHORTENER_FOR_ADMINS",False),
        max(0,env_int("AUTO_DELETE_TIME",0)),max(4,env_int("PYROGRAM_WORKERS",32)),
        max(1,env_int("BROADCAST_CONCURRENCY",10)),max(1,env_int("RATE_LIMIT_REQUESTS",12)),
        max(1,env_int("RATE_LIMIT_WINDOW",60)),max(1,env_int("BATCH_MAX",1000)),
        max(0,env_int("PAYLOAD_TTL",0)),os.getenv("PAYLOAD_SECRET",token),
        os.getenv("START_MESSAGE","👋 Welcome, {mention}!"),os.getenv("START_PHOTO","").strip()
    )

settings=load_settings()

def LOGGER(name:str, client_name:str)->logging.Logger:
    logger=logging.getLogger(f"{client_name}.{name}")
    if logger.handlers: return logger
    logger.setLevel(logging.INFO)
    fmt=logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    fh=RotatingFileHandler("bot.log",maxBytes=10_000_000,backupCount=5,encoding="utf-8"); fh.setFormatter(fmt)
    sh=logging.StreamHandler(); sh.setFormatter(fmt)
    logger.addHandler(fh); logger.addHandler(sh); return logger

PORT=settings.port; OWNER_ID=settings.owner_id; ADMINS=list(settings.admins)
API_ID=settings.api_id; API_HASH=settings.api_hash; TOKEN=settings.bot_token; WORKERS=settings.workers
DB_URI=settings.database_url; DB_NAME=settings.database_name; DB_CHANNEL=settings.channel_id
PROTECT=settings.protect_content; DISABLE_BTN=env_bool("DISABLE_BUTTONS",False); AUTO_DEL=settings.auto_delete_time
SHORT_URL=settings.shortlink_url; SHORT_API=settings.shortlink_api; SHORT_TUT=os.getenv("SHORT_TUTORIAL_URL","")
MESSAGES={
"START":settings.start_message,"FSUB":os.getenv("FSUB_MESSAGE","Please join the required channels first."),
"ABOUT":os.getenv("ABOUT_MESSAGE","Telegram FileStore + URL Shortener"),
"REPLY":os.getenv("REPLY_MESSAGE","Use /help for commands."),"SHORT_MSG":os.getenv("SHORT_MESSAGE","Your short link is ready."),
"START_PHOTO":settings.start_photo,"FSUB_PHOTO":os.getenv("FSUB_PHOTO",""),"SHORT_PIC":os.getenv("SHORT_PHOTO",""),"SHORT":os.getenv("SHORT_PANEL_PHOTO","")
}

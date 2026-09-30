import logging
from logging.handlers import RotatingFileHandler

def get_logger(name="filestore"):
    logger=logging.getLogger(name)
    if logger.handlers: return logger
    logger.setLevel(logging.INFO); fmt=logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    fh=RotatingFileHandler("bot.log",maxBytes=10_000_000,backupCount=5,encoding="utf-8"); fh.setFormatter(fmt)
    logger.addHandler(fh); logger.addHandler(logging.StreamHandler()); return logger

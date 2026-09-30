import asyncio
import time
from collections import defaultdict,deque

class RateLimiter:
    def __init__(self,limit:int,window:int):
        self.limit=max(1,int(limit)); self.window=max(1,int(window)); self.events=defaultdict(deque); self.lock=asyncio.Lock()
    async def allow(self,user_id:int)->bool:
        now=time.monotonic()
        async with self.lock:
            q=self.events[int(user_id)]
            while q and now-q[0]>=self.window: q.popleft()
            if len(q)>=self.limit: return False
            q.append(now); return True

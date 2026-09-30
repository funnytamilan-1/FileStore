from urllib.parse import urlparse
import aiohttp

class Shortener:
    def __init__(self,base:str,api_key:str,timeout:float=10):
        self.base=(base or "").strip().rstrip("/"); self.api_key=api_key or ""; self.timeout=timeout
    async def shorten(self,url:str)->str:
        parsed=urlparse(url)
        if parsed.scheme not in {"http","https"} or not parsed.netloc: raise ValueError("invalid target URL")
        if not self.base or not self.api_key: raise RuntimeError("shortener is not configured")
        endpoint=self.base if self.base.startswith(("http://","https://")) else "https://"+self.base
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(endpoint,params={"api":self.api_key,"url":url}) as response:
                if response.status==429: raise RuntimeError("shortener rate limited")
                if response.status>=400: raise RuntimeError(f"shortener HTTP {response.status}")
                payload=await response.json(content_type=None)
        result=(payload.get("shortenedUrl") or payload.get("shorturl") or payload.get("shortened_url") or payload.get("url")) if isinstance(payload,dict) else payload
        if not isinstance(result,str) or not result.startswith(("http://","https://")): raise RuntimeError("shortener returned an invalid URL")
        return result

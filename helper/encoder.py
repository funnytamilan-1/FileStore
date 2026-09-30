import base64
import hashlib
import hmac
import json
import time

class PayloadCodec:
    def __init__(self,secret:str,ttl:int=0,max_items:int=1000):
        if not secret: raise ValueError("payload secret cannot be empty")
        self.key=hashlib.sha256(secret.encode()).digest(); self.ttl=max(0,int(ttl)); self.max_items=max(1,int(max_items))
    def encode(self,kind:str,channel_id:int,message_ids):
        if kind not in {"file","batch","custom"}: raise ValueError("invalid payload kind")
        ids=[int(x) for x in message_ids]
        if not ids or len(ids)>self.max_items or any(x<=0 for x in ids): raise ValueError("invalid message ids")
        body={"v":1,"k":kind,"c":int(channel_id),"m":ids,"t":int(time.time())}
        raw=json.dumps(body,separators=(",",":"),sort_keys=True).encode()
        signature=hmac.new(self.key,raw,hashlib.sha256).hexdigest().encode()
        return base64.urlsafe_b64encode(raw+b"."+signature).rstrip(b"=").decode()
    def decode(self,token:str):
        if not token or len(token)>4096: raise ValueError("invalid payload")
        try:
            padded=token+"="*(-len(token)%4); raw=base64.b64decode(padded.encode(),altchars=b"-_",validate=True)
            body,signature=raw.rsplit(b".",1)
            if len(signature)!=64: raise ValueError("invalid signature length")
            expected=hmac.new(self.key,body,hashlib.sha256).hexdigest().encode()
            if not hmac.compare_digest(signature,expected): raise ValueError("bad signature")
            if not hmac.compare_digest(base64.urlsafe_b64encode(raw).rstrip(b"=").decode(),token): raise ValueError("non-canonical payload")
            data=json.loads(body.decode()); kind=data.get("k"); channel=int(data["c"]); ids=tuple(int(x) for x in data["m"]); issued=int(data["t"])
            if data.get("v")!=1 or kind not in {"file","batch","custom"} or channel>=0 or not ids or len(ids)>self.max_items or any(x<=0 for x in ids): raise ValueError("invalid payload data")
            if self.ttl and time.time()-issued>self.ttl: raise ValueError("expired payload")
            return kind,channel,ids
        except Exception as exc: raise ValueError("invalid payload") from exc

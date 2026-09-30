import time
import pytest
from helper.encoder import PayloadCodec
from helper.validators import ids_range

def test_payload_roundtrip():
    codec=PayloadCodec("secret")
    token=codec.encode("file",-100123,[4])
    assert codec.decode(token)==("file",-100123,(4,))

def test_payload_tamper():
    codec=PayloadCodec("secret"); token=codec.encode("file",-100123,[4])
    changed="A" if token[-1]!="A" else "B"
    with pytest.raises(ValueError): codec.decode(token[:-1]+changed)

def test_payload_expiry():
    codec=PayloadCodec("secret",ttl=1); token=codec.encode("file",-100123,[4]); time.sleep(1.1)
    with pytest.raises(ValueError): codec.decode(token)

def test_batch_range():
    assert ids_range(3,1)==[3,2,1]

@pytest.mark.asyncio
async def test_rate_limiter():
    from helper.rate_limit import RateLimiter
    limiter=RateLimiter(2,60)
    assert await limiter.allow(1)
    assert await limiter.allow(1)
    assert not await limiter.allow(1)

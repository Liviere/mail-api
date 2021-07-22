import asyncio
from aiocache.factory import Cache


async def remove_entries(
    ip: str,
    sid: str,
    ip_cache: Cache.REDIS,
    sid_cache: Cache.REDIS
):
    # Remove the restriction for the given ip and session after 60 seconds
    await asyncio.sleep(60)
    await ip_cache.delete(ip)
    await sid_cache.delete(sid)
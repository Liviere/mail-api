from functools import lru_cache

from aiocache import Cache, caches

from settings import Settings


@lru_cache()
def get_settings():
    return Settings()


@lru_cache()
def use_caches():
    settings = get_settings()
    common = {'endpoint': settings.REDIS_CRE["host"],
              'port': settings.REDIS_CRE["port"],
              'timeout': 2}

    caches.set_config({
        settings.REQUESTS_SID_CACHE: {
            'cache': "aiocache.RedisCache",
            "db": 0,
            'serializer': {
                'class': "aiocache.serializers.JsonSerializer"
            },
            **common
        },

        settings.REQUESTS_IP_CACHE: {
            'cache': "aiocache.RedisCache",
            "db": 1,
            'serializer': {
                'class': "aiocache.serializers.JsonSerializer"
            },
            **common
        }
    })
    return caches


async def close_caches(settings: Settings):
    print("Closing Caches")
    caches = use_caches()
    sidCache = caches.get(settings.REQUESTS_SID_CACHE)
    ipCache = caches.get(settings.REQUESTS_IP_CACHE)
    await close_cache(sidCache)
    await close_cache(ipCache)


async def clear_caches(settings: Settings):
    print("Clearing Caches")
    caches = use_caches()
    sidCache = caches.get(settings.REQUESTS_SID_CACHE)
    ipCache = caches.get(settings.REQUESTS_IP_CACHE)
    await sidCache.clear()
    await ipCache.clear()


async def close_cache(cache: Cache.REDIS):
    await cache.clear()
    await cache.close()

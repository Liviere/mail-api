from functools import lru_cache

from aiocache import caches

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

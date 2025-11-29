from flask_caching import Cache

def cache_init_app(app):
    cache = Cache(config={
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_HOST': 'localhost',
        'CACHE_REDIS_PORT': 6379,
        'CACHE_REDIS_DB': 2,
        'CACHE_DEFAULT_TIMEOUT': 30
    })
    cache.init_app(app)
    return cache
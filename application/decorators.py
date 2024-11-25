from functools import wraps
from time import time

from django.core.cache import cache


def throttle(interval=5, timeout=10):
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"
            last = cache.get(key)

            if last and (time() - last) < interval * 60:
                return

            result = func(*args, **kwargs)
            cache.set(key, time(), timeout=timeout * 60)

            return result

        return wrapper

    return decorator

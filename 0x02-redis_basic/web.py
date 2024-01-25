#!/usr/bin/env python3
"""Defines get_page function"""

import redis
import requests
from functools import wraps
from typing import Callable

redis_client = redis.Redis()


def count_cache(method: Callable) -> Callable:
    """Counts how many times a particular URL was accessed"""
    @wraps(method)
    def wrapper(url):
        """Wrapper function for the decorated method."""
        redis_client.incr(f"count:{url}")

        result = method(url)
        redis_client.setex(f"result:{url}", 10, result)

        return result

    return wrapper


@count_cache
def get_page(url: str) -> str:
    """Returns HTML of a URL"""
    return requests.get(url).text

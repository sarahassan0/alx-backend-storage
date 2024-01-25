#!/usr/bin/env python3
"""A script to  Writing strings to Redis"""


import redis
import uuid
from typing import Union, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of times a method is called."""

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """Wrapper function for the decorated method."""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)

        return method(self, *args, **kwds)

    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to add input and output paramters of callable to 2 lists"""

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """Wrapper function for the decorated method."""
        generated_key = method(self, *args, **kwds)

        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(f"{method.__qualname__}:inputs", str(args))
            self._redis.rpush(f"{method.__qualname__}:outputs", generated_key)

        return generated_key

    return wrapper

class Cache:
    """A Cache class that stores data in Redis."""

    def __init__(self):
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Method that takes a data argument and returns a string"""
        key: str = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self, key: str, fn: Union[Callable, None] = None
    ) -> Union[str, bytes, int, float]:
        """Get value and pass it to the callable"""
        value = self._redis.get(key)

        if fn is not None:
            return fn(value)

        return value

    def get_str(self, key: str) -> str:
        """Parametrize method for getting a string from the cache"""
        return self.get(key, lambda x: x.decode("utf-8"))

    def get_int(self, key: str):
        """Automatically parametrize Cache.get
        with the correct conversion function"""
        return self._redis.get(key, int)

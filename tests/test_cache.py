from termloop.cache import CacheStore
from time import sleep


def test_cache_round_trip(tmp_path) -> None:
    cache = CacheStore(str(tmp_path))
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hello"}]}
    value = {"id": "chatcmpl-test", "choices": []}

    assert cache.get(payload) is None
    cache.set(payload, value)
    assert cache.get(payload) == value


def test_cache_ttl_expiry(tmp_path) -> None:
    cache = CacheStore(str(tmp_path), enabled=True, ttl_seconds=1)
    payload = {"model": "qwen-plus", "messages": [{"role": "user", "content": "ttl"}]}
    value = {"id": "chatcmpl-ttl", "choices": []}
    cache.set(payload, value)
    assert cache.get(payload) == value
    sleep(1.2)
    assert cache.get(payload) is None

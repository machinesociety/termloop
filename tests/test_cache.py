from termloop.cache import CacheStore


def test_cache_round_trip(tmp_path) -> None:
    cache = CacheStore(str(tmp_path))
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hello"}]}
    value = {"id": "chatcmpl-test", "choices": []}

    assert cache.get(payload) is None
    cache.set(payload, value)
    assert cache.get(payload) == value


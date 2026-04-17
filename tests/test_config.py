from termloop.config import Settings


def test_provider_map_defaults_to_dashscope() -> None:
    settings = Settings(
        providers="{}",
        dashscope_api_key="",
        dashscope_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    mapping = settings.provider_map()
    assert "dashscope" in mapping
    assert mapping["dashscope"].small_model == "qwen-turbo"


def test_provider_key_must_not_use_file_prefix() -> None:
    settings = Settings(providers='{"dashscope":{"api_key":"file:/tmp/key.txt"}}')
    try:
        settings.provider_map()
    except ValueError:
        assert True
        return
    assert False, "Expected provider_map to reject file-based api_key sources"


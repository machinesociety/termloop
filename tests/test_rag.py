from termloop.rag import RagStore


def test_rag_respects_min_score(tmp_path) -> None:
    store = RagStore(str(tmp_path))
    store.add_text("source-a", "distributed system design reliability scaling")
    store.add_text("source-b", "gardening tomatoes and peppers in summer")

    query = "system reliability optimization latency"
    high = store.search(query, min_score=0.1)
    low = store.search(query, min_score=0.8)

    assert high
    assert not low

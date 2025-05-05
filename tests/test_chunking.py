import pytest

from docintel.chunking import chunk_text, estimate_tokens, split_sentences


def test_chunk_boundaries_and_overlap():
    text = ("Alpha beta gamma. " * 80).strip()
    chunks = chunk_text("doc_1", text, max_chars=180, overlap=20, min_chunk_chars=60)
    assert len(chunks) > 2
    assert all(len(chunk.text) <= 180 for chunk in chunks)
    assert [chunk.ordinal for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.start_char < chunk.end_char for chunk in chunks)


def test_empty_text_returns_no_chunks():
    assert chunk_text("doc_1", "") == []


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_chars": 0},
        {"max_chars": 100, "overlap": -1},
        {"max_chars": 100, "overlap": 100},
        {"max_chars": 100, "min_chunk_chars": 101},
    ],
)
def test_invalid_chunk_parameters(kwargs):
    with pytest.raises(ValueError):
        chunk_text("doc_1", "hello world", **kwargs)


def test_token_estimate_and_sentence_split():
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcdefgh") == 2
    assert split_sentences("First. Second! Third?") == ["First.", "Second!", "Third?"]

# _ci-ref-13847

# _ci-ref-23845

# _ci-ref-43540

# _ci-ref-62879

# _ci-ref-64325

# _ci-ref-20287

# _ci-ref-95696

# _ci-ref-88878

# _ci-ref-68816

# _ci-ref-88852

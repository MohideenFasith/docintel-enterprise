from docintel.chunking import chunk_text
from docintel.extraction import extract_metadata
from docintel.index import LexicalIndex, tokenize
from docintel.models import DocumentRecord, DocumentStatus


def record(doc_id: str, title: str, content: str, tags=None, source="api"):
    return DocumentRecord(
        id=doc_id,
        title=title,
        content=content,
        source=source,
        tags=tags or [],
        metadata={},
        extracted=extract_metadata(content),
        status=DocumentStatus.INDEXED,
        content_sha256=doc_id * 8,
    )


def test_tokenize_removes_common_stopwords():
    assert tokenize("The quick brown fox and the dog") == ["quick", "brown", "fox", "dog"]


def test_search_ranks_relevant_document():
    index = LexicalIndex()
    first = record("a", "GPU serving", "paged attention kernel optimization cuda")
    second = record("b", "Invoice", "monthly cloud billing report")
    index.index_document(first, chunk_text(first.id, first.content, max_chars=100, overlap=5, min_chunk_chars=10))
    index.index_document(second, chunk_text(second.id, second.content, max_chars=100, overlap=5, min_chunk_chars=10))
    hits = index.search("cuda kernel")
    assert hits[0].document_id == "a"
    assert "cuda" in hits[0].matched_terms


def test_search_filters_by_tag_and_source():
    index = LexicalIndex()
    a = record("a", "Budget", "cloud cost forecast", tags=["finance"], source="s3")
    b = record("b", "Budget", "cloud cost anomaly", tags=["ops"], source="api")
    for item in (a, b):
        index.index_document(item, chunk_text(item.id, item.content, max_chars=100, overlap=5, min_chunk_chars=10))
    assert [h.document_id for h in index.search("cloud cost", required_tag="finance")] == ["a"]
    assert [h.document_id for h in index.search("cloud cost", source="api")] == ["b"]


def test_remove_document_removes_postings():
    index = LexicalIndex()
    item = record("a", "Search", "uniqueunicornterm")
    index.index_document(item, chunk_text(item.id, item.content, max_chars=100, overlap=5, min_chunk_chars=10))
    assert index.search("uniqueunicornterm")
    index.remove_document("a")
    assert index.search("uniqueunicornterm") == []

# _ci-ref-83807

# _ci-ref-54663

# _ci-ref-31093

# _ci-ref-84128

# _ci-ref-79041

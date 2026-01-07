from docintel.extraction import extract_domains, extract_metadata


def test_extract_metadata_finds_entities():
    text = "Email ops@example.com on 2026-08-18. Pay USD 1,250.50. Visit https://example.com/a. Call +91 98765 43210."
    result = extract_metadata(text)
    assert result.emails == ["ops@example.com"]
    assert result.dates == ["2026-08-18"]
    assert result.amounts == ["USD 1,250.50"]
    assert result.urls == ["https://example.com/a"]
    assert result.phones
    assert result.word_count > 5


def test_extract_metadata_empty_and_no_entities():
    empty = extract_metadata("")
    assert empty.word_count == 0
    assert empty.line_count == 0
    plain = extract_metadata("nothing sensitive here")
    assert plain.emails == []
    assert plain.amounts == []


def test_extract_domains_deduplicates_hosts():
    urls = ["https://Example.com/a", "https://example.com/b", "https://docs.python.org/3/"]
    assert extract_domains(urls) == ["example.com", "docs.python.org"]

# _ci-ref-50654

# _ci-ref-26961

# _ci-ref-49936

# _ci-ref-46780

# _ci-ref-19882

# _ci-ref-73208

# _ci-ref-59947

# _ci-ref-37600

# _ci-ref-23622

# _ci-ref-71349

# _ci-ref-34434

# _ci-ref-28623

# _ci-ref-77081

# _ci-ref-85784

# _ci-ref-63347

# _ci-ref-17954

# _ci-ref-46231

# _ci-ref-38476

# _ci-ref-55656

# _ci-ref-23824

# _ci-ref-70774

# _ci-ref-23941

# _ci-ref-10285

# _ci-ref-48116

# _ci-ref-23768

# _ci-ref-84211

# _ci-ref-66811

# _ci-ref-88586

# _ci-ref-70062

# _ci-ref-84095

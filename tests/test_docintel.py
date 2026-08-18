from docintel.models import DocumentIn
from docintel.service import DocumentService

def test_ingest_route_extract_search():
    s=DocumentService();d=s.ingest(DocumentIn(title="Invoice 42",text="Payment due USD 125.00. Contact billing@example.com for payment details."))
    assert d.metadata["route"]=="finance"
    assert "billing@example.com" in d.metadata["emails"]
    hits=s.search("payment details")
    assert hits and hits[0]["document_id"]==d.id

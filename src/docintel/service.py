from uuid import uuid4
from .models import DocumentIn,Document,Chunk
from .chunking import chunk_text
from .extraction import extract_metadata
from .index import InvertedIndex
from .workflow import route_document
class DocumentService:
    def __init__(self):self.docs={};self.index=InvertedIndex()
    def ingest(self,item:DocumentIn)->Document:
        did=str(uuid4());meta={**item.metadata,**extract_metadata(item.text),"route":route_document(item.title,item.text)}
        chunks=[Chunk(id=f"{did}:{i}",document_id=did,ordinal=i,text=t) for i,t in enumerate(chunk_text(item.text))]
        doc=Document(id=did,title=item.title,text=item.text,metadata=meta,chunks=chunks);self.docs[did]=doc
        for c in chunks:self.index.add(c)
        return doc
    def get(self,did):
        if did not in self.docs:raise KeyError(did)
        return self.docs[did]
    def search(self,q,limit=10):return self.index.search(q,limit)

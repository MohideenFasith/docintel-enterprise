from fastapi import FastAPI,HTTPException,Query
from .models import DocumentIn
from .service import DocumentService
app=FastAPI(title="DocIntel Enterprise",version="0.1.0");service=DocumentService()
@app.get("/health")
def health():return {"status":"ok"}
@app.post("/documents",status_code=201)
def ingest(d:DocumentIn):return service.ingest(d)
@app.get("/documents/{did}")
def get(did:str):
    try:return service.get(did)
    except KeyError:raise HTTPException(404,"document not found")
@app.get("/search")
def search(q:str=Query(min_length=2),limit:int=Query(10,ge=1,le=100)):return service.search(q,limit)

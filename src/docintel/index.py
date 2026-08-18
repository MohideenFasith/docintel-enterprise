import re
from collections import defaultdict
TOKEN=re.compile(r"[a-z0-9]{2,}")
def tokens(text:str):return TOKEN.findall(text.lower())
class InvertedIndex:
    def __init__(self):self.postings=defaultdict(lambda:defaultdict(int));self.chunks={}
    def add(self,chunk):
        self.chunks[chunk.id]=chunk
        for t in tokens(chunk.text):self.postings[t][chunk.id]+=1
    def search(self,query:str,limit:int=10):
        scores=defaultdict(int)
        for t in tokens(query):
            for cid,n in self.postings.get(t,{}).items():scores[cid]+=n
        ranked=sorted(scores.items(),key=lambda x:(-x[1],x[0]))[:limit]
        return [{"chunk_id":cid,"score":score,"document_id":self.chunks[cid].document_id,"text":self.chunks[cid].text} for cid,score in ranked]

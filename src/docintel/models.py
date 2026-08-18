from pydantic import BaseModel,Field
class DocumentIn(BaseModel): title:str=Field(min_length=1,max_length=300); text:str=Field(min_length=1,max_length=2_000_000); metadata:dict[str,str]=Field(default_factory=dict)
class Chunk(BaseModel): id:str; document_id:str; ordinal:int; text:str
class Document(BaseModel): id:str; title:str; text:str; metadata:dict[str,str]=Field(default_factory=dict); chunks:list[Chunk]=Field(default_factory=list)

def chunk_text(text:str,max_chars:int=700,overlap:int=80)->list[str]:
    text=" ".join(text.split())
    if max_chars<=overlap:raise ValueError("max_chars must exceed overlap")
    chunks=[]; start=0
    while start<len(text):
        end=min(len(text),start+max_chars)
        if end<len(text):
            cut=text.rfind(" ",start,end)
            if cut>start+max_chars//2:end=cut
        chunks.append(text[start:end].strip())
        if end>=len(text):break
        start=max(start+1,end-overlap)
    return [c for c in chunks if c]

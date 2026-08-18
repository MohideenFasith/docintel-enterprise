def route_document(title:str,text:str)->str:
    hay=(title+" "+text[:1000]).lower()
    if any(k in hay for k in ("invoice","amount due","payment")):return "finance"
    if any(k in hay for k in ("contract","agreement","terms")):return "legal"
    if any(k in hay for k in ("resume","curriculum vitae","candidate")):return "hr"
    return "general"

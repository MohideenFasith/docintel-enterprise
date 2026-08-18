import re
def extract_metadata(text:str)->dict[str,str]:
    emails=sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",text)))
    amounts=sorted(set(re.findall(r"(?:USD|EUR|INR|\$|€|₹)\s?[0-9][0-9,]*(?:\.[0-9]{1,2})?",text)))
    return {"emails":",".join(emails),"amounts":",".join(amounts)}

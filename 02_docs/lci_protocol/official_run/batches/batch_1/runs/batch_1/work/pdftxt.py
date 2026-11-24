import sys; sys.path.insert(0,'/tmp/pylib')
import pypdf
f=sys.argv[1]; kw=sys.argv[2:] 
r=pypdf.PdfReader(f)
out=[]
for i,p in enumerate(r.pages):
    t=p.extract_text() or ""
    out.append(f"--- page {i+1}\n"+t)
txt="\n".join(out)
if kw:
    import re
    lines=txt.split("\n")
    for j,l in enumerate(lines):
        if any(k.lower() in l.lower() for k in kw): print(j,l[:200])
else: print(txt[:6000])

import sys; sys.path.insert(0,'/tmp/pylib')
import pypdf
r=pypdf.PdfReader(sys.argv[1])
open(sys.argv[2],'w').write("\n".join(f"--- page {i+1}\n"+(p.extract_text() or "") for i,p in enumerate(r.pages)))

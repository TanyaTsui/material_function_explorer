from bwh import *
for n,l in [("market for hydrated lime, packed","CH"),]:
    pass
import sys
for q in sys.argv[1:]:
    for a in DB:
        if q.lower() in a['name'].lower() or q.lower() in a['reference product'].lower():
            print(a['name'],'|',a['reference product'],'|',a['location'],'|',a['unit'])

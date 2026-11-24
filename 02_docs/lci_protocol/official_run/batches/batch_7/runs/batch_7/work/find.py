import bwx,sys,bw2data as bd
pre=sys.argv[1]; locs=sys.argv[2].split(',') if len(sys.argv)>2 else None
for a in bd.Database(bwx.DB):
    n=a['name']
    if n.startswith(pre) and (not locs or a['location'] in locs): print(n,'|',a['reference product'],'|',a['location'],'|',a['unit'],'|',a['code'])

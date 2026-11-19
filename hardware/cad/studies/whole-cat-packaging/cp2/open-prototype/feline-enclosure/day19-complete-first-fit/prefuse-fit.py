from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
parts={'fixed':rd(H19/'space-map.json')['members']+[n for n in D.members if n.startswith('I19_FuseBand_')],'yaw':[],'pitch':[]}
for w,qs in rd(P/'prefuse-extensions.json').items():
 for q in qs:
    p=np.array(q['points']);od=2.5
    if w=='XA02':
        d=np.linalg.norm(p-p[-1],axis=1);screen(w+' pad',0,0,circle(p[(d<2)&(d>.2)],.35));p=p[d>=2]
    screen(w+' '+str(q['factory_stock_mm']),0,0,circle(p[1:-1],od/2))
wr('prefuse-fit.json',dict(rows=rows));print([(r['field'],r['hits']) for r in rows if r['hits']])

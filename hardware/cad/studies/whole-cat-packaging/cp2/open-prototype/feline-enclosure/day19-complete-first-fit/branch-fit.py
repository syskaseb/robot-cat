from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
parts={'fixed':rd(H19/'space-map.json')['members']+[n for n in D.members if n.startswith('I19_FuseBand_')],'yaw':[],'pitch':[]}
data=rd(P/'changed-branch-lays.json')
for w,qs in data['rows'].items():
 for q in qs:
    p=np.array(q['points']);od=q['diameter']
    if w=='XA02':
        ds=np.linalg.norm(p-p[-1],axis=1);screen(w+' bare',0,0,circle(p[(ds<2)&(ds>.19)],.38));p=p[ds>=2]
    if w=='XA03':
        ds=np.linalg.norm(p-p[0],axis=1);screen(w+' bare',0,0,circle(p[(ds<2)&(ds>.19)],.38));p=p[ds>=2]
    screen(w+' '+str(q['stock_mm']),0,0,circle(p[1:-1],od/2))
wr('changed-branch-fit.json',dict(rows=rows));print([(r['field'],[(h['part'],h['point']) for h in r['hits']]) for r in rows if r['hits']])

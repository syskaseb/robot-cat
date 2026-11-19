from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
parts={'fixed':['H19_FrontFrame'],'yaw':[],'pitch':[]};lo=np.array([-74.6,15.6,73.1]);hi=np.array([-52.7,30.7,76.15])
def region(tag,ps):
 p=np.asarray(ps).reshape(-1,3);p=p[np.all((p>=lo)&(p<=hi),axis=1)]
 if len(p):screen(tag,0,0,p)
def run(tag,ps,dia):
 p=np.asarray(ps);ok=np.flatnonzero(np.all((p>=lo-dia)&(p<=hi+dia),axis=1))
 if len(ok):region(tag,circle(p,dia/2))
for k,v in rd(P/'lower-approaches.json').items():run(k,v['points'],v['diameter'])
b=rd(P/'changed-branch-lays.json')['rows'];b.update(rd(P/'fl-hand-space.json'))
for k,arr in b.items():
 for i,v in enumerate(arr):run(k+str(i),v['points'],v['diameter'])
for k,v in rd(H19/'named-approaches.json').items():run(k,v['points'],v['diameter'])
for k,v in rd(H19/'whole-termination-plan.json')['FHAC'].items():
 if v.get('minimum_lay'):run(k,v['minimum_lay'],4.2)
wr('affected-bearer.json',dict(rows=rows,bounds=[lo.tolist(),hi.tolist()],scope='only new short HY bearer surrounding the open driver approach; rear change removes material',native_sha256=sha(native)));print([(r['field'],r['hits']) for r in rows if r['hits']])

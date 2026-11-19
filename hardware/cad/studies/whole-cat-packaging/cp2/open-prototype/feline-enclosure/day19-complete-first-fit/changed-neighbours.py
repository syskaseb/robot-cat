from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
front=[[-121,-29,40,-65,-24,75],[-77,-23,40,-48,36,98],[-28.1,-39.1,41,10.1,-20.7,90.5],[-111.95,-103.1,40.4,13,-65,91],[-177,-114,100,-143,-100,199]]
rear=[[108,37,40,116,41,76]]
boxes={'H19_FrontFrame':front,'E19_RearBase':rear,'E19_ForeLid':[[-27.2,69.8,142.6,13.3,98.3,173.2]],'E19_RearLid':[[58.6,-21.5,117.4,63.4,-15.1,173]],'WAGO615_power_0_0':[D.bounds('WAGO615_power_0_0')]}
for n in ['NIGHT_INLINE_FL_W026','NIGHT_INLINE_FL_W041']:boxes[n]=[D.bounds(n)]
for n in D.members:
 if n.startswith('I19_FuseBand_'):boxes[n]=[D.bounds(n)]
def touched(tag,points):
 global parts
 pts=np.asarray(points).reshape(-1,3)
 for n,regions in boxes.items():
    mask=np.zeros(len(pts),dtype=bool)
    for b in regions:mask|=np.all((pts>=b[:3])&(pts<=b[3:]),axis=1)
    if np.any(mask):
        parts={'fixed':[n],'yaw':[],'pitch':[]};screen(tag,0,0,pts[mask])
for w,q in rd(H19/'named-approaches.json').items():touched(w,circle(q['points'],q['diameter']/2))
plan=rd(H19/'whole-termination-plan.json')
for n,q in plan['FHAC'].items():
 if n=='F_HP.in':continue
 if q.get('minimum_lay'):
    p=np.asarray(q['minimum_lay']);p=p[np.r_[True,np.linalg.norm(np.diff(p,axis=0),axis=1)>.001]]
    touched(n+' factory installation',circle(p,2.1))
l=rd(F/'service-lay.json')
for q in [*l['fixed'].values(),*l['pitch_transfer']]:
 if q['unit']=='DATA500':touched('DATA500',circle(q['points'],3.4));continue
 pp=profile(q['points'],3.5,1.8)
 for y in ([-20,0,20] if q['unit']=='MG_pitch' else [0]):
    r,t=transforms(y,0)['yaw'];touched(q['unit']+str(q.get('yaw',y)),pp.reshape(-1,3)@r.T+t if q['unit']=='MG_pitch' else pp)
src=rd(O/'day19-whole-appearance-and-moving-neck-correction/whole-lay.json')
ffc=rd(O/'day18-open-front-assembly/occupied-layout.json')['FFC']
for q in src['motion']:
 for i,p in enumerate(q['cores']):touched('ToF'+str((i,q['yaw'],q['pitch'])),circle(p,1.05))
 touched('FFC'+str((q['yaw'],q['pitch'])),next(v['corners'] for v in ffc if v['yaw']==q['yaw'] and v['pitch']==q['pitch']))
wr('changed-profiles.json',dict(actual_candidate_tests=len(rows),rows=rows));print([(r['field'],r['hits']) for r in rows if r['hits']])

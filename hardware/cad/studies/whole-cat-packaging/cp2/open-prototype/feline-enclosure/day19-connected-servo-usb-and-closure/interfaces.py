"""Named installed hazards, with exact local material witness after section screening."""
from pathlib import Path
import math,json,numpy as np,runpy,ast,hashlib
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core';C=P.parent/'day19-closed-head-neck-and-module-interfaces';D19=P.parent/'day19-whole-appearance-and-moving-neck-correction'
src=(C/'changed-seam.py').read_text()
exec(src[:src.index('lay=json.loads')].replace('whole-cat19C.FCStd','whole-cat19F.FCStd'))
qsrc=(E/'occupied-check.py').read_text()
exec(qsrc[qsrc.index('def circle('):qsrc.index("if sys.argv[1]=='final'")])
exec(qsrc[qsrc.index('from collections import defaultdict'):qsrc.index('for q in routes:')])
lay=json.loads((P/'service-lay.json').read_bytes())
real=['TTP223_touch']+[n for n in real if n not in ['BR_FLANK_HP_PAIR','ReSpeakerLite_on_REMOVABLE_back']]+['E19_ReSpeakerSource','F19_ForeCap','F19_RearCap']
parts=dict(fixed=real,yaw=['E19_UpperYawCover','MG92B_Head_pitch','D19D_YawSaddle','BR_FLANK_HP_PAIR'],pitch=['D19D_PitchBack','D19D_OpticsCarrier'])
def write():
    (P/'occupied-check.json').write_bytes((json.dumps(dict(rows=rows,sha256=hashlib.sha256(native.read_bytes()).hexdigest(),meaning='positive exact point in installed material rejects the sampled lay. Nine poses are discrete. Clear sections are a screening result.',physical_PASS=False),indent=1)+'\n').encode())
for q in list(lay['fixed'].values())+lay['pitch_transfer']:
    name=q['unit'];yaws=[-20,0,20] if name=='MG_pitch' else [q.get('yaw',0)]
    pts=np.asarray(q['points'])
    for y in yaws:
        # Both connector mouths are intentionally mated. First and last cross-sections
        # in the mouth plane do not qualify connector insertion or housing contact.
        a=circle(pts,3.4) if name=='DATA500' else profile(pts,3.5,1.8)
        if name=='MG_pitch':
            R,T=transforms(y,0)['yaw'];a=a.reshape(-1,3)@R.T+T
        screen(name,y,0,a)
        for i,b in enumerate(q.get('branches',[])):screen(name+' fan '+str(i),y,0,circle(np.linspace(b[0],b[-1],41),.9))
    if name=='MG_pitch':
        basepoints=profile(pts,3.5,1.8).reshape(-1,3)
        for yy in [-20,0,20]:
            R,T=transforms(yy,0)['yaw']
            for pp in [-10,10]:screen('MG_pitch',yy,pp,basepoints@R.T+T)
    write()
old=json.loads((D19/'whole-lay.json').read_bytes())
ffc=json.loads((source/'occupied-layout.json').read_bytes())['FFC']
# Same four actual jacket profiles at the changed forelid and adjoining moving cheek.
parts['fixed']=['E19_ForeLid','E19_RearLid','E19_BUS_PCB','E19_BUS_population','D18C_DATA_BUS_FULL26_PROJECT_BOOT','F19_ForeCap','F19_RearCap','D19D_YawMatedPair','B19_TailMatedPair','E19_ReSpeakerSource','Speaker']
for q in old['motion']:
    y,p=q['yaw'],q['pitch']
    for k,cc in enumerate(q['cores']):screen('ToF '+str(k),y,p,circle(cc,1.05))
    screen('FFC190',y,p,next(v['corners'] for v in ffc if v['yaw']==y and v['pitch']==p))
write()
for i,q in enumerate(old['fixed']):screen('ToF fixed '+str(i),0,0,circle(q['centreline'][:-2],1.05))
# A profile exactly at the mate face is half-open at its endpoint. Compare every
# full-profile point in the mouth cross-section in the co-yaw connector frame.
for q in lay['pitch_transfer']:
    y=q['yaw'];R,T=transforms(y,0)['yaw'];local=(profile(q['points'],3.5,1.8).reshape(-1,3)-T)@R
    b=D.bounds('BR_FLANK_HP_PAIR');near=local[np.all(local[:,1:]>=b[1:3]-.00002,axis=1)&np.all(local[:,1:]<=b[4:] +.00002,axis=1)&(local[:,0]<b[3]+4)]
    for row in rows:
        if row['field']!='JR_pitch' or row['yaw']!=y:continue
        for hit in row['hits']:
            if hit['part']=='BR_FLANK_HP_PAIR' and len(near):
                hit['minimum_signed_distance_from_mouth_mm']=float(min(near[:,0])-b[3])
                hit['classification']='end-face rounding within 0.00002 mm' if min(near[:,0])-b[3]>=-.00002 else 'material intrusion'
write();print([(r['field'],r['yaw'],r['pitch'],[h['part'] for h in r['hits']]) for r in rows if r['hits']][:40])

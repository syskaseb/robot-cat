"""Named physical decisions on the changed layer only, sampled jacket/installed hardware."""
from pathlib import Path
import json,numpy as np,ast,runpy,math,hashlib,sys
P=Path(__file__).parent;C=P.parent/'day19-closed-head-neck-and-module-interfaces';D19=P.parent/'day19-whole-appearance-and-moving-neck-correction'
src=(C/'changed-seam.py').read_text()
exec(src[:src.index('lay=json.loads')].replace('whole-cat19C.FCStd','whole-cat19E.FCStd'))
routes=json.loads((P/('unit-layout.json' if sys.argv[1]=='first' else 'installed-looms.json')).read_bytes())['rows'];lay=json.loads((D19/'whole-lay.json').read_bytes())
def circle(path,r):
    c=np.asarray(path);u=np.gradient(c,axis=0);u/=np.linalg.norm(u,axis=1)[:,None];v=np.eye(3)[np.argmin(abs(u),axis=1)];v-=u*(v*u).sum(axis=1)[:,None];v/=np.linalg.norm(v,axis=1)[:,None];w=np.cross(u,v)
    return np.array([c]+[c+r*(math.cos(a)*v+math.sin(a)*w) for a in np.arange(10)*math.tau/10]).reshape(-1,3)
real=['E19_ForeBase','E19_RearBase','E19_ForeLid','E19_RearLid','E19_FrontShroud','E19_BUS_PCB','E19_BUS_population','D19D_YawMatedPair','BR_FLANK_HP_PAIR','B19_TailMatedPair','F0_FHAC0002_30A','Battery_GEA223S30X6GT','Pi4B_actual_PCB','Speaker','ReSpeakerLite_on_REMOVABLE_back','BNO085','MAX98357A_amp','MAIN_Pololu4853','AUX_Pololu4092','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','MG92B_Tail','S0_body','OP_S1_PRIMARY_CASE_CONSERVATIVE','Monitor_MOD05015']+[n for n in D.members if n.startswith(('Motor_ATO','NIGHT_INLINE','E19_Wago','PBAY_','WAGO415_')) and n!='WAGO415_data_1_0']
if sys.argv[1]=='final':real=[n for n in real if n!='ReSpeakerLite_on_REMOVABLE_back']+['E19_ReSpeakerSource','E19_BatteryDoor']
parts=dict(fixed=real,yaw=['E19_UpperYawCover','D19D_YawSaddle','MG92B_Head_pitch'],pitch=['D19D_PitchBack','D19D_OpticsCarrier'])
# Cache only objects whose bounds meet a tested field; exact witness when the surface mesh suggests material.
from collections import defaultdict
class Cache(dict):
    def __missing__(self,n):
        val=mesh(n);self[n]=val;return val
meshcache=Cache();rows=[]
exec(src[src.index('def screen('):src.index('for y in (-20')])
for q in routes:
    name=q['unit'];pts=q['centreline'];y=q.get('yaw',0)
    if name=='DATA500':a=circle(pts,3.4)
    else:a=profile(pts,3.5,1.8)
    screen(name,y,0,a)
    if name.startswith('JR300'):
        end=np.array(pts[-1]);u=np.array(q['fan_direction'])
        for k in [-1,0,1]:
            d=u*np.cos(.125*k)+np.array([0,1,0])*np.sin(.125*k);screen(name+' lap '+str(k),0,0,circle(np.linspace(end,end+42*d,55),.9))
# Focus the ToF/FFC check on the new source BUS + its full USB approach, moving
# cover and microphone, rather than retesting 123 illustrative axes.
parts['fixed']=['E19_BUS_PCB','E19_BUS_population','D18C_DATA_BUS_FULL26_PROJECT_BOOT','E19_ForeLid','E19_RearLid','E19_FrontShroud','ReSpeakerLite_on_REMOVABLE_back','E19_ForeBase','E19_RearBase']
ffc=json.loads((source/'occupied-layout.json').read_bytes())['FFC']
if sys.argv[1]=='final':parts['fixed']=[n for n in parts['fixed'] if n!='ReSpeakerLite_on_REMOVABLE_back']+['E19_ReSpeakerSource']
for q in lay['motion']:
    y,p=q['yaw'],q['pitch'];R,T=transforms(y,p)['pitch']
    for k,cc in enumerate(q['cores']):
        screen('ToF moving '+str(k),y,p,circle(cc,1.05))
    screen('FFC190',y,p,next(v['corners'] for v in ffc if v['yaw']==y and v['pitch']==p))
for i,q in enumerate(lay['fixed']):screen('ToF body '+str(i),0,0,circle(q['centreline'][:-2],1.05))
out=dict(source_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),rows=rows,physical_PASS=False,meaning='material witness rejects proposed lay. Port boots project fields; conductor/conductor crossings not treated as hard part contacts.')
(P/('occupied-check-'+sys.argv[1]+'.json')).write_text(json.dumps(out,indent=1)+'\n')
print([(q['field'],[h['part'] for h in q['hits']]) for q in rows if q['hits']][:26])

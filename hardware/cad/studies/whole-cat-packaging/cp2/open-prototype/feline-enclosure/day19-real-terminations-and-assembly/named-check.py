from pathlib import Path
import math,json,hashlib,ast,runpy,numpy as np,sys
P=Path(__file__).parent;C=P.parent/'day19-closed-head-neck-and-module-interfaces';E=P.parent/'day19-simple-box-common-core';F=P.parent/'day19-connected-servo-usb-and-closure'
src=(C/'changed-seam.py').read_text();exec(src[:src.index('lay=json.loads')].replace('whole-cat19C.FCStd','whole-cat19G.FCStd'))
qsrc=(E/'occupied-check.py').read_text();exec(qsrc[qsrc.index('def circle('):qsrc.index('real=[')])
exec(qsrc[qsrc.index('from collections import defaultdict'):qsrc.index('for q in routes:')])
s=src[src.index('def screen('):src.index('for y in (-20')]
exec(s)
tr=json.loads((P/'named-approaches.json').read_bytes());plan=json.loads((P/'whole-termination-plan.json').read_bytes())
hard=['E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','E19_ForeBase','E19_RearBase','E19_FrontShroud','E19_ReSpeakerSource','Speaker','G19_PermaProto1608','E19_BUS_PCB','E19_BUS_population','Battery_GEA223S30X6GT','Pi4B_actual_PCB','OP_S1_PRIMARY_CASE_CONSERVATIVE','S0_body','F0_FHAC0002_30A','MG92B_Tail','PCA9685_Adafruit815_PCB','BNO085','MAX98357A_amp','E19_KeyedTail','MAIN_Pololu4853']+[n for n in D.members if n.startswith(('E19_Wago','PBAY_F_','Motor_ATO','WAGO415','WAGO615')) and n!='WAGO415_data_1_0']
parts={'fixed':hard,'yaw':['E19_UpperYawCover','BR_FLANK_HP_PAIR'],'pitch':['D19D_PitchBack']}
def save():
 (P/(sys.argv[1]+'-profiles.json')).write_bytes((json.dumps(dict(rows=rows,native=hashlib.sha256(native.read_bytes()).hexdigest(),basis='named crossings of shared supply/return stations, purchased ports and revised material; no manufacturing axes'),indent=1)+'\n').encode())
for w in ['W002','W003','W078','W079','W080','XB12','XB13','XS13','XB22','XB23','XS23','XB32','XB33','XS33','EXT025','EXT023']:
 q=tr[w];p=np.asarray(q['points']);screen(w,0,0,circle(p[1:-1],q['diameter']/2));save()
for k,q in enumerate(plan['JR']['pitch']['branches']):
 for yaw in [-20,0,20]:screen('pitch free fan '+str(k),yaw,0,circle(q['points'],.9))
# Reuse the expensive installed world by identity; screen old FFC and ToF only against the eight affected members.
parts={'fixed':['E19_RearBase','E19_FrontShroud','E19_ForeLid','F19_ForeCap','E19_ReSpeakerSource','G19_MIC_C_PlugAllow'],'yaw':['E19_UpperYawCover','G19_RemoteR_pitch'],'pitch':[]}
old=json.loads((P.parent/'day19-whole-appearance-and-moving-neck-correction/whole-lay.json').read_bytes())
ffc=json.loads((source/'occupied-layout.json').read_bytes())['FFC']
for q in old['motion']:
 y,p=q['yaw'],q['pitch']
 for i,cc in enumerate(q['cores']):screen('ToF '+str(i),y,p,circle(cc,1.05))
 screen('FFC190',y,p,next(v['corners'] for v in ffc if v['yaw']==y and v['pitch']==p))
save();print([(r['field'],[v['part'] for v in r['hits']]) for r in rows if r['hits']][:25])

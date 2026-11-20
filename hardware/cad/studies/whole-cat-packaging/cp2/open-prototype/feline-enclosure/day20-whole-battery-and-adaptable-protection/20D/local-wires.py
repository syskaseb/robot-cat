"""Check typed local inlet leads and the two new regional entries."""
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile
from xml.etree import ElementTree
import json, os
import numpy as np

import FreeCAD as App
import Part

d=Path(__file__).resolve().parent
g=run_path(str(d/'geometry.py')); w=run_path(str(d/'layout.py'))['wire_budgets']()
p=d.parent/'20C'/'whole-cat20C.FCStd'
spec={
'W075':(w['W075']['points'],4.8),
'W076_factory':(w['W076_complete_FHAC_out']['shape_points'],4.8),
'W001':(w['W001']['allocated_waypoints'],3.1),
'W076_custom':(w['W076_custom']['allocated_waypoints'],4.2),
}
rigid=['H19_FrontFrame','E19_RearBase','E19_ForeLid','E19_RearLid','PCA9685_Adafruit815_PCB',
       'E19_WagoForePos','E19_WagoRearPos','E19_WagoForeNeg','E19_WagoRearNeg',
       'Pi4B_actual_PCB','BNO085','D19D_YawSaddle','PBAY_P_AUX','E19_ReSpeakerSource',
       'WAGO615_power_0_0','S0_body','S0_ring_IN_0_0','C20_MTA_FR','C20_MTA_RR']
regions=['Pi_components_and_cooling','G19_Group_JRP','D19_SIDE_BUNDLE_POS','H19_MainTrunk']
def sampled(points,step=4.0):
    arrays=[np.asarray(points[0]).reshape(1,3)]
    for a,b in zip(points,points[1:]):
        count=max(1,int(np.ceil(np.linalg.norm(np.asarray(b)-np.asarray(a))/step)))
        arrays.append(np.linspace(a,b,count+1)[1:])
    return np.concatenate(arrays)

with ZipFile(p) as z:
    xml=ElementTree.fromstring(z.read('Document.xml'))
    members={x.get('name'):x.find('./Properties/Property[@name="Shape"]/Part') for x in xml.findall('./ObjectData/Object')}
    def read(n):
        s=Part.Shape();s.importBrepFromString(z.read(members[n].get('file')).decode('ascii'));return s
    ref={n:read(n) for n in rigid+regions if members.get(n) is not None}
ref.update({k:v for k,v in g['forms']().items() if 'Clamp' not in k})
bb={n:np.asarray(g['bounds'](s),float) for n,s in ref.items()}
results={}
for n in ('W076_factory','W001','W076_custom'):
    line,od=spec[n]
    points=sampled(line); rad=od/2
    hits={}; clear={}
    for label,s in ref.items():
        box=bb[label]
        candidates=points[((points>=box[:3]-rad-1.5)&(points<=box[3:]+rad+1.5)).all(axis=1)]
        if not len(candidates):
            continue
        local_lo=candidates.min(axis=0)-rad-2.
        local_hi=candidates.max(axis=0)+rad+2.
        s=s.common(g['cube']([*local_lo,*local_hi]))
        if s.isNull() or not s.Faces:
            continue
        near=None
        for xyz in candidates:
            v=Part.Vertex(App.Vector(*xyz))
            distance=s.distToShape(v)[0]-rad
            if distance>0 and s.isInside(v.Point,0.001,False):
                distance=-rad
            if near is None or distance<near[0]:
                near=[round(float(distance),4),xyz.round(3).tolist()]
        if near is not None:
            (hits if near[0]<-0.05 else clear)[label]=near
    results[n]={'outer_OD_mm':od,'contact_needing_local_disposition':hits,'sampled_nearby_gaps_mm':clear}
    print(n,hits,clear,flush=True)
f=d/'20D-local-wires.json';t=f.with_suffix('.tmp')
before=f.read_bytes() if f.exists() else None
with t.open('x',encoding='utf-8',newline='\n') as s:
    json.dump(results,s,indent=2);s.write('\n')
assert (f.read_bytes() if f.exists() else None)==before
os.replace(t,f)

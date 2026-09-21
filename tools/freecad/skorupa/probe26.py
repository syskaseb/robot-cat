"""Read-only supplier geometry / battery-service audit; no source CAD changes."""
from pathlib import Path
import json,hashlib
import FreeCAD as A
import Part
from probe21 import world, visible_names

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v26'
SOURCE=ROOT/'hardware/skorupa/v25/Kot_v25_DOMOWA_OSLONA.FCStd'

def bbox(s):
    b=s.BoundBox
    return [b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]

def main():
    OUT.mkdir(exist_ok=True)
    step=Part.Shape()
    step.read(str(ROOT/'hardware/reference/waveshare-bus-servo-adapter-a/Bus Servo Adapter (A).step'))
    report={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'supplier_step':{'bounds':bbox(step),'solids':len(step.Solids),'valid':step.isValid()},'step_solids':[],'battery_hits':[]}
    for i,s in enumerate(step.Solids):
        b=s.BoundBox
        if b.XLength>25 or b.YLength>25:
            cylinders=[]
            for f in s.Faces:
                if isinstance(f.Surface,Part.Cylinder):
                    c=f.Surface
                    cylinders.append({'radius':c.Radius,'axis':list(c.Axis),'center':list(c.Center)})
            report['step_solids'].append({'index':i,'bbox':bbox(s),'volume':s.Volume,'cylinders':cylinders})
    d=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
    shapes={o.Name:world(o) for o in d.Objects if o.Name in vis and o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()}
    moving=['Part__Feature005','BatteryCarrier23','Battery','BatteryLiner23','BatteryStrap123','BatteryStrap223']+['Battery'+kind+end+side for kind in ['Screw','Nut'] for end in ['Front','Rear'] for side in ['L','R']]
    for dz in [.1,1,5,10,20]:
        for n in moving:
            s=shapes[n].copy();s.translate(A.Vector(0,0,-dz))
            for other,t in shapes.items():
                if other in moving or other=='Belly22' or other.startswith('BellyScrew'):continue
                if s.BoundBox.intersect(t.BoundBox):
                    v=s.common(t).Volume
                    if v>.001:report['battery_hits'].append({'dz':dz,'part':n,'obstacle':other,'volume':v})
    (OUT/'supplier-service-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()

"""Read-only service-route audit of v23, before deciding new geometry."""
from pathlib import Path
import json
import FreeCAD as A
import Part
from probe21 import world,visible_names
from build22 import box
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'hardware/skorupa/v23/Kot_v23_AKUMULATOR_PETG.FCStd'
OUT=ROOT/'hardware/skorupa/v24'
V=A.Vector
MOVING=['Part__Feature005','BatteryCarrier23','Battery','BatteryLiner23','BatteryStrap123','BatteryStrap223']+['Battery'+kind+end+side for kind in ['Screw','Nut'] for end in ['Front','Rear'] for side in ['L','R']]

def main():
    OUT.mkdir(exist_ok=True)
    d=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
    shapes={o.Name:world(o) for o in d.Objects if o.Name in vis and o.isDerivedFrom('Part::Feature') and not o.Shape.isNull() and not o.Name.startswith('Axis_')}
    moving=Part.makeCompound([shapes[n] for n in MOVING])
    targets={n:s for n,s in shapes.items() if n not in MOVING and n!='Belly22'}
    report=dict(removal=[],frame_axes=[],plate_faces=[])
    for dz in [.1,1,5,10,20,30,40,60,90,120,150]:
        s=moving.copy(); s.translate(V(0,0,-dz)); hits=[]
        for n,t in targets.items():
            if s.BoundBox.intersect(t.BoundBox):
                v=s.common(t).Volume
                if v>.001: hits.append([n,v])
        report['removal'].append(dict(down_mm=dz,hits=hits)); print(dz,hits,flush=True)
    for n in ['FrameFront20','FrameRear20']:
        s=shapes[n]
        faces=[]
        for f in s.Faces:
            surf=f.Surface
            if hasattr(surf,'Radius') and hasattr(surf,'Axis') and abs(surf.Axis.z)>.999 and abs(surf.Radius-1.025)<.001 and f.BoundBox.ZMax<2:
                faces.append([round(surf.Center.x,4),round(surf.Center.y,4),surf.Radius*2])
        report['frame_axes'].append(dict(name=n,bores=faces))
    for i,f in enumerate(shapes['Part__Feature005'].Faces,1):
        if f.Area>1000: report['plate_faces'].append(dict(face=i,area=f.Area,zmin=f.BoundBox.ZMin,zmax=f.BoundBox.ZMax,normal=list(f.normalAt(0,0))))
    # Conservative space reservation only: NOT a known connector or cable.
    for name,s in [('plug_service_box',box(78,104,-12,12,10,31)),('riser_7mm_bundle',Part.makeCylinder(3.5,47,V(98.7,0,31)))]:
        hits=[]
        for n,t in shapes.items():
            if s.BoundBox.intersect(t.BoundBox):
                v=s.common(t).Volume
                if v>.001: hits.append([n,v])
        report[name]=hits
    (OUT/'service-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)
if __name__=='__main__': main()

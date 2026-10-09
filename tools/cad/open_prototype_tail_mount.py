"""Qualify the complete CP2 tail mechanical attachment, without wiring credit."""
from pathlib import Path
import json
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT = BASE / 'tail-mount-checkpoint'


def inspect():
    import FreeCAD as A
    OUT.mkdir(exist_ok=True)
    d = A.openDocument(str(BASE / 'OpenPrototypePlan.FCStd'))
    rows = []
    try:
        for o in d.Objects:
            if not hasattr(o, 'Shape') or o.Shape.isNull():
                continue
            b = o.Shape.BoundBox
            if (b.XMin < 128 and b.XMax > 108 and b.YMin < 28 and
                    b.YMax > -28 and b.ZMin < 70 and b.ZMax > 30):
                rows.append(dict(name=o.Name, label=o.Label, valid=o.Shape.isValid(),
                    bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                    solids=len(o.Shape.Solids)))
        print(json.dumps(rows, indent=2), flush=True)
        (OUT / 'mount-interface-inspection.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    finally:
        A.closeDocument(d.Name)


def plan():
    import FreeCAD as A
    import Part
    import open_prototype_side_source_routes as scene
    from open_prototype_tail_clearance import near, box, wire, profiles
    from check_main_p0_placement import SavedShapes
    tick=time.monotonic()
    p=json.loads((BASE/'wiring-checkpoint/source-group-allocation.json').read_text())['family']
    docs,fixed,rings,torso,paths=scene.load_scene(p)
    OUT.mkdir(exist_ok=True)
    result=dict(status='PLANNED_SHARED_TAIL_AND_MONITOR',contacts=[],errors=[],pairs=0,
        spacer_height_mm=19,spacer_diameter_mm=7,spacer_bore_mm=2.6,
        axes_xy_mm=[[x,y] for x in (112,122) for y in (-22.5,22.5)],
        monitor_bounds_mm=[45.5,37.5,47.72,86.5,62.5,59.72],
        physical_pass=False,selected=False,stage_completed=False)
    try:
        ctx=docs[2];mount=docs[1]
        for o in mount.Objects:
            if hasattr(o,'Shape') and not o.Shape.isNull() and ('Monitor' in o.Name or o.TypeId=='PartDesign::Body'):
                b=o.Shape.BoundBox
                print(json.dumps(dict(mount_object=o.Name,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])),flush=True)
        # New load path roots directly on the preserved P0 plate. Historical
        # 105mm electronics posts are NOT installed in the CP2 prototype.
        reader=SavedShapes();source=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
        xml=reader.doc(source)
        for n in ('Part__Feature038','FrameRear20'):
            s=reader.shape(source,n);s.Placement=reader.placement(xml['Rigid_'+n])*s.Placement
            fixed.append(('Root_'+n,s,'retained P0 material'))
        fixed=[r for r in fixed if r[0] not in ('Monitor_CP2','LowerCarrier')]
        proposed=[]
        carrier=mount.LowerCarrier.Shape.copy()
        for i,(x,y) in enumerate(result['axes_xy_mm']):
            s=Part.makeCylinder(3.5,19,A.Vector(x,y,38.52)).cut(Part.makeCylinder(1.3,19,A.Vector(x,y,38.52)))
            carrier=carrier.cut(Part.makeCylinder(3.8,15,A.Vector(x,y,38.52)))
            proposed.append((f'TailLift{i}',s))
        # Whole monitor relocation includes a rooted outrigger, four case pads
        # and two independent tie paths. No pad is floating in space.
        carrier=carrier.fuse(Part.makeBox(41,40.5,3,A.Vector(45.5,22,39.72)))
        for x in (45.5,82.5):
            for y in (37.5,58.5):
                carrier=carrier.fuse(Part.makeBox(4,4,5,A.Vector(x,y,42.72)))
        for x in (54,78):
            for y in (34,63):
                carrier=carrier.cut(Part.makeBox(2.8,3.5,5,A.Vector(x,y,38.72)))
        carrier=carrier.removeSplitter()
        proposed.append(('LowerCarrierMatched',carrier))
        proposed.append(('MonitorNew',Part.makeBox(41,25,12,A.Vector(45.5,37.5,47.72))))
        retained_profiles=profiles(p)
        # New lower-bound monitor pads are permitted only on the real carrier.
        for name,s in proposed:
            assert s.isValid() and len(s.Solids)==1
            for n,t,basis in fixed:
                if not near(s,t,0):continue
                result['pairs']+=1
                try:
                    assert t.isValid(),n
                    c=s.common(t);assert c.isValid()
                    if c.Volume>1e-5:result['contacts'].append(dict(a=name,b=n,volume_mm3=c.Volume,basis=basis))
                except Exception as e:result['errors'].append(dict(a=name,b=n,error=str(e)))
            for n,(parts,r,_,_) in retained_profiles.items():
                c=wire(parts)
                if not near(s,c,r):continue
                result['pairs']+=1;distance=s.distToShape(c)[0]
                if distance<r-1e-6:result['contacts'].append(dict(a=name,b=n,distance_mm=distance,required_mm=r))
        for i,(name,s) in enumerate(proposed):
            for n,t in proposed[i+1:]:
                if near(s,t,0):
                    result['pairs']+=1;v=s.common(t).Volume
                    if v>1e-5:result['contacts'].append(dict(a=name,b=n,volume_mm3=v))
        result['source_sha256']=reader.hashes
        result['worker_seconds']=time.monotonic()-tick
        result['finished_utc']=datetime.now(timezone.utc).isoformat()
        (OUT/'plate-rooted-shared-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result),flush=True)
    finally:
        for d in docs:
            if d.Name in A.listDocuments():A.closeDocument(d.Name)


if __name__ == '__main__':
    plan() if '--plan' in sys.argv else inspect()

"""Qualify the sole fore-neck domain witness without rerunning material pairs."""
import json
import time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from build_feline_layout_envelope import NECK_STATIONS


def main():
    tick=time.monotonic();source=OUT/'n01-reconciled-port-contracts-gate.json'
    dest=OUT/'n01-reconciled-port-contracts-qualified.json';assert not dest.exists()
    old=json.loads(source.read_text());assert old['status']=='COUPLED_CHANGED_CONTRACTS_REJECTED'
    assert not any(old[k] for k in ('contacts','reservation_contacts','jacket_conflicts','errors','wall_failures'))
    assert len(old['outside'])==1 and old['outside'][0]['name']=='W076/retained1/end'
    profiles=[]
    for x,width,zlow,zhigh in NECK_STATIONS:
        pts=[A.Vector(x,y,z) for y,z in ((-width/2,zlow),(width/2,zlow),(width/2,zhigh),(-width/2,zhigh))]
        profiles.append(Part.makePolygon(pts+[pts[0]]))
    neck=Part.makeLoft(profiles,True,True);assert neck.isValid() and len(neck.Solids)==1
    r=next(r for r in old['land_recipes'] if r['id']==old['outside'][0]['name'])
    s=Part.makeCylinder(r['radius_mm'],r['straight_mm'],A.Vector(*r['start_mm']),A.Vector(*r['axis']))
    outside=s.cut(neck);assert outside.isNull() or outside.isValid()
    assert outside.Volume<1e-5
    gap=s.distToShape(Part.makeCompound(neck.Shells))[0];assert gap>=3.65
    report=dict(status='CHANGED_PORTS_STATIC_CLEAR_IN_PLANNED_TORSO_NECK_FULL_WIRING_OPEN',
        selected=False,N01_complete=False,physical_pass=False,geometry_changed=False,
        source_material_pairs_reused=old['pairs'],unchanged_collision_or_motion_rerun=False,
        scope='15changed port contracts,2actual-reference crimp throat jacket lands, rotated POST_F0 and nominal K1474 mould. Static only; no all178/restraint/fullwiring/motion/native/skin approval.',
        original_rejection_retained=source.relative_to(ROOT).as_posix(),
        correction='Original checker used torso alone for foreS0 despite already planned overlapping neck. No cable/neck dimensions changed.',
        neck_is_planning_volume_not_printable_cowl=True,neck_stations_mm=NECK_STATIONS,
        outside_neck_mm3=outside.Volume,wire_to_neck_planning_boundary_mm=gap,
        material_contacts=0,reservation_contacts=0,jacket_conflicts=0,errors=[],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (source,Path(__file__),Path(__file__).with_name('build_feline_layout_envelope.py'))},
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(report['status'],report['worker_seconds'],'neck_gap_mm',round(gap,3))


if __name__=='__main__':main()

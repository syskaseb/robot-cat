"""Actual loop/head witnesses and material-derived fixed-root vertical bound.

The boss/core-bend bound alone omitted moving HipExtension material. Diagnose
before any further orientation/offset choice. No model or prior plan mutation.
"""
import json
import math
import time
from pathlib import Path
import FreeCAD as A
from support_entry_port import build
from loom_land_port import box
from diagnose_remaining_support_endpoints import moved,transform
import build_remaining_loom_supports as G
P=G.P


def run():
    tick=time.monotonic();pf=P.OUT/'body-rail-hip-retention-plan.json';plan=json.loads(pf.read_text())
    sf=P.OUT/'remaining-supports/SourceCarriersCurrent.FCStd';reader=G.B.H.P.SavedShapes()
    rf=P.OUT/'body-rail-hip-ports.json';ports=json.loads(rf.read_text())
    mf=P.OUT/'body-low-hip-rail-exit-plan.json';mathplan=json.loads(mf.read_text())
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    rows=[];limits=[]
    for row in plan['changed']:
        owner=row['owner'].removesuffix('FixedCarrier');loom=row['land']['loom']
        port=next(r for g in ports['groups'] if g['id']==row['owner'] for r in g['ports'] if r['land_id']==row['land']['id'])
        profile=build(row['land'],port);band=profile['band']
        head=box([8.2,-3,-2.5,14.2,3,2.5]);head.translate(A.Vector(0,0,profile['recipe']['band_axial_offset_mm']))
        head.Placement=profile['placement']*head.Placement
        loop=band.copy().cut(head.copy());assert loop.isValid()
        assert abs(band.Volume-loop.Volume-head.Volume)<1e-6
        base=reader.shape(sf,owner+'SourceCarrier');code=next(r['cad_code'] for r in mathplan['hips'] if r['loom']==loom)
        bb=band.BoundBox;prism=P.box([bb.XMin-.25,bb.YMin-.25,-200,bb.XMax+.25,bb.YMax+.25,200])
        bound=[]
        for h in (-15,0,15):
            target=moved(base,transform(axes,code,h,0,'Hip'))
            volumes={name:s.copy().common(target.copy()).Volume for name,s in (('loop',loop),('head',head))}
            intersection=target.copy().common(prism.copy());assert intersection.isNull() or intersection.isValid()
            floor=None if intersection.isNull() or intersection.Volume<1e-6 else intersection.BoundBox.ZMin
            if floor is not None:bound.append(floor)
            rows.append(dict(loom=loom,hip=h,loop_volume_mm3=volumes['loop'],head_volume_mm3=volumes['head'],
                             actual_material_floor_in_expanded_band_XY_prism_mm=floor))
        if bound:
            top_offset=band.BoundBox.ZMax-row['land']['start_world_mm'][2]
            limits.append(dict(loom=loom,band_top_offset_from_root_mm=top_offset,
                               maximum_root_Z_for_sampled_extension_mm=min(bound)-top_offset-.25))
    result=dict(status='FIXED_BAND_ACTUAL_MOTION_SPACE_DIAGNOSIS_NOT_NEW_LAYOUT',rows=rows,
        vertical_constraints=limits,conservative_common_root_Z_bound_mm=min(r['maximum_root_Z_for_sampled_extension_mm'] for r in limits) if limits else None,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (pf,sf,rf,mf,af,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False,
        scope='Actual valid loop/head intersections and actual HipExtension material in nominal band expandedXY vertical prism, threeHipposes. This bound is a planning constraint, not acceptance of a lowered root or continuous sweep.')
    (P.OUT/'body-fixed-band-motion-space.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(worker_seconds=result['worker_seconds'],contacts=[r for r in rows if r['loop_volume_mm3']>1e-5 or r['head_volume_mm3']>1e-5],limits=limits,common_bound=result['conservative_common_root_Z_bound_mm'])),flush=True)


if __name__=='__main__':run()

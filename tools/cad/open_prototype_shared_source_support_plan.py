"""One common five-source platform/load-path preflight before native detail.

Four NEW holes in the retained upper printed carrier, NOT invented PCB holes.
Bench tighten before Pi/boards; output grips/stations still require integration.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,time
import FreeCAD as A
import Part
from open_prototype_shared_distribution_carriers import planned_shapes,MODEL as RAILS
from open_prototype_entry_chambers import MOUNTS,CONTEXT
from open_prototype_wiring_endpoints import ROOT,BASE,read,sha

OUT=BASE/'wiring-checkpoint'


def main():
    dest=OUT/'shared-source-support-plan.json'
    previous=read(dest) if dest.exists() else None
    if previous:
        assert previous['status']=='REJECTED_ANCHOR_PLAN_BEFORE_DETAIL'
        assert {tuple(r['anchor']) for r in previous['errors']}=={(-25,-20),(-25,20)}
    tick=time.monotonic();allocation=read(OUT/'shared-allocation-plan.json')
    doc=A.openDocument(str(MOUNTS));ctx=A.openDocument(str(CONTEXT));rail=A.openDocument(str(RAILS))
    # Actual upperplate is Y±27, not its bosses' wider bbox. Put BOTH
    # foot rows inside that material with1mm edge allowance, BEFORE native CAD.
    # Derive whole support cells from source AND retained column/hole areas.
    # Existing frame bolts are atX-25/Y±20, not free mounting material.
    # LeftX-14 separates12mm feet from those heads; rightX65 is between AUX
    # and PWM footprints. Under-plate ribs support the longer left cantilever.
    axes=[(x,y) for x in (-14,65) for y in (-20,20)]
    r=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,contacts=[],errors=[],outside_torso=[],tested_pairs=0,bearing=[],
        new_printed_carrier_holes_xy_mm=axes,new_holes_NOT_supplier_PCB_holes=True,
        source_plate_bounds_mm=[-62,-27.5,113,82,27.5,115],pillar_OD_mm=8,foot_OD_mm=12,
        previous_preflight_snapshot_commit='b1ffd6f',
        previous_gate=previous,
        load_path_cause_change='Use free receiving-plate cells separated from source AND existing frame bolt axesX-25/Y20, with two underside ribs. Old anchors were not free because existing bore/bolt footprint was omitted. No changed cases/routes; no claim that a bbox is a collision verdict.',
        rejected_pre_detail_anchor_plan=dict(rows_y_mm=[-23,23],cause='12mm feet exceeded actual54mm plate width; bbox includes unrelated bosses',
            next_cause_change='Whole pair of foot rows uses actual plate material and1mm edge margin; source/wire allocation unchanged'),
        pillar_bottom_top_mm=[77.72,113],captured_nut_bottom_top_mm=[77.72,80.12],
        nominal_screws='4M3x10 from underside:underhead74.22,tip84.22;4washer0.5/4AF5.5nuts2.4,provisional delivered hardware fit',
        fixture_quantity_change={'PETG_common_platform':1,'M3x10':4,'M3_washer':4,'M3_nut':4},
        independent_input_seats=[dict(wires=['F_PI'],centre_x_mm=-53.5,y_mm=[42.25,51.25],floor_z_mm=118),
            dict(wires=['F_AUX'],centre_x_mm=-7,y_mm=[42.25,51.25],floor_z_mm=118),
            dict(wires=['F_HY','F_HP','F_TY'],centres_x_mm=[28.25,33,37.75],y_mm=[-52.75,-43.75],floor_z_mm=118)],
        assembly=['Insert captive platform nuts from underside before carrier placement',
            'Bench mate platform to UpperCarrier and tighten4underside screws before Pi/boards; do NOT claim driver access through installed Pi',
            'Install board/upper carrier module then source holders; independently restrain inputs and output insulation',
            'ATO access stays above; no routine rail/platform removal or74WAGO disconnects'],
        remaining=['Native UpperCarrier4holes/common platform/body ties/input/outputgrips and bothfixed3wirestations',
            'Full output-load fanouts,4MTA native mounts/all8tails,S1/PWM/body/leg/stock',
            'Delivered pinout/fit and phase2 load/creep/no-crush/access tests'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (MOUNTS,CONTEXT,RAILS,OUT/'shared-allocation-plan.json',Path(__file__))})
    try:
        new={'CommonPlatformPlate':Part.makeBox(144,55,2,A.Vector(-62,-27.5,113))}
        for i,y in enumerate((-18,14)):
            new['CommonPlatformRib'+str(i)]=Part.makeBox(144,4,4,A.Vector(-62,y,109))
        for i,(x,y) in enumerate(axes):
            post=Part.makeCylinder(4,35.28,A.Vector(x,y,77.72));foot=Part.makeCylinder(6,5,A.Vector(x,y,77.72))
            new['CommonPillar'+str(i)]=post.fuse(foot).cut(Part.makeCylinder(1.7,40,A.Vector(x,y,77.72)))
            # Probe retained ACTUAL face, not broad bbox or remembered plate Z.
            probe=Part.makeCylinder(6,.1,A.Vector(x,y,77.62));hit=probe.common(doc.UpperCarrier.Shape)
            assert hit.isValid();coverage=hit.Volume/probe.Volume
            r['bearing'].append(dict(xy_mm=[x,y],covered_fraction=coverage,area_mm2=hit.Volume/.1))
            if coverage<=.99:r['errors'].append(dict(anchor=[x,y],error='Retained actual plate face does not support whole foot; shared anchor layout needs change'))
        if r['errors']:
            r['status']='REJECTED_ANCHOR_PLAN_BEFORE_DETAIL'
            print(json.dumps(dict(status=r['status'],bearing=r['bearing'],errors=r['errors'])),flush=True)
            return
        targets=planned_shapes(allocation,doc,ctx)
        targets.update({b.Name:b.Shape for b in rail.Objects if b.TypeId=='PartDesign::Body' and b.Name!='DistributionSpacer'})
        for o in doc.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2':continue
            superseded=o.Name.startswith(('SourceLeftCarrier','SourceRightCarrier','SideRail','SideColumn','SideDistributionRail','F_PI_','F_AUX_','F_HY_','F_HP_','F_TY_'))
            if superseded or o.Name.endswith('_CurrentReference'):continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith('NominalPCB') or o.Name.startswith('BUSsupplier'):targets[o.Name]=o.Shape
        for group in doc.Objects:
            if 'Group' in group.PropertiesList and 'Hardware' in group.Name and group.Name!='SideMountHardware':
                for o in group.Group:
                    if 'Shape' in o.PropertiesList and not o.Shape.isNull():targets['hardware/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','S0_','S1_')) and o.Name!='P0_MG92BMount29':targets[o.Name]=o.Shape
        for n,s in new.items():
            assert s.isValid() and len(s.Solids)==1
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:r['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in targets.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                r['tested_pairs']+=1
                try:
                    assert t.isValid();hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
                except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
        r['status']='COMMON_PLATFORM_LOAD_PATH_PREFLIGHT_CLEAR_NATIVE_RESTRAINTS_OPEN' if not any(r[k] for k in ('contacts','errors','outside_torso')) else 'COMMON_PLATFORM_PLAN_REQUIRES_SHARED_CHANGE'
    finally:
        for d in (doc,ctx,rail):A.closeDocument(d.Name)
        r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==v for n,v in r['source_sha256'].items())
    r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ('status','contacts','outside_torso','errors','bearing','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()

"""One shared4MTA mounting load-path preflight, not four offset trials.

Freeze purchased allocation and both exits; include current source restraints,
all100entry reservations and actual receiving material BEFORE native detail.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,time,subprocess,hashlib
import FreeCAD as A
import Part
from open_prototype_shared_distribution_carriers import planned_shapes,MODEL as RAILS
from open_prototype_common_source_platform import MODEL as SOURCES
from open_prototype_entry_chambers import MOUNTS,CONTEXT
from open_prototype_wiring_endpoints import ROOT,BASE,read,sha

OUT=BASE/'wiring-checkpoint'


def main():
    dest=OUT/'common-mta-support-plan.json'
    previous=read(dest)
    assert previous['status']=='COMMON4MTA_PLAN_REQUIRES_CAUSE_CHANGE_BEFORE_NATIVE'
    assert {q['b'] for q in previous['contacts']}=={'S1_driver_5'}
    saved=subprocess.check_output(['git','show','cbdbb4e:'+dest.relative_to(ROOT).as_posix()],cwd=ROOT)
    assert hashlib.sha256(saved).hexdigest()==sha(dest),'Preserve rejected low load path before change'
    tick=time.monotonic();allocation=read(OUT/'shared-allocation-plan.json');source=read(OUT/'common-source-platform-package.json')
    assert sha(SOURCES)==source['model_sha256'] and not any(source[k] for k in ('contacts','errors','outside_torso'))
    doc=A.openDocument(str(MOUNTS));ctx=A.openDocument(str(CONTEXT));rail=A.openDocument(str(RAILS));native=A.openDocument(str(SOURCES))
    r=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,contacts=[],errors=[],outside_torso=[],bearing=[],tested_pairs=0,
        frozen_allocation_commit='337b6c6',native_source_commit='57afce2',
        changed_mount_roles=['FL','FR','RL','RR'],both_factory_exits_preserved=True,full8tails_qualified=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (MOUNTS,CONTEXT,RAILS,SOURCES,OUT/'shared-allocation-plan.json',OUT/'common-source-platform-package.json',Path(__file__))},
        previous_preflight_snapshot_commit='cbdbb4e',
        cause_change='Rear load path roots on current paired side rails ABOVE S1 driver,not tall receiving-plate columns through its horizontal access. Integral8mm solid posts need no4new screws; unchanged front allocation checks reused.',
        assembly=['Fit side rails with integral rear MTA seats using retained4rail bolts before WAGO','Fit common source platform and integral front MTA arms before restraints','Fit purchased4MTA,independent both-side lead grips and replaceable body ties; no lead extension invented'],
        new_hardware_candidate={'rear_M3x10':0,'rear_M3_washer':0,'rear_M3_nut':0,'body_T18I':8},
        factory_lead_basis='Both9mm first exit reservations only;100mm/side is PROJECT assumption,not catalogueL140 guarantee',
        remaining=['Full8factorytails/connections/extensions/grips/stock','MTA body bands and delivered casing/lid fit','Full head/tail/source/S1/PWM/body/legs and removal'],
        load_path='Front integral arms on common source floor; rear integral roots on paired distribution carriersX126..138,Y+-18 atZ109.01..113.01,solidOD8posts to137/seat137..139. No low rear carrier holes or addedbolts.',
        planned_rear_axes_xy_mm=[[134,-18],[134,18]],
        fore_unchanged_evidence='cbdbb4e contains no FL/FR mount contacts/errors/outside; do NOT repeat their unchanged checks',
        print_bound_after_rear_integration_max_x_mm=139.5)
    try:
        shapes={}
        for name,sign in [('FL',1),('FR',-1)]:
            y=sign*30.5
            for i,x in enumerate((-29,-1)):
                shapes[name+'Arm'+str(i)]=Part.makeBox(6,8,2,A.Vector(x-3,25.5 if sign>0 else -33.5,113))
                shapes[name+'Post'+str(i)]=Part.makeCylinder(3,15.6,A.Vector(x,y,115))
            shapes[name+'Seat']=Part.makeBox(35,22,2,A.Vector(-32.5,29.5 if sign>0 else -51.5,130.6))
        for name,y,owner in [('RL',18,'LeftDistributionCarrier'),('RR',-18,'RightDistributionCarrier')]:
            shapes[name+'Root']=Part.makeBox(12,8,4,A.Vector(126,y-4,109.01))
            shapes[name+'Post']=Part.makeCylinder(4,23.99,A.Vector(134,y,113.01))
            shapes[name+'Seat']=Part.makeBox(37,22,2,A.Vector(102.5,7 if name=='RL' else -29,137))
            parent=rail.getObject(owner).Shape;joined=parent
            for n in (name+'Root',name+'Post',name+'Seat'):joined=joined.fuse(shapes[n])
            assert joined.isValid() and len(joined.Solids)==1,owner
            overlap=shapes[name+'Root'].common(parent);assert overlap.isValid() and overlap.Volume>0
            r['bearing'].append(dict(owner=owner,integral_root_overlap_mm3=overlap.Volume,
                receiving_bolts_retained=True,solid_post_OD_mm=8,union_valid_1solid=True))
        targets=planned_shapes(allocation,doc,ctx)
        targets.update({b.Name:b.Shape for b in rail.Objects if b.TypeId=='PartDesign::Body' and b.Name!='DistributionSpacer'})
        for o in native.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and (o.TypeId in ('PartDesign::Body','Part::Feature')):targets['current/'+o.Name]=o.Shape
        for o in doc.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name in ('UpperCarrier','BUS_CP2'):continue
            if o.Name.startswith(('SourceLeftCarrier','SourceRightCarrier','SideRail','SideColumn','SideDistributionRail','F_PI_','F_AUX_','F_HY_','F_HP_','F_TY_')) or o.Name.endswith('_CurrentReference'):continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith('NominalPCB') or o.Name.startswith('BUSsupplier'):targets[o.Name]=o.Shape
        for group in doc.Objects:
            if 'Group' in group.PropertiesList and 'Hardware' in group.Name and group.Name!='SideMountHardware':
                for o in group.Group:
                    if 'Shape' in o.PropertiesList and not o.Shape.isNull():targets['hardware/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) and o.Name!='P0_MG92BMount29':targets[o.Name]=o.Shape
        for n,s in shapes.items():
            if n.startswith(('FL','FR')):continue # frozen unchanged parent result
            assert s.isValid() and len(s.Solids)==1
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:r['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in targets.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                r['tested_pairs']+=1
                try:
                    assert t.isValid();hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:
                        if (n=='RLRoot' and m=='LeftDistributionCarrier') or (n=='RRRoot' and m=='RightDistributionCarrier'):continue # checked1solid integral union,not overlapping printedcopies
                        r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
                except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
        r['status']='COMMON4MTA_LOAD_PATH_PREFLIGHT_CLEAR_NATIVE_AND8TAILS_OPEN' if not any(r[k] for k in ('contacts','errors','outside_torso')) else 'COMMON4MTA_PLAN_REQUIRES_CAUSE_CHANGE_BEFORE_NATIVE'
    finally:
        for d in (doc,ctx,rail,native):A.closeDocument(d.Name)
        r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==v for n,v in r['source_sha256'].items())
    print(json.dumps({k:r[k] for k in ('status','contacts','errors','outside_torso','bearing','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()

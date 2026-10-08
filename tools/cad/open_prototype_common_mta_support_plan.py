"""One shared4MTA mounting load-path preflight, not four offset trials.

Freeze purchased allocation and both exits; include current source restraints,
all100entry reservations and actual receiving material BEFORE native detail.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,time
import FreeCAD as A
import Part
from open_prototype_shared_distribution_carriers import planned_shapes,MODEL as RAILS
from open_prototype_common_source_platform import MODEL as SOURCES
from open_prototype_entry_chambers import MOUNTS,CONTEXT
from open_prototype_wiring_endpoints import ROOT,BASE,read,sha

OUT=BASE/'wiring-checkpoint'


def main():
    dest=OUT/'common-mta-support-plan.json';assert not dest.exists(),'Receive existing shared plan before another layout'
    tick=time.monotonic();allocation=read(OUT/'shared-allocation-plan.json');source=read(OUT/'common-source-platform-package.json')
    assert sha(SOURCES)==source['model_sha256'] and not any(source[k] for k in ('contacts','errors','outside_torso'))
    doc=A.openDocument(str(MOUNTS));ctx=A.openDocument(str(CONTEXT));rail=A.openDocument(str(RAILS));native=A.openDocument(str(SOURCES))
    r=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,contacts=[],errors=[],outside_torso=[],bearing=[],tested_pairs=0,
        frozen_allocation_commit='337b6c6',native_source_commit='57afce2',
        changed_mount_roles=['FL','FR','RL','RR'],both_factory_exits_preserved=True,full8tails_qualified=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (MOUNTS,CONTEXT,RAILS,SOURCES,OUT/'shared-allocation-plan.json',OUT/'common-source-platform-package.json',Path(__file__))},
        assembly=['Prepare rear captive nuts/receiving holes on bench before boards','Fit common source platform and integral front MTA arms before restraints','Fit purchased4MTA,independent both-side lead grips and replaceable body ties; no lead extension invented'],
        new_hardware_candidate={'rear_M3x10':4,'rear_M3_washer':4,'rear_M3_nut':4,'body_T18I':8},
        factory_lead_basis='Both9mm first exit reservations only;100mm/side is PROJECT assumption,not catalogueL140 guarantee',
        remaining=['Full8factorytails/connections/extensions/grips/stock','MTA body bands and delivered casing/lid fit','Full head/tail/source/S1/PWM/body/legs and removal'],
        load_path='Front integral arms on existing common source floor; rear shared support uses full receiving cells atX134,Y+-13/23 outside PWM board. Not supplierPCB holes.',
        planned_rear_axes_xy_mm=[[134,y] for y in (-23,-13,13,23)])
    try:
        shapes={}
        for name,sign in [('FL',1),('FR',-1)]:
            y=sign*30.5
            for i,x in enumerate((-29,-1)):
                shapes[name+'Arm'+str(i)]=Part.makeBox(6,8,2,A.Vector(x-3,25.5 if sign>0 else -33.5,113))
                shapes[name+'Post'+str(i)]=Part.makeCylinder(3,15.6,A.Vector(x,y,115))
            shapes[name+'Seat']=Part.makeBox(35,22,2,A.Vector(-32.5,29.5 if sign>0 else -51.5,130.6))
        for name,ys in [('RL',(13,23)),('RR',(-23,-13))]:
            for i,y in enumerate(ys):
                bore=Part.makeCylinder(1.7,61.28,A.Vector(134,y,77.72))
                shapes[name+'Post'+str(i)]=Part.makeCylinder(3,59.28,A.Vector(134,y,77.72)).cut(bore)
                shapes[name+'Foot'+str(i)]=Part.makeCylinder(4,5,A.Vector(134,y,77.72)).cut(bore)
                probe=Part.makeCylinder(4,.1,A.Vector(134,y,77.62));hit=probe.common(native.UpperCarrier.Shape)
                assert hit.isValid();coverage=hit.Volume/probe.Volume
                r['bearing'].append(dict(xy_mm=[134,y],area_mm2=hit.Volume/.1,coverage=coverage))
                if coverage<.99:r['errors'].append(dict(xy_mm=[134,y],error='Not full actual receiving material; reject layout before details'))
            shapes[name+'Seat']=Part.makeBox(35,22,2,A.Vector(102.5,7 if name=='RL' else -29,137))
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
            assert s.isValid() and len(s.Solids)==1
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:r['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in targets.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                r['tested_pairs']+=1
                try:
                    assert t.isValid();hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:
                        if m=='current/CommonSourcePlatform' and 'Arm' in n:continue # integral floor ownership,not twoprintedcopies
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

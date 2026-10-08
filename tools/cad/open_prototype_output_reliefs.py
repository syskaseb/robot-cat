"""Add four independent insulation seats to the two existing source carriers.

No separate brackets or screws;4 replaceable ties keep output loads off bought
holders and WAGO. Only added material/slots and mating wire/tie budgets checked.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import time
import tempfile
import shutil
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT=BASE/'wiring-checkpoint'
SOURCE=OUT/'BranchOutputsAssembly.FCStd'
MODEL=OUT/'OutputReliefsAssembly.FCStd'


def build_plan():
    guide=read(OUT/'branch-output-plan.json')
    rows=[]
    for r in guide['output_recipes']:
        x,y,z=r['start_mm'];sign=r['start_departure'][0]
        rows.append(dict(holder=r['holder'],native='SourceLeftCarrier' if y>0 else 'SourceRightCarrier',
            start_mm=r['start_mm'],floor_x_mm=sorted([x,x+sign*9]),floor_y_mm=[y-6.5,y+6.5],
            wire_axis_z_mm=z,floor_top_z_mm=z-2,carrier_bottom_z_mm=88.99 if y>0 else 87.99,
            carrier_top_z_mm=90.99 if y>0 else 89.99,
            slot_centres_mm=[[x+sign*4.5,y+q] for q in (-3.6,3.6)],
            straight_insulation_grip_mm=9,slot_width_mm=3.5,slot_y_depth_mm=1.7,
            intact_factory_insulation_only=True))
    return dict(status='FOUR_SHARED_INTEGRAL_OUTPUT_SEATS_PLAN',rows=rows,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
            (SOURCE,OUT/'branch-output-plan.json',OUT/'branch-output-checks.json',Path(__file__))},
        additional_ties=4,tie_sku='11102370',additional_print_parts=0,
        replaces_two_source_carrier_prints=True,additional_screws_connectors=0,
        assembly=['Install same two source carriers on retained rail ties; new seats are integral.',
            'Lay the four output tails on9mm straight intact-insulation seats before bending.',
            'Pass one T18I through two full-depth slots per output; head beside insulation, not over ATO lid.',
            'With source isolated, ATO service cuts only holder body ties. Leave output and input insulation ties installed.',
            'Full carrier removal releases4 output restraint ties and load connections, then existing input/rail ties; whole-wiring recipe remains OPEN.'],
        physical_gates=['Delivered OD and strap bend/slot fit','No crush/pull/creep','Covered joints and full load routes'],
        selected=False,stage_completed=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    import MeshPart
    from open_deck_p0_supports import sketch,feature
    from open_deck_p0_plate import rect
    from open_prototype_fhac_supports import ring
    tick=time.monotonic();plan=build_plan()
    (OUT/'output-relief-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    d=A.openDocument(str(SOURCE));names=[d.Name]
    result=dict(status='OUTPUT_RELIEFS_PENDING',source_sha256=plan['source_sha256'],contacts=[],errors=[],
        tested_pairs=0,selected=False,stage_completed=False,physical_pass=False)
    try:
        p=d.Parameters;p.addProperty('App::PropertyLength','OutputGripSlotWidth');p.OutputGripSlotWidth=3.5
        changed=[];previous={};ties={}
        for name in ('SourceLeftCarrier','SourceRightCarrier'):
            b=d.getObject(name);previous[name]=b.Shape.copy();rows=[r for r in plan['rows'] if r['native']==name]
            carrier_top=rows[0]['carrier_top_z_mm']
            sk=sketch(b,name+'OutputPostPlan',carrier_top)
            for r in rows:rect(sk,r['floor_x_mm'][0],r['floor_y_mm'][0],9,13)
            b.Tip=feature(b,'Pad',name+'OutputPosts',sk,8)
            top=rows[0]['floor_top_z_mm'];assert abs(top-carrier_top-8)<1e-6
            sk=sketch(b,name+'OutputTiePlan',top)
            for r in rows:
                for x,y in r['slot_centres_mm']:rect(sk,x-1.75,y-.85,3.5,1.7,'Parameters.OutputGripSlotWidth')
            b.Tip=feature(b,'Pocket',name+'OutputTieThrough',sk,10)
            changed.append(b)
        d.recompute()
        original={}
        for b in changed:
            assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True),b.Name
            assert all(sk.FullyConstrained and sk.solve()==0 for sk in b.Group if sk.TypeId=='Sketcher::SketchObject')
            original[b.Name]=b.Shape.Volume
        p.OutputGripSlotWidth=3.2;d.recompute()
        assert all(b.Shape.Volume>original[b.Name] for b in changed)
        p.OutputGripSlotWidth=3.5;d.recompute()
        assert all(abs(b.Shape.Volume-original[b.Name])<1e-5 for b in changed)
        slots=[]
        for r in plan['rows']:
            b=d.getObject(r['native']);x=sum(r['floor_x_mm'])/2;y=r['start_mm'][1];z=r['wire_axis_z_mm'];bottom=r['carrier_bottom_z_mm']-1.2
            for cx,cy in r['slot_centres_mm']:
                probe=Part.makeBox(3.3,1.5,z-bottom+2,A.Vector(cx-1.65,cy-.75,bottom-1))
                hit=probe.common(b.Shape);assert hit.isValid() and hit.Volume<1e-6
                slots.append(dict(holder=r['holder'],centre_mm=[cx,cy],full_depth_clear=True))
            box=[x-1.25,y-4.2,bottom,x+1.25,y+4.2,z+3.2]
            head=[x-2.4,y+4.2,z-.5,x+2.4,y+8.7,z+3]
            ties[r['holder']+'_OutputTie']=ring(A,Part,0,2.5,box,head)
        targets={}
        for ob in d.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull() or ob in changed:continue
            if ob.TypeId in ('PartDesign::Body','App::Link') or ob.Name.endswith(('_CurrentReference','NominalPCB')) or ob.Name.startswith('BUSsupplier'):
                targets[ob.Name]=ob.Shape
        def check(a,s,b,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid(),'Invalid BRep'
                h=s.common(t);assert h.isValid()
                if h.Volume>1e-5:result['contacts'].append(dict(a=a,b=b,volume_mm3=h.Volume,bounds_mm=bounds(h)))
            except Exception as exc:result['errors'].append(dict(a=a,b=b,error=str(exc)))
        additions={}
        for b in changed:
            added=b.Shape.cut(previous[b.Name]);assert added.isValid() and added.Volume>0
            additions[b.Name]=added
            for n,t in targets.items():check(b.Name+'_added',added,n,t)
        for n,s in ties.items():
            for b in changed:check(n,s,b.Name,b.Shape)
            for m,t in targets.items():check(n,s,m,t)
        check('LeftAdded',additions['SourceLeftCarrier'],'RightAdded',additions['SourceRightCarrier'])
        for i,(n,s) in enumerate(ties.items()):
            for m,t in list(ties.items())[i+1:]:check(n,s,m,t)
        result.update(slot_checks=slots,new_ties=4,new_print_parts=0,new_screws_connectors=0,
            parameter_trial='OutputGripSlotWidth3.5->3.2->3.5 across both carriers',
            full_load_route_joint_and_current_wire_stock_still_open=True)
        if not result['contacts'] and not result['errors']:
            for n,s in ties.items():
                ob=d.addObject('Part::Feature',n+'_CurrentReference');ob.Shape=s
                ob.addProperty('App::PropertyString','Qualification');ob.Qualification='Provisional bent strap/head budget; delivery bend fit OPEN'
            exports={}
            for b in changed:
                mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
                assert mesh.isSolid() and not mesh.hasNonManifolds()
                dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength];assert max(dims)+10<256
                dest=OUT/('Load'+b.Name+'.stl');mesh.write(str(dest));exports[dest.name]=sha(dest)
            d.saveAs(str(MODEL));A.closeDocument(d.Name)
            with tempfile.TemporaryDirectory(prefix='robot-cat-output-reopen-') as td:
                dest=Path(td)/MODEL.name;shutil.copy2(MODEL,dest);q=A.openDocument(str(dest));q.recompute()
                for n,v in original.items():assert q.getObject(n).Shape.isValid() and abs(q.getObject(n).Shape.Volume-v)<1e-5
                A.closeDocument(q.Name)
            result.update(status='FOUR_OUTPUT_RELIEFS_NOMINAL_PREPARATION_CHECKED',native_sha256=sha(MODEL),exports=exports,relocated_reopen=True)
        else:result['status']='OUTPUT_RELIEFS_REQUIRE_SHARED_LAYOUT_CHANGE'
    finally:
        for name in names:
            if name in A.listDocuments():A.closeDocument(name)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'output-relief-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':main()

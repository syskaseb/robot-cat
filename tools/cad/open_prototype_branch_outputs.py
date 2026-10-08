"""One shared four-output recipe, retaining native source mounts and inputs.

Native sketches/pipes are editable wire reservations, not four printed parts.
Known1608 copper groups bind logical PWM roles without inventing U1 pins.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import time
import tempfile
import shutil
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT=BASE/'wiring-checkpoint'
SOURCE=OUT/'SourceFixturesAssembly.FCStd'
MODEL=OUT/'BranchOutputsAssembly.FCStd'
POP=ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json'
BOARD=BASE/'mounting-checkpoint/board-mount-plan.json'


def build_plan():
    holders=read(OUT/'fhac-mount-plan.json')['source_plan']
    r,vertical,last=6.,39.5,15.
    length=9+math.pi*r+vertical+last
    rows=[]
    for h in holders:
        if h['holder']=='F_PI':continue
        sign=h['output_departure'][0]
        start=h['output_exit_mm']
        end=[start[0]+sign*(9-last),start[1],start[2]+2*r+vertical]
        rows.append(dict(holder=h['holder'],logical_output_role=h['holder']+'.out',
            start_mm=start,start_departure=h['output_departure'],end_mm=end,
            end_departure=[-sign,0,0],insulation_grip_straight_mm=9,
            terminal_straight_mm=last,bare_lap_allowance_on_terminal_mm=8,
            guide_length_mm=length,nominal_factory_blank_mm=83,
            factory_minimum_available_mm=84.5,minimum_length_margin_mm=84.5-length,
            target='AUX.VIN' if h['holder']=='F_AUX' else
                {'F_HY':'C_HY.V+','F_HP':'C_HP.V+','F_TY':'C_TY.V+'}[h['holder']],
            route_only=True,independent_output_grip_and_load_route_open=True))
    pop=read(POP)
    terms={t['ref']:t for t in pop['terminals']}
    board=read(BOARD)
    z=board['pcb_bottom_planes_mm']['PWM1608']+pop['board']['thickness_mm']
    # Origin derives from mounting-hole pairs, not from the shifted old view.
    xy=board['board_hole_axes_world_xy_mm']['PWM1608']
    local_holes=pop['board']['holes']
    origins=[[a[i]-b[('x','y')[i]] for i in range(2)] for a,b in zip(xy,local_holes)]
    assert max(abs(a-b) for a,b in zip(*origins))<1e-7
    origin=origins[0]
    pwms=[]
    for i in (1,2,3):
        role,landing=f'R{i}.2',f'B{i}.out'
        a,b=terms[role],terms[landing]
        assert a['net']==b['net'] and a['source_copper_group']==b['source_copper_group']
        pwms.append(dict(logical_role=role,chosen_physical_landing=landing,net=a['net'],
            copper_group=a['source_copper_group'],local_xy_mm=[b['x'],b['y']],
            current_nominal_pad_top_mm=[origin[0]+b['x'],origin[1]+b['y'],z],
            isolated_from_unknown_U1_external_padmap=True,
            solder_and_current_population_fit_phase2=True))
    return dict(status='FOUR_FACTORY_OUTPUTS_SHARED_RECIPE_NOT_FULL_WIRING',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
            (SOURCE,OUT/'fhac-mount-plan.json',OUT/'local-boundary-plan.json',POP,BOARD,Path(__file__))},
        output_recipes=rows,chosen_PWM_landings=pwms,
        quarter_radius_mm=r,factory_OD_design_allowance_mm=4,
        radius_and_OD_not_supplier_guarantee=True,
        shared_layout='One vertical side loop per existing outlet. Return terminal above beside, not above central ATO tool zone. Existing input/holder layout unchanged.',
        new_print_parts=0,new_electrical_connectors=0,
        assembly=['Power disconnected; keep bankR47 and source-input reliefs installed.',
            'Lay four factory tails to side loops with9mm straight intact-insulation seats.',
            'Leave ATO central tool zones clear; do not tie outputs to removable lids.',
            'Provide independent common-rail restraints and covered terminal joins before load wiring.',
            'AUX end remains insulated/unpowered until delivered padmap/polarity identified.'],
        selected=False,stage_completed=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    import Sketcher
    tick=time.monotonic()
    plan=build_plan()
    (OUT/'branch-output-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    d=A.openDocument(str(SOURCE))
    ctx=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'))
    tail=A.openDocument(str(OUT/'TailLocalCurrent.FCStd'))
    names=[x.Name for x in (d,ctx,tail)]
    result=dict(status='FOUR_BRANCH_OUTPUTS_PENDING',source_sha256=plan['source_sha256'],
        selected=False,stage_completed=False,physical_pass=False,contacts=[],errors=[],tested_pairs=0)
    try:
        p=d.Parameters
        p.addProperty('App::PropertyLength','BranchOutputOD');p.BranchOutputOD=4
        bodies=[]
        for row in plan['output_recipes']:
            b=d.addObject('PartDesign::Body',row['holder']+'_OutputGuide')
            b.addProperty('App::PropertyString','Qualification')
            b.Qualification='Wire reservation only; supplier OD/bend, independent relief and full load path OPEN'
            b.Placement=A.Placement(A.Vector(*row['start_mm']),A.Rotation(A.Vector(0,0,1),0 if row['start_departure'][0]>0 else 180))
            path=d.addObject('Sketcher::SketchObject',row['holder']+'_OutputPath');b.addObject(path)
            path.Placement=A.Placement(A.Vector(),A.Rotation(A.Vector(1,0,0),90))
            V=lambda x,y:A.Vector(x,y,0)
            r=plan['quarter_radius_mm'];top=r+39.5
            geometries=[Part.LineSegment(V(0,0),V(9,0)),
                Part.ArcOfCircle(Part.Circle(V(9,r),A.Vector(0,0,1),r),-math.pi/2,0),
                Part.LineSegment(V(9+r,r),V(9+r,top)),
                Part.ArcOfCircle(Part.Circle(V(9,top),A.Vector(0,0,1),r),0,math.pi/2),
                Part.LineSegment(V(9,top+r),V(-6,top+r))]
            for g in geometries:
                i=path.addGeometry(g,False);path.addConstraint(Sketcher.Constraint('Block',i))
            profile=d.addObject('Sketcher::SketchObject',row['holder']+'_OutputProfile');b.addObject(profile)
            profile.Placement=A.Placement(A.Vector(),A.Rotation(A.Vector(0,1,0),90))
            profile.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),2),False)
            profile.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
            index=profile.addConstraint(Sketcher.Constraint('Diameter',0,4))
            profile.renameConstraint(index,'WireDiameter');profile.setExpression('Constraints.WireDiameter','Parameters.BranchOutputOD')
            pipe=b.newObject('PartDesign::AdditivePipe',row['holder']+'_FactoryTail')
            pipe.Profile=profile;pipe.Spine=(path,[]);pipe.Transition=0;b.Tip=pipe
            bodies.append(b)
        d.recompute()
        initial={}
        for b,row in zip(bodies,plan['output_recipes']):
            assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True),b.Name
            for sk in (d.getObject(row['holder']+'_OutputPath'),d.getObject(row['holder']+'_OutputProfile')):
                assert sk.FullyConstrained and sk.solve()==0,sk.Name
                sk.Visibility=False
            path=d.getObject(row['holder']+'_OutputPath')
            assert abs(sum(e.Length for e in path.Shape.Edges)-row['guide_length_mm'])<1e-6
            initial[b.Name]=b.Shape.Volume
        p.BranchOutputOD=3.8;d.recompute()
        assert all(b.Shape.Volume<initial[b.Name] for b in bodies)
        p.BranchOutputOD=4;d.recompute()
        assert all(abs(b.Shape.Volume-initial[b.Name])<1e-5 for b in bodies)
        targets={}
        for ob in d.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull() or ob in bodies:continue
            if ob.TypeId in ('PartDesign::Body','App::Link') or ob.Name.endswith(('_CurrentReference','NominalPCB')) or ob.Name.startswith('BUSsupplier'):
                targets['mount/'+ob.Name]=ob.Shape
        for ob in ctx.Objects:
            if 'Shape' in ob.PropertiesList and not ob.Shape.isNull() and ob.Name.startswith(('P0_','Head_','TailBridge')):
                if ob.Name=='P0_MG92BMount29':continue
                targets['context/'+ob.Name]=ob.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        def check(a,s,b,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid(),'Invalid BRep, not clearance'
                common=s.common(t);assert common.isValid()
                if common.Volume>1e-5:result['contacts'].append(dict(a=a,b=b,volume_mm3=common.Volume,bounds_mm=bounds(common)))
            except Exception as exc:result['errors'].append(dict(a=a,b=b,error=str(exc)))
        for i,b in enumerate(bodies):
            for n,t in targets.items():check(b.Name,b.Shape,n,t)
            for other in bodies[i+1:]:check(b.Name,b.Shape,other.Name,other.Shape)
        result.update(output_count=4,new_print_parts=0,native_editable_sketch_pipes=True,
            profile_parameter_trial='BranchOutputOD4->3.8->4 across all4 pipes',
            guide_lengths_mm=[r['guide_length_mm'] for r in plan['output_recipes']],
            PWM_landings=plan['chosen_PWM_landings'],independent_output_grips_and_full_body_routes_open=True)
        if not result['contacts'] and not result['errors']:
            d.saveAs(str(MODEL))
            A.closeDocument(d.Name)
            with tempfile.TemporaryDirectory(prefix='robot-cat-branch-reopen-') as td:
                copy=Path(td)/MODEL.name;shutil.copy2(MODEL,copy)
                reopened=A.openDocument(str(copy));reopened.recompute()
                for name,v in initial.items():
                    s=reopened.getObject(name).Shape
                    assert s.isValid() and abs(s.Volume-v)<1e-5
                A.closeDocument(reopened.Name)
            result.update(status='FOUR_BRANCH_OUTPUT_GUIDES_NOMINAL_PREPARATION_CHECKED',
                native_sha256=sha(MODEL),relocated_reopen=True)
        else:result['status']='FOUR_BRANCH_OUTPUTS_REQUIRE_SHARED_LAYOUT_CHANGE'
    finally:
        for name in names:
            if name in A.listDocuments():A.closeDocument(name)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'branch-output-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':main()

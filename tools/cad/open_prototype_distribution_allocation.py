"""One shared spatial hypothesis, before rebuilding twenty relocated mounts.

Uses stored valid case geometry, not bbox collision verdicts. This is a
reservation gate, not routed wiring, native supports, or manufacturer data.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds
from open_prototype_entry_chambers import MOUNTS, CONTEXT, occupancy

OUT = BASE/'wiring-checkpoint'
UPPER_Y = 62.25


def build_plan():
    rows = read(BASE/'mounting-checkpoint/distribution-mount-plan.json')['distribution']
    slots = dict(G_TAIL=1, D_RR=4)
    distribution = []
    for i, row in enumerate(rows):
        level = (i % 10) // 5
        slot = slots.get(row['role'], i % 5)
        sign = 1 if row['side']=='L' else -1
        y = (75 if not level else (20 if slot==4 else UPPER_Y))*sign
        distribution.append(dict(row, centre_mm=[-47+40*slot,y,120 if level else 67.99]))
    # Five parallel holders, alternating input sides. The outputs descend
    # outside the board perimeter. Existing broad carrier edges must be
    # redesigned together if they occupy these reserved output corridors.
    holders = []
    for name, x, sign, port in [('F_PI',-40,1,'P_SYS.2'),
            ('F_AUX',35,1,'P_REAR.3'),('F_HY',10,-1,'P_AUX.2'),
            ('F_HP',60,-1,'P_AUX.3'),('F_TY',-15,-1,'P_AUX.4')]:
        holders.append(dict(holder=name,input_mm=[x,25.5*sign,125],
            output_mm=[x,-25.5*sign,125],axis=[0,-sign,0],target=port,
            factory_radius_assumption_mm=6,output_first_straight_mm=3,
            output_straight_before_joint_mm=15,new_wire_grip_straight_mm=21.5,
            sleeve_clearance_OD_mm=6))
    # Apply to original logical ports, not the already-permuted old proof.
    permutation={'P_REAR.2':'P_REAR.5','P_REAR.3':'P_REAR.2','P_REAR.5':'P_REAR.3'}
    loads=occupancy(read(OUT/'routing-scope-plan.json'),permutation)
    paths=[MOUNTS,CONTEXT,OUT/'TailLocalCurrent.FCStd',
        BASE/'mounting-checkpoint/distribution-mount-plan.json',
        OUT/'source-layout-plan.json',OUT/'routing-scope-plan.json',__file__]
    return dict(status='SHARED_CASE_AND_EXIT_ALLOCATION_HYPOTHESIS',
        distribution=distribution,holders=holders,same_bus_permutation=permutation,
        occupied_ports=loads,selected=False,stage_completed=False,physical_pass=False,
        mts=[dict(native='MTA_'+leg+'_CP2',centre_mm=centre,
                  both_factory_tail_reservations_mm=100,tail_length_not_catalog=True)
             for leg,centre in [('FL',[-15,40.5,140.6]),('FR',[-15,-40.5,140.6]),
                                ('RL',[120,18,147]),('RR',[120,-18,147])]],
        corridor_basis=dict(upper_entry_end_Y_mm=UPPER_Y-11-9,
            source_output_axis_Y_mm=25.5+3+6,sleeve_radius_mm=3,
            entry_reservation_radius_mm=2.1,
            clear_gap_mm=(UPPER_Y-11-9-2.1)-(25.5+3+6+3),
            reason='Separate ALL upper inward ports from descending factory output/splice corridors, not individual wire offsets'),
        invalidated_interfaces=['All20 WAGO placements/mounts/port frames',
            'Both source carriers and all5 holder restraints',
            'All4 MTA seats/both tails and changed source/load routes',
            'Changed input/output and S1/PWM/leg/body lengths and restraints'],
        retained=['BankR47','P0/E6/15 drives/replaceable MG92B','MAIN46.52',
            'Torso325x200x160','Both factory exits of4 MTA'],
        assembly=['Mount boards and unchanged bank; install new distribution rails',
            'Bench prepare isolated source holders; secure each independently',
            'Route and restrain wires independently of adhesive/lever retention',
            'Isolate battery for ATO access; no routine74-port WAGO disconnection'],
        open_gates=['All five real input routes and prefuse50mm bound',
            'Full outputs beyond reserved joint/grip and board/carrier load paths',
            'S1 four R25.2 routes, PWM exits and actual service motion',
            'Native editable mounts, lever qualification, final stock and export',
            'S0 external-terminal datum and U1 delivered pinout'],
        source_sha256={Path(p).relative_to(ROOT).as_posix():sha(Path(p)) for p in paths})


def main():
    import FreeCAD as A
    import Part
    tick=time.monotonic();plan=build_plan()
    previous=OUT/'shared-allocation-checks.json'
    if previous.exists():
        old_gate=read(previous)
        plan['previous_gate']=old_gate.get('previous_gate',old_gate)
        plan['previous_gate_disposition']='Baseline: rear MTA level occupied new upper ports; exits crossed entry stems. F_HP old source-plan input frame inconsistent with saved casing: its transformed body result invalidated, other contacts retained. This revision changes shared corridors and ALL4 MTA stations, not individual wire offsets.'
    docs=[A.openDocument(str(p)) for p in (MOUNTS,CONTEXT,OUT/'TailLocalCurrent.FCStd')]
    mount,ctx,tail=docs
    result=dict(status='PENDING',contacts=[],support_changes=[],outside_torso=[],
        errors=[],tested_pairs=0,ports=[],input_necessary_bounds=[],
        source_sha256=plan['source_sha256'],selected=False,stage_completed=False,
        physical_pass=False,full_routes_and_supports_open=True)
    if 'previous_gate' in plan:result['previous_gate']=plan['previous_gate']
    new={};targets={}
    try:
        torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1 and not torso.check(True)
        for row in plan['distribution']:
            s=mount.getObject(row['native']).Shape.copy();b=s.BoundBox
            centre=A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2)
            s.translate(A.Vector(*row['centre_mm'])-centre);new[row['native']]=s
            b=s.BoundBox
            for port in range(1,6):
                p=[b.XMin+5.5+(port-1)*(row['size_mm'][0]-11)/4,
                    b.YMin if row['side']=='L' else b.YMax,(b.ZMin+b.ZMax)/2]
                d=[0,-1 if row['side']=='L' else 1,0]
                role=f"{row['role']}.{port}"
                result['ports'].append(dict(role=role,point_mm=p,departure=d,
                    occupied=bool(plan['occupied_ports'].get(role)),
                    provisional_pitch_not_supplier_cavity=True))
                new['entry/'+role]=Part.makeCylinder(2.1,9,A.Vector(*p),A.Vector(*d))
        for row in plan['mts']:
            s=ctx.getObject(row['native']).Shape.copy();b=s.BoundBox
            centre=A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2)
            s.translate(A.Vector(*row['centre_mm'])-centre);new[row['native']]=s
            # Only first straight allowances, not100mm routed tails or an
            # inherited stock choice. Both sides remain mandatory next gate.
            b=s.BoundBox
            for sign in (-1,1):
                p=A.Vector(b.XMin if sign<0 else b.XMax,row['centre_mm'][1],row['centre_mm'][2])
                new[row['native']+'/exit'+str(sign)]=Part.makeCylinder(2,9,p,A.Vector(sign,0,0))
        for row in plan['holders']:
            name=row['holder']
            axis=A.Vector(*row['axis']);p=A.Vector(*row['input_mm'])
            rotation=A.Rotation(A.Vector(1,0,0),axis)
            s=mount.getObject(name+'_body_budget_CurrentReference').Shape.copy()
            b=s.BoundBox
            assert abs(b.XLength-51)<1e-6 and abs(b.YLength-20.25)<1e-6 and abs(b.ZLength-22)<1e-6,'Stored FHAC allowance frame mismatch'
            centre=A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2)
            s.translate(-centre)
            s.rotate(A.Vector(0,0,0),rotation.Axis,rotation.Angle*180/math.pi)
            s.translate(p+axis*25.5+A.Vector(0,0,1));new[name+'/case']=s
            cb=s.BoundBox
            new[name+'/ATO_tool_budget']=Part.makeBox(22,10,35,A.Vector(row['input_mm'][0]-11,-5,cb.ZMax))
            for key,point,direction in [('input',row['input_mm'],-axis),('output',row['output_mm'],axis)]:
                new[name+'/'+key+'_straight']=Part.makeCylinder(2,3,A.Vector(*point),direction)
            # Continuous R6 turn downward,15mm straight,covered splice,21.5mm
            # new insulation grip. Intentional overlaps within one holder are
            # not reported as separate-wire collisions.
            p=A.Vector(*row['output_mm']);a=p+axis*3;c=a+A.Vector(0,0,-6)
            b=c+axis*6;mid=c+(axis+A.Vector(0,0,1))*(6/math.sqrt(2))
            cut=b+A.Vector(0,0,-15)
            edges=[Part.makeLine(p,a),Part.Arc(a,mid,b).toShape(),Part.makeLine(b,cut)]
            path=Part.Wire(edges)
            circle=Part.Wire([Part.makeCircle(2,p,axis)])
            new[name+'/factory_output']=path.makePipeShell([circle],True,False)
            new[name+'/sleeve']=Part.makeCylinder(3,26.5,cut+A.Vector(0,0,14),A.Vector(0,0,-1))
            new[name+'/new_grip']=Part.makeCylinder(1.05,21.5,cut,A.Vector(0,0,-1))
            target=next(r for r in result['ports'] if r['role']==row['target'])
            strip=14 if row['holder'] in ('F_PI','F_AUX') else 11
            lower=math.dist(row['input_mm'],target['point_mm'])+strip
            limit=50 if strip==14 else 84.5
            result['input_necessary_bounds'].append(dict(holder=name,target=row['target'],
                direct_plus_strip_mm=lower,limit_mm=limit,impossible=lower>limit,
                not_bend_or_route_acceptance=True))
        changed_names={r['native'] for r in plan['distribution']}
        for o in mount.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2' or o.Name in changed_names:continue
            if o.Name.startswith(('F_PI_','F_AUX_','F_HY_','F_HP_','F_TY_')):continue
            # Old swept-wire snapshots are donor references, NOT new routes.
            if o.Name.endswith('_CurrentReference') and o.Name.startswith(('W','XB','XS')):continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier'):
                targets['mount/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and (o.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) or 'Carrier' in o.Name) and o.Name!='P0_MG92BMount29':targets['context/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        def check(n,s,m,t,category):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid(),'Invalid geometry is not clearance'
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result[category].append(dict(a=n,b=m,volume_mm3=hit.Volume))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        for n,s in new.items():
            assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
            if not n.endswith('/ATO_tool_budget'):
                outside=s.cut(torso);assert outside.isValid()
                if outside.Volume>1e-5:result['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in targets.items():
                category='support_changes' if 'Carrier' in m or mount.getObject(m.split('/')[-1]) and mount.getObject(m.split('/')[-1]).TypeId=='PartDesign::Body' else 'contacts'
                check(n,s,m,t,category)
        items=list(new.items())
        native_by_role={r['role']:r['native'] for r in plan['distribution']}
        for i,(n,s) in enumerate(items):
            for m,t in items[i+1:]:
                if n.split('/')[0]==m.split('/')[0]:continue
                if n.startswith('entry/') and m.startswith('entry/'):continue
                if n==native_by_role.get(m.removeprefix('entry/').rsplit('.',1)[0]):continue
                check(n,s,m,t,'contacts')
        result['status']='SHARED_ALLOCATION_HAS_OPEN_CONSTRAINTS' if any(result[k] for k in ('contacts','outside_torso','errors')) or any(r['impossible'] for r in result['input_necessary_bounds']) else 'CASE_AND_EXIT_RESERVATIONS_CLEAR_FULL_ROUTES_SUPPORTS_OPEN'
    finally:
        for doc in docs:A.closeDocument(doc.Name)
    assert all(sha(ROOT/p)==h for p,h in plan['source_sha256'].items())
    result.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    for name,data in [('shared-allocation-plan',plan),('shared-allocation-checks',result)]:
        (OUT/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','outside_torso','errors','input_necessary_bounds','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()

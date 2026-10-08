"""One shared spatial hypothesis, before rebuilding twenty relocated mounts.

Uses stored valid case geometry, not bbox collision verdicts. This is a
reservation gate, not routed wiring, native supports, or manufacturer data.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import sys
import time
import open_prototype_bundle_spines as V
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds
from open_prototype_entry_chambers import MOUNTS, CONTEXT, occupancy

OUT = BASE/'wiring-checkpoint'
UPPER_Y = 62.25


def input_recipe(start, end, direction, radius=6):
    """Two exact tangent arcs, with3mm factory exit and9mm insulation grip.

    A length preflight, NOT joint clearance or a supplier bend qualification.
    Smaller transverse shifts use shallow arcs; large shifts add one straight.
    """
    delta=V.sub(end,start);along=V.dot(delta,direction)
    lateral=V.sub(delta,V.mul(direction,along))
    shift=math.sqrt(V.dot(lateral,lateral))
    assert shift>1e-8 and abs(V.dot(direction,direction)-1)<1e-8
    side=V.mul(lateral,1/shift)
    angle=math.acos(1-shift/(2*radius)) if shift<2*radius else math.pi/2
    middle=max(0,shift-2*radius)
    first=along-2*radius*math.sin(angle)-9
    if first<3-1e-8:raise ValueError('No space for both exit and insulation grip before CAD')
    a=V.add(start,V.mul(direction,first));centre=V.add(a,V.mul(side,radius))
    radial=V.sub(V.mul(direction,math.sin(angle)),V.mul(side,math.cos(angle)))
    b=V.add(centre,V.mul(radial,radius))
    m1=V.add(centre,V.mul(V.sub(V.mul(direction,math.sin(angle/2)),V.mul(side,math.cos(angle/2))),radius))
    c=V.add(b,V.mul(side,middle));centre2=V.add(c,V.mul(radial,radius))
    q=V.add(centre2,V.mul(side,radius))
    m2=V.add(centre2,V.mul(V.add(V.mul(direction,-math.sin(angle/2)),V.mul(side,math.cos(angle/2))),radius))
    assert math.dist(V.add(q,V.mul(direction,9)),end)<1e-7
    parts=[dict(kind='line',start=start,end=a),dict(kind='arc',start=a,mid=m1,end=b)]
    if middle>1e-8:parts.append(dict(kind='line',start=b,end=c))
    parts.extend([dict(kind='arc',start=c,mid=m2,end=q),dict(kind='line',start=q,end=end)])
    return dict(segments=parts,centreline_mm=first+9+2*radius*angle+middle,
        first_straight_mm=first,grip_straight_mm=9,radius_assumption_mm=radius,
        arc_angle_deg=angle*180/math.pi,OD_assumption_mm=4,
        supplier_bend_or_mutual_clearance_qualified=False)


def save_input_length_preflight():
    allocation=read(OUT/'shared-allocation-plan.json')
    ports={r['role']:r for r in read(OUT/'shared-allocation-checks.json')['ports']}
    rows=[]
    for row in allocation['holders']:
        target=ports[row['target']]
        d=V.mul(row['axis'],-1)
        assert V.dot(d,target['departure'])<-1+1e-8
        r=input_recipe(row['input_mm'],target['point_mm'],d)
        strip=14 if row['holder'] in ('F_PI','F_AUX') else 11
        limit=50 if strip==14 else 84.5
        total=r['centreline_mm']+strip
        rows.append(dict(holder=row['holder'],target=row['target'],recipe=r,
            strip_allowance_mm=strip,required_blank_mm=total,
            nominal_fit_blank_mm=math.ceil(total),limit_mm=limit,
            exceeds_limit=total>limit,limit_not_a_route_or_thermal_acceptance=True))
    p=dict(status='LENGTH_ALLOCATION_REQUIRES_SHARED_CHANGE' if any(r['exceeds_limit'] for r in rows) else 'INPUT_LENGTHS_FIT_JOINT_GEOMETRY_STILL_OPEN',
        rows=rows,selected=False,stage_completed=False,physical_pass=False,
        constraints=['Preserve all five inputs and both exits; no automatic extension or stock increase',
            'Resolve lower-row S1 occupation AND source role/order/full input routes together before next heavy run',
            'No third casing-only gate; mutual input clearance and all changed endpoints still open'],
        geometry_gate_source_snapshot_commit='eeca478',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (
            OUT/'shared-allocation-plan.json',OUT/'shared-allocation-checks.json',
            Path(__file__),Path(V.__file__))},finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'shared-input-length-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],rows=[{k:r[k] for k in ('holder','required_blank_mm','limit_mm','exceeds_limit')} for r in rows])),flush=True)


def build_plan():
    rows = read(BASE/'mounting-checkpoint/distribution-mount-plan.json')['distribution']
    # Reorder equal615 roles together with source roles. AUX then reaches
    # P_REAR without an overlong prefuse run; the three southern inputs remain
    # in target-port order rather than crossing an entire holder bay.
    slots = dict(G_TAIL=1, D_RR=4, P_REAR=1, P_FRONT=2)
    distribution = []
    for i, row in enumerate(rows):
        level = (i % 10) // 5
        slot = slots.get(row['role'], i % 5)
        sign = 1 if row['side']=='L' else -1
        y = (75 if not level else (20 if slot==4 else UPPER_Y))*sign
        x=-47+40*slot if level else -62+37*slot
        distribution.append(dict(row, centre_mm=[x,y,120 if level else 67.99]))
    # Five parallel holders, alternating input sides. The outputs descend
    # outside the board perimeter. Existing broad carrier edges must be
    # redesigned together if they occupy these reserved output corridors.
    holders = []
    for name, x, sign, port in [('F_PI',-40,1,'P_SYS.2'),
            ('F_AUX',-15,1,'P_REAR.3'),('F_HY',10,-1,'P_AUX.2'),
            ('F_HP',35,-1,'P_AUX.3'),('F_TY',60,-1,'P_AUX.4')]:
        holders.append(dict(holder=name,input_mm=[x,25.5*sign,125],
            output_mm=[x,-25.5*sign,125],axis=[0,-sign,0],target=port,
            factory_radius_assumption_mm=6,output_first_straight_mm=3,
            output_straight_before_joint_mm=15,new_wire_grip_straight_mm=21.5,
            sleeve_clearance_OD_mm=6))
    # Apply to original logical ports, not the already-permuted old proof.
    permutation={'P_REAR.2':'P_REAR.5','P_REAR.3':'P_REAR.2','P_REAR.5':'P_REAR.3'}
    loads=occupancy(read(OUT/'routing-scope-plan.json'),permutation)
    input_rows=[]
    for holder in holders:
        role,number=holder['target'].rsplit('.',1)
        block=next(r for r in distribution if r['role']==role)
        centre=block['centre_mm'];width,depth,_=block['size_mm']
        target=[centre[0]-width/2+5.5+(int(number)-1)*(width-11)/4,
            centre[1]+(-depth/2 if block['side']=='L' else depth/2),centre[2]]
        recipe=input_recipe(holder['input_mm'],target,V.mul(holder['axis'],-1))
        strip=14 if holder['holder'] in ('F_PI','F_AUX') else 11
        limit=50 if strip==14 else 84.5
        total=recipe['centreline_mm']+strip
        input_rows.append(dict(holder=holder['holder'],target=holder['target'],
            target_mm=target,recipe=recipe,strip_allowance_mm=strip,
            required_blank_mm=total,limit_mm=limit,exceeds_limit=total>limit))
    paths=[MOUNTS,CONTEXT,OUT/'TailLocalCurrent.FCStd',
        BASE/'mounting-checkpoint/distribution-mount-plan.json',
        OUT/'source-layout-plan.json',OUT/'routing-scope-plan.json',__file__,Path(V.__file__)]
    return dict(status='SHARED_CASE_AND_EXIT_ALLOCATION_HYPOTHESIS',
        distribution=distribution,holders=holders,same_bus_permutation=permutation,
        input_recipes=input_rows,
        allocation_cause_change='Whole lower ten-case row uses37mm pitch and lastcaseXMax101<S1XMin114.2. Equal P_FRONT/P_REAR roles exchange upper slots; five source roles follow their port order. No new parts/splice or individual wire offset. Full five tangent input routes now part of joint gate, not a third bare-casing trial.',
        previous_geometry_snapshot_commit='eeca478',
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
    assert not any(r['exceeds_limit'] for r in plan['input_recipes']), 'Reject full bent blank BEFORE CAD'
    previous=OUT/'shared-allocation-checks.json'
    if previous.exists():
        old_gate=read(previous)
        plan['previous_gate']=old_gate.get('previous_gate',old_gate)
        plan['previous_gate_disposition']='First baseline retained, with invalid F_HP old-frame result. Second joint geometry snapshot eeca478 is preserved in Git:5 RL_G/S1 contacts,0outside/0errors. This gate changes whole lower row AND equal upper role/source assignment and includes ALL5 full input curves; no third bare-case/offset attempt.'
    docs=[A.openDocument(str(p)) for p in (MOUNTS,CONTEXT,OUT/'TailLocalCurrent.FCStd')]
    mount,ctx,tail=docs
    result=dict(status='PENDING',contacts=[],support_changes=[],outside_torso=[],
        errors=[],tested_pairs=0,ports=[],input_necessary_bounds=[],factory_input_rows=[],
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
            assert all(abs(v-w)<1e-6 for v,w in zip((b.XLength,b.YLength,b.ZLength),row['size_mm'])), 'Distribution reservation frame mismatch'
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
            inlet=next(r for r in plan['input_recipes'] if r['holder']==name)
            assert math.dist(inlet['target_mm'],next(r['point_mm'] for r in result['ports'] if r['role']==inlet['target']))<1e-7
            inlet_edges=[]
            for segment in inlet['recipe']['segments']:
                a,b=A.Vector(*segment['start']),A.Vector(*segment['end'])
                inlet_edges.append(Part.makeLine(a,b) if segment['kind']=='line' else Part.Arc(a,A.Vector(*segment['mid']),b).toShape())
            for a,b in zip(inlet_edges,inlet_edges[1:]):
                assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
                assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-7
            actual_radii=[e.Curve.Radius for e in inlet_edges if isinstance(e.Curve,Part.Circle)]
            assert min(actual_radii)>=6-1e-7
            wire=Part.Wire(inlet_edges)
            assert abs(wire.Length-inlet['recipe']['centreline_mm'])<1e-6
            new[name+'/factory_input']=wire.makePipeShell([
                Part.Wire([Part.makeCircle(2,A.Vector(*row['input_mm']),-axis)])],True,False)
            result['factory_input_rows'].append(dict(holder=name,target=inlet['target'],
                actual_centreline_mm=wire.Length,minimum_actual_radius_mm=min(actual_radii),
                required_blank_mm=inlet['required_blank_mm'],limit_mm=inlet['limit_mm'],
                first_straight_mm=inlet['recipe']['first_straight_mm'],last_grip_straight_mm=9,
                target_mm=inlet['target_mm'],factory_bend_and_OD_are_assumptions=True))
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
                # Factory input occupies its own intended port straight.
                holder_inputs={r['holder']+'/factory_input':'entry/'+r['target'] for r in plan['input_recipes']}
                if holder_inputs.get(n)==m or holder_inputs.get(m)==n:continue
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


if __name__=='__main__':
    if '--input-length-plan' in sys.argv:save_input_length_preflight()
    elif '--proposed-input-plan' in sys.argv:
        p=build_plan()
        compact={k:p[k] for k in ('status','distribution','holders','input_recipes','allocation_cause_change','previous_geometry_snapshot_commit','source_sha256','selected','stage_completed','physical_pass')}
        (OUT/'shared-allocation-input-plan.json').write_text(json.dumps(compact,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(inputs=[{k:r[k] for k in ('holder','required_blank_mm','limit_mm','exceeds_limit')} for r in p['input_recipes']],allocation=p['allocation_cause_change'])),flush=True)
    else:main()

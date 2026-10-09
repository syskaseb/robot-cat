"""Coupled power-island allocation; a negative planning gate, never a selection.

All twenty bus roles and both exits of four MTA/five FHAC are explicit.
Unrouted outputs remain OPEN rather than inheriting obsolete coordinates.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import sys
import time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha
from open_prototype_direct_mta_plan import route
from open_prototype_distribution_allocation import input_recipe
from open_prototype_complete_main_space import line, quarter, length
from open_prototype_entry_chambers import occupancy

OUT = BASE / 'wiring-checkpoint'
DEST = OUT / 'power-island-plan.json'


def build(layered=False):
    tick = time.monotonic()
    stations = []
    def station(role, centre, model='415', rotation='0'):
        stations.append(dict(role=role, centre_mm=centre, model=model,
            rotation=rotation, size_mm=([37,11,22] if rotation=='X90' else
                [19,30,9] if model=='415' and rotation in ('90','-90') else
                [37,22,11] if model=='615' else [30,19,9]),
            supplier_cavity_datum_known=False, mount_status='REQUIRES_MATCHED_NATIVE_MOUNT'))
    for i, role in enumerate(['FL_P','FR_P','FL_G','RL_P','RR_P']):
        x={'RL_P':73,'RR_P':107}.get(role,-62+37*i) if layered else -62+37*i
        station(role, [x,75,67.99])
    for i, role in enumerate(['D_FL','RL_G','RR_G']):
        station(role, [12+37*i,-75,67.99],rotation='180')
    station('FR_G',[-95,-50,55] if layered else [-25,50,67.99])
    station('D_FR',[12,50,67.99])
    station('P_SYS',[94,40,140] if layered else [-46,-33,145],'615','X90')
    station('P_FRONT',[-25,-40,145] if layered else [-14,-46,141.2],'615','X90' if layered else '180')
    station('P_REAR',[94,-40,140] if layered else [79.5,-41,120],'615','X90' if layered else '180')
    station('P_AUX',[34.5,16,142] if layered else [25,42,141.2],rotation='-90')
    for role,centre,model in [('G1',[-80,-42,105],'615'),
            ('G2',[-80,-17,115],'415'),('G_AUX',[34,-51,70],'415'),
            ('G_TAIL',[108,-43,109],'415'),('D_RL',[60,0,140],'415'),
            ('D_RR',[100,0,140],'415')]:
        station(role,[144,-68,81] if layered and role=='G_TAIL' else centre,model)
    assert len(stations)==len({r['role'] for r in stations})==20
    ports={}
    for s in stations:
        x,y,z=s['centre_mm'];pitch=6.5 if s['model']=='615' else 4.75
        depth=22 if s['model']=='615' else 19
        for n in range(1,6):
            shift=(n-3)*pitch;rot=s['rotation']
            point,dep=([x+shift,y-depth/2,z],[0,-1,0])
            if rot=='180':point,dep=[x-shift,y+depth/2,z],[0,1,0]
            if rot=='X90':point,dep=[x+shift,y,z-11],[0,0,-1]
            if rot=='-90':point,dep=[x-depth/2,y-shift,z],[-1,0,0]
            ports[f"{s['role']}.{n}"]=dict(point_mm=point,departure=dep,
                basis='Envelope-derived provisional entry, NOT supplier cavity datum')
    # A complete bijection inside each existing copper bus; no new connection.
    permutation={}
    for bus,mapping in [('P_FRONT',[(1,3),(2,1),(3,5),(4,4),(5,2)] if layered else [(1,4),(2,2),(3,1),(4,5),(5,3)]),
            ('P_REAR',[(1,2),(2,1),(3,5),(4,4),(5,3)] if layered else [(1,2),(2,5),(3,1),(4,4),(5,3)]),
            ('P_SYS',[(1,1),(2,5),(3,2),(4,4),(5,3)]),
            ('FL_P',[(1,5),(5,1)]),('FR_P',[(1,5),(5,1)])]:
        permutation.update({f'{bus}.{a}':f'{bus}.{b}' for a,b in mapping})
    scope=read(OUT/'routing-scope-plan.json');loads=occupancy(scope,permutation)
    assert len(ports)==100 and sum(bool(loads[p]) for p in ports)==86
    assert all(len(loads[p])<=1 for p in ports)
    endpoint=read(OUT/'endpoint-plan.json');ends=[]
    for w in endpoint['body_conductors']:
        for e in w['ends']:
            old=e['role'];current=permutation.get(old,old)
            ends.append(dict(wire=w['id'],net=w['net'],original_role=old,
                current_role=current,datum=ports.get(current),
                status='CANDIDATE_BUS_DATUM' if current in ports else 'END_REQUIRES_ROUTE_REBIND'))
    assert len(ends)==160
    tails=[];mta=[]
    for leg,x,outx,ident,source,output,target in [
            ('FL',-50,-52.5,'W041','P_FRONT.1' if layered else 'P_FRONT.2','W026','FL_P.5'),
            ('FR',0,-15.5,'W042','P_FRONT.5' if layered else 'P_FRONT.1','W037','FR_P.5'),
            ('RL',69 if layered else 45,63.5 if layered else 39.5,'W044','P_REAR.1' if layered else 'P_REAR.5','W045','RL_P.1'),
            ('RR',103 if layered else 85,97.5 if layered else 76.5,'W052','P_REAR.5' if layered else 'P_REAR.1','W053','RR_P.1')]:
        mta.append(dict(role='MTA_'+leg,centre_mm=[x,21,120],size_mm=[22,35,16],
            rotation_z_deg=90,source_exit_mm=[x,3.5,120],output_exit_mm=[x,38.5,120]))
        for wire,side,start,role,radius,strip in [
                (ident,'source',[x,3.5,120],source,6,14),
                (output,'output',[x,38.5,120],target,7.5,11)]:
            end=ports[role]['point_mm']
            if layered and side=='source':
                mid=[end[0],end[1]+6,end[2]-15]
                recipe=route(start,mid,6)
                arc=quarter(mid,[0,-1,0],[0,0,1],6)
                recipe['segments'] += [arc,line(arc['end'],end)]
                recipe['centreline_mm'] += math.pi*3+9
                recipe['grip_direction']=[0,0,1]
            else:recipe=route(start,end,radius)
            blank=recipe['centreline_mm']+strip
            assert blank<=100
            # Check the physical ID ends in the new port, not just its net.
            assert any(e['wire']==wire and e['current_role']==role for e in ends)
            tails.append(dict(wire=wire,leg=leg,side=side,target=role,recipe=recipe,
                required_blank_mm=blank,assumed_factory_limit_mm=100,
                factory_limit_not_catalog=True,independent_grip_mm=9))
    holders=[]
    holder_specs=[
            ('F_PI',[-9.5,-33,119],'P_SYS.5',[1,0,0],None),
            ('F_AUX',[94.5,-15,120],'P_REAR.3',[1,0,0],None),
            ('F_HY',[-50,36.5,141.2],'P_AUX.2',[0,-1,0],None),
            ('F_HP',[-25,29,141.2],'P_AUX.3',[0,-1,0],None),
            ('F_TY',[0,28.25,141.2],'P_AUX.4',[0,-1,0],None)]
    if layered:
        holder_specs=[('F_PI',[116,40,114],'P_SYS.5',[1,0,0],None),
            ('F_AUX',[116,-40,114],'P_REAR.3',[1,0,0],None)]+[
            (role,[1,y,139],target,[-1,0,0],None) for role,y,target in
            [('F_HY',42,'P_AUX.2'),('F_HP',16,'P_AUX.3'),('F_TY',-10,'P_AUX.4')]]
    for role,start,target,axis,parts in holder_specs:
        end=ports[target]['point_mm']
        if layered and role in ('F_PI','F_AUX'):
            a=[end[0]+6,start[1],start[2]];arc=quarter(a,[-1,0,0],[0,0,1],6)
            parts=[line(start,a),arc,line(arc['end'],end)]
        elif layered:
            recipe=input_recipe(start,end,[1,0,0],6);parts=recipe['segments']
        elif role=='F_PI':
            a=[-27,-33,119];arc=quarter(a,[-1,0,0],[0,0,1],6)
        elif role=='F_AUX':
            a=[85.5,-15,120];arc=quarter(a,[-1,0,0],[0,-1,0],6)
        else:
            a=[start[0],end[1]-6,start[2]];arc=quarter(a,[0,1,0],[1,0,0],6)
        if not layered:parts=[line(start,a),arc,line(arc['end'],end)]
        centreline=recipe['centreline_mm'] if layered and role not in ('F_PI','F_AUX') else length(parts)
        blank=centreline+(14 if role in ('F_PI','F_AUX') else 11)
        limit=50 if role in ('F_PI','F_AUX') else 84.5
        assert blank<=limit
        original_target=next((e['current_role'] for e in ends if e['wire']=='W043'
            and e['original_role']=='P_SYS.2'),None) if role=='F_PI' else next(
            permutation.get(e,e) for r in endpoint['distribution_boundary']
            if role+'.in' in r['ends'] for e in r['ends'] if e!=role+'.in')
        assert target==original_target,(role,target,original_target)
        output=[v+51*d for v,d in zip(start,axis)]
        centre=[v+25.5*d for v,d in zip(start,axis)];centre[2]+=1
        holders.append(dict(role=role,input_mm=start,output_mm=output,axis=axis,
            centre_mm=centre,size_mm=[51,20.25,22] if axis[0] else [20.25,51,22],
            input_target=target,input_segments=parts,input_blank_mm=blank,
            minimum_factory_mm=84.5,prefuse_project_limit_mm=limit,
            output_status='OPEN: covered joint and downstream route need shared allocation',
            restraint_status='Last input straight reserved; independent native restraint OPEN'))
    result=dict(status='COUPLED_POWER_ISLAND_PLAN_NOT_LAYOUT_ACCEPTANCE',
        selected=False,stage_completed=False,W5_complete=False,physical_pass=False,
        changed_cause=('Separate three head/tail FHAC above central MTA, short Pi/AUX islands at rear sides, vertical source entries and matched lower output buses'
            if layered else 'One lower front S1/F0 island with upper source distribution and central straight-through MTA; moved ground/data cases clear control'),
        stations=stations,ports=ports,permutation=permutation,body_ends=ends,
        occupied_ports=86,NC_ports=14,mta=mta,tails=tails,holders=holders,
        s1=dict(centre_mm=[-46,-55.5,55],rotation_z_deg=180,size_mm=[24,37,42],
            control_centre_mm=[-46,-91,55],control_size_mm=[28,34,28],
            terminal_barrels_mm={'W064':[-17.877,-33,43],
                'W065':[-74.123,-33,43],'W067':[-40,-33,77.123],
                'W068':[-52,-33,77.123]},routes_status='ALL4_FULL_ROUTES_OPEN'),
        f0=dict(centre_mm=[-2.5,-58.8,50],size_mm=[51,20.25,22],
            placement_delta_mm=[20,0,0],source_routes_and_mounts='INVALIDATED_REQUIRES_REBIND'),
        installation_dependencies=[
            'Deenergized assembly only; isolation/polarity preparation is not a power-on test',
            'S1 rings before MAIN because upper ring tool may cross MAIN; repair dependency must be qualified',
            'Rebuild matched S1/F0/station supports only after the shared allocation gate',
            'Both connector sides/independent grips and ATO access must remain reachable from assembled prototype'],
        invalidated=['20 old station mounts','MTA mounts at former poses',
            'S1/F0 mounts and four old S1 blanks totalling920mm','All inherited station wire datums'],
        open_items=['Full five FHAC output joints/routes and mutual input clearance',
            'Four complete S1 routes and lower/upper ring/tool clearance',
            'Remaining body/leg/source routes and cable-end binding',
            'WAGO lever/access and independent cable grips','Actual full411object BRep clearance',
            'Matched native mounts/assembly/removal/export/lengths/stock',
            'Delivered U1 pinout/S0 datums/MTA per-side usable lengths remain delivery gates'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (
            OUT/'obstacle-map-current.json',OUT/'endpoint-plan.json',OUT/'routing-scope-plan.json',
            Path(__file__),ROOT/'tools/cad/open_prototype_direct_mta_plan.py')},
        worker_seconds=round(time.monotonic()-tick,6),
        finished_utc=datetime.now(timezone.utc).isoformat())
    return result


def gate(layered=False):
    """One whole allocation budget gate, including13 newly declared inputs.

    This rejects impossible space budgets, NOT measured supplier collisions.
    It deliberately cannot accept the plan with output/S1/full routes OPEN.
    """
    import FreeCAD as A
    import Part
    from open_prototype_entry_chambers import CONTEXT
    tick=time.monotonic();plan_path=OUT/'power-island-layered-plan.json' if layered else DEST
    plan=read(plan_path)
    rebuilt=build(layered)
    for field in ('stations','ports','permutation','body_ends','mta','tails','holders','s1','f0'):
        assert rebuilt[field]==plan[field], 'Gate must use the same generated geometry/net binding: '+field
    dest=OUT/('power-island-layered-gate.json' if layered else 'power-island-gate.json')
    assert not dest.exists(), 'Receive existing gate; no unchanged repeat'
    from open_prototype_entry_chambers import MOUNTS
    tail_path=OUT/'TailLocalCurrent.FCStd'
    files=[plan_path,CONTEXT,OUT/'obstacle-map-current.json',Path(__file__),MOUNTS,tail_path]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    doc=A.openDocument(str(CONTEXT));mount=A.openDocument(str(MOUNTS));tail=A.openDocument(str(tail_path))
    scene=[];pipes=[];retained=[]
    result=dict(status='PENDING',selected=False,stage_completed=False,
        physical_pass=False,source_sha256=pins,errors=[],outside=[],
        budget_overlaps=[],input_overlaps=[],tested_budget_pairs=0,
        tested_input_pairs=0,plan_geometry_rebuilt_equal=True,retained_contacts=[],
        tested_retained_pairs=0,
        scope='31station/MTA/FHAC/S1/F0 budgets plus external S1 control;13input paths;9retained whole-module budgets plus valid retained solids from the411object inventory. Full output/assembly clearance remains OPEN.')
    def box(c,size):
        return Part.makeBox(*size,A.Vector(*[x-d/2 for x,d in zip(c,size)]))
    def add(name,c,size,external=False):
        s=box(c,size);assert s.isValid() and len(s.Solids)==1
        scene.append((name,s,external))
    def tube(parts,od):
        edges=[Part.makeLine(A.Vector(*p['start']),A.Vector(*p['end']))
            if p['kind']=='line' else Part.Arc(A.Vector(*p['start']),
                A.Vector(*p['mid']),A.Vector(*p['end'])).toShape() for p in parts]
        path=Part.Wire(edges);first=edges[0]
        circle=Part.Wire([Part.makeCircle(od/2,first.Vertexes[0].Point,
            first.tangentAt(first.FirstParameter))])
        s=path.makePipeShell([circle],True,False)
        assert s.isValid() and len(s.Solids)==1,'Invalid sweep is not clearance'
        return s
    try:
        torso=doc.TorsoEnvelope.Shape;assert torso.isValid() and len(torso.Solids)==1
        for s in plan['stations']+plan['mta']+plan['holders']:
            add(s['role'],s['centre_mm'],s['size_mm'])
        add('S1_body',plan['s1']['centre_mm'],plan['s1']['size_mm'])
        add('F0',plan['f0']['centre_mm'],plan['f0']['size_mm'])
        add('S1_control',plan['s1']['control_centre_mm'],plan['s1']['control_size_mm'],True)
        assert len(scene)==32
        modules=[]
        for r in read(OUT/'obstacle-map-current.json')['objects']:
            if (r['basis'].startswith('Canonical whole-component/reference envelope')
                    or r['name']=='U1UnknownModuleReservation') and r['name']!='F0_CP2':
                b=r['bounds_mm'];modules.append((r['name'],box(
                    [(b[k]+b[k+3])/2 for k in range(3)],
                    [b[k+3]-b[k] for k in range(3)]),False))
        assert len(modules)==9
        result['retained_budget_names']=[n for n,_,_ in modules]
        inventory=read(OUT/'obstacle-map-current.json')['objects']
        excluded=[]
        for r in inventory:
            n=r['name']
            if r['kind'] in ('candidate_station','replaceable_support') or n.startswith('S1'):
                excluded.append(dict(name=n,reason='Relocated candidate/support/S1; matched replacement qualification OPEN'))
                continue
            if r['basis'].startswith('Canonical whole-component/reference envelope') or n=='U1UnknownModuleReservation':
                continue # Explicit whole-component budgets already in modules.
            obj=tail.CurrentTailSupport if n=='CurrentTailSupport' else doc.getObject(n) or mount.getObject(n)
            assert obj is not None and hasattr(obj,'Shape'), 'Unresolved retained reference: '+n
            s=obj.Shape
            assert s.isValid() and s.Solids, 'Invalid preserved BRep is not clearance: '+n
            retained.append((n,s,r['kind']))
        assert sum(n.startswith('F_') and '_CP2_' in n for n,_,_ in retained)>=48
        assert any(n=='CurrentTailSupport' for n,_,_ in retained)
        assert any(n=='F_PWM_CP2' for n,_,_ in retained)
        result.update(retained_solid_count=len(retained),excluded_changed_interfaces=excluded)
        for n,s,external in scene:
            if not external:
                outside=s.cut(torso);assert outside.isValid()
                if outside.Volume>1e-6:
                    result['outside'].append(dict(name=n,volume_mm3=round(outside.Volume,6)))
        for i,(n,s,_) in enumerate(scene):
            for other,q,_ in scene[:i]+modules:
                if not s.BoundBox.intersect(q.BoundBox):continue
                hit=s.common(q);assert hit.isValid()
                result['tested_budget_pairs']+=1
                if hit.Volume>1e-6:
                    result['budget_overlaps'].append(dict(a=n,b=other,volume_mm3=round(hit.Volume,6)))
        for r in plan['tails']:
            pipes.append((r['wire'],tube(r['recipe']['segments'],4),r['target'].split('.')[0],
                'MTA_'+r['leg'] if 'leg' in r else next(m['role'] for m in plan['mta']
                    if m['source_exit_mm']==r['recipe']['segments'][0]['start']
                    or m['output_exit_mm']==r['recipe']['segments'][0]['start'])))
        for r in plan['holders']:
            pipes.append((r['role']+'_input',tube(r['input_segments'],4),
                r['input_target'].split('.')[0],r['role']))
        assert len(pipes)==13
        for n,s,*_ in scene+pipes:
            for other,q,kind in retained:
                if not s.BoundBox.intersect(q.BoundBox):continue
                hit=s.common(q);assert hit.isValid();result['tested_retained_pairs']+=1
                if hit.Volume>1e-6:result['retained_contacts'].append(dict(candidate=n,
                    reference=other,kind=kind,volume_mm3=round(hit.Volume,6),
                    interpretation='Planning volume intersects retained valid BRep; not measured supplier-part contact'))
        for i,(n,s,receiver,source) in enumerate(pipes):
            outside=s.cut(torso);assert outside.isValid()
            if outside.Volume>1e-6:result['outside'].append(dict(name=n,volume_mm3=round(outside.Volume,6)))
            for other,q,_ in scene+modules:
                # Named face exits of the same declared source/receiver only.
                # All third-party budgets remain in scope.
                if other in (receiver,source) or not s.BoundBox.intersect(q.BoundBox):continue
                hit=s.common(q);assert hit.isValid();result['tested_input_pairs']+=1
                if hit.Volume>1e-6:result['input_overlaps'].append(dict(a=n,b=other,volume_mm3=round(hit.Volume,6)))
            for other,q,_,_ in pipes[:i]:
                if not s.BoundBox.intersect(q.BoundBox):continue
                hit=s.common(q);assert hit.isValid();result['tested_input_pairs']+=1
                if hit.Volume>1e-6:result['input_overlaps'].append(dict(a=n,b=other,volume_mm3=round(hit.Volume,6)))
        result['status']='REQUIRES_COUPLED_CAUSE_CHANGE' if any(result[k] for k in
            ('outside','budget_overlaps','input_overlaps','retained_contacts')) else 'BUDGET_GATE_ONLY_FULL_OUTPUT_AND_ASSEMBLY_OPEN'
    except Exception as exc:
        result['errors'].append(str(exc));raise
    finally:
        for d in (doc,mount,tail):A.closeDocument(d.Name)
        result.update(worker_seconds=round(time.monotonic()-tick,3),
            finished_utc=datetime.now(timezone.utc).isoformat())
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    print(json.dumps(result),flush=True)


if __name__=='__main__' and '--gate' in sys.argv:
    gate('--layered' in sys.argv)
elif __name__=='__main__':
    layered='--layered' in sys.argv
    result=build(layered)
    if layered:DEST=OUT/'power-island-layered-plan.json'
    assert not DEST.exists(), 'Receive existing plan; no unchanged repeat'
    DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],stations=len(result['stations']),
        mta_tails=len(result['tails']),holder_inputs=[round(h['input_blank_mm'],3) for h in result['holders']],
        seconds=result['worker_seconds'])),flush=True)

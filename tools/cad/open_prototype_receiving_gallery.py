"""One coupled receiving-face plan; validate space before rebuilding mounts.

Four power stations turn toward X. Five complete source inputs and output
joints are allocated together, not five casing-only retries. The eight main
feeds and four S1 conductors have explicit endpoint/grip reservations; their
full continuations are OPEN and must not be inferred from this gate.
"""
from datetime import datetime, timezone
from pathlib import Path
import copy, json, math, time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds
from open_prototype_entry_chambers import MOUNTS, CONTEXT
from open_prototype_distribution_allocation import input_recipe
from open_prototype_complete_main_space import line, quarter
from open_prototype_bundle_spines import add, mul

OUT = BASE/'wiring-checkpoint'
PLAN = OUT/'receiving-gallery-plan.json'
PROOF = OUT/'receiving-gallery-checks.json'


def build():
    allocation = read(OUT/'shared-allocation-plan.json')
    old_ports = read(OUT/'shared-allocation-checks.json')['ports']
    distribution = copy.deepcopy(allocation['distribution'])
    changed = {'P_SYS': [145,50,120], 'P_REAR': [145,-50,120],
               'P_FRONT': [84,0,140], 'P_AUX': [-28,50,138]}
    poses = {r['role']:r for r in distribution}
    ports = copy.deepcopy(old_ports)
    for row in distribution:
        row['rotation_z_deg'] = -90 if row['role'] in changed else 0
        if row['role'] in changed:
            row['old_centre_mm'] = row['centre_mm'][:]
            row['centre_mm'] = changed[row['role']]
    for p in ports:
        role = p['role'].split('.')[0]
        if role not in changed: continue
        row = poses[role]; c0 = row['old_centre_mm']; c1 = row['centre_mm']
        x,y,z = [p['point_mm'][i]-c0[i] for i in range(3)]
        p['point_mm'] = [c1[0]+y,c1[1]-x,c1[2]+z]
        dx,dy,dz = p['departure']; p['departure'] = [dy,-dx,dz]
        p['basis'] = 'Rotated existing PROJECT entry frame, not delivered manufacturer datum'
    by_port = {p['role']:p for p in ports}
    holders=[]
    for name, inlet, axis, target in [
        ('F_PI',[110,40,120],[-1,0,0],'P_SYS.2'),
        ('F_AUX',[110,-50,120],[-1,0,0],'P_REAR.3'),
        ('F_HY',[7,50,138],[1,0,0],'P_AUX.2'),
        ('F_HP',[7,25,138],[1,0,0],'P_AUX.3'),
        ('F_TY',[7,0,138],[1,0,0],'P_AUX.4')]:
        end=by_port[target]['point_mm']; direction=mul(axis,-1)
        if math.dist(add(inlet,mul(direction,math.dist(inlet,end))),end)<1e-7:
            recipe=dict(segments=[line(inlet,end)],centreline_mm=math.dist(inlet,end),
                        first_straight_mm=math.dist(inlet,end),grip_straight_mm=9)
        else: recipe=input_recipe(inlet,end,direction,6)
        strip=14 if name in ('F_PI','F_AUX') else 11
        limit=50 if strip==14 else 84.5
        assert recipe['centreline_mm']+strip<=limit, (name,recipe)
        output=add(inlet,mul(axis,51)); a=add(output,mul(axis,3))
        parts=[line(output,a)]
        if name=='F_HY':
            # One planned bypass: above Pi, then outside D_RL; not a pinched
            # vertical drop through either retained casing.
            turn=quarter(a,axis,[0,1,0],6); parts.append(turn)
            a=add(turn['end'],[0,18,0]);parts.append(line(turn['end'],a))
            turn=quarter(a,[0,1,0],[0,0,-1],6)
        else: turn=quarter(a,axis,[0,0,-1],6)
        parts.append(turn); cut=add(turn['end'],[0,0,-15])
        parts.append(line(turn['end'],cut))
        holders.append(dict(holder=name,input_mm=inlet,output_mm=output,axis=axis,
            target=target,input_parts=recipe['segments'],input_centreline_mm=recipe['centreline_mm'],
            input_blank_mm=recipe['centreline_mm']+strip,input_limit_mm=limit,
            output_parts=parts,cut_mm=cut,factory_OD_assumed_mm=4,factory_radius_assumed_mm=6,
            sleeve_OD_assumed_mm=6,sleeve_blank_mm=26.5,new_wire_OD_mm=2.1,
            output_load_continuation_open=True))
    main_targets={'W041':'P_FRONT.2','W042':'P_FRONT.3','W044':'P_REAR.5','W052':'P_REAR.2',
                  'W026':'FL_P.1','W037':'FR_P.1','W045':'RL_P.1','W053':'RR_P.1'}
    endpoints=read(OUT/'endpoint-plan.json')['body_conductors']
    s1=[]
    for ident,target in [('W064','P_FRONT.1'),('W065','P_REAR.1'),
                         ('W067','P_SYS.3'),('W068','P_SYS.4')]:
        original=next(r for r in endpoints if r['id']==ident)
        switch=next(e for e in original['ends'] if e['role'].startswith('S1.'))
        s1.append(dict(id=ident,ring=copy.deepcopy(switch),target=target,
            entry_mm=by_port[target]['point_mm'],departure=by_port[target]['departure'],
            full_route_and_replacement_of_legacy_920mm_open=True))
    pins=(MOUNTS,CONTEXT,OUT/'shared-allocation-plan.json',OUT/'shared-allocation-checks.json',
          OUT/'routing-space-map.json',OUT/'endpoint-plan.json',Path(__file__))
    return dict(status='RECEIVING_FACE_AND_FIVE_COMPLETE_SOURCE_ENDS_HYPOTHESIS',
        selected=False,stage_completed=False,physical_pass=False,
        distribution=distribution,ports=ports,holders=holders,mts=allocation['mts'],
        main_targets=main_targets,S1=s1,
        HELU_manufacturer=dict(url='https://assets-cdn.helukabel.com/suppliers/Helukabel/documents/db/HELUKABEL_M23201_EN_GB.pdf',
            revision_date='2025-07-24',page=1,part=23802,approx_OD_mm=4.2,
            fixed_radius_OD_multiplier=6,fixed_radius_nominal_mm=25.2,
            no_sharper_bend_permitted_for_convenience=True),
        invalidated=['Four rotated power-WAGO mounts and all affected fanouts',
            'Five FHAC cases/input/output seats, common platform and splice restraints'],
        preserved=['P0/E6/15drives/MG92B/325x200x160/MAIN46.52/bankR47',
            'Four MTA casings and validated mounting poses; not their full factory-tail routes',
            'Sixteen unchanged WAGO case poses; no new selection of historical mounts'],
        sequence=['Bench install retained fasteners/boards; supplier pinouts remain delivery gates',
            'Restrain each input/output independently on insulation, never through WAGO levers',
            'Five ATOs accessed from open roof without disconnecting74WAGO ends',
            'Before native rebuild solve all8main/S1/body/head/tail/leg continuations in this same space'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins})


def main():
    import FreeCAD as A
    import Part
    assert not PLAN.exists() and not PROOF.exists(), 'Receive existing result; no unchanged rerun'
    tick=time.monotonic();plan=build();PLAN.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (MOUNTS,CONTEXT,OUT/'CommonMtaMounts.FCStd')]
    mount,ctx,native=docs;items={};owners={};actual={}
    result=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,
        contacts=[],errors=[],outside=[],pairs=0,paths=[],source_sha256=dict(plan['source_sha256'],
            **{(OUT/'CommonMtaMounts.FCStd').relative_to(ROOT).as_posix():sha(OUT/'CommonMtaMounts.FCStd')}))
    def put(n,s,owner):
        assert s.isValid() and len(s.Solids)==1 and not s.check(True), n
        items[n]=s;owners[n]=owner
    def pipe(n,parts,od,owner):
        edges=[Part.makeLine(A.Vector(*p['start']),A.Vector(*p['end'])) if p['kind']=='line'
            else Part.Arc(A.Vector(*p['start']),A.Vector(*p['mid']),A.Vector(*p['end'])).toShape() for p in parts]
        for a,b in zip(edges,edges[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
            assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-7
        e=edges[0];w=Part.Wire(edges)
        put(n,w.makePipeShell([Part.Wire([Part.makeCircle(od/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False),owner)
        result['paths'].append(dict(name=n,centreline_mm=w.Length))
    try:
        for row in plan['distribution']+plan['mts']:
            o=mount.getObject(row['native']) or ctx.getObject(row['native']);s=o.Shape.copy();b=s.BoundBox
            s.translate(-A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2))
            if row.get('rotation_z_deg'):s.rotate(A.Vector(),A.Vector(0,0,1),row['rotation_z_deg'])
            s.translate(A.Vector(*row['centre_mm']));put(row['native'],s,row['native'])
        for row in plan['holders']:
            n=row['holder'];s=mount.getObject(n+'_body_budget_CurrentReference').Shape.copy();b=s.BoundBox
            s.translate(-A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2))
            rot=A.Rotation(A.Vector(1,0,0),A.Vector(*row['axis']))
            s.rotate(A.Vector(),rot.Axis,rot.Angle*180/math.pi)
            s.translate(A.Vector(*row['input_mm'])+A.Vector(*row['axis'])*25.5+A.Vector(0,0,1))
            put(n+'/case',s,n+'/case');pipe(n+'/input',row['input_parts'],4,n+'/input')
            pipe(n+'/output',row['output_parts'],4,n+'/output')
            cut=A.Vector(*row['cut_mm'])
            put(n+'/sleeve',Part.makeCylinder(3,26.5,cut+A.Vector(0,0,14),A.Vector(0,0,-1)),n+'/output')
            put(n+'/new_insulation',Part.makeCylinder(1.05,21.5,cut,A.Vector(0,0,-1)),n+'/output')
            b=s.BoundBox
            put(n+'/ATO_tool_budget',Part.makeBox(22,10,35,A.Vector((b.XMin+b.XMax)/2-11,(b.YMin+b.YMax)/2-5,b.ZMax)),n+'/tool')
        ports={p['role']:p for p in plan['ports']}
        for n,role in plan['main_targets'].items():
            p=ports[role];a=add(p['point_mm'],mul(p['departure'],9))
            pipe(n+'/entry9mm',[line(a,p['point_mm'])],4.2,n)
        for row in plan['S1']:
            p=row['ring'];a=p['point_mm'];b=add(a,mul(p['departure'],9))
            pipe(row['id']+'/ring9mm',[line(a,b)],4.2,row['id'])
            p=ports[row['target']];a=add(p['point_mm'],mul(p['departure'],9))
            pipe(row['id']+'/entry9mm',[line(a,p['point_mm'])],4.2,row['id'])
        for o in native.Objects:
            if o.TypeId=='PartDesign::Body':actual[o.Name]=o.Shape
        for o in mount.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
            if o.Name.endswith('NominalPCB') or o.Name.startswith('BUSsupplier') or o.Name=='U1BoardAllowance':actual[o.Name]=o.Shape
            if 'Group' in o.PropertiesList and 'Hardware' in o.Name:
                actual.update({p.Name:p.Shape for p in o.Group if 'Shape' in p.PropertiesList and not p.Shape.isNull()})
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) and o.Name!='P0_MG92BMount29':actual[o.Name]=o.Shape
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['pairs']+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        entries={r['holder']+'/input':r['target'].split('.')[0]+'_CP2' for r in plan['holders']}
        entries.update({n+'/entry9mm':role.split('.')[0]+'_CP2' for n,role in plan['main_targets'].items()})
        entries.update({r['id']+'/entry9mm':r['target'].split('.')[0]+'_CP2' for r in plan['S1']})
        pairs=list(items.items())
        for i,(n,s) in enumerate(pairs):
            if not n.endswith('/ATO_tool_budget'):
                outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
                if outside.Volume>1e-5:result['outside'].append(dict(part=n,volume_mm3=outside.Volume,bounds_mm=bounds(outside)))
            for m,t in actual.items():
                if n.endswith('/ring9mm') and m==next(r['ring']['native'] for r in plan['S1'] if r['id']==n.split('/')[0]):continue
                check(n,s,m,t)
            for m,t in pairs[i+1:]:
                if owners[n]==owners[m] or entries.get(n)==m or entries.get(m)==n:continue
                if n.endswith('_CP2') and m.endswith('_CP2'):continue # unchanged valid cases, except changed cases below
                check(n,s,m,t)
        # Changed casing pairs must never be hidden by the unchanged-pair reuse.
        changed={r['native'] for r in plan['distribution'] if r['rotation_z_deg']}
        casings=[(n,s) for n,s in pairs if n.endswith('_CP2')]
        for i,(n,s) in enumerate(casings):
            for m,t in casings[i+1:]:
                if n in changed or m in changed:check(n,s,m,t)
        result['status']='RECEIVING_GALLERY_REQUIRES_CAUSE_CHANGE' if any(result[k] for k in ('contacts','outside','errors')) else 'RECEIVING_GALLERY_SOURCE_ENDS_CLEAR_FULL_MAIN_ROUTES_AND_MOUNTS_OPEN'
    finally:
        for d in docs:A.closeDocument(d.Name)
        result.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        PROOF.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/p)==h for p,h in result['source_sha256'].items())
    print(json.dumps({k:result[k] for k in ('status','pairs','contacts','outside','errors','worker_seconds')}),flush=True)


if __name__=='__main__': main()

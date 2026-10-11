"""Read-only actual nominal material gate for the ONE coupled cable plan.

No solver, recompute, new native detail or inherited green moving-loop screen.
Both changed rails and the already qualified BUS carrier are explicit. A
nominal contact stops motion qualification; bbox only selects exact pairs.
"""
import json,time
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,SHA
from current_material_reservations import terminal_owners


def run():
    tick=time.monotonic();source=OUT/'fl-bus-group-plan.json'
    plan=json.loads(source.read_text())
    assert plan['status']=='COUPLED_FL_BUS_PLANNING_ONLY' and not plan['endpoint_failures']
    assert len(plan['routes'])==40
    for n,h in plan['source_sha256'].items():assert SHA(ROOT/n)==h,n
    prior=OUT/plan['retained_families_reference'];reference=json.loads(prior.read_text())
    replaced=set(plan['rear_receiving_changes'])|{'FL3'}
    looms=[q for q in reference['looms'] if q['loom'] not in replaced]
    looms+=list(plan['rear_receiving_changes'].values())+[plan['candidate_FL3']]
    assert len(looms)==12
    from current_complete_harness_context import context,W,Part
    from plan_current_tail_complete import tie_z
    A=W.A;reader,pins,targets,old=context();pins.update((source,prior,Path(__file__)))
    native=OUT/'BUSCarrierCurrent.FCStd';pins.add(native)
    targets['UpperCarrier001']=reader.shape(native,'UpperCarrier001')
    for n,r in plan['rails'].items():
        assert n in targets,n
        targets[n]=W.box(r['casing_mm'])
    # Retain the actual previously prepared BUS band and head. They are not
    #the source jaw material already integrated into UpperCarrier001.
    cols=[p[2]['start'] for p in plan['source_prefixes'].values()]
    x=sum(p[0] for p in cols)/2;z=cols[0][2]+4.5
    band,head=tie_z(z,x-5.8,x+2.3,min(p[1] for p in cols)-2.2,max(p[1] for p in cols)+2.2)
    targets.update(BUSBand=band,BUSHead=head)
    for n in plan['invalidated_wire_ids']:old.pop(n,None)
    result=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,W5_complete=False,
        physical_pass=False,native_changed=False,nominal_looms=12,complete_static_guides=40,
        motion_qualified=False,delivered_connector_and_insulation_fit_open=True)

    def wire(parts):
        edges=[]
        for q in parts:
            if q['kind']=='bezier':
                c=Part.BezierCurve();c.setPoles([A.Vector(*v) for v in q['poles_mm']]);edges.append(c.toShape())
            else:edges.extend(W.makewire([q]).Edges)
        c=Part.Wire(edges);assert c.isValid()
        return c

    def trim(c,first,land):
        """Trim real curve travel, including arcs, not an endpoint chord."""
        es=list(c.Edges)
        while land>1e-8:
            i=0 if first else -1;e=es[i]
            if e.Length<=land+1e-8:land-=e.Length;es.pop(i);continue
            t=e.getParameterByLength(land if first else -land)
            es[i]=e.Curve.toShape(t,e.LastParameter) if first else e.Curve.toShape(e.FirstParameter,t)
            land=0
        q=Part.Wire(es);assert q.isValid();return q

    def pair(n,c,r,m,t,rr=0):
        if not W.near(c,t,r+rr):return
        if not c.isValid() or not t.isValid():
            result['errors'].append(dict(a=n,b=m,cause='INVALID_BREP'));return
        result['pairs']+=1
        try:d,pts,_=c.distToShape(t)
        except Exception as e:
            result['errors'].append(dict(a=n,b=m,cause=repr(e)));return
        if d<r+rr-1e-4:result['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=r+rr,
            witness_mm=[list(v) for v in pts[0]] if pts else None))

    curves={};ownership={};roles={}
    endfile=OUT/plan['body_ends_reference'];pins.add(endfile)
    ends=json.loads(endfile.read_text())
    for q in ends.get('wires',ends.get('leg_body_ends')):roles[q['wire']]=q['body_role'].split('.')[0]
    roles.update(W002='D_FL',W003='G2',W007='D_FR',W025='G1')
    for row in looms:
        pose=next(v for v in row['poses'] if not any(v['angles']))
        p=[]
        if row['initial_land_mm']:p.append(dict(kind='line',start=pose['start'],end=pose['flex_start']))
        p+=pose.get('departure_parts_mm',[])+pose.get('transition_parts_mm',[])
        p+= [dict(kind='bezier',poles_mm=q) for q in pose.get('spans_mm',[])]
        p+=pose.get('return_parts_mm',[])
        c=wire(p)
        assert abs(sum(e.Length for e in c.Edges)-row['initial_land_mm']-row['fixed_bundle_guide_mm'])<.001
        curves['Loom/'+row['loom']]=(c,3)
        for v in row['cores'].values():ownership[v['wire']]='Loom/'+row['loom']
    for n,q in plan['routes'].items():curves[n]=(wire(q['parts']),2.1 if n=='W025' else 1)
    for n,(c,r) in curves.items():
        for m,t in targets.items():
            if not t.Solids:continue
            receiver=roles.get(n)
            cc=trim(c,False,3) if receiver and m in terminal_owners(receiver) else c
            # W025/W007 start at changed FL rails, ending at G1/D_FR.
            if n in ('W025','W007') and m==('FL_G' if n=='W025' else 'D_FL'):cc=trim(cc,True,3)
            pair(n,cc,r,m,t)
        for m,(t,rr) in old.items():pair(n,c,r,m,t,rr)
        for m,(t,rr) in curves.items():
            if m<=n:continue
            # Only the packed-core split's first5mm intentionally shares
            #the jacket endpoint; remote overlap remains tested exactly.
            cc=trim(c,True,5) if ownership.get(n)==m else c
            tt=trim(t,True,5) if ownership.get(m)==n else t
            pair(n,cc,r,m,tt,rr)
        print('Coupled material',n,'contacts',len(result['contacts']),'errors',len(result['errors']),flush=True)
    result.update(status='REJECTED_COUPLED_NOMINAL_MATERIAL' if result['contacts'] or result['errors'] else 'COUPLED_NOMINAL_MATERIAL_ONLY_MOTION_NATIVE_OPEN',
        worker_seconds=time.monotonic()-tick,source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():SHA(p) for p in pins}})
    (OUT/'fl-bus-group-material.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    return result


if __name__=='__main__':run()

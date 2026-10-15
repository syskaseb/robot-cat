"""Four source allocations integrated with current W024/twenty receiver grips.

The shared source gate is reused, with an explicitly pinned context adapter;
no historic recipes/native files are overwritten. Twelve full core breakouts
then receive the same actual-material checks. Rooted arms/36cores stay open.
"""
import json,time
from pathlib import Path
import core_receiver_port as T
import check_near_axis_hip_sources as C
P=C.P


def run():
    tick=time.monotonic();layout=P.OUT/'body-receiver-relief-layout.json';gripsfile=P.OUT/'receiver-relief-approach-plan.json'
    current,grips=[json.loads(f.read_text()) for f in (layout,gripsfile)]
    assert current['status']=='BODY20_ROUTES_AND_RECEIVER_GRIPS_EXACT_CHANGED_WIRE_CLEAR_ROOT_ARMS_NATIVE_OPEN'
    assert not current['contacts'] and not current['errors']
    for receipt in (current,grips):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    original=C.prepare_context;context=[]
    def adapted(plan):
        result=original(plan)
        targets,old,pins,family,axes,own,bare,files,subsets=result
        old['body/W024']=(P.wire(current['routes']['W024']['parts']),1)
        for name,q in grips['grips'].items():
            actual=T.build(q['land'],q['normal'],q['offset']);goal=actual['arrival_world_mm']
            actual['seed']=P.box([v-2 for v in goal]+[v+2 for v in goal])
            for kind in ('body','band','seed'):targets['Receiver_'+name+'/'+kind]=actual[kind]
        files.extend([layout,gripsfile,Path(__file__),Path(T.__file__)])
        context.append(result);return result
    C.prepare_context=adapted
    try:C.run('body-axial-layout-chosen.json','body-axial-source-receiver-space.json')
    finally:C.prepare_context=original
    source_gate=P.OUT/'body-axial-source-receiver-space.json';received=json.loads(source_gate.read_text())
    assert received['status']=='NEAR_AXIS_SOURCE_SAMPLED_CLEAR_ARMS_BREAKOUTS_NATIVE_OPEN' and not received['contacts'] and not received['errors'],received['status']
    assert len(received['completed'])==44,'Incomplete source/port gate'
    targets,old,pins,family,axes,own,bare,files,subsets=context[0]
    planfile=P.OUT/'body-axial-layout-chosen.json';plan=json.loads(planfile.read_text());source_curves={};ports={}
    for row in plan['hips']:
        for pose in row['poses']:
            h=pose['angle']
            if h in C.ANGLES:source_curves[row['loom']+'/'+str(h)]=(P.wire(pose['parts']+C.B.moved_parts(row['source_parts'],row['source'],h,0,axes)),row['loom'])
        for moving in (False,True):
            _,port=C.make_port(row,moving)
            for kind in ('body','band'):
                for h in C.ANGLES if moving else (0,):
                    s=C.moved(port[kind],C.transform(axes,row['cad_code'],h,0,'Hip')) if moving else port[kind]
                    ports[row['loom']+'/'+str(moving)+'/'+kind+'/'+str(h)]=s
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'axial-source-receiver-fan-pairs.json',bounds.near)
    contacts=[];errors=[];checks=0;completed=[];previous=[]
    def check(a,s,b,t,rs=1.25,rt=0):
        nonlocal checks
        if not bounds.near(s,t,rs+rt+.0001):return
        checks+=1
        try:
            gap,vol=cache.check(s,t,rs,rt)
            if vol>1e-5 or gap<rs+rt-1e-6:contacts.append(dict(a=a,b=b,gap_mm=gap,required_mm=rs+rt))
        except (AssertionError,ValueError) as e:errors.append(dict(a=a,b=b,error=str(e)))
    def save():
        receipt=dict(status='REJECTED_AXIAL_SOURCE_RECEIVER_BREAKOUTS' if contacts or errors else
            'FOUR_SOURCES_TWELVE_BREAKOUTS_TWENTY_RECEIVER_GRIPS_SAMPLED_CLEAR_ROOT_ARMS_OPEN' if len(completed)==12 else 'PARTIAL_AXIAL_SOURCE_RECEIVER_BREAKOUT_GATE',
            contacts=contacts,errors=errors,changed_fan_pairs=checks,completed_fans=completed,
            inherited_source_port_pairs=received['pairs'],body_routes=20,receiver_grips=20,
            source_sha256={**received['source_sha256'],source_gate.relative_to(P.ROOT).as_posix():P.SHA(source_gate)},
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            scope='FourcompleteHip1sourcefamilies/8lands/bands/12corebreakouts againstfullretainedmaterial/current20bodycurves/current20receivergripsandseeds. ThreecoupledHipmaterialsamples;31mathposes.8sourcearms/36receiverarms/native/remaining16bodycores/stock stillOPEN.')
        out=P.OUT/'axial-source-receiver-integration.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(receipt,indent=2)+'\n');tmp.replace(out);cache.save()
    for row in plan['hips']:
        for core in row['source_fans']:
            name=row['loom']+'/'+core['core'];wire=P.wire(core['parts']);after=P.wire(core['after_5mm'])
            for target,s in targets.items():check(name,wire,target,s)
            for target,(w,r) in old.items():check(name,wire,target,w,rt=r)
            for target,s in ports.items():check(name,wire,target,s)
            for target,(w,loom) in source_curves.items():check(name,after if loom==row['loom'] else wire,target,w,rt=3)
            for target,w in previous:check(name,wire,target,w,rt=1)
            previous.append((name,wire));completed.append(name);save()
            print('integrated source fan',name,'pairs',checks,'contacts',len(contacts),'errors',len(errors),flush=True)
    save()


if __name__=='__main__':run()

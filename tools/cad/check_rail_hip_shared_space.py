"""One complete four-carrier/flex/three-core-fan shared material candidate.

Old accepted interfaces stay frozen. Whole-carrier replacement includes arms;
own jacket exemptions are local arc-length trims, never a whole owner skip.
Only sampled motion and local breakout space are qualified here, not W5.
"""
import itertools
import json
import math
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_low_hip_shared_space import AtomicMaterial,ownership,same_leg_pose
from whole_current_body_material import load
from immutable_bounds import ImmutableBounds
from plan_continuous_joint_family import self_screen
from plan_current_moving_looms import add,mul,dot,exact_turn_to
from plan_current_mta_interfaces import line,curve
import current_body_fanout_material as M

P=M.P
ANGLES=(-15,0,15)


def fan(row,direction):
    root=row['fixed_anchor_world_mm'];side=1 if root[1]>0 else -1
    offsets={core:[1.5*math.cos(math.radians(angle+side*30)),1.5*math.sin(math.radians(angle+side*30)),0]
             for core,angle in (('D',0),('V',120),('G',240))}
    minimum=min(dot(o,direction) for o in offsets.values());result=[]
    for core,offset in offsets.items():
        entry=5+minimum-dot(offset,direction);start=add(root,offset);bend=add(start,[0,0,entry])
        arc=exact_turn_to(bend,[0,0,1],direction,10)
        # Exclude exactly first5mm ONLY against this same factory jacket.
        theta=max(0,5-entry)/10;angle=math.pi/2
        def at(t):return add(add(bend,[0,0,10*math.sin(t)]),mul(direction,10*(1-math.cos(t))))
        trimmed=curve(at(theta),arc['end'],at((theta+angle)/2),10,angle-theta)
        result.append(dict(core=core,entry_mm=entry,parts=[line(start,bend),arc],after_5mm=[trimmed]))
    return result


def run():
    tick=time.monotonic();files=[P.OUT/n for n in ('body-rail-hip-retention-plan.json','body-low-hip-rail-exit-plan.json')]
    retention,plan=[json.loads(f.read_text()) for f in files]
    for data in (retention,plan):
        for n,h in data['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    archive=P.ROOT/retention['archive'];assert P.SHA(archive)==retention['archive_sha256'];objects={}
    with zipfile.ZipFile(archive) as z:
        for row in json.loads(z.read('index.json')):
            s=Part.Shape();s.importBrepFromString(z.read(row['file']).decode());assert s.isValid() and len(s.Solids)==1
            objects[row['name']]=s
    targets,old,pins=load();familyfile=P.OUT/'leg-source-near-member-plan.json';family=json.loads(familyfile.read_text())
    rootsfile=P.OUT/'remaining-loom-roots-plan.json';roots=json.loads(rootsfile.read_text())
    axesfile=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    codes={r['loom']:r['cad_code'] for r in family['hips']}
    for row in retention['changed']:
        assert targets.pop(row['owner']+'/0/0') is not None
        assert targets.pop(row['band']+'/0/0') is not None
    owners,bare=ownership(targets,family,roots)
    for row in plan['hips']:
        loom=row['loom'];old={n:q for n,q in old.items() if not n.startswith('leg/'+loom+'/')}
        source=next(r for r in family['routes'] if r['loom']==loom)
        for h in ANGLES:old[f'factory-source/{loom}/{h}']=(P.wire(M.B.moved_parts(source['source_parts'],source['source'],h,0,axes)),3)
    bf=P.OUT/'body-fanout-layout.json';body=json.loads(bf.read_text())
    for name,r in body['routes'].items():old['new-body/'+name]=(P.wire(r['parts']),1)
    curves={};short={};info={};ground=[]
    floor=min(s.BoundBox.ZMin for n,s in targets.items() if any(stage=='Ankle' and n==key+'/0/0/0' for key,(code,stage) in bare.items()))
    for row in plan['hips']:
        for pose in row['poses']:
            assert self_screen(pose['parts']) is None,(row['loom'],pose['angle'])
            w=P.wire(pose['parts']);ground.append(dict(loom=row['loom'],angle=pose['angle'],gap_mm=w.BoundBox.ZMin-3-floor))
            if pose['angle'] not in ANGLES:continue
            name=row['loom']+'/'+str(pose['angle']);curves[name]=w;short[name]=P.wire(pose['parts'][:-1]);info[name]=(row,pose)
    bounds=ImmutableBounds();cache=AtomicMaterial(P.OUT/'rail-hip-shared-pairs.json',bounds.near)
    contacts=[];errors=[];pairs=0;completed=[];fan_results=[];last_save=time.monotonic()
    def check(a,s,b,t,rs=0,rt=0,bucket=None):
        nonlocal pairs,last_save
        if not bounds.near(s,t,rs+rt+.0001):return
        pairs+=1
        try:
            gap,volume=cache.check(s,t,rs,rt)
            if volume>1e-5 or ((rs or rt) and gap<rs+rt-1e-6):
                (contacts if bucket is None else bucket).append(dict(a=a,b=b,gap_mm=gap,required_mm=rs+rt,volume_mm3=volume))
        except (AssertionError,ValueError) as e:errors.append(dict(a=a,b=b,error=str(e)))
        if time.monotonic()-last_save>20:
            save();last_save=time.monotonic();print('rail Hip gate',a,'pairs',pairs,'contacts',len(contacts),'errors',len(errors),flush=True)
    def save():
        result=dict(status='REJECTED_RAIL_HIP_SHARED_SPACE' if contacts or errors or any(r['gap_mm']<0 for r in ground) else 'PARTIAL_RAIL_HIP_GATE',
            contacts=contacts,errors=errors,pairs=pairs,completed=completed,ground=ground,fans=fan_results,
            material_instances=len(targets),complete_changed_carriers=4,additional_T18I=0,
            scope='Complete four fixed carriers/bands, three sampled flex poses each,124nominal geometry poses, all retained material/wires,12wholecore breakouts. Not complete body paths, native mounts, assembly or stock.',
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[archive,familyfile,rootsfile,axesfile,bf,Path(__file__),Path(__file__).with_name('check_low_hip_shared_space.py')]}},
            computed_pairs=cache.computed,reused_pairs=cache.reused,selected=False,W5_complete=False,physical_pass=False,continuous_sweep_verified=False,
            worker_seconds=round(time.monotonic()-tick,3))
        dest=P.OUT/'body-rail-hip-shared-space.json';tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(dest);cache.save();return result
    names=list(objects);ownbands={r['band']:r['land']['loom'] for r in retention['changed']}
    for i,n in enumerate(names):
        for other,s in targets.items():check(n,objects[n],other,s)
        for other,(w,r) in old.items():check(n,objects[n],other,w,0,r+.25)
        for other in names[:i]:check(n,objects[n],other,objects[other])
        for other,w in curves.items():check(n,objects[n],other,w,0,3 if ownbands.get(n)==info[other][0]['loom'] else 3.25)
        completed.append(n);save();print('rail carrier received',n,'contacts',len(contacts),flush=True)
    names=list(curves)
    for i,n in enumerate(names):
        row,pose=info[n];code=row['cad_code'];h=pose['angle'];loom=row['loom']
        for other,s in targets.items():
            if not same_leg_pose(owners.get(other),code,h):continue
            band=other.startswith((loom+'IndependentBand/','Band_'+loom+'/Hip/Moving/'))
            check(n,curves[n],other,s,3 if band else 3.25)
        for other,(w,r) in old.items():
            own=False
            if other.startswith(('leg/','factory-source/')):
                _,otherloom,hh,*_=other.split('/')
                if codes[otherloom]==code and int(hh)!=h:continue
                own=otherloom==loom
            check(n,short[n] if own else curves[n],other,w,3.25,r)
        for other in names[:i]:
            if info[other][0]['loom']!=loom:check(n,curves[n],other,curves[other],3.25,3)
        completed.append(n);save();print('rail flex received',n,'contacts',len(contacts),flush=True)
    # All four directional choices include all three cores, not independent fans.
    domains={}
    for row in plan['hips']:
        loom=row['loom'];domains[loom]=[]
        for direction in ([1,0,0],[-1,0,0],[0,1,0],[0,-1,0]):
            rows=fan(row,direction);blocked=[];wires=[]
            for core in rows:
                name=loom+'/'+core['core'];w=P.wire(core['parts']);trim=P.wire(core['after_5mm']);wires.append(w)
                for other,s in {**targets,**objects}.items():check(name,w,other,s,1.25,0,blocked)
                for other,(q,r) in old.items():check(name,w,other,q,1.25,r,blocked)
                for other,q in curves.items():check(name,trim if info[other][0]['loom']==loom else w,other,q,1.25,3,blocked)
            for i,w in enumerate(wires):
                for j in range(i):check(loom+'/fan'+str(i),w,loom+'/fan'+str(j),wires[j],1.25,1,blocked)
            receipt=dict(loom=loom,direction=direction,cores=rows,contacts=blocked)
            fan_results.append(receipt)
            if not blocked:domains[loom].append(receipt)
        completed.append(loom+'/whole-three-core-fans');save()
    viable=[]
    for choice in itertools.product(*domains.values()):
        blocked=[]
        for i,a in enumerate(choice):
            for b in choice[:i]:
                for x in a['cores']:
                    for y in b['cores']:check(a['loom']+'/'+x['core'],P.wire(x['parts']),b['loom']+'/'+y['core'],P.wire(y['parts']),1.25,1,blocked)
        if not blocked:viable.append([dict(loom=r['loom'],direction=r['direction']) for r in choice]);break
    result=save();result['joint_fan_choices']=viable
    result['status']='RAIL_HIP_SAMPLED_MATERIAL_AND_LOCAL_FANS_CLEAR_NATIVE_OPEN' if not contacts and not errors and viable and all(r['gap_mm']>=0 for r in ground) else 'REJECTED_RAIL_HIP_SHARED_SPACE'
    (P.OUT/'body-rail-hip-shared-space.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],contacts=len(contacts),fan_domains={k:len(v) for k,v in domains.items()},pairs=pairs,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()

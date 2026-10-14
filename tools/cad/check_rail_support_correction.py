"""Changed material of five complete carriers, synchronized full scene gate.

Unchanged material is inherited, not repeatedly rechecked. Every new wire sees
complete replacement carriers and all retained bodies. Physical ownership and
Hip/Knee timing are distinct from logical loom names.
"""
import itertools
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_rail_hip_shared_space import fan
from check_low_hip_shared_space import AtomicMaterial,ownership
from whole_current_body_material import load
from immutable_bounds import ImmutableBounds
from diagnose_remaining_support_endpoints import transform,moved
import current_body_fanout_material as M
P=M.P
ANGLES=(-15,0,15)


def coexist(a,b):
    """Static and independent legs coexist; same leg shares upstream joints."""
    if a is None or b is None or a[0]!=b[0]:return True
    if a[2]!=b[2]:return False
    return a[1]=='Hip' or b[1]=='Hip' or a[3]==b[3]


def run():
    tick=time.monotonic();mf=P.OUT/'body-rail-support-correction-material.json';pf=P.OUT/'body-low-hip-rail-exit-plan.json'
    material,plan=[json.loads(f.read_text()) for f in (mf,pf)]
    for data in (material,plan):
        for n,h in data['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    archive=P.ROOT/material['archive'];assert P.SHA(archive)==material['archive_sha256'];objects={}
    with zipfile.ZipFile(archive) as z:
        for row in json.loads(z.read('index.json')):
            s=Part.Shape();s.importBrepFromString(z.read(row['file']).decode());assert s.isValid() and len(s.Solids)==1
            objects[row['name']]=s
    targets,old,pins=load();ff=P.OUT/'leg-source-near-member-plan.json';family=json.loads(ff.read_text())
    rf=P.OUT/'remaining-loom-roots-plan.json';roots=json.loads(rf.read_text())
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    _,bare=ownership(targets,family,roots);keys=sorted(bare,key=len,reverse=True)
    def owned(name):
        for key in keys:
            if name.startswith(key+'/'):
                code,stage=bare[key];h,k,*_=map(int,name[len(key)+1:].split('/'))
                return None if code is None else (code,stage,h,k)
        return None
    info={n:owned(n) for n in targets};changes={};change_info={};change_bands={}
    def replace(name,shape,band_loom=None):
        prefix=name+'/'
        instances=[n for n in targets if n.startswith(prefix)]
        assert instances,name
        # One exact positive difference at rest; transform it with its owner.
        previous=targets[prefix+'0/0'];addition=shape if band_loom else shape.copy().cut(previous.copy()).removeSplitter()
        assert addition.isNull() or addition.isValid(),name
        for n in instances:
            scope=info[n]
            t=transform(axes,scope[0],scope[2],scope[3],scope[1]) if scope else A.Placement()
            targets[n]=moved(shape,t)
            if not addition.isNull() and addition.Volume>1e-8:
                changes[n]=moved(addition,t);change_info[n]=scope
                if band_loom:change_bands[n]=band_loom
    for group in material['groups']:replace(group['id'],objects[group['id']])
    for lid in material['changed_band_ids']:replace('Band_'+lid,objects['Band_'+lid],lid.split('/')[0])
    codes={r['loom']:r['cad_code'] for r in family['hips']}
    for row in plan['hips']:
        loom=row['loom'];old={n:q for n,q in old.items() if not n.startswith('leg/'+loom+'/')}
        source=next(r for r in family['routes'] if r['loom']==loom)
        for h in ANGLES:old[f'factory-source/{loom}/{h}']=(P.wire(M.B.moved_parts(source['source_parts'],source['source'],h,0,axes)),3)
    bf=P.OUT/'body-fanout-layout.json';body=json.loads(bf.read_text())
    for name,row in body['routes'].items():old['new-body/'+name]=(P.wire(row['parts']),1)
    def wire_scope(name):
        if name.startswith('leg/'):
            _,loom,h,k=name.split('/');return (codes[loom],'Knee',int(h),int(k))
        if name.startswith('factory-source/'):
            _,loom,h=name.split('/');return (codes[loom],'Hip',int(h),0)
        return None
    curves={};short={};curve_info={};ground=[]
    floor=min(s.BoundBox.ZMin for n,s in targets.items() if any(stage=='Ankle' and n==key+'/0/0/0' for key,(code,stage) in bare.items()))
    for row in plan['hips']:
        for pose in row['poses']:
            w=P.wire(pose['parts']);ground.append(w.BoundBox.ZMin-3-floor)
            if pose['angle'] not in ANGLES:continue
            name=row['loom']+'/'+str(pose['angle']);curves[name]=w;short[name]=P.wire(pose['parts'][:-1]);curve_info[name]=(row,pose)
    bounds=ImmutableBounds();cache=AtomicMaterial(P.OUT/'rail-support-shared-pairs.json',bounds.near)
    contacts=[];errors=[];pairs=0;completed=[];fan_results=[];last_save=time.monotonic()
    def save():
        result=dict(status='REJECTED_RAIL_SUPPORT_CORRECTION' if contacts or errors else 'PARTIAL_RAIL_SUPPORT_CORRECTION',
            pairs=pairs,contacts=contacts,errors=errors,completed=completed,fans=fan_results,minimum_nominal_ground_gap_mm=min(ground),
            full_material_instances=len(targets),changed_material_instances=len(changes),complete_changed_supports=5,
            computed_pairs=cache.computed,reused_pairs=cache.reused,worker_seconds=round(time.monotonic()-tick,3),
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (mf,pf,archive,ff,rf,af,bf,Path(__file__),Path(__file__).with_name('check_rail_hip_shared_space.py'))}},
            scope='Exact positive new carrier material and sixchanged bands vs complete retained/replacement parts,alloldwires andfournewflexes. Newflexes see complete parts,12localfans allocatedjointly. Coupled Hip/Knee poses; otherlegs/head independent. Whole bodyroutes/grips/stock/assembly not accepted.',
            selected=False,W5_complete=False,physical_pass=False,continuous_sweep_verified=False)
        dest=P.OUT/'body-rail-support-shared-space.json';tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(dest);cache.save();return result
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
            save();last_save=time.monotonic();print('rail support gate',a,'pairs',pairs,'contacts',len(contacts),flush=True)
    for name,s in changes.items():
        scope=change_info[name]
        for other,q in targets.items():
            if other==name or not coexist(scope,info[other]):continue
            check(name,s,other,q)
        for other,(w,r) in old.items():
            if not coexist(scope,wire_scope(other)):continue
            sameband=other.startswith('leg/'+change_bands.get(name,'NONMATE')+'/')
            check(name,s,other,w,0,r if sameband else r+.25)
        for other,w in curves.items():
            row,pose=curve_info[other];ws=(row['cad_code'],'Hip',pose['angle'],0)
            if coexist(scope,ws):check(name,s,other,w,0,3 if change_bands.get(name)==row['loom'] else 3.25)
        completed.append(name);save();print('rail changed material',name,'contacts',len(contacts),flush=True)
    names=list(curves)
    for i,name in enumerate(names):
        row,pose=curve_info[name];loom=row['loom'];scope=(row['cad_code'],'Hip',pose['angle'],0)
        for other,s in targets.items():
            if not coexist(scope,info[other]):continue
            band=other.startswith((loom+'IndependentBand/','Band_'+loom+'/Hip/Moving/','Band_'+loom+'/Hip/Fixed/'))
            check(name,curves[name],other,s,3 if band else 3.25)
        for other,(w,r) in old.items():
            if not coexist(scope,wire_scope(other)):continue
            own=other.startswith('factory-source/'+loom+'/')
            check(name,short[name] if own else curves[name],other,w,3.25,r)
        for other in names[:i]:
            if curve_info[other][0]['loom']!=loom:check(name,curves[name],other,curves[other],3.25,3)
        completed.append(name);save()
    domains={}
    for row in plan['hips']:
        loom=row['loom'];domains[loom]=[]
        for direction in ([1,0,0],[-1,0,0],[0,1,0],[0,-1,0]):
            cores=fan(row,direction);blocked=[];ws=[]
            for core in cores:
                name=loom+'/'+core['core'];w=P.wire(core['parts']);trim=P.wire(core['after_5mm']);ws.append(w)
                for other,s in targets.items():check(name,w,other,s,1.25,0,blocked)
                for other,(q,r) in old.items():check(name,w,other,q,1.25,r,blocked)
                for other,q in curves.items():check(name,trim if curve_info[other][0]['loom']==loom else w,other,q,1.25,3,blocked)
            for i,w in enumerate(ws):
                for q in ws[:i]:check(loom+'/core',w,loom+'/core',q,1.25,1,blocked)
            receipt=dict(loom=loom,direction=direction,cores=cores,contacts=blocked);fan_results.append(receipt)
            if not blocked:domains[loom].append(receipt)
        completed.append(loom+'/fans');save()
    viable=[]
    for choice in itertools.product(*domains.values()):
        blocked=[]
        for i,a in enumerate(choice):
            for b in choice[:i]:
                for x in a['cores']:
                    for y in b['cores']:check(a['loom'],P.wire(x['parts']),b['loom'],P.wire(y['parts']),1.25,1,blocked)
        if not blocked:viable.append([dict(loom=r['loom'],direction=r['direction']) for r in choice]);break
    result=save();result['joint_fan_choices']=viable
    result['status']='FIVE_CORRECTED_SUPPORTS_FLEX_AND_LOCAL_FANS_SAMPLED_CLEAR_NATIVE_OPEN' if not contacts and not errors and viable and min(ground)>=0 else 'REJECTED_RAIL_SUPPORT_CORRECTION'
    (P.OUT/'body-rail-support-shared-space.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],contacts=len(contacts),pairs=pairs,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()

"""One changed-interface gate:8ports,4whole Hip1 flexes,retained frame/wires.

The four superseded carrier PORT/ARM recipes alone are replaced by proven
retained subsets. Hip timing is coupled within a leg; other legs are independent.
No roots/arms/native or wholeW5 are accepted by this local gate.
"""
import itertools
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import current_body_fanout_material as M
from whole_current_body_material import load as load_whole_material
from immutable_bounds import ImmutableBounds
from material_pair_receipts import MaterialPairReceipts

P=M.P
ANGLES=(-15,0,15)


class AtomicMaterial(MaterialPairReceipts):
    def save(self):
        tmp=self.path.with_suffix('.tmp')
        tmp.write_text(json.dumps(dict(checker_sha256=self.revision,records=self.records),separators=(',',':'))+'\n')
        tmp.replace(self.path)


def same_leg_pose(owner,leg,angle):
    return owner is None or owner[0]!=leg or owner[1]==angle


def load_candidate():
    pf=P.OUT/'body-low-hip-retention-plan.json';mf=P.OUT/'body-low-hip-exit-plan.json'
    ports,mathplan=[json.loads(f.read_text()) for f in (pf,mf)]
    for receipt in (ports,mathplan):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    archive=P.ROOT/ports['archive'];assert P.SHA(archive)==ports['archive_sha256']
    shapes={}
    with zipfile.ZipFile(archive) as z:
        for r in json.loads(z.read('index.json')):
            s=Part.Shape();s.importBrepFromString(z.read(r['file']).decode())
            assert s.isValid() and len(s.Solids)==1,r['name']
            shapes[r['name']]=s
    return ports,mathplan,shapes,(pf,mf,archive)


def ownership(targets,family,roots):
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    bare={'P0_'+r['name']:tuple(r['stage'].split('_')[1:]) for r in members if r['stage'].startswith('Motion_')}
    for row in family['hips']:
        code=row['cad_code'];leg=row['physical_leg']
        bare[row['loom']+'IndependentBand']=(code,'Hip')
        bare[leg+'SourceCaseBond']=(code,'Hip')
        bare[leg+'SourceCarrier']=(code,'Hip')
    for group in roots['groups']:
        code,stage=tuple(group['owner_stage'].split('_')[1:]) if group['owner_stage']!='Body' else (None,'Body')
        if code:
            bare[group['id']]=(code,stage)
            bare[group['id']+'Bond']=(code,stage)
            for land in group['lands']:bare['Band_'+land['id']]=(code,stage)
    result={};names=sorted(bare,key=len,reverse=True)
    for name in targets:
        for key in names:
            if name.startswith(key+'/'):
                h=int(name[len(key)+1:].split('/')[0]);result[name]=(bare[key][0],h);break
    return result,bare


def run():
    tick=time.monotonic();ports,mathplan,objects,files=load_candidate()
    targets,old,pins=load_whole_material();familyfile=P.OUT/'leg-source-near-member-plan.json'
    family=json.loads(familyfile.read_text());rootsfile=P.OUT/'remaining-loom-roots-plan.json'
    roots=json.loads(rootsfile.read_text());axesfile=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes=json.loads(axesfile.read_text())['axes']
    loom_codes={r['loom']:r['cad_code'] for r in family['hips']}
    for row in ports['retained']:targets[row['owner']+'/0/0']=objects['Retained_'+row['owner']]
    for name in ports['removed_old_bands']:assert targets.pop('Band_'+name+'/0/0') is not None
    own,bare=ownership(targets,family,roots)
    for row in mathplan['hips']:
        loom=row['loom']
        old={n:q for n,q in old.items() if not n.startswith('leg/'+loom+'/')}
        source=next(r for r in family['routes'] if r['loom']==loom)
        for h in ANGLES:
            old[f'factory-source/{loom}/{h}']=(P.wire(M.B.moved_parts(source['source_parts'],source['source'],h,0,axes)),3)
    bf=P.OUT/'body-fanout-layout.json';body=json.loads(bf.read_text())
    for name,r in body['routes'].items():old['new-body/'+name]=(P.wire(r['parts']),1)
    new={name:objects[name] for row in ports['ports'] for name in (row['body'],row['band'])}
    band_loom={row['band']:row['land']['loom'] for row in ports['ports']}
    bounds=ImmutableBounds();cache=AtomicMaterial(P.OUT/'low-hip-shared-pairs.json',bounds.near)
    contacts=[];errors=[];pairs=0;completed=[];last_save=time.monotonic();ground=[]
    curves={};short={};curve_info={}
    for row in mathplan['hips']:
        for pose in row['poses']:
            if pose['angle'] not in ANGLES:continue
            name=row['loom']+'/'+str(pose['angle']);curves[name]=P.wire(pose['parts'])
            short[name]=P.wire(pose['parts'][:-1]);curve_info[name]=(row,pose)
    ankle_nominal=[targets[n].BoundBox.ZMin for n in targets if any(
        stage=='Ankle' and n==key+'/0/0/0' for key,(code,stage) in bare.items())]
    assert ankle_nominal,'No actual nominal ankle/foot geometry for ground datum'
    floor=min(ankle_nominal)
    for n,w in curves.items():ground.append(dict(wire=n,lowest_jacket_Z_mm=w.BoundBox.ZMin-3,nominal_foot_floor_Z_mm=floor,
        nominal_gap_mm=w.BoundBox.ZMin-3-floor))
    def save():
        result=dict(status='REJECTED_LOW_HIP_SHARED_SPACE' if contacts or errors or any(r['nominal_gap_mm']<0 for r in ground)
            else 'LOW_HIP_CURVES_AND_EIGHT_PORTS_SAMPLED_CLEAR_ARMS_NATIVE_OPEN',
            pairs=pairs,contacts=contacts,errors=errors,completed=completed,ground=ground,
            material_instances=len(targets),fixed_port_shapes=len(new),changed_flex_poses=len(curves),hip_angles=list(ANGLES),
            scope='Exact new8compactprofiles/4Hip1three-pose flexes vs FULL UNCLIPPED retained current bodies/otherwires/11qualifiedbodycurves/eachother. Same-leg Hip synchronized; otherleg/head sampled independently.8new rootedarms and completeW5 excluded and OPEN.',
            mating_scope='Only nominal jacket-to-own-band contact uses R3 instead of3.25; own unchanged factory join shares moving endpoint, so last9mm moving land omitted only for that same-wire pair. No wholeframe/support omitted.',
            computed_pairs=cache.computed,reused_pairs=cache.reused,selected=False,W5_complete=False,physical_pass=False,continuous_sweep_verified=False,
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (*files,familyfile,rootsfile,axesfile,bf,Path(__file__),Path(__file__).with_name('material_pair_receipts.py'),Path(__file__).with_name('component_pair_receipts.py'))}},
            worker_seconds=round(time.monotonic()-tick,3))
        dest=P.OUT/'body-low-hip-shared-space.json';tmp=dest.with_suffix('.tmp')
        tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(dest);cache.save();return result
    def check(a,s,b,t,rs=0,rt=0):
        nonlocal pairs,last_save
        if not bounds.near(s,t,rs+rt+.0001):return
        pairs+=1
        try:
            gap,volume=cache.check(s,t,rs,rt)
            if volume>1e-5 or ((rs or rt) and gap<rs+rt-1e-6):
                contacts.append(dict(a=a,b=b,gap_mm=gap,required_mm=rs+rt,volume_mm3=volume))
        except (AssertionError,ValueError) as e:errors.append(dict(a=a,b=b,error=str(e)))
        if time.monotonic()-last_save>20:
            save();last_save=time.monotonic()
            print('lowHip shared',a,'pairs',pairs,'contacts',len(contacts),'errors',len(errors),flush=True)
    all_new=list(new)
    for i,n in enumerate(all_new):
        for name,s in targets.items():check(n,new[n],name,s)
        for name,(w,radius) in old.items():check(n,new[n],name,w,0,radius+.25)
        for other in all_new[:i]:check(n,new[n],other,new[other])
        for name,w in curves.items():
            row,pose=curve_info[name];radius=3 if band_loom.get(n)==row['loom'] else 3.25
            check(n,new[n],name,w,0,radius)
        completed.append(n);save()
        print('received lowHip profile',n,'pairs',pairs,'contacts',len(contacts),flush=True)
    names=list(curves)
    for i,n in enumerate(names):
        row,pose=curve_info[n];code=row['cad_code'];h=pose['angle'];loom=row['loom']
        for name,s in targets.items():
            if not same_leg_pose(own.get(name),code,h):continue
            band=name.startswith((loom+'IndependentBand/', 'Band_'+loom+'/Hip/Moving/'))
            check(n,curves[n],name,s,3 if band else 3.25)
        for name,(w,radius) in old.items():
            if name.startswith('leg/'):
                _,other_loom,other_h,*_=name.split('/')
                if loom_codes[other_loom]==code and int(other_h)!=h:continue
            if name.startswith('factory-source/'):
                _,other_loom,other_h=name.split('/')
                if loom_codes[other_loom]==code and int(other_h)!=h:continue
                same=other_loom==loom
            else:same=False
            check(n,short[n] if same else curves[n],name,w,3.25,radius)
        for other in names[:i]:
            if curve_info[other][0]['loom']!=loom:check(n,curves[n],other,curves[other],3.25,3)
        parts=pose['parts'];edges=[P.wire([p]) for p in parts]
        for a in range(len(edges)):
            for b in range(a+2,len(edges)):check(n+'/part'+str(a),edges[a],n+'/part'+str(b),edges[b],3.25,3)
        completed.append(n);save()
        print('received lowHip flex',n,'pairs',pairs,'contacts',len(contacts),'errors',len(errors),flush=True)
    result=save();print(json.dumps({k:result[k] for k in ('status','pairs','worker_seconds','computed_pairs','reused_pairs')}),flush=True)


if __name__=='__main__':run()

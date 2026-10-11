"""Check three complete source guides; rejected S0-IN extension not waived."""
import itertools,json,time,zipfile
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA

def run():
    tick=time.monotonic();f=OUT/'positive-source-plan.json';p=json.loads(f.read_text())
    names=('W075','W076_FACTORY','W066')
    assert not [v for v in p['rejected'] if v['b'] in names],p['rejected']
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    dg=OUT/'data-bridges-checks.json';data=json.loads(dg.read_text())
    assert data['status']=='THREE_DATA_BRIDGES_SAMPLED_CLEAR_NATIVE_OPEN'
    assert not data['contacts'] and not data['errors']
    for n,h in data['source_sha256'].items():assert SHA(ROOT/n)==h,n
    from current_full_harness_context import context,W,Part
    from current_body_harness_context import clipped
    reader,pins,targets,old=context();df=OUT/'data-bridges-plan.json'
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in json.loads(df.read_text())['routes'].items()})
    pins.update((f,df,dg,Path(__file__)))
    new={n:(W.makewire(p['routes'][n]['parts']),p['routes'][n]['radius_mm']) for n in names}
    for n in new:old.pop(n,None)
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],checked_guides=list(names),native_parts_changed=0,
      cached_leg_stage_poses=0,selected=False,W5_complete=False,physical_pass=False,
      unqualified_extension='W076_EXTENSION cheap crossing of XB32 and unknown S0 terminal bay, explicitly outside this check',
      approved_motion_limits=False,continuous_sweep_verified=False)
    def pair(n,c,rr,m,t,rad=0,pose=None):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,m);r['pairs']+=1;d,points,_=c.distToShape(t)
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,
          pose=pose,witness_mm=[list(v) for v in points[0]] if points else None))
    def save(status):
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={
          **reader.hashes,**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins}})
        (OUT/'positive-source-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    for n,(c,rr) in new.items():
        endpoints={'W075':('XT60_CP2','F0_CP2'),'W076_FACTORY':('F0_CP2','PostF0Splice_CP2'),'W066':('S0_ring_OUT','P_SYS_new')}[n]
        for m,t in targets.items():
            if not t.Solids:continue
            cc=c
            for first,role in ((True,endpoints[0]),(False,endpoints[1])):
                if m==role:cc=clipped(cc,first,3)
            pair(n,cc,rr,m,t)
        for m,(t,rad) in old.items():pair(n,c,rr,m,t,rad)
        for m,(t,rad) in new.items():
            if m>n:pair(n,c,rr,m,t,rad)
        print('Positive source',n,'contacts',len(r['contacts']),flush=True)
    if r['contacts']:save('REJECTED_THREE_POSITIVE_SOURCE_MATERIAL');return
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';archive=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text());pins.update((af,archive))
    with zipfile.ZipFile(archive) as z:geometry=json.loads(z.read('geometry.json'))
    for code in ('FL','FR','RL','RR'):
        ax={a['stage']:a for a in axes['axes'] if a['code']==code}
        for index,stage in enumerate(('Hip','Knee','Ankle')):
            components=['P0_'+q['name'] for q in geometry['components'] if q['stage']==f'Motion_{code}_{stage}']
            for angles in itertools.product((-15,0,15),repeat=index+1):
                transform=W.A.Placement();r['cached_leg_stage_poses']+=1
                for st,angle in zip(('Hip','Knee','Ankle'),angles):
                    a=ax[st];pivot=W.A.Vector(*a['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*a['axis']),angle)
                    transform=transform*W.A.Placement(pivot-rot.multVec(pivot),rot)
                for name in components:
                    t=targets[name].copy();t.Placement=transform*t.Placement
                    for n,(c,rr) in new.items():pair(n,c,rr,name,t,pose=dict(leg=code,stage=stage,angles=angles))
            print('Positive source stage',code,stage,'contacts',len(r['contacts']),flush=True)
    for yaw in (-15,0,15):
        for pitch in (-10,0,5):
            for m,t in W.F.H.head(reader,yaw,pitch).items():
                if m=='Foundation' or not t.Solids:continue
                for n,(c,rr) in new.items():pair(n,c,rr,'head/'+m,t,pose=dict(yaw=yaw,pitch=pitch))
    save('THREE_POSITIVE_SOURCE_GUIDES_SAMPLED_CLEAR_IN_EXTENSION_OPEN' if not r['contacts'] else 'REJECTED_THREE_POSITIVE_SOURCE_MOTION')

if __name__=='__main__':run()

"""Actual three-bridge gate, reuse unchanged ground/front/source evidence."""
import itertools,json,time,zipfile
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA

def run():
    tick=time.monotonic();f=OUT/'data-bridges-plan.json';p=json.loads(f.read_text())
    assert not p['rejected'],p['rejected']
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    from current_full_harness_context import context,W,Part
    from current_body_harness_context import clipped
    reader,pins,targets,old=context();pins.update((f,Path(__file__),ROOT/'tools/cad/current_full_harness_context.py'))
    new={n:(W.makewire(v['parts']),v['radius_mm']) for n,v in p['routes'].items()}
    for n in new:old.pop(n,None)
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],native_parts_changed=0,
      cached_leg_stage_poses=0,angle_grid_degrees=[-15,0,15],approved_motion_limits=False,
      continuous_sweep_verified=False,selected=False,W5_complete=False,physical_pass=False)
    def pair(n,c,rr,m,t,rad=0,pose=None):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,m);r['pairs']+=1;d,points,_=c.distToShape(t)
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,pose=pose,
          witness_mm=[list(v) for v in points[0]] if points else None))
    def save(status):
        r['contact_target_bounds_mm']={m:[getattr(targets[m].BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
          for m in {v['b'] for v in r['contacts']} if m in targets}
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={
          **reader.hashes,**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins}})
        (OUT/'data-bridges-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    for n,(c,rr) in new.items():
        for m,t in targets.items():
            if not t.Solids:continue
            cc=c
            for first,role in ((True,p['routes'][n]['endpoints'][0]),(False,p['routes'][n]['endpoints'][-1])):
                if m==role.split('.')[0]:cc=clipped(cc,first,3)
            pair(n,cc,rr,m,t)
        for m,(t,rad) in old.items():pair(n,c,rr,m,t,rad)
        for m,(t,rad) in new.items():
            if m>n:pair(n,c,rr,m,t,rad)
        print('Data bridge',n,'contacts',len(r['contacts']),flush=True)
    if r['contacts']:save('REJECTED_DATA_SHARED_MATERIAL');return
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';archive=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text());pins.update((af,archive))
    with zipfile.ZipFile(archive) as z:geometry=json.loads(z.read('geometry.json'))
    for code in ('FL','FR','RL','RR'):
        ax={a['stage']:a for a in axes['axes'] if a['code']==code}
        for index,stage in enumerate(('Hip','Knee','Ankle')):
            names=['P0_'+q['name'] for q in geometry['components'] if q['stage']==f'Motion_{code}_{stage}']
            for angles in itertools.product(r['angle_grid_degrees'],repeat=index+1):
                transform=W.A.Placement();r['cached_leg_stage_poses']+=1
                for st,angle in zip(('Hip','Knee','Ankle'),angles):
                    a=ax[st];pivot=W.A.Vector(*a['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*a['axis']),angle)
                    transform=transform*W.A.Placement(pivot-rot.multVec(pivot),rot)
                for name in names:
                    t=targets[name].copy();t.Placement=transform*t.Placement;pose=dict(leg=code,stage=stage,angles=angles)
                    for n,(c,rr) in new.items():pair(n,c,rr,name,t,pose=pose)
            print('Data leg stage',code,stage,'contacts',len(r['contacts']),flush=True)
    for yaw in (-15,0,15):
        for pitch in (-10,0,5):
            for m,t in W.F.H.head(reader,yaw,pitch).items():
                if m=='Foundation' or not t.Solids:continue
                for n,(c,rr) in new.items():pair(n,c,rr,'head/'+m,t,pose=dict(yaw=yaw,pitch=pitch))
    save('THREE_DATA_BRIDGES_SAMPLED_CLEAR_NATIVE_OPEN' if not r['contacts'] else 'REJECTED_DATA_SAMPLED_MOTION')

if __name__=='__main__':run()

"""Read-only outward IN lug/complete wire gate; nominal case ambiguity explicit."""
import itertools,json,time,zipfile
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA

def run():
    tick=time.monotonic();f=OUT/'s0-in-extension-plan.json';p=json.loads(f.read_text());assert not p['rejected']
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    pf=OUT/'positive-source-plan.json';gf=OUT/'positive-source-checks.json';g=json.loads(gf.read_text())
    assert g['status']=='THREE_POSITIVE_SOURCE_GUIDES_SAMPLED_CLEAR_IN_EXTENSION_OPEN'
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n
    from current_full_harness_context import context,W,Part
    from current_body_harness_context import clipped
    reader,pins,targets,old=context();pins.update((f,pf,gf,Path(__file__)))
    for src,names in ((pf,('W075','W066')),(OUT/'data-bridges-plan.json',('W007','W011','W012'))):
        pp=json.loads(src.read_text());pins.add(src)
        old.update({n:(W.makewire(pp['routes'][n]['parts']),pp['routes'][n]['radius_mm']) for n in names})
    change=p['source_change'];pivot=W.A.Vector(*change['stud_centre_mm'])
    rot=W.A.Rotation(W.A.Vector(0,0,1),change['rotation_z_degrees'])
    oldtip=W.A.Vector(*json.loads(pf.read_text())['routes']['W076_EXTENSION']['parts'][-1]['end'])
    assert (pivot+rot.multVec(oldtip-pivot)-W.A.Vector(*change['new_barrel_tip_mm'])).Length<1e-6
    ring=targets['S0_ring_IN'].copy();ring.rotate(pivot,W.A.Vector(0,0,1),change['rotation_z_degrees'])
    assert ring.isValid() and ring.Solids;targets['S0_ring_IN']=ring
    targets['PostF0Splice_CP2']=W.box(p['post_F0']['casing_mm'])
    new={n:(W.makewire(v['parts']),v['radius_mm']) for n,v in p['routes'].items()}
    for n in new:old.pop(n,None)
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,W5_complete=False,physical_pass=False,
      cached_leg_stage_poses=0,native_parts_changed=0,S0_stud_datums_manufacturer_verified=False,
      S0_nominal_case_lug_overlap_mm3=ring.common(targets['S0_body_CP2']).Volume,
      nominal_case_overlap_is_NOT_actual_metal_contact=True,M4_complete=False)
    def pair(m,t,rad=0,pose=None):
        for n,(c,rr) in new.items():
            cc=c
            endpoints=('PostF0Splice_CP2','S0_ring_IN') if n=='W076_EXTENSION' else ('F0_CP2','PostF0Splice_CP2')
            if m in endpoints:cc=clipped(cc,m==endpoints[0],3)
            if W.near(cc,t,rr+rad):
                r['pairs']+=1;d,pts,_=cc.distToShape(t)
                if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,
                  required_mm=rr+rad,pose=pose,witness_mm=[list(v) for v in pts[0]] if pts else None))
        if rad:
            if W.near(ring,t,rad):
                r['pairs']+=1;d,pts,_=ring.distToShape(t)
                if d<rad-1e-4:r['contacts'].append(dict(a='candidate_S0_ring_IN',b=m,distance_mm=d,required_mm=rad))
            return
        post=targets['PostF0Splice_CP2']
        if m!='PostF0Splice_CP2' and t.Solids and W.near(post,t,0):
            r['pairs']+=1;hit=post.common(t);assert hit.isValid()
            if hit.Volume>1e-5:r['contacts'].append(dict(a='candidate_POST_F0',b=m,volume_mm3=hit.Volume,pose=pose))
        if m in ('S0_ring_IN','S0_stud_IN','S0_washer_IN','S0_nut_IN','S0_body_CP2') or not t.Solids:return
        if W.near(ring,t,0):
            r['pairs']+=1;hit=ring.common(t);assert hit.isValid()
            if hit.Volume>1e-5:r['contacts'].append(dict(a='candidate_S0_ring_IN',b=m,volume_mm3=hit.Volume,pose=pose))
    def save(status):
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={
          **reader.hashes,**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins}})
        (OUT/'s0-in-extension-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','pairs','contacts','worker_seconds','S0_nominal_case_lug_overlap_mm3')}),flush=True)
    for m,t in targets.items():
        if t.Solids:pair(m,t)
    for m,(t,rad) in old.items():pair(m,t,rad)
    for n,(c,rr) in old.items():
        if W.near(targets['PostF0Splice_CP2'],c,rr):
            r['pairs']+=1;d=targets['PostF0Splice_CP2'].distToShape(c)[0]
            if d<rr-1e-4:r['contacts'].append(dict(a='candidate_POST_F0',b=n,distance_mm=d,required_mm=rr))
    a,ar=new['W076_EXTENSION'];b,br=new['W076_FACTORY'];r['pairs']+=1
    d=a.distToShape(b)[0]
    if d<ar+br-1e-4:r['contacts'].append(dict(a='W076_EXTENSION',b='W076_FACTORY',distance_mm=d,required_mm=ar+br))
    if r['contacts']:save('REJECTED_OUTWARD_S0_IN_MATERIAL');return
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';archive=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text());pins.update((af,archive))
    with zipfile.ZipFile(archive) as z:geom=json.loads(z.read('geometry.json'))
    for code in ('FL','FR','RL','RR'):
        aa={a['stage']:a for a in axes['axes'] if a['code']==code}
        for i,stage in enumerate(('Hip','Knee','Ankle')):
            names=['P0_'+v['name'] for v in geom['components'] if v['stage']==f'Motion_{code}_{stage}']
            for angles in itertools.product((-15,0,15),repeat=i+1):
                T=W.A.Placement();r['cached_leg_stage_poses']+=1
                for st,a in zip(('Hip','Knee','Ankle'),angles):
                    ax=aa[st];v=W.A.Vector(*ax['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*ax['axis']),a)
                    T=T*W.A.Placement(v-rot.multVec(v),rot)
                for m in names:
                    t=targets[m].copy();t.Placement=T*t.Placement;pair(m,t,pose=dict(leg=code,stage=stage,angles=angles))
    for yaw in (-15,0,15):
        for pitch in (-10,0,5):
            for m,t in W.F.H.head(reader,yaw,pitch).items():
                if m!='Foundation' and t.Solids:pair('head/'+m,t,pose=dict(yaw=yaw,pitch=pitch))
    save('OUTWARD_S0_IN_SAMPLED_CLEAR_TERMINAL_CASE_FIT_OPEN' if not r['contacts'] else 'REJECTED_OUTWARD_S0_IN_MOTION')

if __name__=='__main__':run()

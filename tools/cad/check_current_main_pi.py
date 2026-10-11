"""Actual retained material gate for the complete four-pad MAIN/Pi proposal.

No blanket PCB exclusion. Bare conductors are checked with their Cu section;
only the named FHAC exit and its own explicit insulated lap are assigned.
"""
import json,time,math
from pathlib import Path
from current_leg_harness_context import context,W,Part,ROOT,OUT
from current_body_harness_context import clipped

def run():
    tick=time.monotonic();f=OUT/'main-pi-plan.json';p=json.loads(f.read_text())
    sf=OUT/'main-pi-screen.json';pre=json.loads(sf.read_text())
    for name,h in pre['source_sha256'].items():assert W.sha(ROOT/name)==h,name
    assert pre['status']=='MAIN_PI_PROXIMITY_ONLY_REAL_MATERIAL_OPEN'
    reader,pins,targets,old=context();pins.update((Path(__file__),f,sf))
    bf=OUT/'bank-input-plan.json';bp=json.loads(bf.read_text());pins.add(bf)
    # Reuse the same declared candidate frame changes, not a new silent cut.
    cut=targets['Foundation']
    for h in bp['required_foundation_passages']:
        x,y=h['centre_xy_mm'];z0,z1=h['z_range_mm']
        cut=cut.cut(Part.makeCylinder(h['diameter_mm']/2,z1-z0,W.A.Vector(x,y,z0)))
    assert cut.isValid();targets['Foundation']=cut
    rem=bp['obsolete_side_attachment_removal'];cut=targets[rem['target']]
    for b in rem['cut_bounds_mm']:cut=cut.cut(W.box(b))
    assert cut.isValid() and not cut.check(True);targets[rem['target']]=cut
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in bp['routes'].items()})
    old.pop('W077_PREFIX',None);targets.pop('F_PI_sleeve',None)
    sleeve=W.box(p['factory_custom_overlap']['sleeve_bounds_mm'])
    rows=p['routes'];new={n:(W.makewire(v['parts']),v['radius_mm']) for n,v in rows.items()}
    new.update({n+'_bare':(W.makewire(q),math.sqrt(.823/math.pi)) for n,q in p['bare_pad_parts'].items()})
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,W5_complete=False,physical_pass=False,
      scope='Actual material and all retained curves; unchanged baseline gallery motion remains rejected separately. Native grips/service remain OPEN.')
    def pair(n,c,rr,m,t,rad=0):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,m);r['pairs']+=1
        d,points,_=c.distToShape(t)
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,
          witness_mm=[list(v) for v in points[0]] if points else None))
    for n,(c,rr) in new.items():
        for m,t in targets.items():
            if not t.Solids:continue
            cc=clipped(c,True,3) if n=='W077' and m=='F_PI_new' else c
            pair(n,cc,rr,m,t)
        for m,(t,rad) in old.items():pair(n,c,rr,m,t,rad)
        for m,(t,rad) in new.items():
            if m<=n or n.removesuffix('_bare')==m.removesuffix('_bare') or {n,m}=={'W077','W078'}:continue
            pair(n,c,rr,m,t,rad)
        print('MAIN/Pi',n,'contacts',len(r['contacts']),flush=True)
    for m,t in targets.items():
        if t.Solids and W.near(sleeve,t,0):
            r['pairs']+=1;hit=sleeve.common(t);assert hit.isValid()
            if hit.Volume>1e-5:r['contacts'].append(dict(a='F_PI_sleeve',b=m,volume_mm3=hit.Volume))
    for m,(t,rr) in {**old,**new}.items():
        if m not in ('W077','W078'):pair(m,t,rr,'F_PI_sleeve',sleeve)
    r.update(status='MAIN_PI_SHARED_MATERIAL_ONLY_NATIVE_OPEN' if not r['contacts'] else 'REJECTED_MAIN_PI_SHARED_MATERIAL',
      worker_seconds=round(time.monotonic()-tick,3),
      source_sha256={**reader.hashes,**{q.relative_to(ROOT).as_posix():W.sha(q) for q in pins}})
    (OUT/'main-pi-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:r[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)

if __name__=='__main__':run()

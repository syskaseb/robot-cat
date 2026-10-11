"""Changed four MAIN/Pi guides against current valid material and Hip guides.

No native change or inherited full-motion acceptance. The sole intended lap
is cropped geometrically when checking its two same-net constituent wires.
"""
import json, time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from current_complete_harness_context import context,W,Part
from current_body_harness_context import clipped
from check_current_hip_axial_looms import parts as hip_parts


def run():
    tick=time.monotonic(); f=OUT/'main-east-comb-plan.json';p=json.loads(f.read_text())
    assert p['status']=='MAIN_EAST_COMB_SCREEN_ONLY_MATERIAL_AND_NATIVE_OPEN'
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    reader,pins,targets,old=context();pins.update((f,Path(__file__)))
    rows=p['routes'];new={n:(W.makewire(r['parts']),r['radius_mm']) for n,r in rows.items()}
    for n in rows:old.pop(n,None)
    old.pop('W077_PREFIX',None)
    # Same casing, same existing sleeve envelope; only the protected lap ends changed.
    targets.pop('F_PI_sleeve',None)
    hip=OUT/'hip-axial-loom-plan.json';hp=json.loads(hip.read_text());pins.add(hip)
    old.update({r['section']:(W.makewire(hip_parts(r,0)),3) for r in hp['loops']})
    result=dict(status='PENDING',pairs=0,contacts=[],errors=[],native_changed=False,
        selected=False,W5_complete=False,physical_pass=False,
        scope='Four changed MAIN/Pi guides; retained cases, all current fixed wires, nominal axial Hip proposal. No Hip or full movement acceptance.')
    def pair(n,c,rr,m,t,rad=0):
        if not W.near(c,t,rr+rad):return
        result['pairs']+=1
        try:
            assert c.isValid() and t.isValid()
            d,pts,_=c.distToShape(t)
            if d<rr+rad-1e-4:
                result['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,
                    witness_mm=[list(v) for v in pts[0]] if pts else None))
        except Exception as e:result['errors'].append(dict(a=n,b=m,cause=repr(e)))
    for n,(c,rr) in new.items():
        for m,t in targets.items():
            if not t.Solids:continue
            cc=clipped(c,True,3) if n=='W077' and m=='F_PI_new' else c
            pair(n,cc,rr,m,t)
        for m,(t,rad) in old.items():pair(n,c,rr,m,t,rad)
        for m,(t,rad) in new.items():
            if m<=n:continue
            if {n,m}=={'W077','W078'}:
                pair(n,clipped(new['W077'][0],False,8),new['W077'][1],m,
                     clipped(new['W078'][0],True,8),new['W078'][1])
            else:pair(n,c,rr,m,t,rad)
        print('MAIN east',n,'contacts',len(result['contacts']),flush=True)
    # Include the retained unchanged sleeve as physical material, not an ignored box.
    sleeve=W.box(p['corrected_source_splice']['sleeve_bounds_mm'])
    for m,t in targets.items():
        if not t.Solids or not W.near(sleeve,t,0):continue
        result['pairs']+=1
        try:
            common=sleeve.common(t);assert common.isValid()
            if common.Volume>1e-5:result['contacts'].append(dict(a='F_PI_sleeve',b=m,volume_mm3=common.Volume))
        except Exception as e:result['errors'].append(dict(a='F_PI_sleeve',b=m,cause=repr(e)))
    for m,(t,rr) in {**old,**new}.items():
        if m not in ('W077','W078'):pair(m,t,rr,'F_PI_sleeve',sleeve)
    # Actual fixed parent geometry for the subsequent native grip load path.
    result['parent_bounds_mm']={n:[getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
        for n,s in targets.items() if s.Solids and ('MAIN' in n.upper() or n in ('LowerCarrier001','UpperCarrier001'))}
    result.update(status='REJECTED_MAIN_EAST_COMB_MATERIAL' if result['contacts'] or result['errors'] else 'MAIN_EAST_COMB_STATIC_MATERIAL_CLEAR_NATIVE_OPEN',
        worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**reader.hashes,**{v.relative_to(ROOT).as_posix():SHA(v) for v in pins}})
    (OUT/'main-east-comb-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','pairs','contacts','errors','parent_bounds_mm','worker_seconds')}),flush=True)
    return result


if __name__=='__main__':run()

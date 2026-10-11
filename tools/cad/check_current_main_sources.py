"""Current complete four-source extension gate; changed interfaces only.

Factory MTA receipt is retained by exact plan hash. This adds complete custom
curves and relocated P_FRONT, no native edits or W5/physical acceptance.
"""
import json,time
from pathlib import Path
import build_current_aux_power as B
W,A,Part,ROOT,BASE=B.W,B.A,B.Part,B.ROOT,B.BASE
OUT=BASE/'body-harness-checkpoint'
def run():
    tick=time.monotonic();p=json.loads((OUT/'main-source-plan.json').read_text())
    m=json.loads((OUT/'mta-interface-plan.json').read_text())
    q=json.loads((OUT/'mta-interface-checks.json').read_text())
    assert not q['contacts'] and not q['errors']
    paths={n:W.makewire(v['parts']) for n,v in p['routes'].items()}
    peers={n:(W.makewire(v['parts']),v['radius_mm']) for n,v in m['factory_routes'].items()}
    r=dict(status='PENDING',contacts=[],errors=[],pairs=0,selected=False,W5_complete=False,physical_pass=False)
    def pair(n,c,rr,name,t,rad):
        if not W.near(c,t,rr+rad):return
        r['pairs']+=1;result=c.distToShape(t);d=result[0]
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=name,distance_mm=d,required_mm=rr+rad,
            closest_mm=[list(v) for v in result[1][0]] if result[1] else None))
    for n,c in paths.items():
        assert c.isValid(),n
        for a,b in zip(c.Edges,c.Edges[1:]):
            gap=(a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length
            dot=a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))
            if gap>1e-5 or dot<1-1e-5:r['errors'].append(dict(wire=n,gap=gap,dot=dot))
        for name,(t,rad) in {**peers,**{k:(paths[k],p['routes'][k]['radius_mm']) for k in paths if k>n}}.items():pair(n,c,p['routes'][n]['radius_mm'],name,t,rad)
    pins={Path(__file__),OUT/'main-source-plan.json',OUT/'mta-interface-plan.json',OUT/'mta-interface-checks.json'}
    reader=W.SavedShapes()
    def write():
        r.update(worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():W.sha(f) for f in pins}})
        (OUT/'main-source-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','contacts','errors','pairs','worker_seconds')}),flush=True)
    if r['contacts'] or r['errors']:
        r['status']='REJECTED_SOURCE_MUTUAL_OR_CONTINUITY_PREFLIGHT';write();return
    aux=BASE/'aux-wiring-checkpoint';sel=json.loads((aux/'selection.json').read_text())
    model=ROOT/sel['native'];assert W.sha(model)==sel['model_sha256'];pins.update((model,aux/'selection.json',aux/'whole-layout-plan.json'))
    wp=json.loads((aux/'whole-layout-plan.json').read_text());targets,_=W.current_scene(reader,wp)
    for n in ('Foundation','UpperCarrier001','E2Fixture'):
        s=reader.shape(model,n)
        if n=='Foundation':s.translate(B.SHIFT)
        targets[n]=s
    for n in reader.doc(model):
        if n.startswith('W1Ref_'):
            s=reader.shape(model,n)
            if s.Solids:targets[n]=s
    for h in m['holders']:targets['MTA/'+h['leg']]=W.box(h['casing_mm'])
    for j in m['joints']:targets[j['id']]=W.box(j['casing_mm'])
    pf=W.box(p['P_FRONT']['casing_mm'])
    retained={n:(W.makewire(v['parts']),v['radius']) for n,v in wp['routes'].items()}
    for folder,file in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        f=BASE/folder/file;pins.add(f)
        for n,v in json.loads(f.read_text())['routes'].items():
            if 'reserved' not in n and n!='F_HY_input_prefix':retained[folder+'/'+n]=(W.makewire(v['parts']),v['radius'])
    for yaw in (-15,0,15):
        for n,(c,rr,f) in W.F.H.local(yaw).items():retained[f'head/{n}/{yaw:+}']=(c,rr);pins.add(f)
        for n in ('XB22','XB23','XS23'):
            f=BASE/'head-wiring-access-checkpoint'/f'{n}_yaw{yaw:+}_Loop.brep'
            retained[f'head/current/{n}/{yaw:+}']=(Part.read(str(f)),1.05);pins.add(f)
    def outside(c,first,land=9):
        edges=list(c.Edges);i=0 if first else -1;e=edges[i]
        assert e.Length>=land-1e-6
        if abs(e.Length-land)<1e-6:edges.pop(i)
        else:
            a=e.valueAt(e.FirstParameter);b=e.valueAt(e.LastParameter);axis=(b-a).normalize()
            edges[i]=Part.makeLine(a+axis*land,b) if first else Part.makeLine(a,b-axis*land)
        return Part.Wire(edges)
    def curve(n,c,rr,name,t):
        if not t.Solids or not W.near(c,t,rr):return
        assert t.isValid(),name;r['pairs']+=1;d=c.distToShape(t)[0]
        if d<rr-1e-4:r['contacts'].append(dict(a=n,b=name,distance_mm=d,required_mm=rr))
    def solid(name,s,n,t):
        if not t.Solids or not W.near(s,t,0):return
        assert s.isValid() and t.isValid(),(name,n);r['pairs']+=1;hit=s.common(t);assert hit.isValid()
        if hit.Volume>1e-5:r['contacts'].append(dict(a=name,b=n,volume_mm3=hit.Volume))
    for n,t in targets.items():solid('P_FRONT_new',pf,n,t)
    for n,(c,rr) in {**retained,**peers}.items():curve(n,c,rr,'P_FRONT_new',pf)
    for n,c in paths.items():
        wid=n.removesuffix('_CUSTOM');rr=p['routes'][n]['radius_mm']
        for name,t in {**targets,'P_FRONT_new':pf}.items():
            clipped=outside(c,True,3 if wid=='W041' else 9) if name==wid+'_Joint' else outside(c,False,3 if wid=='W044' else 2.5 if wid=='W052' else 9) if name==('P_FRONT_new' if wid in ('W041','W042') else 'P_REAR') else c
            curve(n,clipped,rr,name,t)
        for name,(t,rad) in retained.items():pair(n,c,rr,name,t,rad)
        print('Source continuation',n,'contacts',len(r['contacts']),'errors',len(r['errors']),flush=True)
    if not r['contacts'] and not r['errors']:
        for yaw in (-15,0,15):
            for pitch in (-10,0,5):
                for name,t in W.F.H.head(reader,yaw,pitch).items():
                    if name=='Foundation':continue
                    solid('P_FRONT_new',pf,'head/'+name,t)
                    for n,c in paths.items():curve(n,c,p['routes'][n]['radius_mm'],'head/'+name,t)
            print('Source continuation head yaw',yaw,'contacts',len(r['contacts']),flush=True)
    r['status']='FOUR_SOURCE_CONTINUATIONS_SPACE_ONLY_RELIEF_OUTPUTS_AND_W5_OPEN' if not r['contacts'] and not r['errors'] else 'REJECTED_COMPLETE_SOURCE_SHARED_ALLOCATION'
    write()
if __name__=='__main__':run()

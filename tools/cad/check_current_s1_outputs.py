"""Only the two changed S1 outputs; retain exact four-source/MTA receipts."""
import json,time
from pathlib import Path
import build_current_aux_power as B
W,Part,ROOT,BASE=B.W,B.Part,B.ROOT,B.BASE
OUT=BASE/'body-harness-checkpoint'

def run():
    tick=time.monotonic();p=json.loads((OUT/'s1-output-plan.json').read_text())
    main=json.loads((OUT/'main-source-plan.json').read_text())
    m=json.loads((OUT/'mta-interface-plan.json').read_text())
    for filename,planfile in [('main-source-checks.json','main-source-plan.json'),('mta-interface-checks.json','mta-interface-plan.json')]:
        gate=json.loads((OUT/filename).read_text());assert not gate['contacts'] and not gate['errors']
        assert gate['source_sha256'][(OUT/planfile).relative_to(ROOT).as_posix()]==W.sha(OUT/planfile)
    paths={n:W.makewire(v['parts']) for n,v in p['routes'].items()}
    peers={n:(W.makewire(v['parts']),v['radius_mm']) for n,v in {**m['factory_routes'],**main['routes']}.items()}
    r=dict(status='PENDING',contacts=[],errors=[],pairs=0,selected=False,W5_complete=False,physical_pass=False)
    pins={Path(__file__),OUT/'s1-output-plan.json',OUT/'main-source-plan.json',OUT/'main-source-checks.json',OUT/'mta-interface-plan.json',OUT/'mta-interface-checks.json'}
    reader=W.SavedShapes()
    def pair(n,c,rr,name,t,rad=0):
        if not W.near(c,t,rr+rad):return
        r['pairs']+=1;d=c.distToShape(t)[0]
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=name,distance_mm=d,required_mm=rr+rad))
    def write(status):
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():W.sha(f) for f in pins}})
        (OUT/'s1-output-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    for n,c in paths.items():
        assert c.isValid(),n
        for a,b in zip(c.Edges,c.Edges[1:]):
            gap=(a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length;dot=a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))
            if gap>1e-5 or dot<1-1e-5:r['errors'].append(dict(wire=n,gap=gap,dot=dot))
        for name,(t,rad) in {**peers,**{k:(paths[k],2.1) for k in paths if k>n}}.items():pair(n,c,2.1,name,t,rad)
    if r['contacts'] or r['errors']:write('REJECTED_CHANGED_S1_PREFLIGHT');return
    aux=BASE/'aux-wiring-checkpoint';sel=json.loads((aux/'selection.json').read_text());model=ROOT/sel['native']
    assert W.sha(model)==sel['model_sha256'];pins.update((model,aux/'selection.json',aux/'whole-layout-plan.json'))
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
    targets['P_FRONT_new']=W.box(p['P_FRONT']['casing_mm'])
    new_heads={n:W.box(b) for n,b in p.get('changed_e2_heads',{}).items()}
    targets.update(new_heads)
    retained={n:(W.makewire(v['parts']),v['radius']) for n,v in wp['routes'].items()}
    for folder,file in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        f=BASE/folder/file;pins.add(f)
        for n,v in json.loads(f.read_text())['routes'].items():
            if 'reserved' not in n and n!='F_HY_input_prefix':retained[folder+'/'+n]=(W.makewire(v['parts']),v['radius'])
    for yaw in (-15,0,15):
        for n,(c,rr,f) in W.F.H.local(yaw).items():retained[f'head/{n}/{yaw:+}']=(c,rr);pins.add(f)
        for n in ('XB22','XB23','XS23'):
            f=BASE/'head-wiring-access-checkpoint'/f'{n}_yaw{yaw:+}_Loop.brep';pins.add(f)
            retained[f'head/current/{n}/{yaw:+}']=(Part.read(str(f)),1.05)
    def clipped(c,first,land):
        es=list(c.Edges);i=0 if first else -1;e=es[i];assert e.Length>=land-1e-6
        if abs(e.Length-land)<1e-6:es.pop(i)
        else:
            a=e.valueAt(e.FirstParameter);b=e.valueAt(e.LastParameter);v=(b-a).normalize()
            es[i]=Part.makeLine(a+v*land,b) if first else Part.makeLine(a,b-v*land)
        return Part.Wire(es)
    # Changed purchased-part poses must clear every retained wire and actual
    # neighbour; keeping the bands does not waive head contacts.
    for n,s in new_heads.items():
        for name,t in targets.items():
            if name==n or not t.Solids or not W.near(s,t,0):continue
            assert t.isValid();r['pairs']+=1;hit=s.common(t);assert hit.isValid()
            if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=name,volume_mm3=hit.Volume))
        for name,(c,rr) in {**retained,**peers}.items():pair(name,c,rr,n,s)
    for n,c in paths.items():
        ring='current/'+p['rings'][n]['native'];assert ring in targets,(ring,[k for k in targets if 'ring' in k])
        endpoint=Part.Vertex(W.A.Vector(*p['rings'][n]['point_mm']))
        assert endpoint.distToShape(targets[ring])[0]<1e-5,(n,'ring endpoint does not meet current material')
        for name,t in targets.items():
            if not t.Solids:continue
            assert t.isValid(),name
            cc=clipped(c,True,9 if n=='W064' else 2.5) if name==('P_FRONT_new' if n=='W064' else 'P_REAR') else clipped(c,False,6 if n=='W064' else 9) if name==ring else c
            pair(n,cc,2.1,name,t)
        for name,(t,rad) in retained.items():pair(n,c,2.1,name,t,rad)
        print('S1 changed output',n,'contacts',len(r['contacts']),flush=True)
    if not r['contacts'] and not r['errors']:
        for yaw in (-15,0,15):
            for pitch in (-10,0,5):
                for name,t in W.F.H.head(reader,yaw,pitch).items():
                    if name=='Foundation' or not t.Solids:continue
                    assert t.isValid(),name
                    for n,c in paths.items():pair(n,c,2.1,'head/'+name,t)
            print('S1 head yaw',yaw,'contacts',len(r['contacts']),flush=True)
    write('TWO_S1_OUTPUTS_SPACE_ONLY_NATIVE_AND_W5_OPEN' if not r['contacts'] and not r['errors'] else 'REJECTED_S1_OUTPUT_SHARED_ALLOCATION')
if __name__=='__main__':run()

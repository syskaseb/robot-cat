"""Bounded planning gate for all4MTA/8factory ends against current parts.

No native edits, unknown endpoints, support exclusions or complete W5 claim.
New custom approaches/retention will require the next shared gate.
"""
import json,time
from pathlib import Path
import build_current_aux_power as B
W,A,Part,ROOT,BASE=B.W,B.A,B.Part,B.ROOT,B.BASE
OUT=BASE/'body-harness-checkpoint'
def fast(p):
    """Positive rejection only; sampled curves cannot qualify clearance."""
    curves={n:(W.makewire(v['parts']),v['radius_mm']) for n,v in p['factory_routes'].items()}
    contacts=[]
    for n,(c,rr) in curves.items():
        for m,(t,rad) in curves.items():
            if n>=m or not W.near(c,t,rr+rad):continue
            d=c.distToShape(t)[0]
            if d<rr+rad-1e-4:contacts.append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad))
    return contacts
def run():
    tick=time.monotonic();reader=W.SavedShapes()
    planpath=OUT/'mta-interface-plan.json';p=json.loads(planpath.read_text())
    bad=fast(p)
    if bad:
        r=dict(status='REJECTED_FACTORY_MUTUAL_PREFLIGHT',contacts=bad,selected=False,W5_complete=False,
               worker_seconds=round(time.monotonic()-tick,3),source_sha256={planpath.relative_to(ROOT).as_posix():W.sha(planpath)})
        (OUT/'mta-interface-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(r),flush=True);return
    aux=BASE/'aux-wiring-checkpoint';selection=json.loads((aux/'selection.json').read_text())
    model=ROOT/selection['native'];assert W.sha(model)==selection['model_sha256']
    w1=json.loads((aux/'whole-layout-plan.json').read_text())
    targets,_=W.current_scene(reader,w1)
    for name in ('Foundation','UpperCarrier001','E2Fixture'):
        s=reader.shape(model,name)
        if name=='Foundation':s.translate(B.SHIFT)
        targets[name]=s
    # Current native W1 reference solids include its real band envelopes,
    # sleeves and individual end insulation, not centreline-only wires.
    for name in reader.doc(model):
        if name.startswith('W1Ref_'):
            s=reader.shape(model,name)
            if s.Solids:targets[name]=s
    curves={}
    for name,row in w1['routes'].items():curves['W1/'+name]=(W.makewire(row['parts']),row['radius'])
    for folder,file in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        for name,row in json.loads((BASE/folder/file).read_text())['routes'].items():
            if 'reserved' in name or name=='F_HY_input_prefix':continue
            curves[folder+'/'+name]=(W.makewire(row['parts']),row['radius'])
    loop_pins=set()
    for yaw in (-15,0,15):
        for name,(s,rr,path) in W.F.H.local(yaw).items():
            assert s.isValid(),path
            curves[f'W2/local/{name}/{yaw:+}']=(s,rr);loop_pins.add(path)
        for name in ('XB22','XB23','XS23'):
            yawtag=f'{yaw:+}'
            path=BASE/'head-wiring-access-checkpoint'/f'{name}_yaw{yawtag}_Loop.brep'
            s=Part.Shape();s.read(str(path));assert s.isValid() and s.Edges,path
            curves[f'W2/{name}/yaw{yawtag}']=(s,1.05);loop_pins.add(path)
    cases={r['leg']:W.box(r['casing_mm']) for r in p['holders']}
    cases.update({r['id']:W.box(r['casing_mm']) for r in p['joints']})
    factory={n:(W.makewire(row['parts']),row['radius_mm']) for n,row in p['factory_routes'].items()}
    assigned={frozenset((n,n.removesuffix('_FACTORY')+'_Joint')) for n in factory}
    r=dict(status='PENDING',contacts=[],errors=[],pairs=0,selected=False,W5_complete=False,physical_pass=False,
        scope='Four nominal casings/eight joint casings/eight complete factory guides only. Eight custom continuations, current bank retention, all other W5 routes and lever/delivered fit remain open.')
    def solid(n,s,m,t):
        if not s.Solids or not t.Solids or not W.near(s,t,0):return
        assert s.isValid() and t.isValid(),(n,m)
        r['pairs']+=1;hit=s.common(t);assert hit.isValid(),(n,m)
        if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
    def curve(n,c,rr,m,t):
        if not t.Solids or not W.near(c,t,rr):return
        assert t.isValid(),m;r['pairs']+=1;dist=c.distToShape(t)[0]
        if dist<rr-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=dist,required_mm=rr))
    for n,s in cases.items():
        for m,t in targets.items():solid(n,s,m,t)
        for m,(c,rr) in curves.items():curve(m,c,rr,n,s)
        for m,t in cases.items():
            if n<m:solid(n,s,m,t)
    for n,(c,rr) in factory.items():
        leg=next(h['leg'] for h in p['holders'] if h['leg'] in ('FL','FR','RL','RR') and
                 p['factory_routes'][n]['body_conductor_id'] in
                 dict(FL=('W041','W026'),FR=('W042','W037'),RL=('W044','W045'),RR=('W052','W053'))[h['leg']])
        for m,t in targets.items():curve(n,c,rr,m,t)
        for m,t in cases.items():
            if m==leg or frozenset((n,m)) in assigned:continue
            curve(n,c,rr,m,t)
        for m,(d,rad) in {**curves,**factory}.items():
            if n==m or m in factory and n>m or not W.near(c,d,rr+rad):continue
            r['pairs']+=1;dist=c.distToShape(d)[0]
            if dist<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=dist,required_mm=rr+rad))
        print('MTA planning gate',n,'contacts',len(r['contacts']),flush=True)
    # Do not run pose gates for an already rejected static allocation.
    if not r['contacts']:
        for yaw in (-15,0,15):
            for pitch in (-10,0,5):
                for m,t in W.F.H.head(reader,yaw,pitch).items():
                    if m=='Foundation':continue
                    for n,s in cases.items():solid(n,s,'head/'+m,t)
                    for n,(c,rr) in factory.items():curve(n,c,rr,'head/'+m,t)
            print('MTA head planning yaw',yaw,'contacts',len(r['contacts']),flush=True)
    pins={planpath,Path(__file__),model,aux/'selection.json',aux/'whole-layout-plan.json',*loop_pins}
    for folder,file in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:pins.add(BASE/folder/file)
    r.update(status='MTA_FACTORY_INTERFACE_SPACE_ONLY_CUSTOMS_AND_NATIVE_OPEN' if not r['contacts'] else 'REJECTED_MTA_FACTORY_SHARED_ALLOCATION',
        worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():W.sha(f) for f in pins}})
    (OUT/'mta-interface-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:r[k] for k in ('status','contacts','errors','pairs','worker_seconds')}),flush=True)
if __name__=='__main__':run()

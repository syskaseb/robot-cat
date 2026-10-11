"""Changed W1 interfaces against the two selected R47 native bank halves.

Read saved world BReps, no recompute or source writes. Historical upper cover
is deliberately omitted by the current open-prototype scope; bank halves are
not silently replaced by their twelve bought holder envelopes.
"""
import json,time
from pathlib import Path
import build_current_aux_power as B
W,G,A,Part,ROOT,BASE,OUT=B.W,B.G,B.A,B.Part,B.ROOT,B.BASE,B.OUT

def run():
    tick=time.monotonic();reader=W.SavedShapes()
    release=ROOT/'hardware/manufacturing/one-batch-prototype-r52/selection.json'
    selected=json.loads(release.read_text());p=G.allocation()['source_plan'];g=G.allocation()
    model=OUT/'AUXPowerCurrent.FCStd'
    receipt=json.loads((OUT/'native-checks.json').read_text())
    assert receipt['status']=='CURRENT_NATIVE_W1_PREPARED'
    assert W.sha(model)==receipt['model_sha256']
    banks={}
    for row in selected['prints']:
        if row['identity'] not in ('electronics:servo-fuse-bank-left','electronics:servo-fuse-bank-right'):continue
        source=ROOT/row['native_file']
        assert W.sha(source)==selected['source_sha256'][row['native_file']],row['identity']
        shape=reader.shape(source,row['native_final'])
        assert shape.isValid() and len(shape.Solids)==1,row['identity']
        banks[row['identity']]=shape
    assert len(banks)==2
    material={}
    for name,source in [('Foundation',B.SOURCE),('UpperCarrier001',B.SOURCE),('E2Fixture',B.E2SOURCE)]:
        new=reader.shape(model,receipt['native_bodies'][name]);old=reader.shape(source,name)
        if name=='Foundation':new.translate(B.SHIFT);old.translate(B.SHIFT)
        delta=new.cut(old);assert delta.isValid(),name
        material['added/'+name]=delta
    material.update(g['bands']);material.update(B.insulation(p))
    targets,_=W.current_scene(reader,p)
    material.update({name:targets[name] for name in ('P_AUX_CP2','G2_CP2','F_AUX_candidate_case','W4_TieHead_PairedSourceGround')})
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],physical_pass=False,selected=False,
           bank_bounds_mm={n:W.bounds(s) for n,s in banks.items()},
           scope='Only changed W1 material/cases/insulation/bands and complete current W1 routes against retained selected R47 bank halves. No old cover or entire W5 acceptance.')
    for n,s in material.items():
        for m,t in banks.items():
            if not s.Solids or not W.near(s,t,0):continue
            r['pairs']+=1
            v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
            if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
    for n,route in p['routes'].items():
        wire=W.makewire(route['parts']);radius=route['radius']
        for m,t in banks.items():
            if not W.near(wire,t,radius):continue
            r['pairs']+=1;distance=wire.distToShape(t)[0]
            if distance<radius-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=distance,required_mm=radius))
    r.update(status='CURRENT_W1_BANK_BOUNDARY_CLEAR' if not r['contacts'] else 'REJECTED_W1_BANK_BOUNDARY',
        worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**reader.hashes,release.relative_to(ROOT).as_posix():W.sha(release),
          Path(__file__).relative_to(ROOT).as_posix():W.sha(Path(__file__)),
          (OUT/'native-checks.json').relative_to(ROOT).as_posix():W.sha(OUT/'native-checks.json')})
    W.save('bank-boundary-checks.json',r)
    print(json.dumps(r),flush=True)

if __name__=='__main__':run()

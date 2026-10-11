"""Shared retained scene for NEW body-harness interfaces, without native edits.

Qualified geometry is pinned, not re-gated. Candidate source guides and two
changed purchased-head poses remain unselected until whole W5 is complete.
"""
import json
from pathlib import Path
import build_current_aux_power as B
W,Part,ROOT,BASE=B.W,B.Part,B.ROOT,B.BASE
OUT=BASE/'body-harness-checkpoint'

def context():
    reader=W.SavedShapes();pins={Path(__file__)};plans={}
    for tag in ('mta-interface','main-source','s1-output'):
        f=OUT/(tag+'-plan.json');g=OUT/(tag+'-checks.json');p=json.loads(f.read_text());q=json.loads(g.read_text())
        assert not q['contacts'] and not q['errors'],tag
        assert q['source_sha256'][f.relative_to(ROOT).as_posix()]==W.sha(f),tag
        plans[tag]=p;pins.update((f,g))
    aux=BASE/'aux-wiring-checkpoint';sf=aux/'selection.json';sel=json.loads(sf.read_text());model=ROOT/sel['native']
    assert W.sha(model)==sel['model_sha256'];pins.update((model,sf,aux/'whole-layout-plan.json'))
    wp=json.loads((aux/'whole-layout-plan.json').read_text());targets,_=W.current_scene(reader,wp)
    for n in ('Foundation','UpperCarrier001','E2Fixture'):
        s=reader.shape(model,n)
        if n=='Foundation':s.translate(B.SHIFT)
        targets[n]=s
    for n in reader.doc(model):
        if n.startswith('W1Ref_'):
            s=reader.shape(model,n)
            if s.Solids:targets[n]=s
    m=plans['mta-interface']
    for h in m['holders']:targets['MTA/'+h['leg']]=W.box(h['casing_mm'])
    for j in m['joints']:targets[j['id']]=W.box(j['casing_mm'])
    targets['P_FRONT_new']=W.box(plans['main-source']['P_FRONT']['casing_mm'])
    targets.update({n:W.box(b) for n,b in plans['s1-output']['changed_e2_heads'].items()})
    retained={n:(W.makewire(v['parts']),v['radius']) for n,v in wp['routes'].items()}
    for tag,key in [('mta-interface','factory_routes'),('main-source','routes'),('s1-output','routes')]:
        retained.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in plans[tag][key].items()})
    for folder,file in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        f=BASE/folder/file;pins.add(f)
        for n,v in json.loads(f.read_text())['routes'].items():
            if 'reserved' not in n and n!='F_HY_input_prefix':retained[folder+'/'+n]=(W.makewire(v['parts']),v['radius'])
    for yaw in (-15,0,15):
        for n,(c,rr,f) in W.F.H.local(yaw).items():retained[f'head/{n}/{yaw:+}']=(c,rr);pins.add(f)
        for n in ('XB22','XB23','XS23'):
            f=BASE/'head-wiring-access-checkpoint'/f'{n}_yaw{yaw:+}_Loop.brep';pins.add(f)
            retained[f'head/current/{n}/{yaw:+}']=(Part.read(str(f)),1.05)
    return reader,pins,targets,retained

def clipped(c,first,land):
    es=list(c.Edges);i=0 if first else -1;e=es[i];assert e.Length>=land-1e-6
    if abs(e.Length-land)<1e-6:es.pop(i)
    else:
        a=e.valueAt(e.FirstParameter);b=e.valueAt(e.LastParameter);v=(b-a).normalize()
        es[i]=Part.makeLine(a+v*land,b) if first else Part.makeLine(a,b-v*land)
    return Part.Wire(es)

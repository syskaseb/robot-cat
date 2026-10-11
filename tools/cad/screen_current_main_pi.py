"""Cheap simultaneous rejection screen before actual MAIN/Pi geometry."""
import json,time
from plan_current_harness_interfaces import ROOT,BASE,OUT,SHA
from open_prototype_path_preflight import screen

def run():
    tick=time.monotonic();pins={__file__};old=[]
    def read(f):pins.add(f);return json.loads(f.read_text())
    for tag,keys in [('mta-interface',['factory_routes']),('main-source',['routes']),
        ('s1-output',['routes']),('source-receiving',['routes','factory_routes']),
        ('leg-stations',['routes']),('bank-input',['routes'])]:
        p=read(OUT/(tag+'-plan.json'))
        for key in keys:
            for n,r in p[key].items():
                if n in ('W026_FACTORY','W077_PREFIX'):continue
                old.append(dict(wire=n,OD_mm=2*r['radius_mm'],segments=r['parts']))
        if tag=='leg-stations':old.append(dict(wire='W026_FACTORY',OD_mm=4.2,segments=p['factory_override']['parts']))
    for folder,file in [('aux-wiring-checkpoint','whole-layout-plan.json'),
        ('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),
        ('pwm-branch-checkpoint','final-plan.json')]:
        p=read(BASE/folder/file)
        for n,r in p['routes'].items():
            if 'reserved' in n or n=='F_HY_input_prefix':continue
            parts=[]
            for s in r['parts']:
                if s['kind']=='spline':parts.extend(dict(kind='line',start=a,end=b) for a,b in zip(s['points'],s['points'][1:]) if a!=b)
                else:parts.append(s)
            old.append(dict(wire=folder+'/'+n,OD_mm=2*r['radius'],segments=parts))
    p=read(OUT/'main-pi-plan.json')
    new=[dict(wire=n,OD_mm=2*r['radius_mm'],segments=r['parts']) for n,r in p['routes'].items()]
    g=screen(dict(tails=old,s1_routes=new,holders=[]));names={r['wire'] for r in new}
    g['near_pairs']=[r for r in g['near_pairs'] if r['b'] in names and {r['a'],r['b']}!={'W077','W078'}]
    g.update(status='REJECTED_MAIN_PI_CHEAP_SHARED_SCREEN' if any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in g['near_pairs']) else 'MAIN_PI_PROXIMITY_ONLY_REAL_MATERIAL_OPEN',
      worker_seconds=time.monotonic()-tick,
      source_sha256={str(__import__('pathlib').Path(f).relative_to(ROOT).as_posix()):SHA(__import__('pathlib').Path(f)) for f in pins})
    (OUT/'main-pi-screen.json').write_text(json.dumps(g,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=g['status'],pairs=[r for r in g['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'],seconds=g['worker_seconds'])))

if __name__=='__main__':run()

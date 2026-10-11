"""One cheap whole-harness screen, with explicit newer planning overlays.

Used only to reject incompatible centreline proposals before FreeCAD.
Interpolated spline stations, bboxes and this receipt are NOT actual fit.
"""
import json,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,OUT,SHA
from open_prototype_path_preflight import screen

def route_rows(extra=()):
    rows={};pins=set()
    def read(f):pins.add(f);return json.loads(f.read_text())
    def add(q,prefix=''):
        for n,r in q.items():
            if 'reserved' in n or n=='F_HY_input_prefix':continue
            parts=[]
            for s in r['parts']:
                if s['kind']=='spline':parts.extend(dict(kind='line',start=a,end=b) for a,b in zip(s['points'],s['points'][1:]) if a!=b)
                else:parts.append(s)
            rows[prefix+n]=dict(wire=prefix+n,OD_mm=2*(r['radius_mm'] if 'radius_mm' in r else r['radius']),segments=parts)
    for tag,keys in [('mta-interface',['factory_routes']),('main-source',['routes']),('s1-output',['routes']),
      ('source-receiving',['routes','factory_routes']),('leg-stations',['routes']),('bank-input',['routes']),('main-pi',['routes']),('front-gallery',['routes'])]:
        p=read(OUT/(tag+'-plan.json'))
        for k in keys:add(p[k])
        if tag=='leg-stations':add({'W026_FACTORY':p['factory_override']})
        if tag=='main-pi':rows.pop('W077_PREFIX',None)
    for folder,file in [('aux-wiring-checkpoint','whole-layout-plan.json'),('head-supply-checkpoint','coupled-plan.json'),
      ('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:add(read(BASE/folder/file)['routes'],folder+'/')
    for f in extra:add(read(f)['routes'])
    return rows,pins

def run():
    tick=time.monotonic();f=OUT/'ground-tree-plan.json';p=json.loads(f.read_text())
    rows,pins=route_rows();pins.update((Path(__file__),f))
    new=[dict(wire=n,OD_mm=2*r['radius_mm'],segments=r['parts']) for n,r in p['routes'].items()]
    for n in p['routes']:rows.pop(n,None)
    g=screen(dict(tails=list(rows.values()),s1_routes=new,holders=[]));names={r['wire'] for r in new}
    bad=[r for r in g['near_pairs'] if r['b'] in names and r['status']=='REJECT_PLANNING_PROXIMITY']
    g.update(status='REJECTED_SHARED_GROUND_PLAN_CHEAP' if bad else 'SHARED_GROUND_PROXIMITY_ONLY_ACTUAL_MATERIAL_OPEN',
      rejected=bad,worker_seconds=time.monotonic()-tick,selected=False,W5_complete=False,physical_pass=False,
      source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins})
    (OUT/'ground-tree-screen.json').write_text(json.dumps(g,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=g['status'],rejected=bad,seconds=g['worker_seconds'])))

if __name__=='__main__':run()

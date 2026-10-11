"""Twelve coupled input guides; candidate local holes, NOT native selection."""
import json,time,hashlib,sys
from pathlib import Path
from plan_current_bank_inputs import ROOT,OUT
BASE=OUT.parent
from open_prototype_path_preflight import screen

def preflight(p):
    old=[];new=[];pins=set()
    def parts(q):
        result=[]
        for s in q:
            if s['kind']=='spline':result.extend(dict(kind='line',start=a,end=b) for a,b in zip(s['points'],s['points'][1:]) if a!=b)
            else:result.append(s)
        return result
    for tag,keys in [('mta-interface',['factory_routes']),('main-source',['routes']),('s1-output',['routes']),('source-receiving',['routes','factory_routes']),('leg-stations',['routes'])]:
        f=OUT/(tag+'-plan.json');pins.add(f);v=json.loads(f.read_text())
        for key in keys:
            for n,r in v[key].items():
                if tag=='mta-interface' and n=='W026_FACTORY':continue
                (new if tag=='leg-stations' else old).append(dict(wire=n,OD_mm=2*r['radius_mm'],segments=r['parts']))
        if tag=='leg-stations' and v.get('factory_override'):
            r=v['factory_override'];new.append(dict(wire='W026_FACTORY',OD_mm=4.2,segments=r['parts']))
    for folder,file in [('aux-wiring-checkpoint','whole-layout-plan.json'),('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        f=BASE/folder/file;pins.add(f)
        for n,r in json.loads(f.read_text())['routes'].items():
            if 'reserved' not in n and n!='F_HY_input_prefix':old.append(dict(wire=folder+'/'+n,OD_mm=r['radius']*2,segments=parts(r['parts'])))
    new.extend(dict(wire=n,OD_mm=3.1,segments=r['parts']) for n,r in p['routes'].items())
    v=screen(dict(tails=old,s1_routes=new,holders=[]));names={r['wire'] for r in new}
    return [r for r in v['near_pairs'] if r['b'] in names and r['status']=='REJECT_PLANNING_PROXIMITY'],pins

def run():
    tick=time.monotonic();f=OUT/'bank-input-plan.json';p=json.loads(f.read_text())
    contacts,pins=preflight(p);pins.update((f,Path(__file__)))
    reader=None;r=dict(status='PENDING',selected=False,W5_complete=False,physical_pass=False,pairs=0,
      contacts=contacts,errors=[],native_parts_changed=0,
      scope='Twelve input curves against retained scene and each other. Foundation holes only temporary candidate BRep; native load path/selection/leg motion/full W5 remain OPEN.')
    def write(status):
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),
          source_sha256={**(reader.hashes if reader else {}),**{q.relative_to(ROOT).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in pins}})
        (OUT/'bank-input-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    if contacts:write('REJECTED_CHEAP_BANK_INPUT_FAN');return
    if '--screen-only' in sys.argv:write('BANK_INPUT_PROXIMITY_SCREEN_ONLY_NOT_BREP');return
    from current_leg_harness_context import context,W,Part
    from current_body_harness_context import clipped
    reader,more,targets,retained=context();pins.update(more)
    original=targets['Foundation'];cut=original
    for hole in p['required_foundation_passages']:
        x,y=hole['centre_xy_mm'];z0,z1=hole['z_range_mm']
        cut=cut.cut(Part.makeCylinder(hole['diameter_mm']/2,z1-z0,W.A.Vector(x,y,z0)))
    assert cut.isValid() and len(cut.Solids)==len(original.Solids)
    targets['Foundation']=cut
    r['candidate_removed_foundation_mm3']=original.Volume-cut.Volume
    removal=p['obsolete_side_attachment_removal'];name=removal['target'];original=targets[name]
    core=original.common(W.box(removal['protected_core_bounds_mm']));cut=original
    for box in removal['cut_bounds_mm']:cut=cut.cut(W.box(box))
    assert cut.isValid() and len(cut.Solids)==len(original.Solids) and not cut.check(True)
    assert abs(cut.common(core).Volume-core.Volume)<1e-5
    assert original.Volume-cut.Volume>0
    targets[name]=cut
    r['candidate_removed_obsolete_attachments_mm3']=original.Volume-cut.Volume
    r['board_carrier_core_unchanged']=True
    r['candidate_lower_carrier_solids']=len(cut.Solids)
    curves={n:W.makewire(v['parts']) for n,v in p['routes'].items()}
    def check(n,c,rr,m,t,rad=0):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,m);r['pairs']+=1;d,points,_=c.distToShape(t)
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,
          witness_mm=[list(v) for v in points[0]] if points else None))
    for n,c in curves.items():
        row=p['routes'][n];target=row['endpoints'][0].split('.')[0]
        for m,t in targets.items():
            if not t.Solids:continue
            cc=clipped(c,False,3) if m==row['native_terminal'] else clipped(c,True,3) if m==target else c
            check(n,cc,1.55,m,t)
        for m,(t,rad) in retained.items():check(n,c,1.55,m,t,rad)
        for m,t in curves.items():
            if m>n:check(n,c,1.55,m,t,1.55)
        print('Bank input',n,'contacts',len(r['contacts']),flush=True)
    if not r['contacts']:
        for yaw in (-15,0,15):
            for pitch in (-10,0,5):
                for m,t in W.F.H.head(reader,yaw,pitch).items():
                    if m!='Foundation' and t.Solids:
                        for n,c in curves.items():check(n,c,1.55,'head/'+m,t)
    write('TWELVE_BANK_INPUT_GUIDES_CANDIDATE_FRAME_CHANGES_ONLY_NATIVE_OPEN' if not r['contacts'] else 'REJECTED_BANK_INPUT_SHARED_LAYOUT')

if __name__=='__main__':run()

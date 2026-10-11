"""Only the coupled changed front allocation, with cached leg-stage poses."""
import itertools,json,time,zipfile
from pathlib import Path
from plan_current_front_gallery import ROOT,OUT,SHA
from open_prototype_path_preflight import screen
BASE=OUT.parent

def preflight(p):
    changed=set(p['routes']);old=[];pins=set()
    def load(f):pins.add(f);return json.loads(f.read_text())
    for tag,keys in [('mta-interface',['factory_routes']),('main-source',['routes']),('s1-output',['routes']),
      ('source-receiving',['routes','factory_routes']),('leg-stations',['routes']),('bank-input',['routes']),('main-pi',['routes'])]:
        q=load(OUT/(tag+'-plan.json'))
        for key in keys:
            for n,r in q[key].items():
                if n in changed or n in ('W026_FACTORY','W077_PREFIX'):continue
                old.append(dict(wire=n,OD_mm=2*r['radius_mm'],segments=r['parts']))
        if tag=='leg-stations':old.append(dict(wire='W026_FACTORY',OD_mm=4.2,segments=q['factory_override']['parts']))
    for folder,file in [('aux-wiring-checkpoint','whole-layout-plan.json'),('head-supply-checkpoint','coupled-plan.json'),
      ('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        for n,r in load(BASE/folder/file)['routes'].items():
            if 'reserved' in n or n=='F_HY_input_prefix':continue
            parts=[]
            for s in r['parts']:
                if s['kind']=='spline':parts.extend(dict(kind='line',start=a,end=b) for a,b in zip(s['points'],s['points'][1:]) if a!=b)
                else:parts.append(s)
            old.append(dict(wire=folder+'/'+n,OD_mm=2*r['radius'],segments=parts))
    new=[dict(wire=n,OD_mm=2*r['radius_mm'],segments=r['parts']) for n,r in p['routes'].items()]
    g=screen(dict(tails=old,s1_routes=new,holders=[]))
    return [r for r in g['near_pairs'] if r['b'] in changed and r['status']=='REJECT_PLANNING_PROXIMITY'],pins

def run():
    tick=time.monotonic();f=OUT/'front-gallery-plan.json';p=json.loads(f.read_text())
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    bad,pins=preflight(p);pins.update((f,Path(__file__)));reader=None
    r=dict(status='PENDING',pairs=0,contacts=bad,errors=[],selected=False,W5_complete=False,physical_pass=False,
      angle_grid_degrees=[-15,0,15],approved_motion_limits=False,continuous_sweep_verified=False,
      changed_cases=2,changed_curves=8,cached_leg_stage_poses=0,native_parts_changed=0)
    def save(status):
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={
          **(reader.hashes if reader else {}),**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins}})
        (OUT/'front-gallery-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)
    if bad:save('REJECTED_FRONT_GALLERY_CHEAP_SHARED_PLAN');return
    from current_leg_harness_context import context,W,Part
    from current_body_harness_context import clipped
    reader,more,targets,old=context();pins.update(more)
    bp=json.loads((OUT/'bank-input-plan.json').read_text());pins.add(OUT/'bank-input-plan.json')
    cut=targets['Foundation']
    for h in bp['required_foundation_passages']:
        x,y=h['centre_xy_mm'];z0,z1=h['z_range_mm'];cut=cut.cut(Part.makeCylinder(h['diameter_mm']/2,z1-z0,W.A.Vector(x,y,z0)))
    targets['Foundation']=cut;rem=bp['obsolete_side_attachment_removal'];cut=targets[rem['target']]
    for box in rem['cut_bounds_mm']:cut=cut.cut(W.box(box))
    targets[rem['target']]=cut
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in bp['routes'].items()})
    main=json.loads((OUT/'main-pi-plan.json').read_text());pins.add(OUT/'main-pi-plan.json')
    old.pop('W077_PREFIX',None);targets['F_PI_sleeve']=W.box(main['factory_custom_overlap']['sleeve_bounds_mm'])
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in main['routes'].items()})
    for n in p['routes']:old.pop(n,None)
    boxes={n:W.box(v['casing_mm']) for n,v in p['stations'].items()}
    targets.update(boxes);new={n:(W.makewire(v['parts']),v['radius_mm']) for n,v in p['routes'].items()}
    def pair(n,c,rr,m,t,rad=0,pose=None):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,m);r['pairs']+=1;d,points,_=c.distToShape(t)
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,pose=pose,
          witness_mm=[list(v) for v in points[0]] if points else None))
    def solid(n,s,m,t,pose=None):
        if not t.Solids or not W.near(s,t,0):return
        assert s.isValid() and t.isValid(),(n,m);r['pairs']+=1;v=s.common(t).Volume
        if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v,pose=pose))
    for n,s in boxes.items():
        for m,t in targets.items():
            if m!=n:solid(n,s,m,t)
        for m,(t,rad) in old.items():pair(m,t,rad,n,s)
    for n,(c,rr) in new.items():
        row=p['routes'][n];assigned=row.get('native_terminal');station=row.get('endpoints',[None])[0]
        for m,t in targets.items():
            if not t.Solids:continue
            cc=c
            if m==assigned:cc=clipped(c,False,3)
            elif station and m==station.split('.')[0]:cc=clipped(c,True,3)
            elif n in ('W026_CUSTOM','W037_CUSTOM') and m==('FL_P' if n=='W026_CUSTOM' else 'FR_P'):cc=clipped(c,False,3)
            elif m==n.removesuffix('_CUSTOM')+'_Joint':cc=clipped(c,True,min(3,c.Edges[0].Length))
            pair(n,cc,rr,m,t)
        for m,(t,rad) in old.items():pair(n,c,rr,m,t,rad)
        for m,(t,rad) in new.items():
            if m>n:pair(n,c,rr,m,t,rad)
        print('Front allocation',n,'contacts',len(r['contacts']),flush=True)
    if r['contacts']:save('REJECTED_FRONT_GALLERY_SHARED_MATERIAL');return
    # Baseline rejection proves unchanged10cases/8curves only. Test all
    # changed objects against unique articulated stage prefixes, not81
    # duplicate full-triple stages per leg. No new hardware limit claim.
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';archive=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text());pins.update((af,archive))
    with zipfile.ZipFile(archive) as z:geometry=json.loads(z.read('geometry.json'))
    for code in ('FL','FR','RL','RR'):
        ax={a['stage']:a for a in axes['axes'] if a['code']==code}
        for index,stage in enumerate(('Hip','Knee','Ankle')):
            names=['P0_'+q['name'] for q in geometry['components'] if q['stage']==f'Motion_{code}_{stage}']
            for angles in itertools.product(r['angle_grid_degrees'],repeat=index+1):
                transform=W.A.Placement();r['cached_leg_stage_poses']+=1
                for st,angle in zip(('Hip','Knee','Ankle'),angles):
                    a=ax[st];pivot=W.A.Vector(*a['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*a['axis']),angle)
                    transform=transform*W.A.Placement(pivot-rot.multVec(pivot),rot)
                for name in names:
                    t=targets[name].copy();t.Placement=transform*t.Placement;pose=dict(leg=code,stage=stage,angles=angles)
                    for n,s in boxes.items():solid(n,s,name,t,pose)
                    for n,(c,rr) in new.items():pair(n,c,rr,name,t,pose=pose)
            print('Front leg stage',code,stage,'contacts',len(r['contacts']),flush=True)
    for yaw in (-15,0,15):
        for pitch in (-10,0,5):
            for m,t in W.F.H.head(reader,yaw,pitch).items():
                if m=='Foundation' or not t.Solids:continue
                for n,s in boxes.items():solid(n,s,'head/'+m,t,dict(yaw=yaw,pitch=pitch))
                for n,(c,rr) in new.items():pair(n,c,rr,'head/'+m,t,pose=dict(yaw=yaw,pitch=pitch))
    save('COUPLED_FRONT_GALLERY_SAMPLED_CLEAR_NATIVE_OPEN' if not r['contacts'] else 'REJECTED_FRONT_GALLERY_SAMPLED_MOTION')

if __name__=='__main__':run()

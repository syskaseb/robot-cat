"""Shared seven-return gate; nominal purchased cases, actual retained BRep.

No native support acceptance. No bounding-box overlap is called contact.
"""
import itertools,json,time,zipfile
from pathlib import Path
from plan_current_ground_tree import ROOT,OUT,SHA
from screen_current_remaining_routes import route_rows
from open_prototype_path_preflight import screen

def run():
    tick=time.monotonic();f=OUT/'ground-tree-plan.json';p=json.loads(f.read_text())
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    rows,pins=route_rows();pins.update((Path(__file__),f))
    for n in p['routes']:rows.pop(n,None)
    newrows=[dict(wire=n,OD_mm=2*v['radius_mm'],segments=v['parts']) for n,v in p['routes'].items()]
    pre=screen(dict(tails=list(rows.values()),s1_routes=newrows,holders=[]))
    bad=[v for v in pre['near_pairs'] if v['b'] in p['routes'] and v['status']=='REJECT_PLANNING_PROXIMITY']
    assert not bad,bad
    from current_leg_harness_context import context,W,Part
    from current_body_harness_context import clipped
    reader,more,targets,old=context();pins.update(more)
    def load(tag):
        fp=OUT/(tag+'-plan.json');pins.add(fp);return json.loads(fp.read_text())
    bp=load('bank-input');cut=targets['Foundation']
    for h in bp['required_foundation_passages']:
        x,y=h['centre_xy_mm'];z0,z1=h['z_range_mm']
        cut=cut.cut(Part.makeCylinder(h['diameter_mm']/2,z1-z0,W.A.Vector(x,y,z0)))
    assert cut.isValid();targets['Foundation']=cut
    rem=bp['obsolete_side_attachment_removal'];cut=targets[rem['target']]
    for b in rem['cut_bounds_mm']:cut=cut.cut(W.box(b))
    assert cut.isValid() and not cut.check(True);targets[rem['target']]=cut
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in bp['routes'].items()})
    main=load('main-pi');old.pop('W077_PREFIX',None)
    targets['F_PI_sleeve']=W.box(main['factory_custom_overlap']['sleeve_bounds_mm'])
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in main['routes'].items()})
    front=load('front-gallery');targets.update({n:W.box(v['casing_mm']) for n,v in front['stations'].items()})
    old.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in front['routes'].items()})
    targets.update({n:W.box(v['casing_mm']) for n,v in p['rear_gallery'].items()})
    targets['FR_G']=W.box(p['front_ground_station']['casing_mm'])
    source=OUT.parent/'OpenPrototypePlan.FCStd'
    for n in ('XT60_CP2','F0_CP2','PostF0Splice_CP2'):
        assert n not in targets,'Unexpected duplicate source alias: '+n
        targets[n]=reader.shape(source,n)
    # plan_current_pwm_east.context deliberately excludes all historical
    # WAGO aliases from its common physical scene. The current full G1
    # reservation must be added here, not silently assumed present.
    assert not any(n.startswith('G1') for n in targets),'Unexpected G1 alias needs explicit supersession'
    targets['G1_CP2']=W.box(p['G1']['casing_mm'])
    for n in p['routes']:old.pop(n,None)
    new={n:(W.makewire(v['parts']),v['radius_mm']) for n,v in p['routes'].items()}
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,W5_complete=False,physical_pass=False,
      native_parts_changed=0,cached_leg_stage_poses=0,angle_grid_degrees=[-15,0,15],approved_motion_limits=False,
      continuous_sweep_verified=False,G1_case_basis='Nominal37x11x22 UP-oriented purchased reservation; delivered lever/body fit gate',
      superseded_partial_interface='MAIN/Pi W060 only; W1 unchanged',removed_targets=[],
      G1_scene_binding='Historical WAGO excluded by base physical context; one new G1_CP2 reservation explicitly installed')
    def save(status):
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={
          **reader.hashes,**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins}})
        (OUT/'ground-tree-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    def pair(n,c,rr,m,t,rad=0,pose=None):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,m);r['pairs']+=1;d,points,_=c.distToShape(t)
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,pose=pose,
          witness_mm=[list(v) for v in points[0]] if points else None))
    def solid(n,s,m,t,pose=None):
        if not t.Solids or not W.near(s,t,0):return
        assert s.isValid() and t.isValid(),(n,m);r['pairs']+=1;hit=s.common(t);assert hit.isValid()
        if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,pose=pose))
    boxes={n:targets[n] for n in ('G1_CP2','FR_G',*p['rear_gallery'])}
    r['source_bounds_mm']={n:[getattr(targets[n].BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
      for n in ('XT60_CP2','F0_CP2','PostF0Splice_CP2')}
    for n,case in boxes.items():
        for m,t in targets.items():
            if m!=n:solid(n,case,m,t)
        for m,(t,rad) in old.items():pair(m,t,rad,n,case)
    for n,(c,rr) in new.items():
        roles=p['routes'][n]['endpoints']
        for m,t in targets.items():
            if not t.Solids:continue
            cc=c
            for first,role in ((True,roles[0]),(False,roles[-1])):
                station=role.split('.')[0]
                assigned='G1_CP2' if station=='G1' else 'G2_CP2' if station=='G2' else 'XT60_CP2' if station=='BAT' else station
                if m==assigned or assigned=='G2_CP2' and m=='W1Ref_G2_CP2':
                    cc=clipped(cc,first,min(3,(cc.Edges[0] if first else cc.Edges[-1]).Length))
            pair(n,cc,rr,m,t)
        for m,(t,rad) in old.items():pair(n,c,rr,m,t,rad)
        for m,(t,rad) in new.items():
            if m>n:pair(n,c,rr,m,t,rad)
        print('Ground return',n,'contacts',len(r['contacts']),flush=True)
    if r['contacts']:save('REJECTED_GROUND_TREE_SHARED_MATERIAL');return
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
                    for n,case in boxes.items():solid(n,case,name,t,pose)
                    for n,(c,rr) in new.items():pair(n,c,rr,name,t,pose=pose)
            print('Ground leg stage',code,stage,'contacts',len(r['contacts']),flush=True)
    for yaw in (-15,0,15):
        for pitch in (-10,0,5):
            for m,t in W.F.H.head(reader,yaw,pitch).items():
                if m=='Foundation' or not t.Solids:continue
                for n,case in boxes.items():solid(n,case,'head/'+m,t,dict(yaw=yaw,pitch=pitch))
                for n,(c,rr) in new.items():pair(n,c,rr,'head/'+m,t,pose=dict(yaw=yaw,pitch=pitch))
    save('COUPLED_GROUND_TREE_SAMPLED_CLEAR_NATIVE_OPEN' if not r['contacts'] else 'REJECTED_GROUND_TREE_SAMPLED_MOTION')

if __name__=='__main__':run()

"""Motion/tools, then one native eight-part lower power-station mount set."""
import itertools,json,time,zipfile,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
import plan_low_power_station_mounts as P
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect,circle
from build_u1_grouped_grips import validate
ROOT,BASE,OUT,SHA=P.ROOT,P.BASE,P.OUT,P.SHA

def run():
    tick=time.monotonic();pf=OUT/'low-power-station-mounts-plan.json';p=json.loads(pf.read_text())
    assert p['status']=='LOW_POWER_STATION_MOUNT_STATIC_CLEAR_MOTION_NATIVE_OPEN'
    assert not p['contacts'] and not p['errors']
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    targets,curves,archive=P.scene();parts,hardware,recipe=P.allocate(targets)
    assert recipe['pads']==p['pads'] and recipe['stations']==p['stations']
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    zf=ROOT/'hardware/simulation/v35/inputs.zip';axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={code:{stage:[] for stage in ('Hip','Knee','Ankle')} for code in ('FL','FR','RL','RR')}
    for row in members:
        if row['stage'].startswith('Motion_'):
            _,code,stage=row['stage'].split('_');membership[code][stage].append('P0_'+row['name'])
    fixed={**parts,**hardware,**{n:targets[n] for n in ('FL_P','FR_P','RL_P','RR_P')}}
    report=dict(contacts=[],errors=[],pairs=0,poses=0,tools=0)
    def collide(n,s,m,t):
        if not P.W.near(s,t,.001):return
        report['pairs']+=1
        if not s.isValid() or not t.isValid():report['errors'].append([n,m]);return
        if s.distToShape(t)[0]<1e-5:
            v=s.common(t).Volume
            if v>1e-5:report['contacts'].append(dict(a=n,b=m,volume_mm3=v))
    for code,groups in membership.items():
        axis={v['stage']:v for v in axes if v['code']==code}
        for angles in itertools.product((-15,0,15),repeat=3):
            T=A.Placement();report['poses']+=1
            for stage,angle in zip(('Hip','Knee','Ankle'),angles):
                ax=axis[stage];pv=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),angle)
                T=T*A.Placement(pv-rot.multVec(pv),rot)
                for name in groups[stage]:
                    s=targets[name].copy();s.Placement=T*s.Placement
                    for n,t in fixed.items():collide(code+str(angles)+'/'+name,s,n,t)
        print('moving leg checked',code,'contacts',len(report['contacts']),flush=True)
    # Open top driver and thin-wall nut driver below: project tool budgets.
    # Cavity contains the own nut/bolt. It does not waive adjacent hardware.
    for st in p['stations']:
        for idx,(x,y) in enumerate(st['clamp_axes_mm']):
            for role,s in [('TopDriver',Part.makeCylinder(2,25,A.Vector(x,y,47.02))),
                ('LowerNutDriver',Part.makeCylinder(4,20,A.Vector(x,y,-25.6)).cut(Part.makeCylinder(3.25,20.2,A.Vector(x,y,-25.7))))]:
                report['tools']+=1
                for n,t in {**targets,**fixed}.items():
                    if t.Solids:collide(st['name']+str(idx)+role,s,n,t)
    receipt={**report,'status':'REJECTED_LOW_POWER_MOUNT_MOTION_OR_TOOL' if report['contacts'] or report['errors'] else 'LOW_POWER_MOUNT_MOTION_TOOL_CLEAR_NATIVE_PENDING',
             'project_pose_grid_deg':[-15,0,15],'continuous_motion_proved':False,
             'approved_motion_limits':False,'native_changed':False,'selected':False,'W5_complete':False,'physical_pass':False,
             'source_sha256':{f.relative_to(ROOT).as_posix():SHA(f) for f in (pf,af,zf,Path(__file__))},
             'worker_seconds':round(time.monotonic()-tick,3)}
    rf=OUT/'low-power-station-mounts-checks.json';rf.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    if report['contacts'] or report['errors']:
        print(json.dumps({k:v for k,v in receipt.items() if k!='source_sha256'}),flush=True);return
    model=OUT/'LowPowerStationMountsCurrent.FCStd';assert not model.exists(),'Receive existing native, do not overwrite'
    d=A.newDocument('LowPowerStationMountsCurrent');par=d.addObject('App::VarSet','MountParameters')
    par.addProperty('App::PropertyLength','TopClampThickness');par.TopClampThickness=5
    volumes={};bodies=[]
    for owner in dict.fromkeys(v['owner'] for v in p['pads']):
        b=d.addObject('PartDesign::Body',owner);bodies.append(b)
        for row in (v for v in p['pads'] if v['owner']==owner):
            x,y,z,X,Y,Z=row['bounds_mm'];old=b.Tip
            sk=sketch(b,owner+row['name']+'Plan',z);rect(sk,x,y,X-x,Y-y)
            ob=b.newObject('PartDesign::Pad',owner+row['name']);ob.Profile=sk
            if old:ob.BaseFeature=old
            if owner.endswith('TopClamp'):ob.setExpression('Length','MountParameters.TopClampThickness')
            else:ob.Length=Z-z
            ob.Refine=True;b.Tip=ob;d.recompute();sk.Visibility=False
            if old:old.Visibility=False
        old=b.Tip;sk=sketch(b,owner+'BoltAxes',50)
        st=next(v for v in p['stations'] if owner.startswith(v['name'][:2]))
        for x,y in st['clamp_axes_mm']:circle(sk,x,y,3.4)
        ob=b.newObject('PartDesign::Pocket',owner+'BoltBores');ob.Profile=sk;ob.BaseFeature=old
        ob.Length=65;ob.Refine=True;b.Tip=ob;d.recompute();old.Visibility=False;sk.Visibility=False
        validate(b);s=parts[owner]
        assert b.Shape.cut(s).Volume<1e-5 and s.cut(b.Shape).Volume<1e-5,owner
        volumes[owner]=b.Shape.Volume
        print('native',owner,flush=True)
    refs={**hardware,**{n:s for n,s in parts.items() if n.endswith('Bond')},
          **{n:targets[n] for n in ('FL_P','FR_P','RL_P','RR_P')}}
    for name,s in refs.items():
        o=d.addObject('Part::Feature','Ref_'+name.replace('-','minus'));o.Label=name;o.Shape=s
        o.addProperty('App::PropertyString','Evidence');o.Evidence='Project assembly envelope; delivered fit/material/tool in phase2'
        if 'Bolt' in name or 'UpperWasher' in name:o.setExpression('Placement.Base.z','MountParameters.TopClampThickness - 5 mm')
    par.TopClampThickness=5.2;d.recompute()
    for b in bodies:
        validate(b)
        if b.Name.endswith('TopClamp'):assert b.Shape.Volume>volumes[b.Name]
    for o in d.Objects:
        if o.Name.startswith('Ref_') and ('Bolt' in o.Label or 'UpperWasher' in o.Label):assert abs(o.Placement.Base.z-.2)<1e-7
    par.TopClampThickness=5;d.recompute()
    for b in bodies:assert abs(b.Shape.Volume-volumes[b.Name])<1e-5
    d.saveAs(str(model));A.closeDocument(d.Name);exports=[]
    with tempfile.TemporaryDirectory(prefix='robot-cat-low-stations-') as td:
        dest=Path(td)/model.name;shutil.copy2(model,dest);d=A.openDocument(str(dest));d.recompute()
        for name,v in volumes.items():
            b=d.getObject(name);validate(b);assert abs(b.Shape.Volume-v)<1e-5
            s=b.Shape.copy();bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
            f=OUT/(name+'_x1.stl');mesh.write(str(f));exports.append(dict(part=name,path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),size_mm=size,quantity=1,brim_each_mm=5))
        A.closeDocument(d.Name)
    receipt.update(status='FOUR_LOW_POWER_STATIONS_NATIVE_MOUNTS_PREPARED',native=model.relative_to(ROOT).as_posix(),native_sha256=SHA(model),
        native_changed=True,editable_parts=8,fully_constrained_sketches=36,exports=exports,parameter_restore_mm=[5,5.2,5],relocated_reopen=True,
        print_orientation='Broad jaw/ledge floor down, local elevated back wall/curbs up. Phase2 support/profile/coupon and PETG creep gates; no slicer approval.',
        hardware_nominal=p['hardware_nominal'],assembly=p['stations'],provisional=p['provisional'],remaining=p['remaining'],
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'low-power-station-mounts-native.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('status','pairs','poses','tools','editable_parts','worker_seconds')}),flush=True)

if __name__=='__main__':run()

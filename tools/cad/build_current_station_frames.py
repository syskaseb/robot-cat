"""Verify changed station supports in motion, then build one editable set.

Foundation is an explicitly inherited saved base with editable new supports;
it replaces ONE current Foundation on future selection, never duplicates it.
All hardware/adhesion/tool budgets remain provisional delivered-fit gates.
"""
import itertools,json,time,zipfile,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
import plan_current_data_ground_mounts as P
import plan_current_head_wiring as H
from immutable_bounds import ImmutableBounds
from exact_pair_receipts import PairReceipts
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect,circle
from build_u1_grouped_grips import validate
ROOT,BASE,OUT,SHA=P.ROOT,P.BASE,P.OUT,P.SHA


def run():
    tick=time.monotonic();pf=OUT/'data-ground-mounts-plan.json';p=json.loads(pf.read_text())
    assert p['status']=='DATA_GROUND_MOUNTS_STATIC_TOOL_CLEAR_MOTION_NATIVE_OPEN'
    assert not p['contacts'] and not p['errors']
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    targets,curves,archive=P.P.scene();parts,hardware,bonds,recipe=P.allocate(targets)
    assert recipe['pads']==p['pads'] and recipe['clamps']==p['clamps'] and recipe['foundation_bearings']==p['foundation_bearings']
    additions={n:s.cut(targets['Foundation']) if n=='FoundationStationSupports' else s for n,s in parts.items()}
    fixed={**additions,**hardware,**bonds}
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';zf=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={code:{stage:[] for stage in ('Hip','Knee','Ankle')} for code in ('FL','FR','RL','RR')}
    for row in members:
        if row['stage'].startswith('Motion_'):
            _,code,stage=row['stage'].split('_');membership[code][stage].append('P0_'+row['name'])
    bounds=ImmutableBounds();cache=PairReceipts(OUT/'station-frames-pair-cache.json',bounds.near);seen=set()
    report=dict(contacts=[],errors=[],pairs=0,leg_poses=0,head_poses=0,joint_sections=0,candidate_joint_conflicts=[],candidate_joint_errors=[])
    def check(n,s,m,t,rad=0):
        if not bounds.near(s,t,rad+.001):return
        key=(id(s),id(t),rad)
        if key in seen:return
        seen.add(key);report['pairs']+=1
        try:gap,volume=cache.check(s,t,0,rad)
        except (AssertionError,ValueError) as e:report['errors'].append([n,m,str(e)]);return
        if volume>1e-5 or gap<rad-1e-4:report['contacts'].append(dict(a=n,b=m,volume_mm3=volume,gap_mm=gap,required_mm=rad))
    # Keep moved shapes alive: id-based within-run de-duplication is otherwise
    # unsafe when Python recycles objects from earlier poses.
    memo={}
    for code,groups in membership.items():
        axis={r['stage']:r for r in axes if r['code']==code}
        for angles in itertools.product((-15,0,15),repeat=3):
            T=A.Placement();report['leg_poses']+=1
            for stage,angle in zip(('Hip','Knee','Ankle'),angles):
                ax=axis[stage];pv=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),angle)
                T=T*A.Placement(pv-rot.multVec(pv),rot)
                for name in groups[stage]:
                    key=(name,angles[:('Hip','Knee','Ankle').index(stage)+1])
                    if key not in memo:
                        s=targets[name].copy();s.Placement=T*s.Placement;memo[key]=s
                    for n,t in fixed.items():check(code+str(angles)+'/'+name,memo[key],n,t)
            if report['contacts'] or report['errors']:break
        cache.save();print('station motion',code,'poses',report['leg_poses'],'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True)
        if report['contacts'] or report['errors']:break
    # Do not spend another 108 checks on a known-unusable UNSELECTED family.
    # Full factory/body joins already failed; new supports must inform a new
    # complete wiring plan. This scope earns no cable or W5 clearance/points.
    report['unselected_joint_scope']='Not checked: full factory/body joins rejected. Prior disconnected-section clearance is NOT transferred to these new supports. Complete current wiring remains OPEN.'
    reader=H.P.SavedShapes()
    if not report['contacts'] and not report['errors']:
        for yaw,pitch in itertools.product((-15,0,15),(-10,0,5)):
            report['head_poses']+=1
            for name,s in H.head(reader,yaw,pitch).items():
                memo['head',yaw,pitch,name]=s
                for n,t in fixed.items():check('head'+str((yaw,pitch))+name,s,n,t)
        cache.save();print('head poses',report['head_poses'],'contacts',len(report['contacts']),flush=True)
    receipt={**report,'status':'REJECTED_CURRENT_STATION_SUPPORT_MOTION' if report['contacts'] or report['errors'] else 'CURRENT_STATION_SUPPORT_MOTION_CLEAR_NATIVE_PENDING',
        'scope':'Changed5station supports/hardware/bonds vs retained P0 leg27poses each and52head members9poses. Rejected unselected joint-cable family explicitly excluded, no clearance or W5 qualification transferred.',
        'continuous_sweep_verified':False,'selected':False,'W5_complete':False,'physical_pass':False,
        'source_sha256':{**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in (pf,af,zf,archive,Path(__file__),Path(P.__file__),Path(H.__file__),Path(__file__).with_name('exact_pair_receipts.py'),Path(__file__).with_name('immutable_bounds.py'))}},
        'worker_seconds':round(time.monotonic()-tick,3)}
    (OUT/'station-frames-motion.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    if report['contacts'] or report['errors']:
        print(json.dumps({k:receipt[k] for k in ('status','contacts','errors','worker_seconds')}),flush=True);return
    model=OUT/'StationFramesCurrent.FCStd';assert not model.exists(),'Receive existing native, do not overwrite'
    d=A.newDocument('StationFramesCurrent');par=d.addObject('App::VarSet','StationParameters')
    par.addProperty('App::PropertyLength','CaseBackHeight');par.CaseBackHeight=5.5
    volumes={};bodies=[]
    for owner,s in parts.items():
        b=d.addObject('PartDesign::Body',owner);bodies.append(b)
        if owner in p['inherited_base']:
            ob=b.newObject('PartDesign::Feature',owner+'InheritedCurrentBase');ob.Shape=targets[p['inherited_base'][owner]]
            ob.addProperty('App::PropertyString','Source');ob.Source='Immutable current archive Foundation, world pose already applied; only new supports editable here'
            b.Tip=ob;d.recompute()
        for row in (r for r in p['pads'] if r['owner']==owner):
            x,y,z,X,Y,Z=row['bounds_mm'];old=b.Tip;n=owner+row['name']
            sk=sketch(b,n+'Plan',z);rect(sk,x,y,X-x,Y-y)
            ob=b.newObject('PartDesign::Pad',n);ob.Profile=sk
            if old:ob.BaseFeature=old
            if row['name'].endswith('LowBack'):ob.setExpression('Length','StationParameters.CaseBackHeight + 3.25 mm')
            else:ob.Length=Z-z
            ob.Refine=True;b.Tip=ob;d.recompute();sk.Visibility=False
            if old:old.Visibility=False
        if owner not in p['inherited_base']:
            old=b.Tip;sk=sketch(b,owner+'ActualBossAxis',15)
            st=next(r for r in p['clamps'] if r['owner']==owner)
            for x,y in st['bolt_axes_mm']:circle(sk,x,y,3.4)
            ob=b.newObject('PartDesign::Pocket',owner+'ActualM3Bore');ob.Profile=sk;ob.BaseFeature=old
            ob.Length=30;ob.Refine=True;b.Tip=ob;d.recompute();old.Visibility=False;sk.Visibility=False
        validate(b)
        assert b.Shape.cut(s).Volume<1e-5 and s.cut(b.Shape).Volume<1e-5,owner
        volumes[owner]=b.Shape.Volume;print('native station',owner,flush=True)
    for name,s in {**hardware,**bonds,**{r['name']:targets[r['name']] for r in p['stations']}}.items():
        ob=d.addObject('Part::Feature','Ref_'+name);ob.Label=name;ob.Shape=s
        ob.addProperty('App::PropertyString','Evidence');ob.Evidence='Current casing or provisional hardware/bond allocation, delivered fit/material remain phase2 gates'
    par.CaseBackHeight=5.7;d.recompute()
    for b in bodies:validate(b);assert b.Shape.Volume>volumes[b.Name],b.Name
    par.CaseBackHeight=5.5;d.recompute()
    for b in bodies:validate(b);assert abs(b.Shape.Volume-volumes[b.Name])<1e-5
    sketches=sum(o.TypeId=='Sketcher::SketchObject' for o in d.Objects)
    d.saveAs(str(model));A.closeDocument(d.Name);exports=[]
    with tempfile.TemporaryDirectory(prefix='robot-cat-station-frames-') as td:
        copy=Path(td)/model.name;shutil.copy2(model,copy);d=A.openDocument(str(copy));d.recompute()
        for name,v in volumes.items():
            b=d.getObject(name);validate(b);assert abs(b.Shape.Volume-v)<1e-5
            s=b.Shape.copy()
            if name!='FoundationStationSupports':s.rotate(A.Vector(),A.Vector(1,0,0),90)
            bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
            f=OUT/(name+'_x1.stl');mesh.write(str(f));exports.append(dict(part=name,path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),size_mm=size,quantity=1,brim_each_mm=5))
        A.closeDocument(d.Name)
    receipt.update(status='TWELVE_STATION_ROOTED_SUPPORTS_NATIVE_PREPARED_W5_OPEN',native=model.relative_to(ROOT).as_posix(),native_sha256=SHA(model),exports=exports,
        editable_parts=5,fully_constrained_sketches=sketches,parameter_restore_mm=[5.5,5.7,5.5],relocated_reopen=True,
        inherited_geometry='Exactly one retained Foundation base, all original material kept. New support pads/sketches editable; old base is explicitly inherited, not claimed fully migrated.',
        replaces_unselected_low_power_mounts=True,hardware_nominal=p['hardware_nominal'],assembly=p['assembly'],provisional=p['provisional'],open=p['open'],
        print_orientation='Foundation: retained floor down. Other4frames: broad side down, support seat bridges as required. Phase2 slicer/coupon/stiffness/creep/adhesion tests open.',
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'station-frames-native.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('status','editable_parts','fully_constrained_sketches','leg_poses','joint_sections','head_poses','worker_seconds')}),flush=True)


if __name__=='__main__':run()

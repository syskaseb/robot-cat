"""One current CP2 head/neck interface screen; retained internals are not rerun."""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, time, math
sys.path.insert(0, str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, prop, sha

BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'head-mount-checkpoint'
HEAD=ROOT/'hardware/cad/studies/head-p8/head-printed-horns-r2/HeadPrintedPitchYawR2_CANDIDATE.FCStd'
MOUNT=BASE/'mounting-checkpoint/RetentionMountsAssembly.FCStd'
SHIFT=A.Vector(-42,0,25)
PITCH=set(('FrontLeft','FrontRightPorted','Rear','Nose','EarL','EarR','PassiveJournal',
           'CageBase','CageRetainerLeft','CageRetainerRight','HornProvisional',
           'Insert_left','Insert_right','M2x14_shaft_left','M2x14_shaft_right',
           'M2_head_left','M2_head_right','UpperScrewL','UpperNutL','UpperScrewR',
           'UpperNutR','NoseScrewL','NoseScrewR','NoseInsertL','NoseInsertR'))
FIXED=set(('Foundation','YawCarrier','YawServoReference','Bridge','ClampPositiveX',
           'ClampNegativeX','ClampWasher0','ClampBolt0','ClampNut0',
           'ClampWasher1','ClampBolt1','ClampNut1'))

def flatten(reader,path,name,pose=None,prefix=''):
    """Group poses are composed once; leaf BReps already own their placement."""
    pose=pose or A.Placement();o=reader.doc(path)[name]
    link=prop(o,'LinkedObject');group=prop(o,'Group')
    if link is not None and link[0].get('name'):
        x=link[0];source=(path.parent/x.get('file')).resolve() if x.get('file') else path
        target=reader.doc(source)[x.get('name')]
        if prop(target,'Group') is not None and prop(target,'Tip') is None:
            lp=reader.placement(o,'LinkPlacement')
            keep=prop(o,'LinkTransform')[0].get('value')=='true'
            adjustment=lp if keep else lp*reader.placement(target).inverse()
            return flatten(reader,source,x.get('name'),pose*adjustment,prefix)
    if group is not None and prop(o,'Tip') is None:
        result={};gp=pose*reader.placement(o)
        for c in group.findall('.//Link'):
            n=c.get('value');child=flatten(reader,path,n,gp,prefix)
            for key,val in child.items():
                assert key not in result,('duplicate physical leaf',key)
                result[key]=val
        return result
    s=reader.shape(path,name);s.Placement=pose*s.Placement
    assert s.isValid() and s.Solids,(path,name)
    return {prefix+name:(s,path,name)}

def moved(shape,name,pitch,yaw):
    s=shape.copy()
    if name in PITCH:s.rotate(A.Vector(-152,0,136),A.Vector(0,1,0),pitch)
    if name not in FIXED:s.rotate(A.Vector(-110,-5.25,0),A.Vector(0,0,1),yaw)
    s.translate(SHIFT);return s

def bbox(s):
    b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]

def run():
    OUT.mkdir(exist_ok=True);dest=OUT/'preflight.json'
    assert not dest.exists(),'Do not repeat unchanged qualification'
    tick=time.monotonic();r=SavedShapes();parts=flatten(r,HEAD,'HeadNoseInsertUnit')
    # Current R53 replacements are in the original world frame, not a box
    # approximation and not the older chain's obsolete wire-support prints.
    replacements={
      'FrontRightPorted':('hardware/cad/studies/head-external-wire-support-r1/FrontRightWirePassage.FCStd','WireInterface0'),
      'Fork':('hardware/cad/studies/head-yaw-end-restraints-r2/ForkYawEndSeatSplices.brep',None),
      'YawCarrier':('hardware/cad/studies/head-fixed-yaw-feed-r3/YawCarrierJRSeat.brep',None),
      'Carrier':('hardware/cad/studies/head-jr-support-r5/PitchCarrierThroughLeadExit.brep',None)}
    pins={};changes=[]
    for name,(rel,obj) in replacements.items():
        p=ROOT/rel;s=r.shape(p,obj) if obj else Part.read(str(p));pins[rel]=sha(p)
        assert name in parts and s.isValid() and len(s.Solids)==1,name
        before=parts[name][0]
        changes.append(dict(name=name,old_bounds=bbox(before),current_bounds=bbox(s)))
        parts[name]=(s,p,obj)
    ctx=BASE/'OpenPrototypePlan.FCStd';external={}
    for name in r.doc(ctx):
        if name.startswith('P0_') and not any(t in name for t in ('Tail','MG92B','Power','Battery')):
            o=r.doc(ctx)[name]
            if prop(o,'Shape') is not None:external[name]=r.shape(ctx,name)
    neck_master=BASE/'mounting-checkpoint/Mounts.FCStd'
    for name in ('LeftRiser','RightRiser','MainSupplierFamily'):
        external[name]=r.shape(neck_master,name)
    for name in ('LowerCarrier','UpperCarrier','Spacer1','Spacer2','Spacer3','Spacer4'):
        external[name]=r.shape(MOUNT,name)
    # The later matched carriers supersede these two saved mounting bodies.
    tail=BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd'
    data=BASE/'wiring-checkpoint/DataShelfCurrent.FCStd'
    external['LowerCarrier']=r.shape(tail,'LowerCarrier')
    external['UpperCarrier']=r.shape(data,'UpperCarrier')
    # Eight real nominal neck stacks, retained verified side-loading sequence.
    for y in (22.5,-22.5):
      for ax in (-80,-70):
       for role,x,z,L,nz,wz in [('lower',ax,35.22,10,42.82,42.52),('upper',ax-42,71.82,12,61.62,63.22)]:
        sign=1 if role=='lower' else -1;key=f'Neck_{y}_{ax}_{role}'
        external[key+'_bolt']=Part.makeCylinder(1,L,A.Vector(x,y,z),A.Vector(0,0,sign)).fuse(Part.makeCylinder(1.9,2,A.Vector(x,y,z),A.Vector(0,0,-sign)))
        external[key+'_washer']=Part.makeCylinder(2.5,.3,A.Vector(x,y,wz)).cut(Part.makeCylinder(1.1,.3,A.Vector(x,y,wz)))
        external[key+'_nut']=Part.makeCylinder(4/math.sqrt(3),1.6,A.Vector(x,y,nz)).cut(Part.makeCylinder(1,1.6,A.Vector(x,y,nz)))
    report=dict(status='PENDING',selected=False,physical_pass=False,complete_M2=False,
        scope='All retained physical head leaves at CP2 pose vs changed neck, MAIN, frame and current carriers; unchanged internal motion evidence reused separately',
        head_shift_mm=list(SHIFT),parts={n:dict(source=p.relative_to(ROOT).as_posix(),object=o,bounds=bbox(s),pitch=n in PITCH,yaw=n not in FIXED) for n,(s,p,o) in parts.items()},
        replacement_frames=changes,contacts=[],errors=[],pairs=0,samples=[],fixed=list(external))
    for pitch in (-10,0,5):
      for yaw in (-15,0,15):
        for name,(source,_,_) in parts.items():
          s=moved(source,name,pitch,yaw)
          for other,t in external.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            report['pairs']+=1
            assert s.isValid() and t.isValid(),(name,other,'invalid input')
            volume=0
            for a in s.Solids:
              for b in t.Solids:
                c=a.common(b)
                if not c.isNull():assert c.isValid();volume+=c.Volume
            if volume>1e-5:report['contacts'].append(dict(head=name,other=other,pitch=pitch,yaw=yaw,volume_mm3=volume))
        report['samples'].append([pitch,yaw]);print('head CP2',pitch,yaw,'pairs',report['pairs'],'hits',len(report['contacts']),flush=True)
    pins.update(r.hashes);pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    assert all(sha(ROOT/n)==h for n,h in pins.items())
    report.update(status='CURRENT_HEAD_EXTERNAL_INTERFACES_CLEAR' if not report['contacts'] else 'REJECTED_CURRENT_HEAD_EXTERNAL_INTERFACES',source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','pairs','worker_seconds')}),flush=True)

if __name__=='__main__':run()

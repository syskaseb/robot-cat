"""Build the changed head wire interfaces; preserve all selected parent files.

Not a complete harness: end transitions, JR storage and fixed-side supports
must be completed before this candidate can replace the selected parts.
"""
import sys,json,hashlib
from pathlib import Path
import FreeCAD as A,Part,MeshPart
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
import xb11_upstream_route as R
from head_external_yaw_loop_r2 import path
from head_external_yaw_loop_r1 import mv
OUT=ROOT/'hardware/cad/studies/head-external-wire-support-r1'
CACHE=ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def load(n):s=Part.Shape();s.read(str(CACHE/(n+'_REST.brep')));return s
def native(name,source,boxes,operation):
    d=A.newDocument(name);base=d.addObject('PartDesign::Feature','PinnedParent');base.Shape=source
    previous=base
    for i,b in enumerate(boxes):
        if isinstance(b,dict):
            tool=d.addObject('Part::Cylinder','WireInterfaceTool'+str(i));tool.Radius=b['radius'];tool.Height=b['length'];tool.Placement=A.Placement(A.Vector(*b['origin']),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
        else:
            tool=d.addObject('Part::Box','WireInterfaceTool'+str(i));tool.Length=b[3]-b[0];tool.Width=b[4]-b[1];tool.Height=b[5]-b[2];tool.Placement.Base=A.Vector(*b[:3])
        f=d.addObject('Part::'+operation,'WireInterface'+str(i))
        if operation=='Cut':f.Base=previous;f.Tool=tool;f.Refine=False
        else:f.Shapes=[previous,tool]
        # MultiFuse uses Shapes, not Base/Tool.
        d.recompute();previous.Visibility=False;tool.Visibility=False;previous=f
    d.recompute();d.saveAs(str(OUT/(name+'.FCStd')))
    s=previous.Shape.copy();assert s.isValid() and len(s.Solids)==1
    try:s.check(True)
    except ValueError as error:
        if name!='FrontRightWirePassage':raise
        s.exportBrep(str(OUT/(name+'_REJECTED.brep')))
        A.closeDocument(d.Name)
        return s,dict(status='REJECTED_NO_STL',strict_bop_error=str(error),valid=True,single_solid=True)
    s.exportBrep(str(OUT/(name+'.brep')))
    if name=='UpperForkWireArm':
        A.closeDocument(d.Name);return s,dict(volume_mm3=s.Volume,added_mm3=s.cut(source).Volume,intermediate_no_stl=True)
    m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    # Fork broad side on bed; front and cover keep the inherited design axes.
    if name=='UpperForkWireArmSlotted':m.transform(A.Placement(A.Vector(),A.Rotation(A.Vector(0,1,0),90)).toMatrix())
    bb=m.BoundBox;m.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
    m.write(str(OUT/(name+'_candidate_x1.stl')))
    assert m.isSolid() and m.countComponents()==1
    dims=[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength];assert max(dims)+10<256
    result=dict(fcstd_sha256=sha(OUT/(name+'.FCStd')),volume_mm3=s.Volume,added_mm3=s.cut(source).Volume,removed_mm3=source.cut(s).Volume,stl_dimensions_mm=dims,closed=True,components=1)
    A.closeDocument(d.Name);return s,result
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    arm=[-136,8,122,-130,63,126];root=[-136,2,121,-130,8,126]
    frontwindow=dict(radius=12,length=21,origin=[-134,44,123],axis='+Y')
    coverwindow=[-94,92,120.5,-56,104,127.5]
    dump('plan.json',dict(status='SOURCE_BEFORE_NATIVE_CONSTRUCTION',arm_bbox=arm,root_bbox=root,front_window=frontwindow,cover_window=coverwindow,
      loop_z_mm=124,cover_bolt_axis_mm=[-84,91,116],cover_bolt_land_requirement_mm=3,
      purpose='Raise outside loop5mm to preserve cover bolt land. Integral fork outrigger and round lower rear front-right passage only; unchanged ears/P0. Rectangular cut rejected after InvalidCurveOnSurface; refinement/healing/fuzzy1e-4 did not repair it.',
      print='Three replacement candidates x1 PETG each; Fork broad side, front/cover inherited orientation to be checked in phase2; brim5 fits256. Not yet selected.',
      wiring='Pitch factory JR250mm preserved. Two HELU0.5mm2 OD2.1 plus Kamami1178401 PWM0.12mm2 OD1.25, design bundleOD5/movingR31.5. No cable through journal or strap slot.',
      assembly='Fit bare fork and front relief before servo. Existing cover screw retained. End restraints/JR adapter and fixed support not completed; do not approve full assembly.',
      planned_replacements=3,new_fasteners=0,physical_pass=False,phase1_complete=False,
      parents_sha256={n:sha(CACHE/(n+'_REST.brep')) for n in ('UpperFork','FrontRightPorted','CoverMountHole4')}))
    # Keep native primitive dimensions editable; no opaque whole-robot boolean.
    fork0=load('UpperFork');fork,fg=native('UpperForkWireArm',fork0,[root,arm],'MultiFuse')
    fork,slotg=native('UpperForkWireArmSlotted',fork,[[-136,58.35,123.05,-130,61.65,124.95]],'Cut')
    front,frg=native('FrontRightWirePassage',load('FrontRightPorted'),[frontwindow],'Cut')
    cover,cg=native('CoverHeadWirePassage',load('CoverMountHole4'),[coverwindow],'Cut')
    rows=[];poses=[];newarm=fork.cut(fork0)
    for yaw in (-15,0,15):
        w,t,r=path(yaw);t.translate(A.Vector(0,0,5));t.exportBrep(str(OUT/f'loop_yaw{yaw:+}.brep'))
        poses.append(dict(yaw=yaw,radius_mm=r,length_mm=w.Length))
        for n,s in [('new_cover',cover),('Deck',load('Deck')),('fixed_tie',load('FixedDeckTie')),('new_fork',mv(fork,yaw)),('pitch_carrier',mv(load('Pitch_Carrier'),yaw)),('pitch_servo',mv(load('Pitch_ServoReference'),yaw))]:
            for i,v in enumerate(s.Solids):
                if R.overlap(v.BoundBox,t.BoundBox):rows.append(dict(target='loop',yaw=yaw,owner=n,solid=i,hit_mm3=R.volume(t.common(v))))
        for pitch in (-10,0,5):
            for n,s in [('FrontRight',front)]+[(n,load(n)) for n in ('FrontLeft','Rear','Nose','EarL','EarR')]:
                v=mv(s,yaw,pitch)
                for label,test in [('loop',t),('new_arm',mv(newarm,yaw))]:
                    for i,solid in enumerate(v.Solids):
                        if R.overlap(solid.BoundBox,test.BoundBox):rows.append(dict(target=label,yaw=yaw,pitch=pitch,owner=n,solid=i,hit_mm3=R.volume(test.common(solid))))
    # Explicit screw land, not only pipe clearance: cutter must miss radius4.2
    # around the retained M2 side screw (1.2 hole +3mm material requirement).
    boltland=Part.makeCylinder(4.2,8,A.Vector(-84,94,116),A.Vector(0,1,0))
    land_removed=R.box(coverwindow).common(boltland).Volume
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    dump('checks.json',dict(status='REJECTED_FRONT_BOP' if frg.get('strict_bop_error') else ('CANDIDATE_INTERFACES_CLEAR' if not hits and land_removed<1e-5 else 'REJECTED'),hits=hits,changed_pairs=rows,
      geometry={'fork_arm':fg,'fork_slot':slotg,'front':frg,'cover':cg},bolt_land_removed_mm3=land_removed,
      nominal_vertical_land_mm=120.5-116-1.2,loop_poses=poses,new_stls=2 if frg.get('strict_bop_error') else 3,
      remaining=['JR factory lead and spool','moving and fixed end transitions and restraints','full fixed yaw feed','continuous sweep and physical fit in phase2'],physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,land_removed=land_removed,poses=poses)),flush=True)
if __name__=='__main__':main()

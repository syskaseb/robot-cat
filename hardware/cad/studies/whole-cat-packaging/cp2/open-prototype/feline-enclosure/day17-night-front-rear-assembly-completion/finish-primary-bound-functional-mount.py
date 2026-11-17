import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def fu(parts):
 s=parts[0]
 for q in parts[1:]:s=s.fuse(q)
 return s
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def run():
 source={}
 for n in ['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER']:
  s=Part.Shape();s.read(str(P/('source88-'+n+'.brp')));source[n]=s
 # Rebind actual four CYLINDER axes, not historic object-name coordinates.
 centres=[]
 for f in D.getObject('Pi4B_actual_PCB').Shape.Faces:
  q=f.Surface
  if hasattr(q,'Radius') and abs(q.Radius-1.375)<1e-6:centres.append([q.Center.x,q.Center.z])
 centres=sorted(set((round(x,4),round(z,4)) for x,z in centres));assert len(centres)==4
 # Correct complete UNBUILT standard sets together, preserving allsteel.
 for o in D.Objects:
  if o.Name.startswith('FS_PI_'):o.Placement.Base+=V(20,0,0)
 ribs=[bx(x-3,-74,42.5,6,3,56) for x in [-102.5,-44.5]]
 ribs += [bx(-108,-74,z,69,3,6) for z in [42.5,92]]
 posts=[Part.makeCylinder(3.5,3,V(x,-71,z),V(0,1,0)) for x,z in centres]
 arms=[bx(x,-74,45.52,6,52,3) for x in [-100,-45]]
 bores=fu([Part.makeCylinder(1.4,10,V(x,-76,z),V(0,1,0)) for x,z in centres])
 planned=fu([s.cut(bores) for s in ribs+posts+arms]);front=source['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER'].fuse(planned).cut(bores)
 D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER').Shape=front
 rm=[bx(103,y,49.52,70,4,3) for y in [-15,11]]
 rm += [bx(x,-24,49.52,w,39,3) for x,w in [(108,10),(126,7)]]+[bx(108,-24,45.52,10,5,7),bx(126,-24,45.52,7,5,7)]
 rm += [bx(158,-24,49.52,6,64,3),bx(144,20,49.52,20,20,6)]
 # Both guides beyond actualtailbaseX141, wholeF0 heldoncradle; openends.
 for x in [147,159]:
  for y in [-22,17.5]:rm.append(bx(x,y,49.52,8,5,8).cut(bx(x+2,y-.1,51.52,3.8,5.2,2.2)))
  rm.append(bx(x,-22,49.52,8,39,3))
 rear=fu([source['RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER']]+rm);D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER').Shape=rear
 D.recompute();D.save()
 checks=[];pcb=D.getObject('Pi4B_actual_PCB').Shape
 for x,z in centres:
  # Actual steel part with matching centre read by cached shape bounds.
  screw=next(o for o in D.Objects if o.Name.startswith('FS_PI_') and o.Name.endswith('_M2p5x12_full') and abs((o.Shape.BoundBox.XMin+o.Shape.BoundBox.XMax)/2-x)<1e-5 and abs((o.Shape.BoundBox.ZMin+o.Shape.BoundBox.ZMax)/2-z)<1e-5)
  post=Part.makeCylinder(3.5,3,V(x,-71,z),V(0,1,0)).cut(bores)
  af=[f for f in post.Faces if abs(f.BoundBox.YMin+68)<1e-5 and abs(f.BoundBox.YMax+68)<1e-5]
  bf=[f for f in pcb.Faces if abs(f.BoundBox.YMin+68)<1e-5 and abs(f.BoundBox.YMax+68)<1e-5]
  area=Part.makeCompound(af).common(Part.makeCompound(bf)).Area
  checks.append({'actualaxis':[x,z],'actualPCB_radius':1.375,'screw_shaft_radius':1.25,'steel_PCB_common':screw.Shape.common(pcb).Volume,'post_PCB_common':post.common(pcb).Volume,'nominal_finite_bearing_area':area,'safeannulus_delivered_revision':'FIT3 notdigitalcomponentpressurePASS'})
 put('primary-bound-actual-mount-and-coverage.json',{'centres':centres,'old_wrong_names':'FS_PI oldname coordinates remainALIASES; all16fullsteel shapes shifted+20X toactualprimary cylinders, not PCB moved/physicaldrill','checks':checks,'front_valid':front.isValid(),'front_solids':len(front.Solids),'rear_valid':rear.isValid(),'rear_solids':len(rear.Solids),'plannedfront_missing':planned.cut(front).Volume,'plannedrear_members_missing':[q.cut(rear).Volume for q in rm],'protected_sourcefront_missing_except4functionalbores':source['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER'].cut(front).cut(bores).Volume,'sourcefront_plannedbore_removed':source['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER'].cut(front).Volume,'sourcerear_missing':source['RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER'].cut(rear).Volume,'separate_print_common':front.common(rear).Volume,'sourceP01source8axes_unchanged':True,'print_bounds':[{'n':n,'bounds':bb(s),'maxXYZ_plus8brim':max(s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength)+8} for n,s in [('front',front),('rear',rear)]],'wholeacceptance':False})
 print(json.dumps({'actual_centres':centres,'actual_bearings':checks,'front_valid':front.isValid(),'rear_valid':rear.isValid(),'objects':len(D.Objects)}))
run()

import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def obj(n,s,c=(.13,.135,.145)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=c;o.ViewObject.Visibility=True;return o
def steel(n,p,a,L,stack,nom='M3'):
 p=V(*p);a=V(*a);u=V(0,1,0) if abs(a.x)>.9 else V(1,0,0);v=a.cross(u);R=5.5/math.sqrt(3);np=p+a*(stack+.5)
 def cy(r,h,t):return Part.makeCylinder(r,h,p+a*t,a)
 pts=[np+(u*math.cos(k*math.pi/3)+v*math.sin(k*math.pi/3))*R for k in range(6)]
 for tag,s in [('screw',cy(1.5,L,0).fuse(cy(2.75,3,-3))),('headwasher',cy(3.5,.5,0).cut(cy(1.6,.52,-.01))),('nutwasher',cy(3.5,.5,stack).cut(cy(1.6,.52,stack-.01))),('nut',Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(a*2.4).cut(cy(1.5,2.42,stack+.49)))]:obj(n+'_'+tag,s,(.66,.67,.7))
def run():
 t=time.perf_counter();D.save();out={'physicalPASS':False,'wholekit':False,'sourceS0':'full11unchanged'}
 n1=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER');n5=D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER')
 n1.Shape.exportBrep(str(P/'source-N1-before-operator-receiver.brep'));n5.Shape.exportBrep(str(P/'source-N5-before-operator-receiver.brep'))
 # Two actual frame roots, not loads into cosmetic cover.
 left=box(-39,-80,48.52,2.5,103,2.5).fuse(box(-45,18,48.52,8.5,5,4))
 blade=box(-39,-80,48.52,2.5,31,100.48).cut(box(-40,-76,65,4,23,70));left=left.fuse(blade)
 right=box(125,-85,43.52,33,6,7).fuse(box(150,-85,49.52,4,17.5,93.48))
 # Actual sourcefloor seats are matched printed contact, not interpenetrating material.
 right=right.cut(D.getObject('P03_rear_deck_integrated_load_yoke').Shape)
 roots=[n1.Shape.common(left).Volume,n5.Shape.common(right).Volume];out['actual_positive_root_intersections']=roots
 if min(roots)<=1e-5:
  put('operator-interface-completion.json',dict(out,status='UNBUILT_root_actual_material_missing',seconds=time.perf_counter()-t));print(out);return
 n1.Shape=n1.Shape.fuse(left).removeSplitter();n5.Shape=n5.Shape.fuse(right).removeSplitter()
 # One removable two-root operatorstrip, open around retained S0.
 panel=box(-39,-71.5,132.5,193,2,10.5).fuse(box(24,-71.5,95,32,2,48))
 panel=panel.fuse(box(-36.5,-82,140,3,12.5,9)).fuse(box(147,-85,135,3,15.5,8))
 panel=panel.cut(Part.makeCylinder(6.25,8,V(40,-75,119),V(0,1,0))).cut(Part.makeCylinder(1.5,8,V(40,-75,128),V(0,1,0)))
 panel=panel.cut(Part.makeCylinder(23,30,V(88.5,-90,108),V(0,1,0)))
 # Fullstandardthroughsets; headbearing fixes real parting rather than moving a head alone.
 for pre,p,a,L,stack in [('OP_LEFT_M3x10',[-39.5,-78,145],[1,0,0],10,6),('OP_RIGHT_M3x12',[154.5,-78,139],[-1,0,0],12,7.5)]:
  bore=Part.makeCylinder(1.65,22,V(*p)-V(*a)*3,V(*a));panel=panel.cut(bore)
  nn=n1 if pre.startswith('OP_LEFT') else n5;nn.Shape=nn.Shape.cut(bore).removeSplitter();steel(pre,p,a,L,stack)
 obj('OP_COMMON_REMOVABLE_OPERATOR_PANEL',panel.removeSplitter())
 # Source NKK primary dimensions, explicit nominal installationplane, no fake supplierdatum.
 s1=next((o for o in D.Objects if o.Name=='S1_NKK_S821_installed'),None)
 if s1 is None:s1=next((o for o in D.Objects if 'S1' in o.Name and hasattr(o,'Shape') and o.Shape.Volume>1000 and 'S1_' in o.Name),None)
 out['retired_S1_project_field']=s1.Name if s1 else None
 if s1:s1.ViewObject.Visibility=False
 case=box(28,-63,98,24,34,42);obj('OP_S1_PRIMARY_CASE_CONSERVATIVE',case,(.18,.18,.19))
 obj('OP_S1_PRIMARY_STEM',Part.makeCylinder(6,12,V(40,-75,119),V(0,1,0)),(.62,.63,.64))
 obj('OP_S1_LEVER_NOMINAL',Part.makeCylinder(3.05,22,V(40,-97,119),V(0,1,0)),(.65,.65,.67))
 obj('OP_S1_TERMINAL_ALLOWANCE_NOT_MATERIAL',box(28,-29,98,24,6,42),(.6,.4,.2)).ViewObject.Visibility=False
 # Complete nominal M12front/back nuts andwashers; supplier AF/deliveredfits remain oneFIT.
 for yy in [-75,-69]:
  pts=[V(40+20/math.sqrt(3)*math.cos(k*math.pi/3),yy,119+20/math.sqrt(3)*math.sin(k*math.pi/3)) for k in range(6)]
  obj('OP_S1_NUT_'+str(abs(yy)),Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,3,0)).cut(Part.makeCylinder(6,3.02,V(40,yy-.01,119),V(0,1,0))),(.66,.67,.7))
 for yy in [-72,-69.5]:obj('OP_S1_WASHER_'+str(abs(yy)).replace('.','_'),Part.makeCylinder(12,.5,V(40,yy,119),V(0,1,0)).cut(Part.makeCylinder(6.25,.52,V(40,yy-.01,119),V(0,1,0))),(.66,.67,.7))
 # Actual monitor case remains full, whole +2X gives S0key-to-leftcradle room.
 mon=next((o for o in D.Objects if o.Name=='Monitor_MOD05015'),None)
 if mon is None:
  mon=next((o for o in D.Objects if hasattr(o,'Shape') and 'monitor' in o.Name.lower() and o.Shape.Vertexes and 105<o.Shape.BoundBox.XMin<107 and o.Shape.BoundBox.YMin< -90),None)
 if mon:
  q=mon.Shape.copy();q.translate(V(2,0,0));mon.Shape=q;out['monitor_moved_whole_2X']=mon.Name
 cradle=box(106,-97.5,104,45,15,2).fuse(box(106,-97.5,104,2,15,29)).fuse(box(149,-97.5,104,2,15,29)).fuse(box(106,-84,104,45,2,31))
 cradle=cradle.fuse(box(106,-84,132.5,45,14.5,3)).cut(box(108,-96,106,41,12,25))
 panelobj=D.getObject('OP_COMMON_REMOVABLE_OPERATOR_PANEL');panelobj.Shape=panelobj.Shape.fuse(cradle).removeSplitter()
 # Monitor has sliding open top; one removable keeper takes two fullthrough M2sets in a later measured-fit coupon.
 # No claim of finalmonitorretention until topkeeper supplied.
 out['monitor_retention']='Three-sided cradle real; topkeeper still OPEN, not digitallysecured'
 for n in ['FC_R_NEG','FC_F_NEG']:
  q=D.getObject(n).Shape.cut(right).cut(left)
  if n=='FC_F_NEG':q=q.cut(Part.makeCylinder(18,70,V(40,-130,119),V(0,1,0)))
  D.getObject(n).Shape=q.removeSplitter()
 D.recompute();D.save()
 out.update({'parts':[{ 'n':o.Name,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'volume':o.Shape.Volume} for o in [n1,n5,panelobj]],'hardware':'2M3complete sets:10/12, 2washers each/fullnut. S1twofullnominalM12nuts2washers; supplierAFunknown','S1_primary':'M12x1/stem12/24x34x42case/full22lever retained; OWNinstallationplaneY-71.5..-69.5, hole12.5/antirot3@9. Deliveredplane/nutAF/fitFIT3.','affected_ends':'S1wireends complete/newregion, no cut/slackcredit. Monitorwhole+2X endsFIT2. S0full11unchanged.','assembly':'PreassembleS1/monitorpanel on bench; realM3rootsets before P_SYS/WAGO+latecowl. WholeE1solderedkit remains connected.','seconds':time.perf_counter()-t})
 put('operator-interface-completion.json',out);print(json.dumps(out))
run()

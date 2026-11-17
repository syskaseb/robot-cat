import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def vol(s):return 0. if s.isNull() or not s.Vertexes else s.Volume
def fu(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def add(n,s,col=(.4,.61,.63)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True;return o
def ring(x,y,z):return Part.makeCylinder(2.5,.5,V(x,y,z)).cut(Part.makeCylinder(1.1,.7,V(x,y,z-.1)))
def nut(x,y,z):
 pts=[V(x+4/math.sqrt(3)*math.cos(i*math.pi/3),y+4/math.sqrt(3)*math.sin(i*math.pi/3),z) for i in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,1.6)).cut(Part.makeCylinder(1,1.8,V(x,y,z-.1)))
def run():
 t=time.perf_counter();o=D.getObject('FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER');old=o.Shape.copy();old.exportBrep(str(P/'source6553-MTA-fixed-lower.brep'))
 windows=[Part.makeCylinder(3.75,9,V(x,25.741,74)) for x in [-.841,20.241]];new=old
 for q in windows:new=new.cut(q)
 by=[]
 for a,b in [(-8,6.5),(13,27.5)]:
  by += [bx(a,25,75,3.25,10.75,3.5),bx(b-3.25,25,75,3.25,10.75,3.5),bx(a,30.75,75,b-a,5,3.5)]
 for q in by:new=new.fuse(q)
 assert new.isValid() and len(new.Solids)==1;o.Shape=new
 # Actual commonPOST flange onreceivedreargrid; fullcase unchanged.
 r=D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER');oldr=r.Shape.copy();oldr.exportBrep(str(P/'source6553-rear-before-POST.brep'))
 mm=[bx(135.5,19,52.52,30,23,3),bx(142,19,55.52,2,23,3),bx(157,19,55.52,2,23,3),bx(142,19,55.52,17,1,3),bx(142,40,55.52,17,1.5,1.48)]
 for x in [139,162]:mm.append(Part.makeCylinder(3.5,10,V(x,31.5,55.52)))
 planned=fu(mm);newr=oldr.fuse(planned)
 for x in [139,162]:
  newr=newr.cut(Part.makeCylinder(1.1,18,V(x,31.5,49))).cut(Part.makeCylinder(2.65,3.52,V(x,31.5,49)))
 assert newr.isValid() and len(newr.Solids)==1;r.Shape=newr
 cap=bx(135.5,19,65.52,30,23,3).cut(bx(145,22,65.4,11,20.2,3.3))
 for x in [139,162]:cap=cap.cut(Part.makeCylinder(1.1,4,V(x,31.5,65.4)))
 add('CB_POST_REMOVABLE_OPEN_LEVER_KEEPER',cap)
 for i,x in enumerate([139,162]):
  add('CB_POST_'+str(i)+'_M2x20',Part.makeCylinder(1,20,V(x,31.5,49.02)).fuse(Part.makeCylinder(1.9,2,V(x,31.5,69.02))),(.67,.68,.7))
  add('CB_POST_'+str(i)+'_topwasher',ring(x,31.5,68.52),(.67,.68,.7));add('CB_POST_'+str(i)+'_bottomwasher',ring(x,31.5,52.02),(.67,.68,.7));add('CB_POST_'+str(i)+'_fullnut',nut(x,31.5,50.42),(.67,.68,.7))
 D.recompute();D.save()
 put('MTA-functional-access-and-POST-realization.json',{'MTA':{'windows':[bb(q) for q in windows],'purpose':'fullAUXhead+washer+1.25guard notshortenedsteel; openforeedge allowsinitialloading','bypass_sections':[3.25,3.5],'bypass_casebottom_gap':1.5,'bypass_lower_to_celltop':1.5,'old_part_missing_except_windows':None,'old_declaredremoved':vol(old.cut(new)),'new_positive_added':vol(new.cut(old)),'bypass_intended_missing':[vol(q.cut(new)) for q in by],'valid':new.isValid(),'solids':len(new.Solids)},'POST':{'case_pose_unchanged':True,'fixed_valid':newr.isValid(),'fixed_solids':len(newr.Solids),'source_rear_missing_except2realnutpockets':vol(oldr.cut(newr)),'cap_valid':cap.isValid(),'fixed_cap_common':vol(newr.common(cap)),'fixed_case_common':vol(newr.common(D.getObject('PBAY_POST_F0').Shape)),'cap_case_common':vol(cap.common(D.getObject('PBAY_POST_F0').Shape)),'full2sets':'2xM2x20 socket+4OD5washers+2fullM2nuts; tip49.02/nut50.42..52.02/topwasher68.52..69.02/underhead69.02; tip1.4; NEEDED_UNCONFIRMED','nut_feed':'realopenbottomro2.65pockets49..52.52; counterholdbeforelateclosures; no cutboughtframe','mouth':'projectfull2chambers+Y approach/centerZ60.52, lowerstop57 leaves1.57toallocatedwire. Actualmanufacturer mouth/lever/safeplasticFIT3, notbboxdatumGO','retention':'realX/Ysidewalls+endstops+removableZkeeper, 2bolts/actualpositiveflange toexistingrearroot; noplasticwirepullpressure','source_foreign_needed':['F0wholeinstallationfield','fulltailroot/servo/bearings','S0all11','stockfields/movingcontext'],'initialorder':'preloadnuts/washers inactualbottompockets;wholecase/ends;capfromabove;connectfullfactorywiresbeforebodycovers'},'wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 print(json.dumps({'MTA_valid':new.isValid(),'MTA_solids':len(new.Solids),'POST_fixed_cap_common':vol(newr.common(cap)),'POST_fixed_case_common':vol(newr.common(D.getObject('PBAY_POST_F0').Shape)),'seconds':time.perf_counter()-t}))
run()

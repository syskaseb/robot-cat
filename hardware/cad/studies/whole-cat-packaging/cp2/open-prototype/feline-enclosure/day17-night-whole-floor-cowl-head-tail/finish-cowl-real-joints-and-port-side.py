import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def obj(n,s,col=(.65,.66,.69)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;return o
def steel(n,p,a,L,bearing):
 p=V(*p);a=V(*a);u=V(1,0,0) if abs(a.x)<.9 else V(0,1,0);v=a.cross(u)
 def cy(r,h,d):return Part.makeCylinder(r,h,p+a*d,a)
 np=p+a*(bearing+.5);r=4/math.sqrt(3);pts=[np+(u*math.cos(k*math.pi/3)+v*math.sin(k*math.pi/3))*r for k in range(6)]
 for tag,s in [('screw',cy(1,L,0).fuse(cy(1.9,2,-2))),('headwasher',cy(2.5,.5,0).cut(cy(1.1,.52,-.01))),('nutwasher',cy(2.5,.5,bearing).cut(cy(1.1,.52,bearing-.01))),('nut',Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(a*1.6).cut(cy(1.025,1.62,bearing+.49)))]:obj(n+'_'+tag,s)
def run():
 t=time.perf_counter();D.save();p03=D.getObject('P03_rear_deck_integrated_load_yoke');old=p03.Shape.copy();old.exportBrep(str(P/'source-P03-before-obsolete-tail-extension-retirement.brep'))
 p03.Shape=old.cut(box(177,-100,40,25,200,40)).removeSplitter()
 # This only retires the old UNBUILT Z-tail fork. Current whole Y-tail fixed load route
 # is in actual RG rear/P01, maxX173; S0 far supports X169..175 stay intact.
 ns={'__file__':str(P/'build-floor-based-cowl.py')};exec((P/'build-floor-based-cowl.py').read_text(encoding='utf-8').split('def run():')[0],ns)
 for sy,n in [(-1,'FC_R_NEG'),(1,'FC_R_POS')]:
  q=D.getObject(n).Shape
  # Purposeful end-lap termination where actual deck supplies the bottom; no mesh fragment deletion.
  q=q.cut(box(165,-130,43.5,17,260,3.5))
  cap=Part.makeLoft([ns['profile'](ns['pars'](x),sy,True) for x in [179.4,181]],True,True)
  q=q.fuse(cap).cut(p03.Shape);D.getObject(n).Shape=q.removeSplitter()
 # Short, rounded fore-port compartment, not another long device window.
 front=D.getObject('FC_F_NEG');o=box(-155.25,-105.6,40.77,36.25,45.6,68.08);o=o.makeFillet(1.5,o.Edges)
 inner=box(-153.65,-104,42.37,38,42.4,64.88);q=front.Shape.fuse(o).cut(inner)
 for c in [box(-117.25,-99.17,39.75,54.5,25.5,18.5),box(-156,-91.65,42.75,32,27.5,28.5)]:q=q.cut(c)
 front.Shape=q.removeSplitter()
 # One accessible roof throughjoint; 5 real base keys + this cross-cowl restraint.
 top=170.6;cx=-60;neg=D.getObject('FC_F_NEG').Shape;pos=D.getObject('FC_F_POS').Shape
 neg=neg.fuse(box(cx-7,-6,top-6,14,28,3)).fuse(box(cx-7,-6,top-6,14,6,4.8))
 pos=pos.fuse(box(cx-7,0,top-9.25,14,26,3)).fuse(box(cx-7,22,top-9.25,14,4,8.05))
 cage=box(cx-3.6,14.4,top-12.85,7.2,7.2,3.6);cage=cage.cut(box(cx-4,15.8,top-11.45,8,4.4,1.8)).cut(Part.makeCylinder(2.65,.8,V(cx,18,top-9.85)))
 pos=pos.fuse(cage)
 bore=Part.makeCylinder(1.15,20,V(cx,18,top-16));access=Part.makeCylinder(2.75,7,V(cx,18,top-3))
 neg=neg.cut(bore).cut(access);pos=pos.cut(bore).cut(access);D.getObject('FC_F_NEG').Shape=neg.removeSplitter();D.getObject('FC_F_POS').Shape=pos.removeSplitter();steel('CJ_FRONT_ROOF',[-60,18,top-2.5],[0,0,-1],10,6.75)
 # Two actual front/rear lapped side joints. All head/washer/nut/tip volumes modeled.
 for sy,fn,rn in [(-1,'FC_F_NEG','FC_R_NEG'),(1,'FC_F_POS','FC_R_POS')]:
  f=D.getObject(fn).Shape;r=D.getObject(rn).Shape
  lip=box(78,108 if sy>0 else -110.15,101,9,2.15,8);root=box(78,108 if sy>0 else -112.2,101,2,4.2,8)
  f=f.fuse(lip).fuse(root);cage=box(80.4,104.4 if sy>0 else -108,101.4,7.2,3.6,7.2)
  # Open+Z feed accepts real full nut/washer on the bench, not a virtual printed thread.
  cage=cage.cut(box(81.8,104.2 if sy>0 else -108.2,103,4.4,4.2,7))
  f=f.fuse(cage);a=V(0,-sy,0);bore=Part.makeCylinder(1.15,20,V(84,sy*119,105),a)
  f=f.cut(bore);r=r.cut(bore);D.getObject(fn).Shape=f.removeSplitter();D.getObject(rn).Shape=r.removeSplitter();steel('CJ_SIDE_'+('P' if sy>0 else 'N'),[84,sy*112.5,105],[0,-sy,0],10,4.5)
 D.recompute();D.save();rows=[]
 for n in ['FC_F_NEG','FC_F_POS','FC_R_NEG','FC_R_POS']:
  s=D.getObject(n).Shape;b=s.BoundBox;rows.append({'n':n,'valid':s.isValid(),'solids':len(s.Solids),'v':s.Volume,'bounds':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]})
 put('cowl-completed-joints-and-effectivity.json',{'parts':rows,'retired_P03_tail_extension_volume':old.Volume-p03.Shape.Volume,'retired_role':'Old Z-tail own fork beyondX177, function already replaced by unchanged actual Y-tail fixed receiver/P01 route. Not bought geometry.','source8P01_and_S0supports_toX175_preserved':True,'base_cowl_M3_sets_active':5,'new_M2x10_sets':3,'front_crown_bearing_planes':{'upper':top-3,'lower':top-9.25,'nut':[top-11.35,top-9.75],'tip':top-12.5},'side_bearing_planes_Yabs':[112,108],'assembly':'Preload real nuts+washers through open seats before offering covers. Base5M3 from received side-access, roofM2 outside+Z, sideM2 outside±Y. No wire or solderedE1 unplug.','Pi_full_fields_preserved':'Foreport localguard actual floor40.77 >= source39.52+1.25; fullGPIO/Delock apertures are functional ports, not smaller parts.','physicalPASS':False,'wholekit':False,'seconds':time.perf_counter()-t})
 print(json.dumps({'parts':rows,'seconds':time.perf_counter()-t}))
run()

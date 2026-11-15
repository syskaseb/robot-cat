import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,math
from pathlib import Path
V=A.Vector;D=A.getDocument('DAY15_PI_BATTERY_CARRIER');P=Path(D.FileName).parent
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def hull(points):
 q=sorted(set(points));cross=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);lo=[];hi=[]
 for p in q:
  while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(q):
  while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
def nutfeed(af,x,y,z,h,end):
 rr=af/math.sqrt(3);p=hull([(x+rr*math.cos(math.pi/6+i*math.pi/3),yy+rr*math.sin(math.pi/6+i*math.pi/3)) for i in range(6) for yy in [y,end]]);return Part.Face(Part.Wire(Part.makePolygon([V(a,b,z) for a,b in p+[p[0]]]).Edges)).extrude(V(0,0,h))
def washerfeed(rad,x,y,z,h,end):
 return Part.makeCylinder(rad,h,V(x,y,z)).fuse(Part.makeCylinder(rad,h,V(x,end,z))).fuse(box(x-rad,min(y,end),z,2*rad,abs(end-y),h))
x=-74.5;y=-34.5;end=-45.5;tray=box(x-6,y-7,92.52,12,14,3);post=Part.makeCylinder(2.5,3,V(x,y,95.52));cage=box(x-4,y-7,87.92,8,11,5.1);raw=tray.fuse(post).fuse(cage)
nf=nutfeed(5.2,x,y,89.92,2.2,end);wf=washerfeed(3.1,x,y,91.92,.6,end);bore=Part.makeCylinder(1.375,16,V(x,y,87.5));cut=nf.fuse(wf).fuse(bore);coupon=raw.cut(cut);assert coupon.isValid() and len(coupon.Solids)==1
o=D.getObject('COUPON_ONE_CORNER_PI_NUT_WASHER') or D.addObject('PartDesign::Feature','COUPON_ONE_CORNER_PI_NUT_WASHER');o.Shape=coupon;o.ViewObject.ShapeColor=(.2,.65,.8)
if 'ReleaseScope' not in o.PropertiesList:o.addProperty('App::PropertyString','ReleaseScope')
o.ReleaseScope='ISOLATED_NOMINAL_FIT_COUPON_ONLY_NOT_OPERATING_P12';D.recompute();D.save()
r=dict(status='ONE_CORNER_COUPON_SAVED_BEFORE_OWNFIT',operating_P12_cut=False,source_corner=[x,y],quantity=1,washerfeed_nominal_OD6=True,pocket_AF5p2_vs_actualAF5=True,sidefeed_actual_open_Y=end,floor_mm=2,roof_mm=3,lower_washer_contact_plane92p52=True,technical_contact_realization='Final pocket ceiling exactly92.52 matches lowerwasher top; no .1air under bearing. Same intended coupon/joint, not operatinggeometryvariant.',posts_height3_unchanged=True,intended_members=[])
for n,s in [('tray',tray),('post',post),('cage',cage)]:
 intended=s.cut(cut);miss=intended.cut(coupon);r['intended_members'].append(dict(name=n,missing_volume=miss.Volume,extent=str(intended.BoundBox)));assert miss.Volume<1e-5
r['positive_raw_connections']=[dict(a='tray',b='post',functional_face_contact_gap=tray.distToShape(post)[0],common_mm3=tray.common(post).Volume),dict(a='tray',b='cage',common_mm3=tray.common(cage).Volume)]
r['own_hardware_checks']=[]
for n in ['PI0_ISO4762_M2p5x12','PI0_upper_ISO7089_washer','PI0_lower_ISO7089_washer','PI0_full_AF5_nut']:
 c=coupon.common(D.getObject(n).Shape);r['own_hardware_checks'].append(dict(name=n,valid=c.isValid(),common_mm3=c.Volume));assert c.isValid() and c.Volume<1e-5
stock=nf # Actual stock full profiles, not entire pocket or moving cone.
actualnut=nutfeed(5,x,y,90.02,2,end);actualwasher=washerfeed(3,x,y,92.02,.5,end);feed=actualnut.fuse(actualwasher);c=coupon.common(feed);r['continuous_full_stock_feed']=dict(valid=c.isValid(),common_mm3=c.Volume,washer_OD=6,nutAF5_height2=True);assert c.isValid() and c.Volume<1e-5
tool=nutfeed(2,x,y,102.02,12,y);c=coupon.common(tool);r['driver_before_PCB_GPIO_mating']=dict(hexAF=2,common_mm3=c.Volume,assembly='loadwasherthenfullnutthroughopennegativeYfeed; insertPi+topwasher+bolt; hex2driver fromabove BEFOREGPIO1992/BUS/mic. Fullpad/component actualtrial remainsFIT.');assert c.Volume<1e-5
coupon.exportBrep(str(P/'Pi-one-corner-coupon.brep'));local=coupon.copy();b=local.BoundBox;local.translate(V(-b.XMin,-b.YMin,-b.ZMin));b=local.BoundBox;r['print_size']=[b.XLength,b.YLength,b.ZLength];assert max(r['print_size'])<256;mesh=MeshPart.meshFromShape(Shape=local,LinearDeflection=.08,AngularDeflection=.15,Relative=False);mesh.write(str(P/'Pi-one-corner-coupon.stl'));r['mesh_closed']=mesh.isSolid();r['orientation']='flatfloorZ0, postup; floor2/roof2.9; horizontalnutfeed bridge~6.2mm needsphysicalPETGcoupon, no slicer/print run';r['installed_Pi']='OPEN_BNO_INSTALLATION_ALLOCATION; do not cut/export wholeP12 until deliveredBNOheader/componentbudget measured';(P/'Pi-coupon-result.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(status=r['status'],own4stockclear=True,fullfeedclear=True,size=r['print_size'],meshclosed=r['mesh_closed'],installed_Pi=r['installed_Pi'])))

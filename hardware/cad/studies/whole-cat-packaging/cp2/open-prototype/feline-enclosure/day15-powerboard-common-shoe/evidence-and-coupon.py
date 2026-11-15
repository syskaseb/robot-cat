import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,math
from pathlib import Path
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-powerboard-common-shoe');D=A.getDocument('DAY15_POWERBOARD_SHOE');V=A.Vector
def hull(points):
 p=sorted(set(points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lo=[]
 for q in p:
  while len(lo)>1 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 hi=[]
 for q in reversed(p):
  while len(hi)>1 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return lo[:-1]+hi[:-1]
def run():
 shoe=D.getObject('P20_COMMON_MAIN_AUX_M2_SHOE').Shape;gate=json.loads((P/'finite-layer-and-joint-gate.json').read_bytes())
 r=dict(reason='Evidence correction SAME geometry: prior rectangular swept cover includes air outside hexnut and cannot prove actual nut interference',prior_cover_common=2.6696676447328,prior_raw_gate_retained=True,rows=[])
 for i,(x,y) in enumerate(gate['primary_holes_MAIN']+gate['primary_holes_AUX']):
  rad=4/math.sqrt(3);end=19.5 if y<34 else 49.5
  pts=[(x+rad*math.cos(k*math.pi/3),yy+rad*math.sin(k*math.pi/3)) for yy in [y,end] for k in range(6)]
  hh=[V(a,b,94.52) for a,b in hull(pts)];s=Part.Face(Part.makePolygon(hh+[hh[0]])).extrude(V(0,0,1.6));c=s.common(shoe)
  r['rows'].append(dict(hole=i,continuous_exact_convex_hex_translation=True,valid=c.isValid(),common=c.Volume,clear=c.isValid() and c.Volume<1e-5))
 # One actual shared nut/post section for physical safe-annulus and stock fit.
 coupon=shoe.common(Part.makeBox(12,10.5,11,V(57.2,20,92.52)));assert coupon.isValid() and len(coupon.Solids)==1
 o=D.addObject('PartDesign::Feature','COUPON_M2_SOURCE_HOLE_POST_AND_FULLNUT_FEED');o.Shape=coupon;o.ViewObject.Visibility=False
 q=coupon.copy();b=q.BoundBox;q.translate(V(-b.XMin,-b.YMin,-b.ZMin));m=MeshPart.meshFromShape(Shape=q,LinearDeflection=.05,AngularDeflection=.2,Relative=False);assert m.isSolid() and m.Volume>0
 m.write(str(P/'COUPON_M2_fullnut_and_post.stl'));coupon.exportBrep(str(P/'COUPON_M2_fullnut_and_post.brep'))
 r['coupon']=dict(qty=1,not_installed_part=True,closed=True,volume=m.Volume,localXYZ=[q.BoundBox.XLength,q.BoundBox.YLength,q.BoundBox.ZLength],Zmin=q.BoundBox.ZMin,hole2p4=True,fullnutAF4x1p6=True,positive_post_height6=True,floor2=True,roof1p4=True,measure='Actual M2 nut/PCB-hole revision/safe annulus/washer and underside components. Do not tighten PCB until inspected. No complete shoe STL release.')
 r['whole_layer_still_HOLD']=True;r['physical_pass']=False
 (P/'actual-nut-feed-and-coupon.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 # Actual material slices for local decision: retain source curves, not empty diagram.
 curves=[]
 for label,z in [('shoe_and_frame_head_Z96p5',96.5),('AUX_M2_to_S0_Z106',106)]:
  for n in ['P20_COMMON_MAIN_AUX_M2_SHOE','CS_P11_rear_gate_positive_ISO10642_M3x10','P06_S0_shared_panel','PB3_M2x12_full','MAIN_Pololu4853','AUX_FULL_POPULATED_OCCUPIED_NOT_PLASTICCASE']:
   s=D.getObject(n).Shape
   if s.BoundBox.ZMin>z+.01 or s.BoundBox.ZMax<z-.01:continue
   sec=s.section(Part.makePlane(85,42,V(50,16,z)));ls=[]
   for e in sec.Edges:
    vs=e.discretize(Deflection=.03);ls.append([[v.x,v.y] for v in vs])
   curves.append(dict(section=label,z=z,part=n,curves=ls))
 (P/'actual-source-sections.json').write_text(json.dumps(curves)+'\n',encoding='utf-8')
 # Footprint touch and PCB pad contact scopes distinguished from populated cover.
 contacts=[]
 for i,xy in enumerate(gate['primary_holes_MAIN']+gate['primary_holes_AUX']):
  x,y=xy;pcb=Part.makeCylinder(1.9,.01,V(x,y,103.515)).cut(Part.makeCylinder(1.2,.02,V(x,y,103.51)))
  contacts.append(dict(hole=i,nominal_ring_area=math.pi*(1.9**2-1.2**2),manufactured_safe_annulus_NOT_verified=True,post_to_actual_shoe_floor_positive=shoe.common(Part.makeCylinder(1.9,.5,V(x,y,97.02))).Volume))
 r['contact_function']=contacts
 (P/'actual-nut-feed-and-coupon.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 for o in D.Objects:
  if not hasattr(o.ViewObject,'ShapeColor'):continue
  if o.Name.startswith(('COUPON_','FEED_','KEY_','CAPTURE_','DIRECT_')) or 'section' in o.Name.lower() or o.Name.startswith(('P12_FULL_OD6','P12_UNCHANGED_R24')):o.ViewObject.Visibility=False
 for n in ['P20_COMMON_MAIN_AUX_M2_SHOE','MAIN_Pololu4853','AUX_Pololu4092','AUX_FULL_POPULATED_OCCUPIED_NOT_PLASTICCASE']:D.getObject(n).ViewObject.Visibility=True
 D.Label='DAY15 COMMON POWER SHOE / HOLD NOT INSTALLED / COUPON ONLY';D.recompute();D.save()
 A.setActiveDocument(D.Name)
 # Close original source without saving MCP label changes; frozen pinned file untouched.
 S=A.getDocument('DAY15_CARRIER_CAPTURE')
 if S:A.closeDocument(S.Name)
 print(json.dumps(dict(whole='HOLD_FINITE_THREE_INTERFACE_CAUSES_NO_RETRY',nutrows=r['rows'],coupon=r['coupon'],objects=len(D.Objects))))
run()

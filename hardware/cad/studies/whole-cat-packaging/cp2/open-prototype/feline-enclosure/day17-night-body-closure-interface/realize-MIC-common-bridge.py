import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def put(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def obj(n,s,color=(.63,.64,.67)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;return o
def nut(x,y,z):
 r=4/math.sqrt(3);v=[V(x+r*math.cos(k*math.pi/3),y+r*math.sin(k*math.pi/3),z) for k in range(6)]
 return Part.Face(Part.makePolygon(v+[v[0]])).extrude(V(0,0,1.6)).cut(cyl(x,y,z-.01,1.025,1.62))
def run():
 t=time.perf_counter();D.save();o=D.getObject('CB_REMOVABLE_BUS_E1_BRIDGE');old=o.Shape.copy();old.exportBrep(str(P/'source-ebd-BUS-E1-bridge.brep'))
 # Supplier board plane chosen explicitly INSIDE current installation allowance.
 # Hole pattern is the received 2 DIAGONAL holes, not four corners.
 axes=[(76.201974,-20.838025),(18.491974,8.081975)]
 plate=box(15,-25,141,85,37,2.5).cut(box(18,-22,140.9,79,31,2.7))
 # Lower legs stay on the actual backrail, clear of full S0. Arms start above S0+1.25.
 parts=[old,plate,box(15,17,136.5,5,3,7),box(84,17,136.5,5,3,7),box(15,10,138.5,5,10,5),box(84,10,138.5,5,10,5)]
 for x,y in axes:parts += [cyl(x,y,141,2.4,2.5),cyl(x,y,143.5,2.4,4.085)]
 q=parts[0]
 for p in parts[1:]:q=q.fuse(p)
 for x,y in axes:q=q.cut(cyl(x,y,138,1.15,16))
 o.Shape=q.removeSplitter()
 steel=[]
 for i,(x,y) in enumerate(axes):
  shapes=[('M2x12_full',cyl(x,y,138.5,1.9,2).fuse(cyl(x,y,140.5,1,12))),('headwasher',cyl(x,y,140.5,2.5,.5).cut(cyl(x,y,140.49,1.1,.52))),('nutwasher',cyl(x,y,149.095,2.5,.5).cut(cyl(x,y,149.085,1.1,.52))),('fullnut',nut(x,y,149.595))]
  for tag,s in shapes:steel.append(obj('HB_MIC_'+str(i)+'_'+tag,s).Name)
 # Full populated SOURCE scope, not a resized plastic case or extra physical part.
 scope=obj('HB_MIC_PRIMARY_POPULATED_SCOPE',box(16,-23.5,145,83.602,34.007,10.93),(.35,.55,.8));scope.ViewObject.Visibility=False
 D.recompute();D.save()
 put('MIC-actual-common-interface.json',{'source':'head-electronics-2026-09-22/measurements.json + sourceSTEP4a9585d0...1528','axes':axes,'PCB_plane':[147.585,149.095],'underside_components_bottom145':True,'shelf_top':143.5,'underside_gap':1.5,'standoff_height':4.085,'nominal_step_populated_top':155.93,'old10mm_cover_not_literal_full_supplier_scope':True,'board_min':[16,-23.5],'steel':steel,'full_M2x12_underhead140p5_tip152p5_nut149p595_151p195':True,'tip_beyond_fullnut':1.305,'mount_contact_safe_annulus':'PHYSICAL_FIT3, no invisible component pressure accepted','fixed_bridge_old_missing_mm3':old.cut(o.Shape).Volume,'newpart_valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'new_volume':o.Shape.Volume,'old_volume':old.Volume,'assembly':'Load lower washers/bolts bench first. Fit populated MIC and two diagonal nuts. BUS+MIC+E1 topcapture bridge lifts as ONE real print; E1 remains soldered. Disconnect actual USB_AUDIO only if its real connector permits. Covers are installed late.','wholePASS':False,'seconds':time.perf_counter()-t})
 print(json.dumps({'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'added':o.Shape.Volume-old.Volume,'seconds':time.perf_counter()-t}))
run()

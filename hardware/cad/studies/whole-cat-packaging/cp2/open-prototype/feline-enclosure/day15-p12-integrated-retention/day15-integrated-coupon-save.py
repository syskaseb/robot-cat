import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,math,shutil
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;D=A.getDocument('DAY15_P12_INTEGRATED');P=Path(D.FileName).parent
x=-74.5;y=-34.5;wy=y+8
base=Part.makeBox(12,22,3.1,V(x-6,y-6,92.42));foot=Part.makeCylinder(4.5,4.1,V(x,y,92.42));roof=Part.makeCone(4.5,2.5,2,V(x,y,96.52));raw=base.fuse(foot).fuse(roof)
rr=5.2/math.sqrt(3);pp=sorted(set((x+rr*math.cos(math.pi/6+i*math.pi/3),yy+rr*math.sin(math.pi/6+i*math.pi/3)) for yy in [y,wy] for i in range(6)))
cross=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);aa=[];bb=[]
for p in pp:
 while len(aa)>1 and cross(aa[-2],aa[-1],p)<=0:aa.pop()
 aa.append(p)
for p in reversed(pp):
 while len(bb)>1 and cross(bb[-2],bb[-1],p)<=0:bb.pop()
 bb.append(p)
hp=aa[:-1]+bb[:-1];nf=Part.Face(Part.Wire(Part.makePolygon([V(a,b,94.42) for a,b in hp+[hp[0]]]).Edges)).extrude(V(0,0,2.1));well=Part.makeCylinder(3.1,6,V(x,wy,94.42));bore=Part.makeCylinder(1.375,8,V(x,y,92.3));cut=nf.fuse(well).fuse(bore);s=raw.cut(cut);assert s.isValid() and len(s.Solids)==1
o=D.addObject('PartDesign::Feature','COUPON_INTERNAL_PI_FULL_NUT_TOP_SIDE');o.Shape=s;o.ViewObject.ShapeColor=(.2,.65,.8);r=dict(status='UPDATED_INTERNAL_NUT_COUPON_OWNFIT_CLEAR',size=[12,22,6.1],floor=2,roof=2,standoff3=True,quantity=1,stock_checks=[],members=[],physical_pass=False,wholekit=False)
for n in ['INT_PI0_full_M2p5x8','INT_PI0_upper_full_washer','INT_PI0_internal_full_nut']:
 c=s.common(D.getObject(n).Shape);r['stock_checks'].append(dict(name=n,common=c.Volume,valid=c.isValid()));assert c.isValid() and c.Volume<1e-5
for n,q in [('base',base),('foot',foot),('roof',roof)]:m=q.cut(cut).cut(s);r['members'].append(dict(name=n,missing=m.Volume));assert m.Volume<1e-5
s.exportBrep(str(P/'internal-Pi-coupon.brep'));local=s.copy();b=local.BoundBox;local.translate(V(-b.XMin,-b.YMin,-b.ZMin));mesh=MeshPart.meshFromShape(Shape=local,LinearDeflection=.08,AngularDeflection=.15,Relative=False);mesh.write(str(P/'internal-Pi-coupon.stl'));r['mesh_closed']=mesh.isSolid();assert r['mesh_closed'];r['nominal_assembly']='drop fullnut throughTOPwell beforePi, pushside8 intoAF5.2capture; addPi/fullupperwasher/M2.5x8; lowerwasherRETIRED by integral2mmroofbearing, not deletedbylabel';r['whole4feed_scope']='whole-kit-first-gate received all4fullmetal/top+sidefeed; physicalFIT/coupon stillrequired';(P/'updated-Pi-coupon-result.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
# Preserve pre-seat P19 BRep for forensic, save actualcurrent correctedcarrier, no STL forknownblockedkit.
shutil.copyfile(P/'P19_shared_lower_carrier.brep',P/'C0-P19-before-stock-access.brep');D.getObject('P19_shared_lower_carrier').Shape.exportBrep(str(P/'P19_shared_lower_carrier.brep'))
stocks=[]
for o in D.Objects:
 if o.Name.startswith('STRAP') and hasattr(o,'Shape'):b=o.Shape.BoundBox;stocks.append(dict(name=o.Name,bounds=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume=o.Shape.Volume))
(P/'actual-stock-fields-and-effectivity.json').write_bytes((json.dumps(dict(fields=stocks,full_two_units200_textile_each=True,closure20_projectconditional=True,fullremainder49p35_modeled=True,metalbuckle_capacity_actualFIT=True,actualheadfields='20x23x6 / Y±11.5 /Z88.5..94.5, authoritativeBRep above originalplanbox',tail_start_Y10=True,part_effectivity='P10+P11+P12 replace correspondingreceivedprints; P19 retiresoldunbuiltBattery_tray/crossarms/edgeposts only. No duplicatedsourceparents; notglobalselection afterS0HOLD.',main_part_STL_release=False),indent=2)+'\n').encode())
old=A.getDocument('DAY15_PI_BATTERY_CARRIER')
if old:A.closeDocument(old.Name)
D.Label='DAY15 internalPi/strapguide — CARRIER rearsteel/S0 HOLD';D.recompute();D.save();G.getDocument(D.Name).Modified=False
(P/'native-save-received.json').write_bytes((json.dumps(dict(doc=D.Name,objects=len(D.Objects),pid=17796,modified=bool(G.getDocument(D.Name).Modified),pending=None,file=D.FileName,utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n').encode())
for o in D.Objects:
 if hasattr(o,'Shape') and hasattr(o.ViewObject,'Visibility'):o.ViewObject.Visibility=(o.Name=='COUPON_INTERNAL_PI_FULL_NUT_TOP_SIDE' or o.Name in ['INT_PI0_full_M2p5x8','INT_PI0_upper_full_washer','INT_PI0_internal_full_nut'])
print(json.dumps(dict(coupon=r,objects=len(D.Objects))))

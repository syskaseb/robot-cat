import FreeCAD as A,FreeCADGui as G,Part,math,json
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cy(x,y,z,r,h,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
D.save();base=D.getObject('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER');b=base.Shape.copy();old=b.copy()
# Restore complete FOUR source-hole bearingposts after activeAMP side-window discovery.
for x in [-41.5,-4.5]:
 for z in [97,125]:
  q=cy(x,-19.5,z,2.75,6,V(0,1,0)).cut(cy(x,-19.6,z,1.1,6.2,V(0,1,0)))
  b=b.fuse(q)
  b=b.cut(Part.makeCone(2,1,1.2,V(x,-19.5,z),V(0,1,0)))
  tag='CF17_BUS_CSK10_'+str(x).replace('-','m').replace('.','p')+'_'+str(z)
  s=Part.makeCone(2,1,1.2,V(x,-19.5,z),V(0,1,0)).fuse(cy(x,-18.3,z,1,8.8,V(0,1,0)))
  o=D.getObject(tag) or D.addObject('PartDesign::Feature',tag);o.Shape=s;o.ViewObject.ShapeColor=(.67,.68,.7)
for o in D.Objects:
 if o.Name.startswith('CB_BUS_') and (o.Name.endswith('M2x12') or o.Name.endswith('basewasher')):o.Label='RETIRED_UNBUILT_SOCKET_AND_BACKWASHER '+o.Name;o.ViewObject.Visibility=False
base.Shape=b.removeSplitter()
# Actualretirement wholeobsoletePi cornerland. The isolated293.896mm3 iswithin this explicitformerPi support role, notrandomsoliddeletion.
src=D.getObject('A17_INTEGRAL_FRONT_DECK_AND_N1');S=Part.Shape();S.read(str(P/'source-A17front.world.brep'));prior=S.copy();ret=bx(-69.25,19.75,140.25,23,10,30);S=S.cut(ret)
# Real shaped relief toretain activeAMP floor. Below101.25 only at rightedge; mainfloor/standoffcentres untouched. Useful residual1.75+ awayfromedge.
recess=bx(-8.55,-20.85,94.1,5.0,8.65,7.15);S=S.cut(recess).removeSplitter();src.Shape=S
# ShortenoldPCA rib receivingcollision source-neutral by prior newcarrierreliefs; no sourcePCAfloor cut.
roots=[]
for x in [-75,85.5]:
 face=Part.Face(Part.makePolygon([V(x-3.4,16.6,134),V(x+3.4,16.6,134),V(x+3.4,23.4,134),V(x-3.4,23.4,134),V(x-3.4,16.6,134)]))
 roots.append({'axis':[x,20],'nominal_contact_area_source':face.common(S).Area,'nominal_contact_area_carrier':face.common(base.Shape).Area})
# Relevant completefullmetal nexttoAMPLIFIER, no assembly-before-PCB waiver.
rr=[]
for a in [o for o in D.Objects if o.Name.startswith('CF17_BUS_CSK10_') or o.Name.startswith('CB_BUS_1_1_') and (o.Name.endswith('nut') or o.Name.endswith('PCBwasher'))]:
 for q in [o for o in D.Objects if o.Name.startswith('CB_AMP_1_')]:
  d=a.Shape.distToShape(q.Shape)[0]
  if d<3:rr.append({'a':a.Name,'b':q.Name,'gap':d,'required':1.25,'clear':d>=1.25})
put('complete-common-joint-final.json',{'carrier':[base.Shape.isValid(),len(base.Shape.Solids),base.Shape.Volume],'A17':[S.isValid(),len(S.Solids),S.Volume],'source_lower134_missing':prior.common(bx(-150,-100,0,260,210,134)).cut(S).Volume,'explicit_replaced_role':'obsoletePi corner supportx-69.25..-46.25/Y19.75..29.75/Z140.25+, replacedbynewfourpostcarrier; sourcedeck/anchor/headroot unchanged','active_AMP_relief':'only openrightedge X-8.55..-3.55/Y-20.85..-12.2/Z94.1..101.25. MainAMPpostcentreX-10.15 andfullbearingat102 preserved. Cornerweb.75locally +full3mmcentralbearing; no strengthPASS, physicalcoupon/loadtest.','root_contact_faces':roots,'parting_common':base.Shape.common(S).Volume,'BUS_complete_joint':'4M2CSK10 headD4/h1.2 inclheadlength, tipY-9.5/fullM2nut-11.4..-9.8=>.3tip; frontwasher retained, post3+plate3, seatresidual1.8. Old4socket12+4backwashers UNBUILTdemandretired, notboughtcuts. New4CSK10 neededunconfirmed','AMP_fullmetal_pairs':rr,'old_fullwasher_raw_gap':1.124228857094193,'wholekit':False,'physicalPASS':False})
# Actual openback passage in MOVING upperheadcap, preserves Y+-49 primarysteel lands.
o=D.getObject('HC_BACK_UPPER');h=Part.Shape();h.read(str(P/'source-HC-back-upper.world.brep'));cut=bx(-153,-36,151.5,34,72,80);n=h.cut(cut).removeSplitter();o.Shape=n;o.Placement=A.Placement()
put('moving-neck-open-channel-disposition.json',{'source':h.Volume,'new':n.Volume,'valid':n.isValid(),'solids':len(n.Solids),'preserved_outside_actual_channel_missing':h.cut(cut).cut(n).Volume,'explicit_function':'rearcentre movingcap slit toexistingopenbackedge; primaryY+-49 skins/gimbalroots retained. Fixed late guard/contact stillneeds actualbody/wholeloom qualification; NOTclosedfrontPASS','channel':str(cut.BoundBox),'PETG_delta_g':(n.Volume-h.Volume)*.00127})
D.recompute();D.save();print(json.dumps({'carrier':len(base.Shape.Solids),'A17':len(S.Solids),'parting':base.Shape.common(S).Volume,'metal_fails':[r for r in rr if not r['clear']],'HCsolids':len(n.Solids)}))

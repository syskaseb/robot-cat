import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;t0=time.perf_counter()
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2,ensure_ascii=False)+'\n').encode())
def bx(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cy(x,y,z,r,h,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def union(ss):
 q=ss[0]
 for s in ss[1:]:q=q.fuse(s)
 return q.removeSplitter()
def ring(x,y,z,r,ri,h):return cy(x,y,z,r,h).cut(cy(x,y,z,ri,h))
def nut(x,y,z,af,h,ri):
 pts=[V(x+af/math.sqrt(3)*math.cos(math.pi/6+i*math.pi/3),y+af/math.sqrt(3)*math.sin(math.pi/6+i*math.pi/3),z) for i in range(6)];f=Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges));return f.extrude(V(0,0,h)).cut(cy(x,y,z,ri,h))
g=D.getObject('CF17_ONE_COHERENT_FRONT_MATERIAL_AND_PORTS') or D.addObject('App::DocumentObjectGroup','CF17_ONE_COHERENT_FRONT_MATERIAL_AND_PORTS')
def add(n,s,col=(.28,.55,.6),scope='PRINT_NOMINAL_CONDITIONAL'):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;g.addObject(o)
 if not hasattr(o,'Scope'):o.addProperty('App::PropertyString','Scope')
 o.Scope=scope;return o
D.save()
# ONE fixedlayer height derived from fullcompletejoint vs headceiling:
# 141+(137.5+1.25-135.1)=144.65 minimum; choose145 in roofinterval.
zz=D.getObject('Pi4B_actual_PCB').Shape.BoundBox.ZMin
if abs(zz-141)<1e-5:
 for nn in ['Pi4B_actual_PCB','Pi_components_and_cooling']:
  D.getObject(nn).Placement.Base+=V(0,0,4)
else:assert abs(zz-145)<1e-5
piz=4
def bxp(x,y,z,a,b,c):return bx(x,y,z+piz,a,b,c)
def cyp(x,y,z,r,h,axis=V(0,0,1)):return cy(x,y,z+piz,r,h,axis)
def ringp(x,y,z,r,ri,h):return ring(x,y,z+piz,r,ri,h)
def nutp(x,y,z,af,h,ri):return nut(x,y,z+piz,af,h,ri)
put('derived-one-fixed-layer.json',{'minimum_PCB_Z':144.65,'chosen_PCB_Z':145,'admissible_roof_max_PCB_Z':154.67,'basis':'Actual8mmcompletePi screw/nut+carrier againstyawhousing: -20caseactualnutcommon.74338 and.519gap. Retainall2MG/range; placeWHOLEfixedcomputer+ports+POWER+landingabove137.5rigidceiling with1.25. No shafttrim/headflip/newPi orientation; entirefixedlayerup4 once, no otherboards auto moved.','all_new_Pi_steel_minZ':139.1,'housing_ceiling':137.5,'guaranteed_vertical_gap':1.6,'new_Pe':[-80.5,-16.5,152.1],'source_family':'same200 width+roll length law updatesendframe, no newcable/R/range','new_GPIO_exit_top':176.48,'roof189_preserved':True})
# Primary datum is the actualfourholes/PCBplanes read from currentPi, notoldWORLD.
origin=V(-126,-28,145);ct=json.loads((P.parent/'n01-pi-full-port-contract.json').read_text(encoding='utf-8'))
fields=[]
for r in ct['parts']:
 x0,y0,x1,y1=r['official_footprint_board_XY_mm'];q=bx(origin.x+x0,origin.y+y0,146.6,x1-x0,y1-y0,r['official_drawing_label_Z_mm']);o=add('CF17_PI_PRIMARY_'+r['role'],q,(.5,.58,.72),'OFFICIAL_FOOTPRINT_CONSERVATIVE_HEIGHT_NOT_SUPPLIER_SOLID');o.ViewObject.Transparency=70;fields.append(o.Name)
add('CF17_PI_SMALL_TOP_COMPONENT_BUDGET',bxp(-126,-28,142.6,85,56,4),(.65,.7,.8),'PROJECT_4mm_NOT_ACTUAL_MATERIAL').ViewObject.Transparency=90
add('CF17_PI_MICROSD_BOTTOM_BUDGET',bxp(-128.265,-5.89,138,15.4,11.99,3),(.65,.7,.8),'PRIMARY_SDxy_PROJECT3mm_UNDERSIDE').ViewObject.Transparency=75
# Keep entire originalcooling envelope; classify air/possiblecooler correctly.
D.getObject('Pi_components_and_cooling').Label='FULL26mm_Pi_COMPONENT_COOLING_AIR_ALLOCATION_not_supplied_cooler_solid';D.getObject('Pi_components_and_cooling').ViewObject.Transparency=85
# Proper selectedfemale1992 matedbody + independentfactorywireexit allowance.
D.getObject('Pi_GPIO1992_factory_female').ViewObject.Visibility=False
add('CF17_POL1992_FULL_MATED_BODY',bxp(-119.05,21.95,144.6,51.1,5.1,14.25),(.35,.5,.75),'SOURCE1992_SELECTED_BODY_mating_PROJECT_FIT')
add('CF17_POL1992_FACTORY_END_REGION',bxp(-119.5,16.5,158.85,52,16,13.63),(.5,.6,.8),'FULL_FACTORY_END_LAY_NOT_RIGID_WIRES').ViewObject.Transparency=80
# WholelargerDATA allocation, nowexplicitUSB_A_rear lowerstacksocket (portchoice).
o=D.getObject('Pi_USB_DATA_Delock_mating');before=o.Shape.Volume;o.Shape=bxp(-38,-13.66,135.1,26,26,24);o.Placement=A.Placement();o.Label='FULL_Lanberg500_DATA_PROJECT26x26x24_at_officialUSB_A_rear_lower';assert abs(o.Shape.Volume-before)<1e-6
power=add('CF17_POWER_DELOCK60047_APPROX_FULL',bxp(-121.3,-42.25,140.2,22,13,8),(.65,.65,.7),'SUPPLIER_APPROX_BODY_mating_PROJECT')
boot=add('CF17_POWER_K1474_SEALED_BOOT_FULL',bxp(-99.3,-45.9,140.2,25,14,8),(.2,.2,.25),'RETAINED_K1474_BOOT_PROJECT_FIT_NO_CUT')
put('primary-Pi-ports-and-power-allocation.json',{'actualholes':'sourcecurrent4axes(-122.5/-64.5,+-24.5), pitch58x49; actualplanes141/142.6; sourceDXF origin(-126,-28,141), components+Z assumedcurrentcomponentface','official_fields':fields,'CSI_primary_shell':[-80.95,-27.7,146.6,-77,-5.3,152.1],'Pe_current':[-80.5,-16.5,152.1],'R2':'FFCactualentryqualifiedagainstnamed11fields andunlabelled4mm, NOTerasing26airfield; actualcoolerprofile/latch/contactsideonebenchsample remains. PrintedframebelowPCB/ventaboveair, no claimedthermalPASS.','DATA':'Lanberg500 complete26x26x24 notshrunk, USB_A_rear lowerprojectcentre(-38,-.66,147.1), notoldunqualifiedY21Ethernetregion; ports/net unchanged, Linuxenumerationlater','POWER':{'Delock':[-121.3,-42.25,140.2,-99.3,-29.25,148.2],'boot':[-99.3,-45.9,140.2,-74.3,-31.9,148.2],'VBUSmouth':[-74.3,-37.15,144.2],'GNDmouth':[-74.3,-40.65,144.2],'frame_binding':'officialUSB_Cxy/actualPCBbottom+3.2 centre, supplier22x13x8approx, engagement/K1474boot25x14x8 projectnotmanufacturer'},'1992':'oldnominalwrongBOXpose withdrawn asunbuiltprojectallocation; fullprimarybody+fullwireendregion preserved at actualheader. Notselectedpart deletion.','wholekit':False,'physicalPASS':False})
D.save()
# Complete Pi jointrevision, nottrimshaft:8mmstandard+1.5landing+1.5standoff.
for o in D.Objects:
 if o.Name.startswith('FS_PI_'):o.ViewObject.Visibility=False;o.Label='RETIRED_UNBUILT12mm_STACK_REFERENCE '+o.Name
pi_sets=[]
for x in [-122.5,-64.5]:
 for y in [-24.5,24.5]:
  tag='CF17_PI_'+str(x).replace('-','m').replace('.','p')+'_'+str(y).replace('-','m').replace('.','p')
  parts=[('M2p5x8_full',cyp(x,y,135.1,1.25,8).fuse(cyp(x,y,143.1,2.25,2.5))),('topwasher',ringp(x,y,142.6,3,1.35,.5)),('bottomwasher',ringp(x,y,137.5,3,1.35,.5)),('fullnut',nutp(x,y,135.5,5,2,1.1))]
  for suffix,s in parts:add(tag+'_'+suffix,s,(.65,.66,.68),'STANDARD_DEMAND_NEEDED_UNCONFIRMED')
  pi_sets.append({'axis':[x,y],'stack':'headunder143.1/topwasher.5+PCB1.6+post1.5+web1.5+bottomwasher.5+fullnut2=7.6; standard8 =>.4tip','full_tipZ':139.1,'fullnutZ':[139.5,141.5]})
# ONE basecarrier: protectedfloor untouched, uses actualtwoexistingN1 topfaces.
rootxs=[-75,85.5]
members=[bxp(-126,-28,138,65,7,1.5),bxp(-126,21,138,65,7,1.5),bxp(-126,-21,138,7,42,1.5),bxp(-68,-21,138,7,42,1.5),bx(-78.5,16.5,134,167.5,7,3)]
for x in [-122.5,-64.5]:
 for y in [-24.5,24.5]:members.append(cyp(x,y,138,3.5,3))
# Usefulintegralbridges into actualrootbeam, nottangentonlycontacts.
members += [bx(-68,21,136.5,7,2.5,6),bx(-78.5,21,136.5,7,7,6)]
# BUS exactsamefull16steel/3mmplate+3posts, opencomponentface+Y.
members += [bx(-47,-19.5,91,54,3,43),bx(-47,-19.5,131.5,5,43,5.5),bx(2,-19.5,131.5,5,43,5.5)]
for x in [-41.5,-4.5]:
 for z in [97,125]:members.append(cy(x,-16.5,z,2.75,3,V(0,1,0)))
# InsulatingPOWERbed andseparateloadlandboot, oneadjustablekeeperlater.
members += [bxp(-129,-49,136,62.5,19.75,4.2),bxp(-125,-31,136,7,10,3.5),bxp(-78,-31,136,7,10,3.5),bxp(-129,-47.5,140.2,62.5,1.6,6)]
q=union(members);uncut=q.copy();cuts=[]
for x in [-122.5,-64.5]:
 for y in [-24.5,24.5]:cuts.append(cyp(x,y,135,1.4,9))
for x in rootxs:cuts += [cy(x,20,123,1.7,18),cy(x,20,136.5,3.7,5)]
# SD insertion/undersideclearance isopenfront, notfloorcut.
cuts.append(bxp(-131,-7.2,136.7,20,14.4,6))
# Realparting forE1keeper fingers andleftrootboss, protectPi lands.
for x in [0,48.5]:cuts.append(bx(x-.2,15.2,129.5,1.9,2,8))
cuts.append(bxp(-79,20.8,137.8,8,3.2,3))
for x in [-41.5,-4.5]:
 for z in [97,125]:cuts.append(cy(x,-22,z,1.1,12,V(0,1,0)))
for x in [-126,-69.5]:
 cuts.append(cyp(x,-38.5,133,1.1,20));cuts.append(bxp(x-2.7,-41.2,134.9,5.4,5.4,2))
for c in cuts:q=q.cut(c)
q=q.removeSplitter();base=add('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER',q)
# SeparateE1topcapture/antirotation, installedAFTERwholePCA/E1, beforePiPCB.
km=[bx(-78.5,16.5,137,167.5,4,2.5)]
for x in rootxs:km.append(cy(x,20,136.5,3.5,3))
for x in [0,48.5]:km.append(bx(x,15.4,130,1.5,1.6,7.8))
k=union(km)
for x in rootxs:k=k.cut(cy(x,20,136.4,1.7,5)).cut(Part.makeCone(1.5,3,1.5,V(x,20,138)))
keeper=add('CF17_REMOVABLE_COMMON_E1_ROOT_KEEPER',k)
# Rootjoint completeCSK16 includesheadlength; bottomwasher/fullnut unchangedplanes.
for o in D.Objects:
 if o.Name.startswith('CB_BRIDGE_'):o.ViewObject.Visibility=False;o.Label='RETIRED_UNBUILT_SOCKET_ROOT_REFERENCE '+o.Name
for i,x in enumerate(rootxs):
 stem=cy(x,20,123.5,1.5,14.5);head=Part.makeCone(1.5,3,1.5,V(x,20,138));add('CF17_ROOT_'+str(i)+'_CSK_M3x16_full',stem.fuse(head),(.65,.66,.68),'STANDARD_DEMAND_NEEDED_UNCONFIRMED')
 add('CF17_ROOT_'+str(i)+'_bottomwasher',ring(x,20,126.5,3.5,1.6,.5),(.65,.66,.68),'STANDARD_DEMAND_NEEDED_UNCONFIRMED');add('CF17_ROOT_'+str(i)+'_fullnut',nut(x,20,124.1,5.5,2.4,1.3),(.65,.66,.68),'STANDARD_DEMAND_NEEDED_UNCONFIRMED')
# OnePOWERpressurekeeper, metalbody insulated fromframe, boot heldindependently.
pm=[bxp(-129,-41,148.2,62.5,5,2)]
for x in [-126,-69.5]:pm.append(cyp(x,-38.5,148.2,3,2))
pk=union(pm)
for x in [-126,-69.5]:pk=pk.cut(cyp(x,-38.5,147.9,1.1,4))
add('CF17_POWER_INDEPENDENT_BOOT_AND_ADAPTER_KEEPER',pk)
for i,x in enumerate([-126,-69.5]):
 add('CF17_POWER_'+str(i)+'_M2x16_full',cyp(x,-38.5,134.5,1,16).fuse(cyp(x,-38.5,150.5,1.9,2)),(.65,.66,.68),'STANDARD_DEMAND_NEEDED_UNCONFIRMED')
 add('CF17_POWER_'+str(i)+'_topwasher',ringp(x,-38.5,150.2,2.5,1.1,.3),(.65,.66,.68),'STANDARD_DEMAND_NEEDED_UNCONFIRMED');add('CF17_POWER_'+str(i)+'_bottomwasher',ringp(x,-38.5,136.6,2.5,1.1,.3),(.65,.66,.68),'STANDARD_DEMAND_NEEDED_UNCONFIRMED');add('CF17_POWER_'+str(i)+'_fullnut',nutp(x,-38.5,135,4,1.6,.9),(.65,.66,.68),'STANDARD_DEMAND_NEEDED_UNCONFIRMED')
put('real-common-carrier-material-checkpoint.json',{'base_valid':q.isValid(),'base_solids':len(q.Solids),'base_volume':q.Volume,'keeper_valid':k.isValid(),'keeper_solids':len(k.Solids),'keeper_volume':k.Volume,'POWERkeeper_valid':pk.isValid(),'POWERkeeper_solids':len(pk.Solids),'POWERkeeper_volume':pk.Volume,'Pi_complete8sets':pi_sets,'root_stack':'twoexistingA17facesZ134/x-75,85.5/Y20; 3mmmaincarrier+3mmkeeperrootboss in.5recess. FullM3CSK16 face139.5 ->tip123.5, fullnut124.1..126.5/.5washer; no topwasher toCSK; facePCBclearance1.5','E1':'realremovabletopkeeper, wholePCA/E1 beforekeeper/Pi; actualsafelandFIT3, no virtualunplug','POWER':'FULLadapter+boot retained withinsulatingbed/outerstop+separatetoppressureland. 2M2x16/fullwashers/nuts+realnutfeedslot/3.3roof. No inventoryassertion/boughtcut.','newmaterial_members':len(members),'beforecutV':uncut.Volume,'explicitowncuts':[str(c.BoundBox) for c in cuts],'member_coverage':'toverifyall outsideexplicitcuts againstfinal, andrealparting/roots/stock. valid1aloneisnotPASS','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t0})
D.recompute();D.save();print(json.dumps({'sourceports_allocated':True,'real_parts':3,'base':[q.isValid(),len(q.Solids),q.Volume],'parting_pending':True,'seconds':time.perf_counter()-t0}))

put('current-primary-port-world-frames.json',{'PCBbottom':145,'PCBtop':146.6,'source_whole_Pi_lift':4,'POWER_adapter':str(D.getObject('CF17_POWER_DELOCK60047_APPROX_FULL').Shape.BoundBox),'POWERboot':str(D.getObject('CF17_POWER_K1474_SEALED_BOOT_FULL').Shape.BoundBox),'W079_mouth':[-74.3,-37.15,148.2],'W080_mouth':[-74.3,-40.65,148.2],'Pe':[-80.5,-16.5,152.1],'GPIO_factory_exit_region_top':176.48,'no_other_bought_module_moves':True})

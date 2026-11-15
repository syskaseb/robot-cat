import FreeCAD as A,FreeCADGui as G,Part,json,hashlib,time,math
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;T=time.perf_counter();OUT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');P=OUT/'day15-shared-module-fit';P.mkdir(exist_ok=True);OLD=OUT/'day14-fasttrack-first-fit/fit-kit-ready'
S=A.getDocument('DAY14_FIT_KIT_READY');D=A.newDocument('DAY15_SHARED_MODULE_PROPOSAL');groups={};retired=[];copied=[]
retire_prefix=['Upper_frame_','Pi_bridge_','Pi_removable_common_tray','BUS_upper_simple_shelf','Logic_common_side_shelf','Logic_shelf_post_','Pi_standoff_']
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 if any(o.Name.startswith(p) for p in retire_prefix):retired.append(o.Name);continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['Status','AssemblyNote','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 copied.append(dict(name=o.Name,source_isSame=q.Shape.isSame(o.Shape)))
props=D.addObject('App::DocumentObjectGroup','NEW_SHARED_SUPPORT_PROPOSAL_NOT_PRINT_RELEASED');hw=D.addObject('App::DocumentObjectGroup','NEW_CLAMP_HARDWARE_NEEDED_UNCONFIRMED');rooms=D.addObject('App::DocumentObjectGroup','NEW_ACCESS_AND_COOLING_NOT_PARTS')
def box(p,s):return Part.makeBox(*s,V(*p))
def bounds(s):
 b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
rows=[]
def feature(n,s,role,group=props,color=(.65,.75,.83)):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;o.addProperty('App::PropertyString','Status').Status='WHOLE_PROPOSAL_UNVERIFIED_NOT_PRINT_PART';o.addProperty('App::PropertyString','AssemblyNote').AssemblyNote=role;group.addObject(o);rows.append(dict(name=n,role=role,bounds_mm=bounds(s),volume_mm3=s.Volume,valid=s.isValid()));return o
def member_union(n,ms,role):
 q=ms[0]
 for s in ms[1:]:q=q.fuse(s)
 assert q.isValid();loss=[s.cut(q).Volume for s in ms];assert max(loss)<1e-5
 o=feature(n,q,role);rows[-1].update(member_missing_mm3=loss,solids=len(q.Solids));return o
# Two flat end-portals, not a new fullrobotarchitecture. Their outerlegs avoid the completebankcase sides.
front=member_union('CF_front_portal',[box((-104,-86,48.52),(6,6,47)),box((-104,80,48.52),(6,6,47)),box((-104,-86,92.52),(6,172,3))],'Fronttwoedgeclamps -> uprightoutsidebank -> fullcrossbeam. FlatprintplaneX future; joints/stock remainproposal.')
rear=member_union('CF_rear_portal',[box((95,-86,48.52),(12,6,58.48)),box((95,80,48.52),(12,6,58.48)),box((95,-86,103),(12,172,4)),box((95,-20,88),(4,6,19)),box((95,16,88),(4,4,19))],'Rearportal crosses ABOVE fivecompleteFHAC at103>=101+2, fixedbodyS0notmoved; inward links clearbattery86.5 by1.5.')
for cy,w in [(-17,6),(18,4)]:feature('CF_long_rail_'+str(cy).replace('-','m'),box((-98,cy-w/2,88),(193,w,8)),'Commoninnerrails ABOVEbattery and INSIDEXT60/AUX lanes; fourboltedendfaces toportals, M3endjoin qualificationOPEN.')
# Shared/removable plates, coarseoccupiedload interfaces, no detailedPCBcasefeatures or exports.
pi=box((-101,-41,92.52),(91,62,3));feature('CF_Pi_shared_tray',pi,'Two common innerrails carryPi via realfourCADholeposts; installed trayendbolts/detailsOPEN. FullPiandfactorymates stayworldposes.')
actualPiHoles=[(-16.5,-34.5),(-74.5,-34.5),(-16.5,14.5),(-74.5,14.5)]
for i,(x,y) in enumerate(actualPiHoles):feature('CF_Pi_post_'+str(i),Part.makeCylinder(2.5,3,V(x,y,95.52)).cut(Part.makeCylinder(1.375,3,V(x,y,95.52))),'ActualsourceCAD r1.375hole axis ->3mmnominalinsulatingstandoff; M2.5 retention andactualundersidefit remaintrial.')
feature('CF_power_logic_ledge',box((55,18.5,88.52),(71,31.5,4)),'CommonMAIN/AUX ledge top92.52 ->boardbottom94, nominal1.48insulationstandoffs; realhole/edgecaps unqualified. No contact waiver.')
feature('CF_upright_logic_strip',box((-96,34,90),(122,8,4)),'Shared uprightAdafruit/E1 loweredge strip; splitopen clamps on realPCBedge, pressure/ports/actualhole fitOPEN beforedetailing.')
bus=D.getObject('BUS25514_installed');bs=bus.Shape.copy();bs.translate(V(98,-12.5,-16));bus.Shape=bs;bus.AssemblyNote='WholeBUS25514 movedtoX18..60/Y-16.5..16.5/Z110..134. Replaces ABOVE-Pi stack with separatecentralbridge; allfactorypower/USB ends preserved, actualports&lengthstrialOPEN.'
feature('CF_BUS_removable_bridge',box((12,-23,104),(54,46,3)),'CentralremovableBUSbridge top107+3mmstandoff ->BUS110; two crossarms2commonlegs toinnerrails; removeBEFOREbattery, disconnectONLYexistingUSB/powerends, neverE1solder.')
for x in [12,62]:feature('CF_BUS_bridge_leg_'+str(x),box((x,-20,96),(4,40,8)),'Broadsharedbridgeverticalweb toinnerrails, actualbutt/fasteningpartingOPEN; no wholemountPASS.')
# Whole clamps around existingprinted deckedge. Purposeful two-sided jaws, no purchasedframehole.
clamps=[]
for rearflag,xc,xlo,xhi,sx,L in [(False,-101,-112,-91,-110,12),(True,101,89,110,92,16)]:
 for sign in [-1,1]:
  y=84*sign;yy=79.5 if sign>0 else -88
  plate=D.getObject('P03_rear_deck_integrated_load_yoke' if rearflag else 'P02_front_deck').Shape
  upper=box((xlo,yy,48.52),(xhi-xlo,8.5,3));lower=box((xlo,yy,39.52 if rearflag else 43.52),(xhi-xlo,8.5,6 if rearflag else 2)).cut(plate)
  # Nativeaxis outsidephysicalplateedge; bothjaws have actualclosedsteelprofile/clearance, not gluedbearing.
  hole=Part.makeCylinder(1.65,20,V(sx,y,35));upper=upper.cut(hole);lower=lower.cut(hole)
  tag=('R' if rearflag else 'F')+('p' if sign>0 else 'm');feature('CL_'+tag+'_upper',upper,'Actualflatupperbearing at48.52, ≥2.5mmedgeoverlap; sameprintedfoundation retained. ONEcoarsewholeclampbeforeprints.')
  feature('CL_'+tag+'_lower',lower,'Sourceconformingstepjaw copiedfromactualplateunderside; not arbitrary3mmassumption; operatesmatchedcontact, slidefromopenedge beforebankinstallation.')
  under=51.52;tip=under-L;washerTop=39.52 if rearflag else 43.52;nutTop=washerTop-.5
  screw=Part.makeCylinder(1.5,L,V(sx,y,tip)).fuse(Part.makeCylinder(2.75,3,V(sx,y,under)));feature('CL_'+tag+'_M3x'+str(L),screw,'Complete nominalstandard M3x'+str(L)+'; fullshafttip/head, demandUNCONFIRMED',hw,(.55,.55,.58))
  washer=Part.makeCylinder(3.5,.5,V(sx,y,washerTop-.5)).cut(Part.makeCylinder(1.65,.5,V(sx,y,washerTop-.5)));feature('CL_'+tag+'_washer',washer,'FullOD7x0.5 lowerwasher; realclampingseat',hw,(.55,.55,.58))
  R=5.5/math.sqrt(3) if False else 5.5/(3**.5);pts=[V(sx+R*math.cos(j*math.pi/3),y+R*math.sin(j*math.pi/3),nutTop-2.4) for j in range(7)]
  nut=Part.Face(Part.Wire(Part.makePolygon(pts).Edges)).extrude(V(0,0,2.4)).cut(Part.makeCylinder(1.5,2.4,V(sx,y,nutTop-2.4)));feature('CL_'+tag+'_nut',nut,'FullAF5.5x2.4 nut; threadsnotfactoryconfirmed',hw,(.55,.55,.58))
  clamps.append(dict(tag=tag,upper='CL_'+tag+'_upper',lower='CL_'+tag+'_lower',plate='P03_rear_deck_integrated_load_yoke' if rearflag else 'P02_front_deck',axis=[sx,y],M3_length=L,underhead=under,tip=tip,washer_top=washerTop,nut_z=[nutTop-2.4,nutTop],purpose='completejaw/sourceplate/stock/assemblycontactgate FIRST; not assumed bearing'))
# Port/cooling/handlay reservations are explicitlynotmaterial.
for n,p,s,role in [('CF_Pi_air_open',(-98,-38,126.12),(85,56,8),'Actualnominalcoolingtop126.12 +8mmopentop; coolingnotthermalqualification'),('CF_right_handlay',(30,22,104),(126,25,25),'Power/logicopenfanabovecommonledge, countsbranchlocallybeforeclamps; actualwires/ends/RstockOPEN'),('CF_BUS_access',(15,-23,134),(48,46,6),'BUSUSB/powerplughandlay onopenbridge beforebackskin; exactsupplierportnormalunverified')]:
 o=feature(n,box(p,s),role,rooms,(.9,.57,.2));o.ViewObject.Transparency=85
D.Label='DAY15 whole shared module proposal — UNVERIFIED';D.recompute();A.setActiveDocument(D.Name);G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();D.saveAs(str(P/'shared-module-proposal.FCStd'))
electrical=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/electronics/kicad-current/design.json')
plan=dict(status='SAVED_WHOLE_PROPOSAL_BEFORE_FIRST_CHEAP_FALSIFIER',created_utc=datetime.now(timezone.utc).isoformat(),parent_manifest=dict(path=str(OLD/'manifest.json'),sha256=hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest()),electrical_source=dict(path=str(electrical),sha256=hashlib.sha256(electrical.read_bytes()).hexdigest()),document=D.Name,objects=len(D.Objects),native_file=D.FileName,retired_UNBUILT_references=retired,retained_identities=copied,proposed_members=rows,clamp_plan=clamps,Pi_source_hole_axes=actualPiHoles,BUS_new_bounds=bounds(bus.Shape),foundation_shapes_UNCHANGED=True,purchased_parts_moved=['BUS25514_installed whole nominalfullbox only'],all_other_purchased_poses='unchanged',first_falsifier='FOUR WHOLEDECKEDGECLAMPS realcontact andfullnewstandardmetal vsnearbyactual126sourcesolids/nofullcompound; bankcase/stock/ports afteractualroot',whole_hypothesis='Two externalendportals onfourclampstoexistingprinteddeck; twoinnercommonrails abovebattery; separatePi left/fullBUS onremovablecentralbridge; currentMAIN/AUXoncommonoutboardledge/uprightlogicstrip. SupportsareWHOLE replaceunbuiltoldrails/trays, not local1mmoffset. Originalfoundation/S0/headtail/sourceworld retained.',factory_stock='4independent220/bothMTAends/fullUSB500Delock/5FHAC>=84.5/K1474Pi350 vsinput210 remain realuntrimmedsourcebudgets; installedreach/slackNULL',remaining=['Allnewclamp/source/toolandjointsUNVERIFIEDbeforegate','boardedge/holes+insulatingstandoffs+S0S1bankretention sharedpressure detailsOPEN','12ATOwholecaseand5FHACfullleads currentretained, actualshortendsnotqualified','batterybridge mustremoveafterdisconnectingactualfactoryBUSends, E1soldernevervirtualdisconnect','source8axis/thread/revision/payload/motion remainphysicalFIT1','sensor/audio/headtailinterfaces/Olaoriginalreference retained, notproductionmount/skin'],physical_pass=False,print_release=False,wall_build_seconds=time.perf_counter()-T)
(P/'proposal.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'savedbeforetests':D.FileName,'objects':len(D.Objects),'retired':len(retired),'newmembers':len(rows),'seconds':plan['wall_build_seconds']}))

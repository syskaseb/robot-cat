import FreeCAD as A,FreeCADGui as G,Part,json,math,hashlib,time
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;changes=[];t0=time.perf_counter()
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def wr(n,d):(P/n).write_bytes((json.dumps(d,indent=2)+'\n').encode())
def move(n,p,rot=None):
 o=D.getObject(n);before=bb(o.Shape);vol=o.Shape.Volume
 if rot:o.Placement=A.Placement(V(),rot).multiply(o.Placement)
 b=o.Shape.BoundBox;o.Placement.Base+=V(*p)-V(b.XMin,b.YMin,b.ZMin)
 changes.append({'name':n,'before':before,'after':bb(o.Shape),'before_volume':vol,'after_volume':o.Shape.Volume});return o
for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female']:
 b=bb(D.getObject(n).Shape);move(n,[b[0],b[1]-20,b[2]])
for o in D.Objects:
 if o.Name.startswith('FORE_PI_') and hasattr(o,'Shape'):
  o.Placement.Base+=V(0,-20,0)
  if o.Name.endswith('_screw'):
   b=o.Shape.BoundBox;x=(b.XMin+b.XMax)/2;y=(b.YMin+b.YMax)/2
   o.Shape=Part.makeCylinder(1.25,14,V(x,y,41.62)).fuse(Part.makeCylinder(2.25,2.5,V(x,y,55.62)));o.Placement=A.Placement();o.Label='NEW_DEMAND_M2.5x14_COMPLETESET_NOT_CUT_SUPPLIER; old16role superseded'
# Whole coupled power input pairs: same-facing mouths, never case-chord credit.
move('PBAY_P_SYS',[-26,-85.5,124.5]);move('PBAY_F_PI',[-55,-46,119.875])
move('PBAY_P_REAR',[78,-72.5,58.5],A.Rotation(V(0,0,1),90));move('PBAY_F_AUX',[49,-33,53.875],A.Rotation(V(0,0,1),-90))
move('WAGO615_power_0_0',[-35,-80,54]);move('WAGO615_power_0_1',[8,-80,54]);move('PBAY_P_AUX',[3,-43,88])
move('F0_FHAC0002_30A',[102,-88,47],A.Rotation(V(0,0,1),90));move('PBAY_POST_F0',[102,-13,47]);move('XT60H_mated_with_boots',[106,-60,75])
# Whole soldered control kit, explicit common rigid transform, not virtual E1unplug.
T=A.Placement(V(0,109,112),A.Rotation(V(1,0,0),90))
for n in ['PCA9685_Adafruit815_PCB','E1_populated_prototype_board']:
 o=D.getObject(n);before=bb(o.Shape);vol=o.Shape.Volume;o.Placement=T.multiply(o.Placement);changes.append({'name':n,'before':before,'after':bb(o.Shape),'before_volume':vol,'after_volume':o.Shape.Volume,'wholekit_transform':'Rx90 + (0,109,112)'})
move('BNO085',[52,12.4,104],A.Rotation(V(1,0,0),90));move('BUS25514_installed',[-38,-21,140]);move('ReSpeakerLite_on_REMOVABLE_back',[14,-24,145]);move('TTP223_touch',[-68,-6,147]);move('Monitor_MOD05015',[106,-96,106])
# Unbuilt old stationaryholder/steel roles are not operating mounts at newposes.
ret=[]
for o in D.Objects:
 if o.Name.startswith(('BUS_','PCA__','BNO__','MIC_','E1_T18I_')) and hasattr(o,'Placement') and hasattr(o,'Shape'):
  o.ViewObject.Visibility=False;ret.append(o.Name)
for n in ['HN_FFC_NEUTRAL_ALLOCATED_FULL_PROFILE','RG_REJECTED_BODY_RETURN_CAPACITY']:
 o=D.getObject(n)
 if o:o.ViewObject.Visibility=False
# A source-preserving outline PROPOSAL, not printable mass or closure evidence.
# Rounded cross-sections vary shoulder/belly/rump longitudinally, no flatwindow.
def section(x,half,lo,hi):
 z=(lo+hi)/2;h=(hi-lo)/2;k=.82;edges=[]
 for ps in [[(0,h),(k*half,h),(half,k*h),(half,0)],[(half,0),(half,-k*h),(k*half,-h),(0,-h)],[ (0,-h),(-k*half,-h),(-half,-k*h),(-half,0)],[(-half,0),(-half,k*h),(-k*half,h),(0,h)]]:
  b=Part.BezierCurve();b.setPoles([V(x,y-3,z+zz) for y,zz in ps]);edges.append(b.toShape())
 return Part.Wire(edges)
stations=[(-153,53,50,119),(-130,105,38,145),(-90,114,36,158),(-35,113,37,167),(25,111,39,168),(85,107,41,159),(137,101,47,155),(161,40,68,129)]
skin=Part.makeLoft([section(*q) for q in stations],True,False)
# Functionalsourcefullkey/monitor/speaker/USB protrusions left visible; no new
# claim of skin joints/FOV/cooling or closed physical acceptance.
D.getObject('NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT').Shape=skin;D.getObject('NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT').Placement=A.Placement();D.getObject('NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT').ViewObject.Visibility=True
D.getObject('NIGHT_HEAD_PROPORTION_ENVELOPE_NOT_PRINT').ViewObject.Visibility=True
wr('whole-layout-functional-decision.json',{'module_changes':changes,'printed_mounts_retired_only_unbuilt':ret,'body_stations_X_halfwidth_low_high':stations,'body_SCOPE':'PROVISIONAL_NOT_PRINT_NOTMASS sourceparts mayprotrude explicitly nothidden','support_function':'sourceP01 -> received2gridhalves+integralheadroot retained. WholePiU/outboardreceivers need functionalrevision; oldintegralPiU material NOTvirtuallydetached. Commonverticalcontrolplane rooted at existingfront/rear gridlands beforebanks; detailedjoints notyetrealized. Not securedmodules.','Pi_complete_new_demand':'4fullM2.5x14 underhead55.62/tip41.62/nut43.02..45.02/2washers samefullgeometry moved20Y; NOTsuppliercut/availabilityunconfirmed; finitegate first.','control_plane':'PCA+E1 wholeRx90; populated/headerleading space mustremain open negativeY. BNO commonplane, BUS/MIC above removablebeforecell.','all12MTA71p43and16WAGO415and8inline':'retained positions;4MTA0100335requiredUNBOUND,no inventedbox/220credit','actualcuts_slack':None,'physicalPASS':False,'wholekit':False})
pairs=[]
for role,face,ys,yf,z in [('W043',-4,-67,-35,130),('XA01',100,-54,-22,64)]:
 for raw in [84.5,94.5]:
  ell=(raw-14-math.pi*16)/2
  pairs.append({'unit':role,'raw':raw,'strip_sameunit':14,'R':16,'straight_each':ell,'analytic_outside_length':2*ell+math.pi*16,'raw_accounted':14+2*ell+math.pi*16,'start_project':[face,ys,z],'end_project':[face,yf,z],'middlecavity_assignment':'logical5W043/logical1XA01 ->projectphysicalmiddle C, otherlogicalportsA/B/D/E unique; allfive commonnodegraphpreserved','entry_normals':'both+X, semicircle tangents +X/-X; nominalenddatum physicalFITnot mfg coordinate','field_bbox':[face,ys-1.95,z-1.95,face+ell+16+1.95,yf+1.95,z+1.95],'profile':'OD3.1+.4outer =r1.95; foreign1.25 outsidefield','no_delivery_reachPASS':True})
wr('two-factory-only-unit-whole-upperplans.json',{'rows':pairs,'methods':'two true straightsegments plussemicircle, not chordasroute; largest raw94.5 variablelongerlegs accommodates surplus; minraw84.5 includesbare/14once','pose_assumptions':'FHACcase inputend chosen+X byfullunit installation. WAGO615 faceprimary+X; exactmiddlemouth/exitdatum still physicalsample/FIT, no fakecataloguepitch.','no_extra5credit':True,'XA01_notcustomextension':True,'W077_XA02_XBcomposites':'existingproperlap/HELU contracts kept, currentrouteupper pending, notall84.5direct','actualcut':None})
D.recompute();D.save()
# FIRST finite changedmodule occupiedgate only; box overlap is not collision.
checks=[]
targets=[('Pi_GPIO1992_factory_female','RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER'),('PBAY_F_PI','BUS25514_installed'),('PBAY_F_PI','PCA9685_Adafruit815_PCB'),('E1_populated_prototype_board','BNO085'),('PBAY_F_AUX','Battery_GEA223S30X6GT'),('PBAY_F_AUX','F0_FHAC0002_30A'),('Monitor_MOD05015','S0_key'),('BNO085','S0_body')]
for a,b in targets:
 x=D.getObject(a).Shape;y=D.getObject(b).Shape;dist=x.distToShape(y)[0];checks.append({'a':a,'b':b,'gap':dist,'threshold':1.25,'valid':x.isValid() and y.isValid(),'scope':'actualshape/currentnominalallocation NOT physicaldelivery'})
 wr('first-coupled-whole-module-gate.json',{'rows':checks,'cursor':len(checks),'remaining':len(targets)-len(checks),'wholePASS':False})
 if dist<1.25-1e-7:break
print(json.dumps({'saved':D.FileName,'changes':len(changes),'firstgate':checks,'seconds':time.perf_counter()-t0}))

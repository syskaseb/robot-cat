import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def fu(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def vol(s):return 0.0 if s.isNull() or len(s.Vertexes)==0 else s.Volume
def outside(a,b,c):
 d=a.cut(b)
 return 0.0 if d.isNull() or len(d.Vertexes)==0 else vol(d.cut(c))
def outside3(a,b,c,d):
 e=a.cut(b)
 if e.isNull() or len(e.Vertexes)==0:return 0.0
 e=e.cut(c)
 return 0.0 if e.isNull() or len(e.Vertexes)==0 else vol(e.cut(d))
def run():
 # Functional change after two head-facing occupiedfields: accessibleOUTER
 # serviceface inside the body sidebay. Not a sequence of tinyclearance nudges.
 tr=A.Placement(V(0,-134.4,156),A.Rotation(V(1,0,0),180))
 for o in D.Objects:
  if o.Name in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating'] or o.Name.startswith('FS_PI_'):o.Placement=tr.multiply(o.Placement)
 # Whole2FL inlinebodies receive the sameleg upperhandlay zone, notlongerleads.
 # MTA0100335 stillUNBOUND; dependent factoryreach is explicitlyOPEN.
 for n in ['NIGHT_INLINE_FL_W041','NIGHT_INLINE_FL_W026']:
  D.getObject(n).Placement.Base+=V(0,0,23)
 source=Part.Shape();source.read(str(P/'source88-RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER.brp'))
 centres=sorted(set((round(f.Surface.Center.x,4),round(f.Surface.Center.z,4)) for f in D.getObject('Pi4B_actual_PCB').Shape.Faces if hasattr(f.Surface,'Radius') and abs(f.Surface.Radius-1.375)<1e-6))
 ribs=[bx(x-3,-63.4,45.52,6,3,64.48) for x in [-102.5,-44.5]]+[bx(-108,-63.4,z,69,3,6) for z in [50,99.5]]
 posts=[Part.makeCylinder(3.5,3,V(x,-66.4,z),V(0,1,0)) for x,z in centres];arms=[bx(x,-63.4,45.52,6,41.4,3) for x in [-100,-45]]
 bores=fu([Part.makeCylinder(1.4,10,V(x,-68,z),V(0,1,0)) for x,z in centres]);planned=fu(ribs+posts+arms).cut(bores);front=source.fuse(planned).cut(bores)
 rear=D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER').Shape
 root=D.getObject('NIGHT_YTAIL_FIXED_RECEIVER_ROOT').Shape;old_rear=rear.copy();junction=rear.common(root).Volume
 # The entireFIXEDtailreceiver is now really oneprint with reargrid/cradle,
 # while servo/bearing/caps/rotatingroot remain separate and sourceunchanged.
 integrated=rear.fuse(root)
 # Purposeful open powerwindows through crossbars; this is an OPEN loadgrid,
 # not the protective bodyfloor. ParallelY22.5rails and outerperimeter remain.
 cuts=[]
 for n in ['PBAY_F_HP','PBAY_F_TY']:
  b=D.getObject(n).Shape.BoundBox
  cuts.append(bx(b.XMin-1.25,b.YMin-1.25,40,b.XLength+2.5,b.YLength+2.5,30))
 # Explicit planned rail-top rebate below wholecell, leaving5.23mm section.
 b=D.getObject('Battery_GEA223S30X6GT').Shape.BoundBox
 cuts.append(bx(b.XMin-1.25,b.YMin-1.25,b.ZMin-1.25,b.XLength+2.5,b.YLength+2.5,25))
 # Complete real open portwindow in own OPEN loadgrid belowfullGPIOunit.
 # MainP01rails/anchors and Pi receivingarms are outside this sidewindow.
 b=D.getObject('Pi_GPIO1992_factory_female').Shape.BoundBox
 cuts.append(bx(b.XMin-1.25,b.YMin-1.25,40,b.XLength+2.5,b.YLength+2.5,22))
 void=fu(cuts);newrear=integrated.cut(void);front=front.cut(void)
 D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER').Shape=front
 D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER').Shape=newrear
 D.getObject('NIGHT_YTAIL_FIXED_RECEIVER_ROOT').ViewObject.Visibility=False
 D.recompute();D.save()
 put('completed-functional-interface-current.json',{'Pi_bounds':{n:bb(D.getObject(n).Shape) for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating']},'Pi_end':[-86.5,-73.5,94.5],'Pi_primary':centres,'Pi_complete12mmsets':4,'Pi_sourcePCB_holes_notnames':True,'sideinterface':'wholeportside OUTERnegativeY accessible beforelatecovers, within currentbodyreference; GPIOlow/componentsawayfromhead; no boughtshape reduction','twoFLinline':'whole2selectedbodies raised23 to sameleg handlayregion110..118.9; no extraunit/leadcredit; MTA0100335fullunit/factoryreach UNBOUND remains OPEN','rear_integral_realization':{'old_fixed_root_separate_role_retired':True,'actual_positive_material_junction_before_union':junction,'fixed_tailroot_missing_except_declaredpowerwindows':outside(root,newrear,void),'all_planned_rear_missing':outside(integrated,newrear,void),'new_added_vs_integrated':vol(newrear.cut(integrated)),'actualparting':'OnlyOWNfixedtailroot+OWNreargrid/cradle one realunder256print; fullbearings/MG/horn/caps/rotatingparts notfused orhidden','retired_reference_object':'NIGHT_YTAIL_FIXED_RECEIVER_ROOT hidden, referencegeometrykept; NOT2operatingprints'},'purposeful_voids':[bb(q) for q in cuts],'protected_remaining_loadroutes':['twoP01Y22.5parallelrails; afterbatteryrebate thickness5.23','outerpositiveYperimeter; negativeYside functionalGPIOwindow replacesblockedperimetersection','source8holes/fullgridlapM3sets unchanged','tailbase7mm/web7mm/topbridge preserved outside declaredsourceintersections'],'front_valid':front.isValid(),'rear_valid':newrear.isValid(),'front_solids':len(front.Solids),'rear_solids':len(newrear.Solids),'separate_common':vol(front.common(newrear)),'plannedfront_missing_except4bores_anddeclaredpowerwindows':outside3(source.fuse(planned),front,bores,void),'manufacturing':'front/rearactualprintparting unchanged atlap; rearintegralroot needs orientation/supportFIT; no slicer/strengthPASS','initiallay':['baregridsplicesteel/nuts beforecases andwholeE1kit','Pi4full12mmthroughsets loaded fromouterY beforeinlineFL andheadsideclosures; wholeportsideaccessible','tailfixedbearingcartridge/caps install onintegralreceiver beforeF0/S0 andlatecovers; no virtualintegralrootdetach','F0 rests onrealcradle and2actualslottedtiebridges; plasticcasecontact/selectedtiefeed/locking onephysicalFIT3, not wirepull','fullpreterminatedMTA/E1/servoJR remainwhole; bodycoverslast; cellaccess partialdemountOPEN'],'wholekit':False,'physicalPASS':False})
 print(json.dumps({'frontsolids':len(front.Solids),'rearsolids':len(newrear.Solids),'integraljunction':junction,'Piend':[-86.5,-73.5,94.5]}))
run()

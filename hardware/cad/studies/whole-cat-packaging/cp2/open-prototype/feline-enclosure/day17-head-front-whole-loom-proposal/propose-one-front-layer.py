import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
def put(n,j):(P/n).write_bytes((json.dumps(j,indent=2,ensure_ascii=False)+'\n').encode())
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
D.save();moves=[]
# One WHOLE fixed computer orientation, not translated mouth/port alone.
C=V(-83.5,-67.2,78);newC=V(-83.5,0,141.8);R=A.Rotation(V(0,0,1),180).multiply(A.Rotation(V(1,0,0),-90));T=A.Placement(newC-R.multVec(C),R)
pi=['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating']+[o.Name for o in D.Objects if o.Name.startswith('FS_PI_')]
for n in pi:
 o=D.getObject(n);before=bb(o.Shape);vol=o.Shape.Volume;o.Placement=T.multiply(o.Placement);moves.append({'object':n,'before':before,'after':bb(o.Shape),'volume_before':vol,'volume_after':o.Shape.Volume})
# Rotate the full camera board/package and complete existing nominal sets about
# the primary optical axis. Full ToF and gimbal mechanism remain unchanged.
cam=D.getObject('Camera3_NoIR_Wide');optical=cam.Placement.multVec(V(12.5,14.4,0));Rc=A.Rotation(V(1,0,0),180);Tc=A.Placement(optical-Rc.multVec(optical),Rc)
camnames=['Camera3_NoIR_Wide','CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT','CAMERA_SOURCE_OPTICAL_WINDOW_REFERENCE']+[o.Name for o in D.Objects if o.Name.startswith('CAM_primary_upper_') or (o.Name.startswith('CAM_standoff_') and bool(o.ViewObject.Visibility))]
for n in camnames:
 o=D.getObject(n);before=bb(o.Shape);vol=o.Shape.Volume;o.Placement=Tc.multiply(o.Placement);moves.append({'object':n,'before':before,'after':bb(o.Shape),'volume_before':vol,'volume_after':o.Shape.Volume})
C0=Tc.multVec(V(-206.85,0,134.6));Pe=T.multVec(V(-86.5,-73.5,94.5))
put('one-whole-front-proposal.json',{'moves':moves,'source_endpoint_identity':{'predecessor_C0':[-206.85,0,134.6],'predecessor_PiCSI':[-86.5,-73.5,94.5],'baseline_identity':'source1a209 retained placements read; earlier endpoint constructor poses matched; physical mouth stillnominal','camera_optical_axis_world':list(optical),'new_camera_C0':list(C0),'new_Pi_CSI':list(Pe),'camera_exit_tangent':list(Rc.multVec(V(0,0,-1))),'Pi_entry_tangent':list(R.multVec(V(0,1,0))),'camera_width':list(Rc.multVec(V(0,1,0))),'Pi_width':list(R.multVec(V(0,0,1)))},'hypothesis':'Fixed upperfore computer plane below existingroof, USB/Delock rearward; camera clocked180 about unchanged opticaxis; upperneck open handlaid FFC/ToF/JR receivinglayer. Same2MG/bearings/horns/ranges. No Pi on movinghead.','support_functions_invalidated':['oldverticalPi4posts+portfacing+cooling/access','camera2nominalholes/lands rotated whole; newcarrier mustrealize','oldBUS/E1bridge cannot be selected unchanged where it crosses newPi plane; one removable shared forecrossbar mustreplace its supportfunction'],'retained_proofs':'A17 floor/sourceP01/4H01/decksplice protectedshape identity; speaker-cowl gaps identity, no replay','affected_ports':['CSI200 whole','Pi GPIO1992 wholefemale/BNO/PCA/TTP fanout','USB-C K1474 sameONEpair andproperdebits','USB_DATA Delock/full500 ifselected','USB_AUDIO MIC wholeunit unknown','BUS/E2 fourindependent225min220, no credit fromFTA looms','coolingair intaketoheadside/outlet throughlateuppercowl; actualfan/chips/sourcecoolfield preserved'], 'camera_image_rotation':'180frame orientation mustbe accounted before eventualcamera use; noROS/power now','no_material_or_STL':True,'wholekit':False,'physicalPASS':False,'actualfit':None,'cut':None,'installedslack':None})
# A plane/skeleton, explicitly NONMATERIAL, marks assembly and load concept.
g=D.addObject('App::DocumentObjectGroup','AFT_WHOLE_FRONT_PROPOSAL_NOT_MATERIAL')
def ref(n,s,col):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.LineColor=col;o.ViewObject.Transparency=55;g.addObject(o);return o
ref('AFT_FIXED_Pi_RECEIVER_PLANE_NOT_PRINT',Part.makePlane(85,56,V(-126,-28,138),V(0,0,1)),(.2,.65,.85))
ref('AFT_FIXED_LOADPATH_LINES_NOT_MATERIAL',Part.makeCompound([Part.makeLine(V(-120,-22.5,48.52),V(-120,-22.5,138)),Part.makeLine(V(-45,22.5,48.52),V(-45,22.5,138))]),(.2,.65,.85))
# No inferred attachment just from line endpoints. Actual floorreceiver support
# and complete platefixings are deferred until this whole proposal is credible.
D.recompute();D.save();print(json.dumps({'new_C0':list(C0),'new_PiCSI':list(Pe),'camera_optic':list(optical),'moved':len(moves),'no_newprint':True}))

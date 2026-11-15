import FreeCAD as A, FreeCADGui as G, Part, math, json, hashlib
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector
S=A.getDocument('DAY15_P12_INTEGRATED')
P=Path(S.FileName).parent.parent/'day15-head-ola-whole-proposal'
P.mkdir(exist_ok=True)
D=A.newDocument('DAY15_HEAD_OLA_WHOLE')
groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label
 q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in o.PropertiesList:
  if prop in ['Source','Notes','Kind','SourcePath','SourceSHA256','Role']:
   try:q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
   except Exception:pass
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def ew(x,y,z,ry,rz,lower=1):
 pts=[]
 for i in range(64):
  a=2*math.pi*i/64;si=math.sin(a)
  pts.append(V(x,y+ry*math.cos(a),z+rz*si*(lower if si<0 else 1)))
 c=Part.BSplineCurve();c.interpolate(pts,PeriodicFlag=True);return Part.Wire(c.toShape())
cos=D.getObject('Ola_ENVELOPE_not_print') or D.addObject('App::DocumentObjectGroup','Ola_ENVELOPE_not_print')
for o in D.Objects:
 if o.Name.startswith('Ola_') and hasattr(o,'Shape'):cos.addObject(o)
def put(n,s,col=(.10,.105,.12)):
 assert s.isValid(),n
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Transparency=0;o.ViewObject.Visibility=True
 if o not in cos.Group:cos.addObject(o)
 if 'ProposalStatus' not in o.PropertiesList:o.addProperty('App::PropertyString','ProposalStatus')
 o.ProposalStatus='PROPOSED_NOT_PRINTSKIN_NOT_LOAD_ROOT; opticalFOV_and_motion_NOT_qualified'
 return o
before={o.Name:hashlib.sha256(o.Shape.exportBrepToString().encode()).hexdigest() for o in S.Objects if hasattr(o,'Shape')}
# Retain the proven visual upper arch; round the lower shoulder/hip profile upward.
body=Part.makeLoft([ew(x,0,z,ry,rz,lo) for x,ry,rz,z,lo in [(-115,50,35,84,.78),(-50,90,55,103,.83),(50,90,55,103,.95),(130,80,53,102,.84),(170,55,35,89,.80)]],True,False)
# Deliberate open rear operating zone: no cosmetic enclosure across S0 key/terminal access.
s0open=Part.makeBox(78,105,70,V(103,-85,82))
body=body.cut(s0open);put('Ola_body_ENVELOPE',body)
# Short fixed shoulder collar, separated from neutral moving head by >=3.1 in X.
neck=Part.makeLoft([ew(x,0,z,ry,rz,.82) for x,z,ry,rz in [(-116,126,23,24),(-104,120,42,35),(-88,112,57,43)]],True,False)
put('Ola_short_shoulder_blend_PROPOSED',neck)
# A shared cheek mask. Oversized forward-through windows preserve full camera/ToF installation boxes.
cheeks=[]
for sy in [-1,1]:
 s=Part.makeSphere(1);m=A.Matrix();m.A11=17;m.A22=24;m.A33=22
 s=s.transformGeometry(m);s.translate(V(-224,sy*25,132));cheeks.append(s)
mask=cheeks[0].fuse(cheeks[1]).fuse(Part.makeBox(12,32,8,V(-233,-16,126)))
camera_window=Part.makeBox(55,30,29,V(-261,-40,128.1))
tof_window=Part.makeBox(55,31,31,V(-263,-15.5,107.5))
mask=mask.cut(camera_window).cut(tof_window)
put('Ola_shared_cheek_mask_PROPOSED',mask,(.13,.135,.15))
# The same windows must continue through head/muzzle cosmetics, not stop at an opaque internal cap.
for n in ['Ola_head_ENVELOPE','Ola_muzzle']:
 put(n,D.getObject(n).Shape.cut(camera_window).cut(tof_window))
for o in cos.Group:o.ViewObject.Visibility=True;o.ViewObject.Transparency=0
for n in ['Ola_eye_gold__1','Ola_eye_gold_1']:
 D.getObject(n).ViewObject.ShapeColor=(.83,.59,.15)
baseline=P.parent/'day15-frame-fastening/visual-baseline/snapshot-source-pins.json'
hidden=json.loads(baseline.read_bytes())['hidden_analytical_fields']
for n in hidden:
 o=D.getObject(n)
 if o:o.ViewObject.Visibility=False
for o in D.Objects:
 if hasattr(o,'Shape') and (o.Name.startswith(('COUPON_','FEED_','KEY_','SECTION_','COVER_','WIRE_','VIEW_','CAPACITY_','STRAP','AL_','CF_','BAT2_','XT_')) or 'bracket_space' in o.Name):o.ViewObject.Visibility=False
# Current operating printed parts must remain visible; hide only replaced coarse support references.
for n in ['P10_front_gate','P11_rear_gate','P12_common_deck_speaker','P19_shared_lower_carrier']:
 D.getObject(n).ViewObject.Visibility=True
for n in ['Battery_tray_shared','Battery_crossarm_0','Battery_crossarm_1']:
 o=D.getObject(n)
 if o:o.ViewObject.Visibility=False
root=[]
for n in ['Yaw608_120','Yaw608_134','Pitch688']:
 o=D.getObject(n);axes=[]
 for f in o.Shape.Faces:
  if isinstance(f.Surface,Part.Cylinder):axes.append(dict(radius=f.Surface.Radius,axis=list(f.Surface.Axis),center=list(f.Surface.Center)))
 root.append(dict(name=n,bounds=bb(o.Shape),cylinders=axes))
gap=D.getObject('Neck_shared_root').Shape.distToShape(D.getObject('P10_front_gate').Shape)[0]
gapbearing=D.getObject('Neck_shared_root').Shape.distToShape(D.getObject('Yaw608_120').Shape)[0]
out=dict(utc=datetime.now(timezone.utc).isoformat(),status='WHOLE_HEAD_AND_OLA_VISUAL_PROPOSAL_ONLY_STRUCTURAL_ROOT_OPEN',source_document=S.Name,source_file=S.FileName,source_sha256=hashlib.sha256(Path(S.FileName).read_bytes()).hexdigest(),bearings=root,root_discontinuity=dict(P10_to_coarse_root_gap=gap,coarse_root_to_lower608_gap=gapbearing),load_chain=['P10 actualfrontgate -> MISSING real fixedneck bridge/bearinghousing','fixed608outerracepair -> MISSING retained8mmshaft/yawcarrier + MG92Bhorncoupling','yawcarrier -> pitch688housing/Yaxis + MG92Bpitchhorninterface MISSING','pitchmovingplate -> Camera3/VL53fullnominalunits; commonplate hole/fastenerbinding MISSING','cosmeticmask -> separatelightremovablecover, NEVER structuralroot'],assembly_two_people=['A holdsopenP10/neckcoupon; B validates realbridge/fasteners BEFORE electronics and before choosing heavyface skin','Benchfit 2x608 and 688 with selectedMG92Bhorns: supplierhorn/shaft/tabpositions and retention physicalFIT3; do not pressunknownservooutput through8mmbearing','Supportopenyaw/pitchcarrier, mount commoncamera/ToFplate then actualCSI+sensorfactoryends beforemask; E1soldered notunplugged','Handlay CSI servicebow behindhead/alongopenleftneck, check fullfactorylength/minbend at actualtwojointlimits BEFORE closure; no claimedR/length/motionpass','Putcheekmask last with openopticalwindows; keep rearS0operatingbay open; micP15->BUSbridge->battery serviceorder unchanged'],CSI=dict(actual_factory_connector_binding='UNKNOWN_CAMERA_REVISION_AND_SELECTED_RIBBON_ENDS',ribbon_width_length_minbend=None,region_only=[[-218,-47,134],[-132,-30,154],[-104,-28,128]],region_status='DIAGRAM_ONLY_NOT_QUALIFIED_CONNECTED_OCCUPIED_PATH',next_physical_check='Use actual Camera3 CSI connector normal and pinnedselectedfullribbon, measure usableloop vs real yaw/pitchlimits; no inventedextension/unplug/lengthcredit'),optics=dict(camera_full_window=[-261,-40,128.1,-206,-10,157.1],ToF_full_window=[-263,-15.5,107.5,-208,15.5,138.5],nominal_profile_clear=True,full_optical_FOV='UNKNOWN_requiresactualcameraandToFopticcones_andneutralmaskfit'),cosmetics=dict(status='PROPOSED_NOT_PRINTSKIN',neck_frontX=-116,head_backX=-119.1,neutral_X_gap=3.1,moving_clearance='UNKNOWN_actualrangeNOTqualified',lowerbody='Round lower half upwards atshoulders/hips; upperarchandtaillengthretained',S0_opening=[103,-85,82,181,20,152],skinwall_mount_mass=None,no_cosmetic_STL=True),all_bought_poses_retained=True,old_negatives_preserved=True,physical_pass=False,head_root_STL=False,actual_fit_cut_slack=None)
(P/'head-root-and-assembly-map.json').write_bytes((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode())
changed=['Ola_body_ENVELOPE','Ola_head_ENVELOPE','Ola_muzzle','Ola_short_shoulder_blend_PROPOSED','Ola_shared_cheek_mask_PROPOSED']
ident=[]
for o in S.Objects:
 if hasattr(o,'Shape') and hasattr(o.ViewObject,'ShapeColor') and o.Name not in changed:
  q=D.getObject(o.Name)
  if not hasattr(q,'Shape'):raise ValueError('LOOKUP '+o.Name+' -> '+q.Name+' '+q.TypeId+' SOURCE '+S.Name+' D '+D.Name)
  ident.append(dict(name=o.Name,source_shape=before[o.Name],current_shape=hashlib.sha256(q.Shape.exportBrepToString().encode()).hexdigest(),copy_operation='Shape.copy worldonce no placementchange no CSG',world_placement_equal=str(q.Shape.Placement)==str(o.Shape.Placement),volume_delta=q.Shape.Volume-o.Shape.Volume,bounds_equal=bb(q.Shape)==bb(o.Shape)))
# Directcopy provenance is recorded; serializedcache/optimalbbox equality is not a new global geometry gate.
(P/'unchanged-shape-identities.json').write_bytes((json.dumps(ident,indent=2)+'\n').encode())
D.Label='DAY15 WHOLE HEAD + OLA — PROPOSED / structuralrootOPEN'
D.recompute();D.saveAs(str(P/'head-ola-proposal.FCStd'))
print(json.dumps(dict(saved=D.FileName,objects=len(D.Objects),unchanged_shapes=len(ident),rootgaps=[gap,gapbearing],cosmetics_changed=changed)))

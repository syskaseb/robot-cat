import FreeCAD as A,FreeCADGui as G,json,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');P=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-frame-fastening';P.mkdir(exist_ok=True);B=P/'visual-baseline';B.mkdir(exist_ok=True);S=A.getDocument('DAY15_ESSENTIAL_SHARED_FRAME');D=A.newDocument('DAY15_FRAME_FASTENING');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['AssemblyNote','Status','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
D.Label='DAY15 FRAME FASTENING — same geometry before correction';D.recompute();A.setActiveDocument(D.Name);D.saveAs(str(P/'frame-fastening.FCStd'));view=G.activeDocument().activeView();view.setAxisCross(False)
engineering={o.Name:dict(visible=o.ViewObject.Visibility,transparency=o.ViewObject.Transparency,color=list(o.ViewObject.ShapeColor)) for o in D.Objects if hasattr(o,'Shape') and hasattr(o.ViewObject,'ShapeColor')}
cosmetic=[];hidden=[]
for o in D.Objects:
 if o.Name not in engineering:continue
 n=o.Name
 if n.startswith('Ola_'):
  o.ViewObject.Visibility=True;o.ViewObject.Transparency=0;cosmetic.append(dict(name=n,source_shape_sha256=hashlib.sha256(o.Shape.exportBrepToString().encode()).hexdigest(),world_bounds=str(o.Shape.BoundBox)))
  if not any(x in n for x in ['eye_gold','nose']):o.ViewObject.ShapeColor=(.12,.13,.145)
 elif n.startswith(('WIRE_','COVER_','SECTION_')) or n in ['Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','MG92B_Head_yaw_bracket_space','MG92B_Head_pitch_bracket_space','MG92B_Tail_bracket_space','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits','CF_Pi_air_open','CF_right_handlay','CF_BUS_access','RS_USB_FULL_SOURCE_COVER','BNO_FULL_SOURCE_INSTALLATION_COVER'] or n.startswith('AL_') and n.endswith(('BAY','FIELD')):
  o.ViewObject.Visibility=False;hidden.append(n)
# Hide only the current analytical helper fields; retained real protruding hardware remains visible.
shots=[]
for filename,z in [('whole-opaque-side.png',A.Vector(0,1,0)),('whole-opaque-front-three-quarter.png',A.Vector(-1,1,.32))]:
 rot=A.Rotation(A.Vector(-1,-1,0) if z.x else A.Vector(-1,0,0),A.Vector(0,0,1),z,'ZXY');view.setCameraOrientation(rot.Q);view.fitAll();view.saveImage(str(B/filename),1800,1200,'White');shots.append(dict(file=filename,sha256=hashlib.sha256((B/filename).read_bytes()).hexdigest(),camera=view.getCamera(),camera_orientation_Q=list(view.getCameraOrientation().Q),same_physical_geometry=True))
source=P.parent/'day15-essential-shared-frame/manifest.json';ola=ROOT/'hardware/reference/appearance/ola-cat-reference.jpg';(B/'snapshot-source-pins.json').write_bytes((json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),source_commit='acd6cfa5892a0c596bbdfe823f80e376899e93e2',source_manifest=dict(path=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest()),source_native=dict(path=S.FileName,sha256=hashlib.sha256(Path(S.FileName).read_bytes()).hexdigest()),ola_reference=dict(path=str(ola),sha256=hashlib.sha256(ola.read_bytes()).hexdigest()),cosmetic_reference_shapes=cosmetic,hidden_analytical_fields=hidden,shots=shots,actual_protruding_parts_not_hidden=True,shape_changed=False,finished_print_skin=False),ensure_ascii=False,indent=2)+'\n').encode())
for n,p in engineering.items():o=D.getObject(n);o.ViewObject.Visibility=p['visible'];o.ViewObject.Transparency=p['transparency'];o.ViewObject.ShapeColor=tuple(p['color'])
view.viewAxonometric();view.fitAll();D.save();print(json.dumps({'visual_baseline':str(B),'shots':[(x['file'],x['sha256']) for x in shots],'doc':D.Name,'objects':len(D.Objects)}))

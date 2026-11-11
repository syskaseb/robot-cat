import FreeCAD as A,Part,json,hashlib,zipfile,time,os
from pathlib import Path
t=time.monotonic();c=time.process_time();O=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');D=A.ActiveDocument;assert os.getpid()==26044
P=json.loads((O/'day11-joint-bank-receiver-load-and-fore-neck-service-premise.json').read_bytes());idx=json.loads((O/'day11-GUI-working-snapshot-source-index.json').read_bytes());target=D.getObject(idx['actor_names_to_objects'][P['first_gate']['target']]);assert target.Shape.isValid()
old=json.loads((O/'day07-FPI-minusY-case-whole-stock-first-gates.json').read_bytes());sh={};pins=[]
with zipfile.ZipFile(O/old['archive']) as z:
 for name in ['SIDE_WHOLE_FHAC_CASE','SIDE_ROUTINE_OPENING']:
  q=next(q for q in old['geometry'] if q['name']==name);raw=z.read(q['entry']);assert hashlib.sha256(raw).hexdigest()==q['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid();sh[name]=s;pins.append(dict(archive=old['archive'],entry=q['entry'],sha256=q['sha256'],name=name,world_once=True))
field=sh['SIDE_ROUTINE_OPENING'];gap,w,_=field.distToShape(target.Shape);co=field.common(target.Shape);assert co.isValid()
section=[];x=-42.8;plane=Part.makePlane(210,180,A.Vector(x,-105,-55),A.Vector(1,0,0),A.Vector(0,1,0))
for name,s in [('CURRENT_P0_SIDERIGHT22',target.Shape),*sh.items()]:
 sec=s.section(plane);curves=[]
 for e in sec.Edges:curves.append([[v.y,v.z] for v in e.discretize(Deflection=.08)])
 section.append(dict(name=name,curves_YZ=curves))
# READONLYsourcefields saved as explicitly hidden diagnostic refs, never newmaterial/selection.
g=D.addObject('App::DocumentObjectGroup','JointBankServiceRead');g.Label='JOINT_SERVICE_SOURCE_READ / unselectedFPI / no newmaterial'
for name,s in sh.items():
 o=D.addObject('Part::Feature','JointService'+('Case' if name.endswith('CASE') else 'Opening'));o.Label=name+' / SAMEpinnedsourcepose read only';o.Shape=s;g.addObject(o);o.Visibility=False
g.Visibility=False;D.recompute()
ar=O/'day11-joint-FPI-service-current-frame-relation.breps.zip';gm=[]
with zipfile.ZipFile(ar,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(name,s) in enumerate([*sh.items(),('CURRENT_P0_SIDERIGHT22',target.Shape),('VALID_SERVICE_COMMON',co)]):
  raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);gm.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume))
 z.writestr('manifest.json',(json.dumps(dict(geometry=gm),indent=2)+'\n').encode())
r=dict(id='day11-joint-FPI-service-current-frame-relation',status='JOINT_SIDE_FPI_ROUTINE_SERVICE_FRAME_ALLOCATION_HOLD' if gap<1.25-1e-7 else 'JOINT_SIDE_FPI_SERVICE_FRAME_PAIR_CLEAR_OTHER_JOINT_INTERFACES_UNRECEIVED',field='SIDE_ROUTINE_OPENING',field_classification='Wholeprojectfuse/cover sideoperation reservation, NOT hand or exactdeliveredlid; allocationHOLD not physicalcontact/allservicepaths impossibility.',source_pose_unchanged=True,new_print=False,new_trunk=False,proposal=P['id']+'.json',proposal_sha256=hashlib.sha256((O/(P['id']+'.json')).read_bytes()).hexdigest(),target_actor=target.SourceActor,source_valid=True,field_valid=True,gap_mm=gap,common_valid=True,common_mm3=co.Volume,required_foreign_mm=1.25,witnesses=[[list(a),list(b)] for a,b in w[:2]],new_missing_pairs_received=1,old_CASE3rows_not_replayed=True,old_iterator_NOT_resumed=True,source_geometry_pins=pins,actual_section_x_mm=x,section=section,archive=ar.name,archive_sha256=hashlib.sha256(ar.read_bytes()).hexdigest(),geometry=gm,N01='0/10',actual_Li_A_U_fit_slack_cut=None,operation_seconds=time.monotonic()-t,process_CPU_seconds=time.process_time()-c,GUI_pid=os.getpid(),objects=len(D.Objects))
pp=O/(r['id']+'.json');pp.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({k:r[k] for k in ['status','gap_mm','common_mm3','operation_seconds','process_CPU_seconds','objects']}))

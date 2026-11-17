import FreeCAD as A,Part,MeshPart,json,time,math
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def run():
 t=time.perf_counter();D.save();front=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER');rear=D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER')
 old={o.Name:o.Shape.copy() for o in [front,rear]}
 for n,s in old.items():s.exportBrep(str(P/('source-'+n+'.brep')))
 # Exact parent mesh-local->source-world translation from the actual original export.
 trans=[-127,-87,41.52]
 edges=[[[23,26.6,7],[23,61,7]],[[127,94,58.48],[128.5,94,58.48]],[[177,94,58.48],[175.5,94,58.48]],[[123,38.5,82.98],[123,38.5,84.98]],[[123,1.5,82.98],[123,1.5,84.98]]]
 patches=[('Pi_receiver_face_gusset',box(-105,-60.4,48.52,2,34.4,2)),('E1_left_underside_gusset',box(-2,6,98.5,3.5,1.75,1.5)),('E1_right_underside_gusset',box(48.5,6,98.5,3.5,1.75,1.5)),('PSYS_upper_end_corner_gusset',box(-5,-48.5,124.5,2.5,1.25,2)),('PSYS_lower_end_corner_gusset',box(-5,-86.75,124.5,2.5,1.25,2))]
 q=front.Shape.copy()
 for n,s in patches:q=q.fuse(s)
 front.Shape=q.removeSplitter()
 # Real OUTBOARD up-and-over load bypass, outside the lowerMTA rail (maxY83).
 # It makes room for the ACTUAL keyed cowl tab below; no bought/frame/deck cut.
 plans=[]
 for o,x,sy in [(front,-70,1),(rear,70,-1),(rear,70,1)]:
  before=o.Shape.copy();yy=80 if sy>0 else -88.5;yo=84.5 if sy>0 else -88.5
  members=[]
  for dx in [-11,7]:
   members += [box(x+dx,yy,43.52,4,8.5,2),box(x+dx,yo,43.52,4,4,9)]
  members.append(box(x-11,yo,48.52,22,4,4))
  q=before
  for m in members:q=q.fuse(m)
  # This exact functional window accommodates the source12x20x2.4 tab plus its returnfoot.
  cut=box(x-7.35,64.65 if sy>0 else -94.6,41.4,14.7,29.95,5.97)
  removed=before.common(cut).Volume;q=q.cut(cut).removeSplitter();o.Shape=q
  plans.append({'owner':o.Name,'x':x,'sy':sy,'old_foot_segment_retired_volume':removed,'cut_bounds':bb(cut),'new_member_volumes_after_declared_window':[m.cut(cut).Volume for m in members],'added_geometry':'two integral feet+outerlegs+upperbridge, same root/frame, NOT separate overlapping prints','minimum_outer_leg_X_web':3.65,'outer_rail_Y':[yo,yo+4],'MTA_actual_outerY83_clearance':1.5 if sy>0 else None,'P01_contact_area_unchanged_by_bounds':'window |Y|>=64.65, P01 max|Y|27.5','members_missing':[max(0.,m.cut(cut).Volume-m.cut(cut).common(q).Volume) for m in members]})
 D.recompute();D.save()
 checks=[]
 for x,sy in [(-70,1),(70,-1),(70,1)]:
  owner=front if x<0 else rear;key=D.getObject('CLOSED_BODY_'+('front' if x<30 else 'rear')+'_'+('positive' if sy>0 else 'negative')).Shape.common(box(x-6,66 if sy>0 else -86,43.62,12,20,2.4));checks.append({'owner':owner.Name,'axis':[x,sy*72],'full_source_key_gap':owner.Shape.distToShape(key)[0],'full_source_key_common':owner.Shape.common(key).Volume,'separate_MTA_common':owner.Shape.common(D.getObject('FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER').Shape).Volume,'note_MTA_common_scope':'Whole existing interface may have inherited contact; only the added outboard arch is allocated clear of actualMTA rail.'})
 source=old[front.Name];new=front.Shape
 allowed=[box(-77.35,64.65,41.4,14.7,29.95,5.97)]
 kept=source
 for c in allowed:kept=kept.cut(c)
 missing=kept.cut(new).Volume
 local=new.copy();b=local.BoundBox;local.translate(V(-b.XMin,-b.YMin,-b.ZMin));mesh=MeshPart.meshFromShape(Shape=local,LinearDeflection=.08,AngularDeflection=.25,Relative=False)
 put('floor-frame-functional-completion.json',{'utc':datetime.now(timezone.utc).isoformat(),'localSTL_to_actualworld':trans,'parent_five_edges_local':edges,'parent_edges_world':[[[v[i]+trans[i] for i in range(3)] for v in e] for e in edges],'five_actual_positive_material_patches':[{'n':n,'bounds':bb(s),'v':s.Volume} for n,s in patches],'arch_plans':plans,'source_front_missing_OUTSIDE_declared_functional_foot_window':missing,'interface_checks':checks,'N1_valid':new.isValid(),'N1_solids':len(new.Solids),'N1_mesh_closed':mesh.isSolid(),'N1_mesh_volume':mesh.Volume,'N1_mesh_facets':mesh.CountFacets,'N1_new_bounds':bb(new),'rear_valid':rear.Shape.isValid(),'rear_solids':len(rear.Shape.Solids),'physicalPASS':False,'seconds':time.perf_counter()-t})
 if mesh.isSolid() and mesh.Volume>0:mesh.write(str(P/'N1_floor_receiver_quality_check.stl'))
 print(json.dumps({'N1_mesh_closed':mesh.isSolid(),'source_missing':missing,'interfaces':checks,'seconds':time.perf_counter()-t}))
run()

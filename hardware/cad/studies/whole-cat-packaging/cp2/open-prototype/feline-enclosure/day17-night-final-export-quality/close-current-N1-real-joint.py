import FreeCAD as A,Part,Mesh,MeshPart,json,time
from pathlib import Path
from collections import Counter
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bb(s):
 b=s.optimalBoundingBox(False,True);return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def run():
 t=time.perf_counter();D.save();o=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER');old=o.Shape.copy();g=Part.makeBox(2,98,2,V(-39.75,-80,48.52));over=old.common(g);q=old.fuse(g).removeSplitter();o.Shape=q
 # Entire additional material above actualfloor, PCB Xmax-41 =>1.25; G1 Xmin-35 =>2.75.
 D.recompute();D.save();put('current-N1-positive-joint-checkpoint.json',{'function':'Realabove-floor longitudinal gusset connectsoperatorrailtooldframe acrossfourdiagonaledgecontacts; no triangle edits/shape shrinking','gusset_box':[-39.75,-80,48.52,-37.75,18,50.52],'source_before_volume':old.Volume,'added_gusset_volume':g.Volume,'actual_positive_overlap':over.Volume,'shared_face_area':over.Area,'new_volume':q.Volume,'delta_volume':q.Volume-old.Volume,'PETG_delta_g':(q.Volume-old.Volume)*.00127,'valid':q.isValid(),'solids':len(q.Solids),'saved_before_tests':True})
 checks=[]
 for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','PBAY_G1','WAGO615_G1','P02_front_deck']:
  x=D.getObject(n)
  if not x:continue
  s=x.Shape;valid=g.isValid() and s.isValid();gap=g.distToShape(s)[0] if valid else None;common=g.common(s).Volume if valid and gap<1.25 else 0
  checks.append({'part':n,'gap':gap,'common':common,'scope':'intendedrealdeckbearing' if n=='P02_front_deck' else 'foreignfullcase_or_cooling','clear_scoped':common<1e-7 if n=='P02_front_deck' else gap is not None and gap>=1.25-1e-7})
 missing=old.cut(q).Volume
 m=MeshPart.meshFromShape(Shape=q,LinearDeflection=.16,AngularDeflection=.3,Relative=False);raw=P/'current-N1-after-real-joint.stl';m.write(str(raw));pts,facets=m.Topology;edges=Counter()
 for face in facets:
  keys=[tuple(round(float(v),6) for v in pts[j]) for j in face]
  for i,j in [(0,1),(1,2),(2,0)]:edges[tuple(sorted((keys[i],keys[j])))]+=1
 bad=[{'ends':k,'incident_faces':v} for k,v in edges.items() if v!=2]
 b=bb(q);dims=[b[i+3]-b[i] for i in range(3)];release=m.isSolid() and not bad and missing<1e-6 and all(c['clear_scoped'] for c in checks) and max(dims)+8<=256 and q.isValid() and len(q.Solids)==1
 result={'before_missing':missing,'coverage_scope':'ALLcurrentd18N1materialpreserved; onlyoneexplicitusefuladdition','checks':checks,'world_mesh_closed':m.isSolid(),'edge_histogram':dict(Counter(edges.values())),'bad_edges':bad,'facets':m.CountFacets,'world_bbox_optimal':b,'dimensions':dims,'brim_support_allowance':8,'fits256':max(dims)+8<=256,'conditional_empty_structural_release':release,'wholekit':False,'physicalPASS':False}
 if release:
  local=q.copy();local.translate(V(-b[0],-b[1],-b[2]));local.exportBrep(str(P/'N1_current_shared_frame.brep'));lm=m.copy();lm.transform(A.Placement(V(-b[0],-b[1],-b[2]),A.Rotation()).toMatrix());f=P/'N1_current_shared_frame.stl';lm.write(str(f));r=Mesh.Mesh(str(f));result.update(reopened_closed=r.isSolid(),reopened_volume=r.Volume,local_translation=[-b[0],-b[1],-b[2]],orientation='sourceXYZ/minXYZto0/flatbottomZ0;8mmallocatedforbrim/support, cavitysupportsifneeded',nominal_hardware='currentreceivedsourcefullsetsunchanged; newgussetnoaddedhardware',actualfit=None,actualcut=None,installedslack=None)
 raw.replace(P/'current-N1-after-real-joint.stl.diagnostic');q.exportBrep(str(P/'N1_current_world.brep'));put('CURRENT-N1-final-quality.json',dict(result,seconds=time.perf_counter()-t));D.save();print(json.dumps(result))
run()

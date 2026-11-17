import FreeCAD as A,Part,Mesh,MeshPart,json,time
from pathlib import Path
from collections import Counter
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bounds(s):
 b=s.optimalBoundingBox(False,True);return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def run():
 t=time.perf_counter();D.save();cowl=D.getObject('FC_F_POS').Shape;fixed=D.getObject('FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER').Shape;g=cowl.distToShape(fixed)[0];common=cowl.common(fixed).Volume
 acoustic={'actual_fixed_receiver_gap':g,'common':common,'required':1.25,'clear':g>=1.25-1e-6 and common<1e-7,'unchanged_positive_scope':'Sourcefullspeaker4mm/keeper1.75/full8M2stock11pairgate; expandedrightsidefromactualfullreceiverbound9.386->working10. Allotherpriorpositivepairs carry onlyqualifiedmonotoneprotectedsubset, notglobalPASS.','sourcefront_Pi_operator_ports_and_allboughtposes':'unchanged','allothernewgeometry_vs_front_union_bounds':'ChangedrightdeltaY>=95.5 vsfrontmaxY88.5; othercowls sourceX>=80 orY<=22, so no newpartingcontact','wholekit':False,'physicalPASS':False};put('acoustic-final-local-gate.json',acoustic)
 access=json.loads((P/'front-real-driver-channels-completed.json').read_text());area=json.loads((P/'actual-front-bearing-and-splice-stock.json').read_text());parting=json.loads((P/'front-access-completion.json').read_text())
 frontok=all(r['complete_same80mm_shank_common']<1e-7 for r in access['rows']) and access['primary_floor_and_counterseat_below50p52_missing']<1e-7 and all(r['current_front_common']<1e-7 for r in area['source_H02_stock']) and all(r['finite_actual_bearing_area']>0 for r in area['contacts']) and all(r['common']<1e-7 for r in parting['parting'])
 rows=[]
 for n,fn,qualified in [('A17_INTEGRAL_FRONT_DECK_AND_N1','A17_front_deck_frame',frontok),('FC_F_POS','A17_speaker_side_cowl',acoustic['clear'])]:
  s=D.getObject(n).Shape.copy();b=bounds(s);dims=[b[i+3]-b[i] for i in range(3)];s.exportBrep(str(P/(fn+'.world.brep')));m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.2,Relative=False);pts,faces=m.Topology;edges=Counter()
  for f in faces:
   keys=[tuple(round(float(v),6) for v in pts[j]) for j in f]
   for i,j in [(0,1),(1,2),(2,0)]:edges[tuple(sorted((keys[i],keys[j])))]+=1
  bad=[{'ends':k,'incident_faces':v} for k,v in edges.items() if v!=2]
  row={'object':n,'version':fn,'qty':1,'valid':s.isValid(),'solids':len(s.Solids),'world_bounds_optimal':b,'dimensions_mm':dims,'maxXYZ_plus8':max(dims)+8,'volume_mm3':s.Volume,'PETG1p27_g':s.Volume*.00127,'mesh_closed':m.isSolid(),'mesh_volume':m.Volume,'facets':m.CountFacets,'edge_histogram':dict(Counter(edges.values())),'bad_edges':bad,'matched_interface_checks_closed':qualified,'orientation':'SourceXYZ/minXYZtranslatedto0; frameundersidefloorrequiresup-to4mmsupport; cowlroofsneedinteriorsupport, reserve8mmaroundactualshape','deflection':.08,'angular':.2,'conditional_unpowered_interface_trial_release':False}
  release=qualified and row['valid'] and row['solids']==1 and m.isSolid() and m.Volume>0 and not bad and max(dims)+8<=256
  local=s.copy();local.translate(V(-b[0],-b[1],-b[2]));local.exportBrep(str(P/(fn+'.local.brep')))
  if release:
   mm=m.copy();mm.transform(A.Placement(V(-b[0],-b[1],-b[2]),A.Rotation()).toMatrix());f=P/(fn+'.stl');mm.write(str(f));reload=Mesh.Mesh(str(f));row.update(reopened_closed=reload.isSolid(),reopened_volume=reload.Volume,local_translation=[-b[0],-b[1],-b[2]],STL=fn+'.stl',conditional_unpowered_interface_trial_release=reload.isSolid() and reload.Volume>0)
  else:
   f=P/(fn+'.stl');m.write(str(f));f.replace(P/(fn+'.stl.unreceived'))
  rows.append(row);put('conditional-print-index.json',{'parts':rows,'wholekit':False,'physicalPASS':False,'actualfit':None,'actualcut':None,'installedslack':None,'source_dependency':'P00/sourceframe actualthread/revision andactualscrewdrive + nominalPCB/speaker-safe-rimFIT; notwholecatrelease','seconds':time.perf_counter()-t})
 D.save();print(json.dumps({'fixed_receiver':acoustic,'parts':rows,'seconds':time.perf_counter()-t}))
run()

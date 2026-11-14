import FreeCAD as A,FreeCADGui as G,Part,Mesh,json,time,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;T=time.perf_counter();B=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit');OLD=B/'fit-kit-final';P=B/'fit-kit-ready';P.mkdir(exist_ok=True);(P/'stl').mkdir(exist_ok=True)
S=A.getDocument('DAY14_FIT_KIT_FINAL');D=A.newDocument('DAY14_FIT_KIT_READY');groups={};identity=[]
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Label=o.Label;q.Shape=o.Shape;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['Status','AssemblyNote','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 identity.append(dict(name=o.Name,same_shape_after_assignment=q.Shape.isSame(o.Shape)))
n='P03_rear_deck_integrated_load_yoke';old=D.getObject(n).Shape
# Real loading port opens through local underside45.52, ending46.52: preserves actual2mm roof to48.52.
port=Part.makeCylinder(4.5,5.1,V(99,15,41.42));s=old.cut(port);assert s.isValid() and len(s.Solids)==1
D.getObject(n).Shape=s;D.getObject(n).AssemblyNote='CompleteM3x50/fullnut+washer: undersideopen9mmloadingportat99,15 -> existingXchannel ->110,15. Roof46.52..48.52 retained2mm. PRELOAD beforedeck/frameassembly.'
removed=old.common(port);assert old.cut(s).Volume>0 and s.cut(old).Volume<1e-5
roof=Part.makeCylinder(4.5,2,V(99,15,46.52)).common(old);assert roof.cut(s).Volume<1e-5
r=json.loads((OLD/'checkpoint.json').read_bytes());r.update(status='SAVED_BEFORE_CHECKS',created_utc=datetime.now(timezone.utc).isoformat(),document=D.Name,source_manifest_sha256=hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest(),source_identity=identity,entry_correction=dict(type='UNDERSIDE_OPEN_PORT_THEN_HORIZONTAL_FEED',centre=[99,15],diameter=9,z=[41.42,46.52],actual_local_underside=45.52,roof=[46.52,48.52],roof_missing_mm3=roof.cut(s).Volume,removed_mm3=removed.Volume,real_open_surface='underside local thin deck, not assumed freeX99edge'))
D.Label='WAVEGO fit kit ready — local checks pending';D.recompute();A.setActiveDocument(D.Name);D.saveAs(str(P/'fit-assembly.FCStd'))
(P/'checkpoint.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());removed.exportBrep(str(P/'actual-feed-port-removed.brep'))
parts=json.loads((OLD/'parts.json').read_bytes())
for row in parts:
 q=P/row['stl'];name=row['name']
 if name==n:
  sh=D.getObject(n).Shape.copy();b=sh.BoundBox;sh.translate(V(-b.XMin,-b.YMin,-b.ZMin));mesh=Mesh.Mesh(sh.tessellate(.08));assert mesh.isSolid();mesh.write(str(q));row['volume_mm3']=s.Volume;row['triangles']=mesh.CountFacets
 else:shutil.copyfile(OLD/row['stl'],q)
 if name=='P06_S0_shared_panel':row['description']='Shared S0panel/boss1mm/integralrearlogicbrace+2closedrail sockets; fourM3x50/fullnut+washer'
 elif name==n:row['description']='Reardeck/loadyoke with fourM3x50 nut+washer seats,2mmroof, actualunderside entry99,15'
 row['joint_nominal']='M3x50/fullnut2.4/washer0.5/boss1' if name in [n,'P06_S0_shared_panel','P05_S0_panel_spacer40'] else 'unchanged frozen role'
 row['changed_from_previous_HOLD']=name==n
(P/'parts.json').write_bytes((json.dumps(parts,ensure_ascii=False,indent=2)+'\n').encode());D.save()
print(json.dumps({'saved_before_checks':D.FileName,'objects':len(D.Objects),'port':r['entry_correction'],'wall':time.perf_counter()-T}))

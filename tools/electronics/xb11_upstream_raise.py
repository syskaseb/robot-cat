"""One bounded correction to demonstrated lower-route hits; retain R1 evidence."""
import copy, json
from pathlib import Path
import xb11_upstream_route as recipe
A,Part,ROOT=recipe.A,recipe.Part,recipe.ROOT
OUT=ROOT/'hardware/electronics/full-cat/xb11-upstream-route-r2'
def main():
    OUT.mkdir(exist_ok=True)
    original=ROOT/'hardware/electronics/full-cat/xb11-upstream-route-r1'
    plan=json.loads((original/'plan.json').read_text(encoding='utf-8'))
    plan.update(status='SOURCE_BEFORE_BOUNDED_LOWER_RUN_CORRECTION',parent_plan_sha256=recipe.sha(original/'plan.json'),
        reason='R1 lower run atZ65 intersects Pi/BusAdapter/ShellMounted20. Raise ONLY lower level to79; R15 fillets still fit shortest final vertical leg30.15mm. No claim about anchors/actual ports.')
    for index in (2,3,4):plan['waypoints_mm'][index][2]=79
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    points=[A.Vector(*p) for p in plan['waypoints_mm']];path=recipe.rounded(points,15)
    tube=path.makePipeShell([Part.Wire([Part.makeCircle(1.25,points[0],A.Vector(-1,0,0))])],True,False)
    assert tube.isValid() and len(tube.Solids)==1
    tube.exportBrep(str(OUT/'XB11_DESIGN.brep'))
    hits=[];sources={};tests=0
    for file,obj in [('hardware/cad/studies/deck-aux-wago-r5/DeckAuxWagoR5.FCStd','Deck'),('hardware/cad/studies/aux-splice-shelf-r2/AuxSpliceShelfR2.FCStd','Shelf')]:
        p=ROOT/file;d=A.openDocument(str(p));sources[file]=recipe.sha(p)
        try:
            for i,s in enumerate(d.getObject(obj).Shape.Solids):
                tests+=1;v=recipe.volume(s.common(tube))
                if v>1e-5:hits.append({'object':obj,'solid':i,'positive_mm3':v})
        finally:A.closeDocument(d.Name)
    cases={'F_HY_design':[0,-85.6,90,20,-64.4,102], 'WAGO221412_design':[50,-81.5,105,68.3,-68.5,113.15],
           'P_AUX_design':[0.5,57,109,19.5,87,118], 'F_TY_design':[0,64.4,93,20,85.6,105],
           'G_TAIL_design':[0.5,-87,109,19.5,-57,118], 'G_AUX_design':[110.5,-84,109,129.5,-54,118]}
    for name,b in cases.items():
        tests+=1;v=recipe.volume(recipe.box(b).common(tube))
        if v>1e-5:hits.append({'object':name,'positive_mm3':v,'bbox_conservative':True})
    p=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';sources[p.relative_to(ROOT).as_posix()]=recipe.sha(p)
    d=A.openDocument(str(p))
    try:
        for o in d.Objects:
            if not hasattr(o,'Shape') or o.Shape.isNull() or not recipe.overlap(o.Shape.BoundBox,tube.BoundBox):continue
            for i,s in enumerate(o.Shape.Solids):
                if not recipe.overlap(s.BoundBox,tube.BoundBox):continue
                tests+=1;common=s.common(tube);v=recipe.volume(common)
                if v>1e-5:
                    b=common.BoundBox
                    hits.append({'object':o.Name,'solid':i,'positive_mm3':v,'source':'E6','intersection_bbox_mm':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]})
    finally:A.closeDocument(d.Name)
    samples=[]
    for edge in path.Edges:
        samples.extend([[p.x,p.y,p.z] for p in edge.discretize(Deflection=.1)])
    result={'source_sha256':sources,'script_sha256':recipe.sha(Path(__file__)),'helper_sha256':recipe.sha(Path(recipe.__file__)),
        'plan_sha256':recipe.sha(OUT/'plan.json'),'path_length_mm':path.Length,'tube_valid':True,'tube_single_solid':True,
        'tests':tests,'hits':hits,'geometry_nominal_clear':not hits,'anchors_complete':False,'selected':False,'physical_pass':False,
        'centerline_samples_mm':samples,'scope':'new level79 route only; represented E6 aliases must not be summed; no other wire/tie/tool certification'}
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='centerline_samples_mm'}),flush=True)
if __name__=='__main__':main()

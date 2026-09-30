"""Full new XB11 path against physical owners, with selected cover replacement.

Cache only intersecting saved solids for subsequent anchor design. No FCStd
mutation, no aggregates/duplicate wrappers used as independent obstacles.
"""
import json, sys
from pathlib import Path
import xb11_upstream_route as recipe
sys.path.insert(0, str(recipe.ROOT/'tools/cad'))
from check_main_p0_placement import SavedShapes, prop
A, Part, ROOT = recipe.A, recipe.Part, recipe.ROOT
OUT = ROOT/'hardware/electronics/full-cat/xb11-upstream-route-r3'

def dump(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')

def main():
    assert not (OUT/'checks.json').exists(), 'Preserve previous geometry result'
    OUT.mkdir(exist_ok=True)
    selection=ROOT/'hardware/manufacturing/one-batch-prototype-r18/selection.json'
    scope=ROOT/'hardware/cad/studies/body-shell-scope-r1/plan.json'
    entries=json.loads(selection.read_text(encoding='utf-8'))['prints']
    assert not any(r.get('source_object')=='ShellMounted20' for r in entries)
    assert any(r['identity']=='body:raised-upper-cover-mount' for r in entries)
    excluded={'ShellMounted20':'old upper shell explicitly excluded by lower-body scope and replaced by selected raised cover',
              'Part__Feature038':'old top plate replaced by selected DeckAuxWagoR5'}
    points=[[.5,72,113.5],[-23,72,113.5],[-23,72,79],[-23,-71.75,79],
            [35,-71.75,79],[35,-71.75,109.15],[50,-71.75,109.15]]
    plan=dict(status='SOURCE_SAVED_BEFORE_NEW_ROUTE', from_endpoint='P_AUX.2',
        to_endpoint='XB11 WAGO221-412 cageA', wire='HELU23502 1mm2 OD2.5',
        fixed_radius_mm=15, waypoints_mm=points, excluded_legacy_owners=excluded,
        replacement_scope_sha256=recipe.sha(scope), selected_set_sha256=recipe.sha(selection),
        anchors_complete=False, actual_port_centers_provisional=True, new_stls=0,
        physical_pass=False, scope='New path only; retained E6 physical owners conservative where not replaced. Add actual selected upper cover and Deck.')
    dump('plan.json',plan)
    pv=[A.Vector(*p) for p in points]; path=recipe.rounded(pv,15)
    tube=path.makePipeShell([Part.Wire([Part.makeCircle(1.25,pv[0],A.Vector(-1,0,0))])],True,False)
    assert tube.isValid() and len(tube.Solids)==1
    tube.exportBrep(str(OUT/'XB11_DESIGN.brep'))
    reader=SavedShapes(); rows=[]; cache=[]
    def test(name, shape, owner):
        assert not shape.isNull()
        for index,solid in enumerate(shape.Solids):
            assert solid.isValid(), (name,index)
            separated=not recipe.overlap(solid.BoundBox,tube.BoundBox)
            if separated: continue
            common=solid.common(tube); v=recipe.volume(common)
            distances=solid.distToShape(tube)[0] if v<1e-5 else 0
            row=dict(owner=owner,name=name,solid=index,positive_mm3=v,distance_mm=distances,
                     solid_bbox_mm=[getattr(solid.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')])
            if v>1e-5:
                row['positive_solid_bboxes_mm']=[[getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')] for s in common.Solids if s.Volume>1e-5]
            rows.append(row)
            filename=f'obstacle_{len(cache):03d}.brep';solid.exportBrep(str(OUT/filename))
            cache.append(dict(file=filename,owner=owner,name=name,solid=index,sha256=recipe.sha(OUT/filename)))
    entry=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';objects=reader.doc(entry)
    asm=objects['RobotCatAssembly24'];assert reader.placement(asm).isIdentity()
    names=[]
    for link in prop(asm,'Group').findall('.//Link'):
        wrapper=link.get('value')
        if not wrapper.startswith('Rigid_'):continue
        children=prop(objects[wrapper],'Group').findall('.//Link');assert len(children)==1
        name=children[0].get('value');assert name not in names;names.append(name)
        if name in excluded:continue
        shape=reader.shape(entry,name);shape.Placement=reader.placement(objects[wrapper])*shape.Placement
        test(name,shape,entry.relative_to(ROOT).as_posix()+'#'+wrapper)
    for file, name in [
        ('hardware/cad/studies/deck-aux-wago-r5/DeckAuxWagoR5.FCStd','Deck'),
        ('hardware/cad/studies/aux-splice-shelf-r2/AuxSpliceShelfR2.FCStd','Shelf'),
        ('hardware/cad/studies/upper-cover-mount-r1/RaisedUpperCoverMount.FCStd','CoverMountHole4')]:
        test(name,reader.shape(ROOT/file,name),file+'#'+name)
    for name,b in {'F_HY_design':[0,-85.6,90,20,-64.4,102],
        'XB11_design':[50,-81.5,105,68.3,-68.5,113.15],
        'P_AUX_design':[.5,57,109,19.5,87,118], 'F_TY_design':[0,64.4,93,20,85.6,105],
        'G_TAIL_design':[.5,-87,109,19.5,-57,118], 'G_AUX_design':[110.5,-84,109,129.5,-54,118]}.items():
        test(name,recipe.box(b),'filled conservative purchased-part planning box')
    assert all(recipe.sha(ROOT/n)==h for n,h in reader.hashes.items())
    hits=[r for r in rows if r['positive_mm3']>1e-5]
    samples=[[v.x,v.y,v.z] for e in path.Edges for v in e.discretize(Deflection=.1)]
    dump('checks.json',dict(source_sha256=reader.hashes,script_sha256=recipe.sha(Path(__file__)),
        plan_sha256=recipe.sha(OUT/'plan.json'),unique_physical_owners=len(names),
        exact_pairs=rows,hits=hits,geometry_nominal_clear=not hits,path_length_mm=path.Length,
        cached_obstacles=cache,centerline_samples_mm=samples,anchors_complete=False,
        new_stls=0,physical_pass=False,selected=False))
    print(json.dumps(dict(pairs=len(rows),hits=hits,path_length_mm=path.Length)),flush=True)

if __name__=='__main__':main()

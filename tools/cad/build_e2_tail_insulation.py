"""One native, parameterized electrical-wrap reference; no printable part.

Paths are pinned formed-copper references. Circle/sweep/fusion
history edits the project insulation-build parameter without opaque printed
solids. Supplier thickness is not inferred from this project parameter.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part
import plan_e2_tail_insulation as E
ROOT,OUT,SHA=E.ROOT,E.OUT,E.SHA
MODEL=OUT/'E2BoardWrapCurrent.FCStd'


def shape_row(s):
    assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    b=s.BoundBox
    return dict(volume_mm3=s.Volume,bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])


def run():
    tick=time.monotonic();receipt=OUT/'e2-tail-insulation-current.json';gate=json.loads(receipt.read_text())
    assert gate['status']=='CHANGED_E2_TAIL_INSULATION_NOMINAL_CLEAR_NATIVE_OPEN'
    assert not gate['contacts'] and not gate['errors']
    for n,h in gate['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert not MODEL.exists(),'Receive existing native result, do not duplicate'
    p=E.allocation();assert p['routes']==gate['routes'] and p['rows']==gate['rows']
    d=A.newDocument('E2BoardWrapCurrent');d.Label='Current E2 formed ends / nominal insulation references'
    params=d.addObject('App::VarSet','Parameters');params.addProperty('App::PropertyLength','TapeBuild');params.TapeBuild=.33
    params.addProperty('App::PropertyString','Basis');params.Basis='PROJECT two-layer radial envelope, not supplier tolerance; unpowered delivery inspection required'
    finals={};saved={}
    for n,row in p['rows'].items():
        bare=p['routes'][n+'_bare'];cu=bare['radius'];jacket=p['routes'][n]['radius']
        newtip=row['jacket_cut_point_world_mm'];overlap_start=row['overlap_start_world_mm'];axis=A.Vector(*row['departure_axis_mm'])
        raw=E.P.wire(bare['parts']);covered=E.trim(raw,row['transition_mm'],raw.Length-(85.8202-row['wrap_stop_world_Z_mm']))
        path=d.addObject('Part::Feature',n+'_QualifiedCopperPath');path.Shape=covered
        path.addProperty('App::PropertyString','Source');path.Source=receipt.relative_to(ROOT).as_posix()+'#'+n+'_bare'
        edge=covered.Edges[0];point=edge.valueAt(edge.FirstParameter);normal=edge.tangentAt(edge.FirstParameter)
        profile=d.addObject('Part::Circle',n+'_WrapProfile');profile.setExpression('Radius',f'{cu:.15f} mm + Parameters.TapeBuild')
        profile.Placement=A.Placement(point,A.Rotation(A.Vector(0,0,1),normal))
        pipe=d.addObject('Part::Sweep',n+'_FormedWrap');pipe.Sections=[profile]
        pipe.Spine=(path,[]);pipe.Solid=True;pipe.Frenet=False
        thick_path=d.addObject('Part::Feature',n+'_OverlapPath')
        thick_path.Shape=E.P.wire(row['overlap_parts'])
        thick_profile=d.addObject('Part::Circle',n+'_OverlapProfile')
        thick_profile.setExpression('Radius',f'{jacket:.15f} mm + Parameters.TapeBuild')
        thick_profile.Placement=A.Placement(A.Vector(*overlap_start),A.Rotation(A.Vector(0,0,1),axis))
        overlap=d.addObject('Part::Sweep',n+'_JacketOverlap');overlap.Sections=[thick_profile]
        overlap.Spine=(thick_path,[]);overlap.Solid=True;overlap.Frenet=False
        final=d.addObject('Part::MultiFuse',n+'_BoardInsulation');final.Shapes=[overlap,pipe];final.Refine=True
        final.addProperty('App::PropertyString','Interpretation');final.Interpretation='Filled outer insulation envelope includes own copper/jacket; NOT a printable solid, not electrical acceptance'
        finals[n]=final
        for o in (path,profile,pipe,overlap,thick_path,thick_profile):o.Visibility=False
        if final.ViewObject is not None:final.ViewObject.ShapeColor=(.08,.08,.08)
    d.recompute()
    for n,o in finals.items():
        saved[n]=o.Shape.copy();shape_row(saved[n]);expected=p['envelopes'][n+'_BoardInsulation']
        assert abs(saved[n].Volume-expected.Volume)<1e-5
        assert saved[n].common(expected).Volume>saved[n].Volume-1e-5
    params.TapeBuild=.35;d.recompute()
    for n,o in finals.items():
        assert shape_row(o.Shape)['volume_mm3']>saved[n].Volume
    params.TapeBuild=.33;d.recompute()
    for n,o in finals.items():assert abs(o.Shape.Volume-saved[n].Volume)<1e-5
    d.saveAs(str(MODEL));A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot_cat_e2_wrap_') as folder:
        relocated=Path(folder)/MODEL.name;shutil.copy2(MODEL,relocated);fresh=A.openDocument(str(relocated))
        fresh.recompute()
        for n in finals:
            s=fresh.getObject(n+'_BoardInsulation').Shape;shape_row(s)
            assert abs(s.Volume-saved[n].Volume)<1e-5
        A.closeDocument(fresh.Name)
    result=dict(status='E2_NATIVE_WRAP_REFERENCE_PREPARED_WHOLE_SELECTION_OPEN',native=MODEL.relative_to(ROOT).as_posix(),
                native_sha256=SHA(MODEL),native_parameterized_envelopes=2,
                parameter_0p33_0p35_0p33_restore=True,fresh_relocated_reopen=True,
                envelopes={n:shape_row(s) for n,s in saved.items()},selected=False,physical_pass=False,
                new_prints=0,new_connectors=0,new_metal_fasteners=0,
                tape_cut_strips_mm=[[300,10],[300,10]],whole_stock_open=True,
                source_sha256={receipt.relative_to(ROOT).as_posix():SHA(receipt),Path(__file__).relative_to(ROOT).as_posix():SHA(Path(__file__)),
                               Path(E.__file__).relative_to(ROOT).as_posix():SHA(Path(E.__file__))},
                worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'e2-tail-insulation-native.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()

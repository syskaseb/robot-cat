"""Receive only a clear common plan into an editable primitive feature tree.

Original four tail risers remain exact native-source references in the fused
scaffold; original tail fasteners stay. This is NOT module attachment approval.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
import MeshPart
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from datetime import datetime as DT,timezone as TZ


def main():
    tick=time.monotonic();planfile=OUT/'grounded-spine-integrated-plan.json';plan=json.loads(planfile.read_text())
    assert plan['status']=='ONE_GROUNDED_SPINE_CURRENT_STATIC_PARTIAL_WIRES_CLEAR_NATIVE_MOTION_OPEN'
    assert not any(plan[k] for k in ('contacts','clearance_failures','errors'))
    assert DT.now(TZ.utc)<DT.fromisoformat('2026-10-17T07:30:00+00:00')
    for p,h in plan['source_sha256'].items():assert sha(ROOT/p)==h,p
    target=OUT/'FelineGroundedSpine.FCStd';assert not target.exists(),'Receive saved native before rebuild'
    reader=SavedShapes();scenario=json.loads((OUT/'motion-receivers-checks.json').read_text());source=ROOT/scenario['native']
    doc=A.newDocument('FelineGroundedSpine');live=doc.Name;parts=[]
    report=dict(status='GROUNDED_SPINE_NATIVE_BUILD_RUNNING',selected=False,physical_pass=False,
        native_built=False,boards_called_mounted=False,full_wiring_complete=False,full_motion_checked=False,
        original_tail_risers_preserved=False,source_sha256={planfile.relative_to(ROOT).as_posix():sha(planfile),
            source.relative_to(ROOT).as_posix():sha(source),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        stock_candidate=plan['stock_candidate'],open=plan['open'])
    receipt=OUT/'grounded-spine-native.json'
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);receipt.write_text(json.dumps(report,indent=2)+'\n')
    try:
        params=doc.addObject('Spreadsheet::Sheet','Parameters');params.set('A1','ColumnWidth');params.set('B1','8 mm');params.setAlias('B1','ColumnWidth')
        for row in plan['recipes']:
            low,high=row['bounds_mm'];name=row['name'];obj=doc.addObject('Part::Box',name+'Blank')
            obj.Length=high[0]-low[0];obj.Width=high[1]-low[1];obj.Height=high[2]-low[2];obj.Placement.Base=A.Vector(*low)
            if name.endswith('Upright'):
                obj.setExpression('Width','Parameters.ColumnWidth');obj.setExpression('Placement.Base.y',f'{(low[1]+high[1])/2} mm - Parameters.ColumnWidth / 2')
            current=obj
            if 'upper_frame_M2_axes_mm' in row:
                for index,(x,y) in enumerate(row['upper_frame_M2_axes_mm']):
                    cyl=doc.addObject('Part::Cylinder',name+'Hole'+str(index));cyl.Radius=1.1;cyl.Height=5;cyl.Placement.Base=A.Vector(x,y,36)
                    cut=doc.addObject('Part::Cut',name+'Through'+str(index));cut.Base=current;cut.Tool=cyl;current=cut
                    prism=doc.addObject('Part::Prism',name+'Nut'+str(index));prism.Polygon=6;prism.Circumradius=4.3/math.sqrt(3);prism.Height=2
                    prism.Placement=A.Placement(A.Vector(x,y,38.22),A.Rotation(A.Vector(0,0,1),30))
                    cut=doc.addObject('Part::Cut',name+'Pocket'+str(index));cut.Base=current;cut.Tool=prism;current=cut
                reuse=plan['original_tail_riser_reuse'].get(name)
                if reuse:
                    refs=[]
                    for oldname in reuse['originals']:
                        ref=doc.addObject('Part::Feature',oldname+'Retained');ref.Shape=reader.shape(source,oldname)
                        ref.addProperty('App::PropertyString','SourceObject');ref.SourceObject=oldname
                        ref.addProperty('App::PropertyString','SourceSHA256');ref.SourceSHA256=sha(source);refs.append(ref)
                    fuse=doc.addObject('Part::MultiFuse',name+'Integrated');fuse.Shapes=[current,*refs];current=fuse
            parts.append(current)
        final=doc.addObject('Part::MultiFuse','GroundedSpine');final.Shapes=parts;final.Refine=True
        doc.recompute();assert final.Shape.isValid() and len(final.Shape.Solids)==1 and not final.Shape.check(True)
        volume=final.Shape.Volume
        # Exact preserved root containment, not a visually similar replacement.
        preserved=[]
        for group in plan['original_tail_riser_reuse'].values():
            for oldname in group['originals']:
                s=reader.shape(source,oldname);outside=s.cut(final.Shape);assert outside.Volume<1e-5
                preserved.append(dict(object=oldname,original_volume_mm3=s.Volume,outside_native_mm3=outside.Volume))
        params.set('B1','8.4 mm');doc.recompute();assert final.Shape.isValid() and len(final.Shape.Solids)==1 and final.Shape.Volume>volume
        params.set('B1','8 mm');doc.recompute();assert abs(final.Shape.Volume-volume)<1e-4
        doc.saveAs(str(target));A.closeDocument(live);live=None
        fresh=A.openDocument(str(target));live=fresh.Name;shape=fresh.getObject('GroundedSpine').Shape
        assert shape.isValid() and len(shape.Solids)==1 and abs(shape.Volume-volume)<1e-4
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.12,AngularDeflection=.25,Relative=False)
        assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
        b=mesh.BoundBox;extents=[b.XLength,b.YLength,b.ZLength];assert max(extents)<=252
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);stl=OUT/'GroundedSpine_candidate_x1.stl';mesh.write(str(stl))
        report.update(status='EDITABLE_GROUNDED_SPINE_NATIVE_STATIC_SCOPE_ONLY',native_built=True,
            native=target.relative_to(ROOT).as_posix(),native_sha256=sha(target),fresh_reopen=True,
            parameter_test_mm=[8,8.4,8],native_box_recipes=len(parts),single_valid_solid=True,
            original_tail_risers_preserved=True,retained_roots=preserved,volume_mm3=volume,
            stl=stl.relative_to(ROOT).as_posix(),stl_sha256=sha(stl),closed_stl=True,mesh_extents_mm=extents,
            print_orientation_and_supports_open=True,assembly=[
                'Disconnect/remove battery before mechanical work; no powered work authorized.',
                'Support the tail, remove existing four rear risers and reuse their original fastener stack in the integrated exact seats.',
                'Front roots use four existing upper frame holes and nominal M2x6; belly lower clamps stay unchanged.',
                'Board adapters, bank retention, panel tabs, tools and whole-wire service still OPEN. No board may be called mounted by this scaffold.'])
        save();print(json.dumps({k:report[k] for k in ('status','native_box_recipes','mesh_extents_mm','worker_seconds')}),flush=True)
    except Exception as exc:
        report.update(status='GROUNDED_SPINE_NATIVE_INCOMPLETE',error=str(exc));save();raise
    finally:
        if live and live in A.listDocuments():A.closeDocument(live)


if __name__=='__main__':main()

"""Reuse the editable local tail support in the actual CP2 frame.

One replacement part, unchanged connectors/lead. Check only this changed part
against current material and bought-part reservations, not planning corridors.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import tempfile
import shutil
import time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT=BASE/'wiring-checkpoint'
SOURCE=ROOT/'hardware/cad/studies/tail-local-finish-r2/TailLocalCompleteSupportR2.FCStd'
FIXTURES=OUT/'SourceFixturesAssembly.FCStd'
CONTEXT=BASE/'OpenPrototypePlan.FCStd'
MODEL=OUT/'TailLocalCurrent.FCStd'


def main():
    import FreeCAD as A
    import Part
    import MeshPart
    tick=time.monotonic()
    plan=read(OUT/'local-boundary-plan.json')
    shift=next(r['shift_mm'] for r in plan['rows'] if r['wire']=='XB32')
    assert shift==[0,0,15]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in
          (SOURCE,FIXTURES,CONTEXT,OUT/'local-boundary-plan.json',Path(__file__))}
    src=A.openDocument(str(SOURCE))
    d=A.newDocument('TailLocalCurrent')
    ctx=A.openDocument(str(CONTEXT))
    fixtures=A.openDocument(str(FIXTURES))
    document_names=[doc.Name for doc in (src,d,ctx,fixtures)]
    result=dict(status='CURRENT_TAIL_INTEGRATION_CHECK_PENDING',source_sha256=pins,
        selected=False,stage_completed=False,physical_pass=False,
        replacement_native='P0_MG92BMount29',additional_installed_parts=0,
        new_connectors=0,new_screws=0,retained_local_ties=5,
        local_factory_lead_uncut_mm=250,contacts=[],errors=[],tested_pairs=0)
    try:
        native=d.copyObject(src.FinishedMount,True)
        params=d.addObject('App::FeaturePython','Parameters')
        params.addProperty('App::PropertyLength','TailRise');params.TailRise=shift[2]
        link=d.addObject('App::Link','CurrentTailSupport')
        link.setLink(native)
        link.setExpression('Placement.Base.z','Parameters.TailRise')
        native.Visibility=False
        link.Visibility=True
        d.recompute()
        shape=link.Shape.copy()
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        original=src.FinishedMount.Shape.copy();original.translate(A.Vector(*shift))
        assert abs(shape.Volume+original.Volume-2*shape.common(original).Volume)<1e-4
        v=shape.Volume;bb=bounds(shape)
        params.TailRise=16;d.recompute()
        assert abs(bounds(link.Shape)[2]-bb[2]-1)<1e-6
        params.TailRise=15;d.recompute()
        assert max(abs(x-y) for x,y in zip(bb,bounds(link.Shape)))<1e-6
        targets={}
        for ob in ctx.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():continue
            if ob.Name=='P0_MG92BMount29':continue
            if ob.Name.startswith(('P0_','Head_','TailBridge')) or ob.Name.endswith('_CP2'):
                if ob.Name.startswith('P0_') and any(w in ob.Name.lower() for w in ('deck','shell','ear','head','nose','neck')):continue
                targets[ob.Name]=ob.Shape
        for ob in fixtures.Objects:
            if ob.Name in ('SourceLeftCarrier','SourceRightCarrier') or ob.Name.endswith('_CurrentReference'):
                if 'Shape' in ob.PropertiesList and not ob.Shape.isNull():targets[ob.Name]=ob.Shape
        for name,other in targets.items():
            a,b=shape.BoundBox,other.BoundBox
            if any(getattr(a,axis+'Max')<getattr(b,axis+'Min') or getattr(b,axis+'Max')<getattr(a,axis+'Min') for axis in 'XYZ'):continue
            result['tested_pairs']+=1
            try:
                assert other.isValid(),'Invalid source shape, not a collision'
                common=shape.common(other)
                assert common.isValid(),'Invalid common result, not a collision'
                if common.Volume>1e-5:
                    result['contacts'].append(dict(owner=name,volume_mm3=common.Volume,
                        bought_envelope_only=name.endswith('_CP2')))
            except Exception as exc:
                result['errors'].append(dict(owner=name,error=str(exc)))
        result.update(current_bounds_mm=bb,native_valid=True,solid_count=1,
            parameter_trial='TailRise15->16->15; unchanged historical source',
            factory_routes_and_local_sleeves_retained_but_full_body_connections_open=True)
        if not result['contacts'] and not result['errors']:
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds()
            dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
            assert max(dims)+10<256
            mesh.translate(-mesh.BoundBox.XMin,-mesh.BoundBox.YMin,-mesh.BoundBox.ZMin)
            stl=OUT/'TailLocalCurrent.stl';mesh.write(str(stl))
            d.saveAs(str(MODEL))
            A.closeDocument(d.Name)
            with tempfile.TemporaryDirectory(prefix='robot-cat-tail-reopen-') as td:
                target=Path(td)/MODEL.name;shutil.copy2(MODEL,target)
                reopened=A.openDocument(str(target));reopened.recompute()
                restored=reopened.CurrentTailSupport.Shape
                assert restored.isValid() and abs(restored.Volume-v)<1e-4
                assert max(abs(x-y) for x,y in zip(bounds(restored),bb))<1e-6
                for ob in reopened.Objects:
                    if ob.TypeId=='App::Link':
                        assert ob.getLinkedObject().Document.Name==reopened.Name
                A.closeDocument(reopened.Name)
            result.update(status='CURRENT_TAIL_LOCAL_SUPPORT_PREPARATION_CHECKED',
                native_sha256=sha(MODEL),exports={stl.name:sha(stl)},
                export_dimensions_mm=dims,export_closed=True,relocated_reopen=True)
        else:result['status']='CURRENT_TAIL_SUPPORT_REQUIRES_SHARED_LAYOUT_CHANGE'
    finally:
        for name in document_names:
            if name in A.listDocuments():A.closeDocument(name)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'tail-integration-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':main()

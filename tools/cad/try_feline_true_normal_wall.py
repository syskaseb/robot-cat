"""One cause-changing native3D thickness attempt, not another2D offset.

Received as a construction study ONLY. No imported module interfaces, wire
routes, print approval or current skin receipt are overwritten or inherited.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from datetime import datetime as DT,timezone as TZ


def main():
    tick=time.monotonic();source=OUT/'FelineTorsoPanels.FCStd';target=OUT/'FelineTrueNormalWallStudy.FCStd'
    assert not target.exists(),'Receive saved study before repeating'
    assert DT.now(TZ.utc)<DT.fromisoformat('2026-10-17T07:26:00+00:00')
    report=dict(status='TRUE_NORMAL_WALL_RUNNING',selected=False,physical_pass=False,native_built=False,
        old2d_wall_not_approved=True,nominal_normal_wall_mm=2.2,full_changed_interfaces_qualified=False,
        source_sha256={source.relative_to(ROOT).as_posix():sha(source),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        strategy='Replace independently offset2D loft stations with native3D Thickness operator on retained outer loft. Open original neck/tail cap faces. Single attempt; on failure change global shell construction, no scalar retry.')
    receipt=OUT/'true-normal-wall-study.json'
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);receipt.write_text(json.dumps(report,indent=2)+'\n')
    doc=A.openDocument(str(source));live=doc.Name
    try:
        doc.saveAs(str(target));report['saved_original_before_costly_operator']=True;save()
        caps=['Face'+str(i+1) for i,f in enumerate(doc.OuterNative.Shape.Faces) if f.optimalBoundingBox().XLength<1e-6]
        assert len(caps)==2
        p=doc.Parameters;p.set('A7','NormalWall');p.set('B7','2.2 mm');p.setAlias('B7','NormalWall')
        wall=doc.addObject('Part::Thickness','TrueNormalWall');wall.Faces=(doc.OuterNative,caps)
        wall.setExpression('Value','-Parameters.NormalWall');wall.Mode='Skin';wall.Join='Arc';wall.Intersection=False
        report['open_faces']=caps;save();print('One native3DThickness operation started',flush=True)
        doc.recompute()
        shape=wall.Shape
        if shape.isNull() or not shape.isValid() or len(shape.Solids)!=1 or shape.check(True):
            report.update(status='TRUE_NORMAL_WALL_OPERATOR_REJECTED_NO_SCALAR_RETRY',operator_state=list(wall.State),operator_status=wall.getStatusString(),
                shape_null=shape.isNull(),shape_valid=False if shape.isNull() else shape.isValid())
            doc.save();report['native']=target.relative_to(ROOT).as_posix();report['native_sha256']=sha(target);save();return
        volume=shape.Volume;doc.save();A.closeDocument(live);live=None
        fresh=A.openDocument(str(target));live=fresh.Name;s=fresh.TrueNormalWall.Shape
        assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-volume)<1e-4
        report.update(status='TRUE_NORMAL_NATIVE_WALL_CONSTRUCTION_ONLY_INTERFACES_OPEN',native_built=True,
            native=target.relative_to(ROOT).as_posix(),native_sha256=sha(target),fresh_reopen=True,volume_mm3=volume,
            native_operator='Part::Thickness',preserved_outer_envelope=True,
            minimum_material_webs_verified=False,full_motion_reused=False,
            next='Common load/retention/S1/fore-cowl/tail-bridge space plan before attaching panels or selecting this shell. Native normal parameter alone is not measured whole-wall or printPASS.')
        save();print(json.dumps({k:report[k] for k in ('status','native_built','worker_seconds')}),flush=True)
    except Exception as exc:
        report.update(status='TRUE_NORMAL_WALL_INCOMPLETE',error=str(exc));save();raise
    finally:
        if live and live in A.listDocuments():A.closeDocument(live)


if __name__=='__main__':main()

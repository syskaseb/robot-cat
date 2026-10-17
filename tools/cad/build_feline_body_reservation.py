"""Current editable body/neck reservation; NEVER overwrite pinned old pad proof.

Ola is a silhouette reference, not a scale drawing. This is not a printable
skin. Derive actual walls/access/moving leg apertures only after shared gates.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Sketcher
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from build_feline_layout_envelope import STATIONS,NECK_STATIONS,section_coefficients


def main():
    tick=time.monotonic();doc=A.newDocument('FelineBodyReservation')
    target=OUT/'FelineBodyReservation.FCStd'
    assert not target.exists(),'Receive saved native reservation before another build'
    report={'selected':False,'physical_pass':False,'printable_skin':False,
            'reference':'hardware/reference/appearance/ola-cat-reference.jpg',
            'wall_thickness_verified':False,'panel_mounts_complete':False}
    try:
        p=doc.addObject('Spreadsheet::Sheet','Parameters')
        for i,(name,value) in enumerate([('Width',196),('Height',160),('CenterZ',32)],1):
            p.set(f'A{i}',name);p.set(f'B{i}',f'{value} mm');p.setAlias(f'B{i}',name)
        sketches=[]
        def loft(name,rows,neck=False):
            body=doc.addObject('PartDesign::Body',name);sections=[]
            for j,row in enumerate(rows):
                if neck:
                    x,w,z0,z1=row;points=[(-w/2,z0),(w/2,z0),(w/2,z1),(-w/2,z1)];center=0
                else:
                    x,w,h=row;c,s=section_coefficients(w,h)
                    points=[(float(y*w/2),float(z*h/2)) for y,z in zip(c,s)];center=32
                sk=doc.addObject('Sketcher::SketchObject',name+'Section'+str(j));body.addObject(sk)
                sk.Placement=A.Placement(A.Vector(x,0,center),A.Rotation(A.Vector(1,1,1),120))
                if not neck:sk.setExpression('Placement.Base.z','Parameters.CenterZ')
                vectors=[A.Vector(y,z,0) for y,z in points];count=len(points)
                import Part
                for i in range(count):sk.addGeometry(Part.LineSegment(vectors[i],vectors[(i+1)%count]),False)
                for i in range(count):sk.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%count,1))
                for i,(y,z) in enumerate(points):
                    k=sk.addConstraint(Sketcher.Constraint('DistanceX',i,1,y))
                    sk.setExpression(f'Constraints[{k}]',f'Parameters.Width * {y/196:.15g}')
                    k=sk.addConstraint(Sketcher.Constraint('DistanceY',i,1,z))
                    if not neck:sk.setExpression(f'Constraints[{k}]',f'Parameters.Height * {z/160:.15g}')
                sections.append(sk);sketches.append(sk)
            doc.recompute();feature=body.newObject('PartDesign::AdditiveLoft',name+'RuledLoft')
            feature.Profile=sections[0];feature.Sections=sections[1:];feature.Ruled=True
            doc.recompute();assert body.Shape.isValid() and len(body.Shape.Solids)==1
            assert not body.Shape.check(True);return body
        torso=loft('TorsoReservation',STATIONS);neck=loft('NeckReservation',NECK_STATIONS,True)
        assert all(s.FullyConstrained for s in sketches)
        original={o.Name:o.Shape.Volume for o in (torso,neck)}
        original_width=torso.Shape.BoundBox.YLength
        p.set('B1','198 mm');doc.recompute()
        assert abs(torso.Shape.BoundBox.YLength-original_width-2)<1e-5
        p.set('B1','196 mm');doc.recompute()
        assert all(abs(doc.getObject(n).Shape.Volume-v)<1e-4 for n,v in original.items())
        overlap=torso.Shape.common(neck.Shape)
        assert overlap.isValid() and overlap.Volume>0,'Contiguous neck/torso overlap required'
        report.update(status='EDITABLE_CURRENT_BODY_NECK_RESERVATION_ONLY',
            native=target.relative_to(ROOT).as_posix(),fully_constrained_sketches=len(sketches),
            width_parameter_test_mm=[196,198,196],torso_dimensions_mm=[torso.Shape.BoundBox.XLength,torso.Shape.BoundBox.YLength,torso.Shape.BoundBox.ZLength],
            neck_torso_overlap_volume_mm3=overlap.Volume,
            silhouette=['Head forward of front legs; keep round head and existing concave ears',
                'Gentle dorsal arc, waist behind ribs, no lateral belly expansion',
                'Visible mechanical legs, concealed torso/neck wiring, curved segmented tail'],
            panel_plan={'split_x_mm':21,'split_y_mm':0,'max_nominal_panel_extents_mm':[163,98,160],
                'print_margin_limit_mm':252,'built':False,
                'open':['Actual wall thickness','Whole moving leg openings','S0/S1 control access',
                    'Neck yaw/pitch sweep','Frame anchors','Cable entries','Panel fasteners and service']})
        doc.saveAs(str(target));name=doc.Name;A.closeDocument(name);doc=None
        reopened=A.openDocument(str(target))
        try:
            for n,v in original.items():
                s=reopened.getObject(n).Shape;assert s.isValid() and abs(s.Volume-v)<1e-4
        finally:A.closeDocument(reopened.Name)
        report.update(native_sha256=sha(target),fresh_reopen=True,worker_seconds=round(time.monotonic()-tick,3),
            source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
                'tools/cad/build_feline_layout_envelope.py':sha(ROOT/'tools/cad/build_feline_layout_envelope.py')})
        (OUT/'body-reservation-native.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report),flush=True)
    finally:
        if doc and doc.Name in A.listDocuments():A.closeDocument(doc.Name)


if __name__=='__main__':main()

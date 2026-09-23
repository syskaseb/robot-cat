"""Audit the cartridge's revised nut exit and conditional precision-tool access."""
import json
from pathlib import Path
import shutil
import tempfile
import pilot

OUT=pilot.CAD/'studies/tail-cartridge-service'
TARGET=OUT/'TailCartridgeService.FCStd'
PREVIOUS=pilot.CAD/'studies/tail-cartridge/TailHornCartridge.FCStd'
PRINTS=['LowerRetainerPETG','UpperCarrierPETG','SupportedRoot34']


def audit():
    import FreeCAD as A
    import Part
    assert not A.GuiUp and not A.listDocuments()
    files=[pilot.PARAMS,pilot.TARGET]+[pilot.CAD/'modules'/(n+'.FCStd') for n in pilot.MODULES]
    hashes={p.relative_to(pilot.ROOT).as_posix():pilot.sha(p) for p in files}
    report={'study_sha256':pilot.sha(TARGET),'previous_sha256':pilot.sha(PREVIOUS),
            'tool_sha256':pilot.sha(Path(__file__)),'unchanged_robot_files':hashes,
            'installed':False,'print_ready':False,'cad_saved':False,'native_solver_tested':False}
    def overlap(a,b):
        return abs(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.
    try:
        with tempfile.TemporaryDirectory(prefix='tail-service-r2-') as tmp:
            dst=Path(tmp)/TARGET.name;shutil.copy2(TARGET,dst)
            d=pilot.document(A,dst);d.recompute()
            assert len(A.listDocuments())==1
            assert not any(o.TypeId=='App::Link' for o in d.Objects)
            saved={n:pilot.global_shape(d.getObject(n)) for n in PRINTS}
            A.closeDocument(d.Name)
            assert pilot.sha(dst)==pilot.sha(TARGET)
        d=pilot.document(A,TARGET);old=pilot.document(A,PREVIOUS)
        shapes={n:pilot.global_shape(d.getObject(n)) for n in PRINTS}
        root=shapes['SupportedRoot34'];before=pilot.global_shape(old.getObject('SupportedRoot34'))
        flat=Part.makeBox(5.3,40,45,A.Vector(154,-25,85))
        expected=before.cut(Part.makeBox(6.6,14,2.5,A.Vector(167.7,-6,95.9))).cut(flat)
        differences=[root.cut(expected).Volume,expected.cut(root).Volume]
        assert max(map(abs,differences))<1e-5
        for name,s in shapes.items():
            s.check(True);assert s.isValid() and len(s.Solids)==1
            assert s.cut(saved[name]).Volume<1e-5 and saved[name].cut(s).Volume<1e-5
            if name!='SupportedRoot34':
                prior=pilot.global_shape(old.getObject(name))
                expected_plate=prior.cut(flat)
                assert s.cut(expected_plate).Volume<1e-5 and expected_plate.cut(s).Volume<1e-5
        sketches=[o for o in d.Objects if o.TypeId=='Sketcher::SketchObject']
        assert len(sketches)==21 and all(o.FullyConstrained and o.solve()==0 for o in sketches)
        report.update(strict_bop=True,relocation={'documents_loaded':1,'external_links':0},
                      modified_prints=PRINTS,fully_constrained_sketches=[o.Name for o in sketches],
                      removed_mm3=before.Volume-root.Volume,expected_difference_mm3=differences)
        var=d.getObject('CartridgeParameters');radius=var.HoleRadius
        try:
            var.HoleRadius=1.3;d.recompute()
            report['parameter_removed_mm3']={n:s.Volume-pilot.global_shape(d.getObject(n)).Volume for n,s in shapes.items()}
            assert all(v>0 for v in report['parameter_removed_mm3'].values())
        finally:
            var.HoleRadius=radius;d.recompute()
        assert all(abs(s.Volume-pilot.global_shape(d.getObject(n)).Volume)<1e-5 for n,s in shapes.items())
        print('Loading robot for service paths...',flush=True)
        robot=pilot.document(A,pilot.TARGET)
        plan=json.loads((pilot.BASE/'assembly-plan.json').read_text())
        allparts={r['name']:pilot.global_shape(robot.getObject(r['name'])) for r in plan['components']}
        allparts['TailRoot29']=root
        allparts.update({n:s for n,s in shapes.items() if n!='SupportedRoot34'})
        for o in d.Objects:
            if o.Name.startswith(('CartridgeBolt','CartridgeNut')):allparts[o.Name]=o.Shape.copy()
        # No fake factory screw or spline: the community envelope has neither.
        nut=allparts['SpindleNut34'];bolt=allparts['SpindleBolt34']
        report['nut_path']=[]
        for i in range(73):
            dy=18-i*.25;n=nut.copy();n.translate(A.Vector(0,dy,0))
            hits=[{'part':k,'mm3':v} for k,s in allparts.items() if k not in ['SpindleNut34','SpindleBolt34'] and (v:=overlap(n,s))>.001]
            report['nut_path'].append({'dy_mm':dy,'intersections':hits,'prior_root_mm3':overlap(n,before),'retained_bolt_mm3':overlap(n,bolt)})
        assert max(r['prior_root_mm3'] for r in report['nut_path'])>1
        assert max(r['retained_bolt_mm3'] for r in report['nut_path'])>1
        def seat(s):
            faces=lambda t:[f for f in t.Faces if isinstance(f.Surface,Part.Plane) and abs(f.CenterOfMass.z-98.4)<1e-6 and abs(f.normalAt(0,0).z)>.9999]
            return sum(f.common(g).Area for f in faces(s) for g in faces(nut))
        report['nut_seat_mm2']={'prior':seat(before),'service':seat(root)}
        assert abs(seat(before)-seat(root))<1e-5
        report['shaft_tool_paths']=[]
        # Conservative cylindrical blade sweep during straight insertion, no handle.
        for diameter in [2.5,3.,6.]:
            probe=Part.makeCylinder(diameter/2,90,A.Vector(171,-6,93.05))
            hits=[{'part':k,'mm3':v} for k,s in allparts.items() if k not in ['SpindleBolt34','SpindleNut34'] and (v:=overlap(probe,s))>.001]
            report['shaft_tool_paths'].append({'diameter_mm':diameter,'swept_z_mm':[93.05,183.05],
                'intersections':hits,'retained_axial_bolt_mm3':overlap(probe,bolt),
                'root_clearance_mm':probe.distToShape(root)[0]})
        report['m2_counterhold_paths']=[]
        for i,(x,y) in enumerate([(x,y) for x in (164.5,177.5) for y in (-12.5,.5)]):
            probe=Part.makeCylinder(1.5,40,A.Vector(x,y,88.2),A.Vector(0,0,-1))
            hits=[{'part':k,'mm3':v} for k,s in allparts.items() if k!=f'CartridgeBolt{i}' and (v:=overlap(probe,s))>.001]
            report['m2_counterhold_paths'].append({'bolt_index':i,'tool_OD_mm':3,'intersections':hits})
        report['conditional_nut_path_clear']=not any(r['intersections'] for r in report['nut_path'])
        report['conditional_precision_blade_clear']=all(not r['intersections'] for r in report['shaft_tool_paths'][:2])
        report['remaining']=['Actual horn screw head/drive/thread and installed height unknown',
            'Blade-only model; handle and hands not validated','M2 counterhold and complete assembly sequence',
            'R1 thin PETG walls retained; new slot reduces collar section','No native joint or dynamic motion validation']
    finally:
        for n in list(A.listDocuments()):A.closeDocument(n)
    assert all(pilot.sha(pilot.ROOT/p)==h for p,h in hashes.items())
    (OUT/'service-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ['removed_mm3','conditional_nut_path_clear','conditional_precision_blade_clear','nut_seat_mm2','shaft_tool_paths','m2_counterhold_paths']}),flush=True)


if __name__=='__main__':audit()

"""Isolated horn cartridge study. Features authored using FreeCAD MCP."""
from pathlib import Path
import json
import sys
import shutil
import tempfile
import pilot

ROOT = pilot.ROOT
OUT = pilot.CAD / "studies/tail-cartridge"
TARGET = OUT / "TailHornCartridge.FCStd"
CENTER = (171., -6.)
PRINTS = ['LowerRetainerPETG', 'UpperCarrierPETG', 'SupportedRoot34']
HOLES = [(x,y) for x in (162.5,179.5) for y in (-11.5,-.5)]
REFERENCE = ROOT / 'hardware/reference/mg92b-horn-2026-09-23/MG92BCommunityReference.FCStd'


def populate():
    """Copy purchased reference geometry; never generate replacement splines."""
    import FreeCAD as A
    assert A.GuiUp
    d=A.getDocument('TailHornCartridge')
    assert not d.getObject('CommunityHornEnvelope')
    ref=A.openDocument(str(REFERENCE), hidden=True)
    try:
        horn=ref.getObject('Fusion105').Shape.copy()
    finally:
        A.closeDocument(ref.Name)
    rotation=A.Rotation(A.Vector(1,1,1),120)
    horn.Placement=A.Placement(A.Vector(171,-6,91)-rotation.multVec(A.Vector(6,33.4,6)),rotation)*horn.Placement
    shapes={'CommunityHornEnvelope':horn}
    purchased=A.getDocument('TailPurchased')
    for i,(x,y) in enumerate(HOLES):
        for source,name,z in [('BoltM2x12','CartridgeBolt',88),('NutM2','CartridgeNut',98)]:
            shape=pilot.global_shape(purchased.getObject(source))
            shape.translate(A.Vector(x,y,z))
            shapes[f'{name}{i}']=shape
    for name,shape in shapes.items():
        o=d.addObject('Part::Feature',name)
        o.Shape=shape
        o.addProperty('App::PropertyString','Provenance','Traceability')
        o.Provenance=('Alberto / otrebla333, Dtto v2.0.1, CC-BY-SA-4.0; approximate envelope, no holes or spline'
                      if name=='CommunityHornEnvelope' else 'Copied nominal TailPurchased geometry; no supplier/thread verification')
        o.ViewObject.ShapeColor=(.82,.76,.54) if name=='CommunityHornEnvelope' else (.65,.68,.72)
    d.Label='Tail horn cartridge - CONCEPT NOT INSTALLED'
    d.recompute()
    d.save()
    A.setActiveDocument(d.Name)


def audit():
    """Independent BRep/fit checks. No geometry generation or CAD writes."""
    import FreeCAD as A
    import Part
    assert not A.GuiUp and not A.listDocuments()
    files=[pilot.PARAMS,pilot.TARGET]+[pilot.CAD/'modules'/(n+'.FCStd') for n in pilot.MODULES]
    hashes={p.relative_to(ROOT).as_posix():pilot.sha(p) for p in files}
    report={'study_sha256':pilot.sha(TARGET),'tool_sha256':pilot.sha(Path(__file__)),
            'reference_sha256':pilot.sha(REFERENCE),'unchanged_robot_files':hashes,
            'installed_in_robot':False,'print_ready':False,'cad_saved_by_audit':False,
            'native_joints_tested':False,'physical_fit_proven':False,
            'scope':'Three new/revised PETG parts and nominal cartridge fasteners vs existing robot, sampled rigid tail rotation; NOT native solver or continuous sweep.'}
    def overlap(a,b):
        return abs(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.
    def snapshot(d):
        return {n:pilot.global_shape(d.getObject(n)) for n in PRINTS}
    try:
        with tempfile.TemporaryDirectory(prefix='cat-cartridge-') as folder:
            dst=Path(folder)/TARGET.name
            shutil.copy2(TARGET,dst)
            d=A.openDocument(str(dst))
            d.recompute()
            assert len(A.listDocuments())==1 and not any(o.TypeId=='App::Link' for o in d.Objects)
            relocated=snapshot(d)
            A.closeDocument(d.Name)
            assert pilot.sha(dst)==pilot.sha(TARGET)
        d=A.openDocument(str(TARGET));d.recompute()
        shapes=snapshot(d)
        report['geometry']={}
        for n,s in shapes.items():
            s.check(True)
            assert s.isValid() and len(s.Solids)==1,n
            assert s.cut(relocated[n]).Volume<1e-6 and relocated[n].cut(s).Volume<1e-6
            bb=s.BoundBox
            report['geometry'][n]={'strict_bop_passed':True,'solids':1,'volume_mm3':s.Volume,
                                  'bbox_mm':[bb.XLength,bb.YLength,bb.ZLength]}
        sketches=[o for o in d.Objects if o.TypeId=='Sketcher::SketchObject']
        assert all(o.FullyConstrained and o.solve()==0 for o in sketches)
        report['fully_constrained_sketches']=[o.Name for o in sketches]
        report['relocation']={'documents_loaded':1,'external_links':0,'fresh_worker':True}
        # One shared interface changes all three mating parts and restores exactly.
        var=d.getObject('CartridgeParameters');old=var.HoleRadius
        try:
            var.HoleRadius=1.3;d.recompute()
            report['parameter_change_removed_mm3']={n:s.Volume-pilot.global_shape(d.getObject(n)).Volume for n,s in shapes.items()}
            assert all(v>0 for v in report['parameter_change_removed_mm3'].values())
        finally:
            var.HoleRadius=old;d.recompute()
        assert all(abs(s.Volume-pilot.global_shape(d.getObject(n)).Volume)<1e-6 for n,s in shapes.items())
        horn=d.getObject('CommunityHornEnvelope').Shape.copy()
        report['horn_intersections_mm3']={n:overlap(horn,s) for n,s in shapes.items()}
        report['horn_clearances_mm']={n:horn.distToShape(s)[0] for n,s in shapes.items()}
        extras={o.Name:o.Shape.copy() for o in d.Objects if o.Name.startswith(('CartridgeBolt','CartridgeNut'))}
        candidate={**shapes,**extras}
        report['internal_intersections']=[{'parts':[n,m],'overlap_mm3':v} for i,(n,s) in enumerate(candidate.items())
            for m,t in list(candidate.items())[i+1:] if (v:=overlap(s,t))>.001]
        print('Loading robot for conditional motion envelope...',flush=True)
        assembly=pilot.document(A,pilot.TARGET)
        plan=json.loads((pilot.BASE/'assembly-plan.json').read_text())
        original={r['name']:pilot.global_shape(assembly.getObject(r['name'])) for r in plan['components']}
        moving={'TailRoot29'}
        while True:
            updated=moving|{j['child'] for j in plan['joints'] if j['parent'] in moving}
            if updated==moving:break
            moving=updated
        report['co_rotated_existing_parts']=sorted(moving)
        original.pop('TailRoot29')
        report['motion_samples']=[]
        touched=set()
        for angle in range(-30,31,5):
            def rotated(s):
                s=s.copy();s.rotate(A.Vector(171,-6,0),A.Vector(0,0,1),angle);return s
            frame={n:rotated(s) if n in moving else s for n,s in original.items()}
            hits=[]
            for n,s in candidate.items():
                s=rotated(s)
                for m,t in frame.items():
                    if not s.BoundBox.intersect(t.BoundBox):continue
                    touched.add(m)
                    v=overlap(s,t)
                    if v>.001:hits.append({'new_part':n,'existing_part':m,'overlap_mm3':v})
            report['motion_samples'].append({'angle_deg':angle,'intersections':hits})
            print(angle,len(hits),flush=True)
        report['existing_parts_with_bbox_overlap']=sorted(touched)
        report['conditional_nominal_fit_passed']=not any(report['horn_intersections_mm3'].values()) and not report['internal_intersections'] and not any(r['intersections'] for r in report['motion_samples'])
        report['fastener_stack_mm']={'lower_retainer':2,'upper_carrier':4,'root_seat':4,'nominal_nut':1.6,'bolt_length':12,'protrusion':.4}
        report['open_gates']=['Actual horn geometry, installed height and central screw','Spindle M3 nut insertion and assembly order after new annular pad','Complete tool-access paths','New native joints and solver motion','PETG print/profile/fit coupon, clamp creep and strength','Whole-robot legacy shell strict BOP failure','Supplier-specific cartridge screws/nuts']
    finally:
        for n in list(A.listDocuments()):A.closeDocument(n)
    assert all(pilot.sha(ROOT/p)==h for p,h in hashes.items())
    (OUT/'cartridge-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps({'geometry':report['geometry'],'horn':report['horn_intersections_mm3'],'internal':report['internal_intersections'],'fit_passed':report['conditional_nominal_fit_passed']}),flush=True)


def survey():
    """Disposable geometry probes, not the authored PartDesign master."""
    import FreeCAD as A
    import Part
    assert not A.GuiUp and not A.listDocuments()
    try:
        source = pilot.document(A, pilot.CAD / "modules/tail/TailSupport.FCStd")
        stationary = {n: pilot.global_shape(source.getObject(n)) for n in
                      ["ServoSupport34", "UpperHousing34", "BearingCap34", "OuterSpacer34"]}
        # Candidate outline: round hub with a narrow extension for the long arm.
        envelope = Part.makeCylinder(13.5, 6, A.Vector(171,-6,88)).fuse(
            Part.makeBox(8.2,32,6,A.Vector(166.9,-19,88)))
        rows = []
        for angle in range(-30,31,5):
            moved=envelope.copy()
            moved.rotate(A.Vector(171,-6,0), A.Vector(0,0,1),angle)
            hits={n: moved.common(s).Volume for n,s in stationary.items() if moved.BoundBox.intersect(s.BoundBox)}
            rows.append({"angle_deg":angle,"intersections_mm3":{n:v for n,v in hits.items() if v>.001}})
        print(json.dumps(rows),flush=True)
    finally:
        for n in list(A.listDocuments()):
            A.closeDocument(n)


if __name__ == "__main__":
    {"survey": survey, "populate":populate, "audit":audit}[sys.argv[1]]()

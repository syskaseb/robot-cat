"""One coupled correction: XL05 clearance in seats, two native Cover openings.

No source route shifts. Preserve the received Carrier by cutting the new
seats before union; open only the two measured grip footprints in Cover.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
base = ROOT / 'tools/electronics/w5_source_grips_native_r1.py'
source = base.read_text(encoding='utf-8').replace('grips-native-r1', 'grips-native-r2')
old = "raw = d.addObject('Part::MultiFuse', 'CarrierWithFourSeats'); raw.Shapes = [link, *raw_seats]; raw.Refine = False"
assert source.count(old) == 1
source = source.replace(old, """# XL05's two received insulated pieces intersected only the new low
    # seat material. Native local tunnel avoids those bounds with0.5mm;
    # cutting the seat BEFORE union preserves the existing Carrier exactly.
    tools.append(box('XL05LowSeatTunnel', [-76.1,-24.3,147.8,-68.2,-19.8,150.2]))
    raw = d.addObject('Part::MultiFuse', 'FourRawSeats'); raw.Shapes = raw_seats; raw.Refine = False""")
old = "final = d.addObject('Part::Cut', 'SourceGripsFinished'); final.Base = raw; final.Tool = cutters; final.Refine = False"
assert source.count(old) == 1
source = source.replace(old, """seats = d.addObject('Part::Cut', 'FourClearedSeats'); seats.Base = raw; seats.Tool = cutters; seats.Refine = False
    final = d.addObject('Part::MultiFuse', 'SourceGripsFinished'); final.Shapes = [link,seats]; final.Refine = False""")
old = 'owners, pins = current_owners(A, Part)'
assert source.count(old) == 1
source = source.replace(old, """cover_parent_path = ROOT/'hardware/cad/studies/w5-source-cover-passages-native-r1/SourceCoverCurvedPassages.FCStd'
    cover_parent = A.openDocument(str(cover_parent_path))
    cover_link = d.addObject('App::Link','ReceivedSourceCover'); cover_link.setLink(cover_parent.SourceCoverFinished)
    cover_link.LinkPlacement = cover_parent.SourceCoverFinished.Placement
    parameters.addProperty('App::PropertyLength','CoverAllowance'); parameters.CoverAllowance=.5
    cover_tools=[]
    # Bounds derived from the actual seat/tie footprints, NOT OCCT's inflated
    # contact bbox (which spanned the whole curved parent surface).
    for wire in ('W065','W067'):
        x,y,z,angle=SEATS[wire]; assert angle==0
        q=box(wire+'CoverGripOpening',[x-10.7,y-4.5,161.5,x+3.8,y+4.5,z+3.5])
        q.setExpression('Length','13.5 mm + 2 * GripParameters.CoverAllowance')
        q.setExpression('Width','8 mm + 2 * GripParameters.CoverAllowance')
        q.setExpression('Placement.Base.x',str(x-10.2)+' mm - GripParameters.CoverAllowance')
        q.setExpression('Placement.Base.y',str(y-4)+' mm - GripParameters.CoverAllowance')
        cover_tools.append(q)
    cover_compound=d.addObject('Part::Compound','TwoGripCoverClearances');cover_compound.Links=cover_tools
    cover=d.addObject('Part::Cut','SourceGripCoverFinished');cover.Base=cover_link;cover.Tool=cover_compound;cover.Refine=False
    d.recompute();d.save();assert cover.Shape.isValid() and len(cover.Shape.Solids)==1 and not cover.Shape.check(True)
    cover_removed=cover_link.Shape.cut(cover.Shape);assert cover_removed.BoundBox.ZMin>125
    cv=cover.Shape.Volume;parameters.CoverAllowance=.6;d.recompute();assert cover.Shape.Volume<cv
    parameters.CoverAllowance=.5;d.recompute();assert abs(cover.Shape.Volume-cv)<1e-5;d.save()
    owners, pins = current_owners(A, Part)
    owners['SourceCover']=cover.Shape.copy();pins += [cover_parent_path,ROOT/'tools/electronics/w5_source_grips_native_r1.py']
    prior=ROOT/'hardware/electronics/full-cat/w5-source-grips-native-r1/checks.json'
    previous=json.loads(prior.read_text(encoding='utf-8'))
    assert previous['status']=='SOURCE_INSULATION_GRIPS_REJECTED' and len(previous['hits'])==7 and not previous['errors']
    assert all(sha(ROOT/k)==v for k,v in {**previous['source_sha256'],**previous['files']}.items())
    pins.append(prior)""")
old = "final.Shape.exportBrep(str(CAD / 'Carrier_WORLD.brep')); added.exportBrep(str(OUT / 'ADDED_SEATS_WORLD.brep'))"
source = source.replace(old, old + "\n    cover.Shape.exportBrep(str(CAD/'Cover_WORLD.brep'))")
old = "mesh.translate(-bb.XMin, -bb.YMin, -bb.ZMin); mesh.write(str(CAD / 'Carrier_UNSELECTED_x1.stl'))"
source = source.replace(old, old + """
        cm=MeshPart.meshFromShape(Shape=cover.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert cm.isSolid() and cm.countComponents()==1;cm.rotate(math.pi,0,0)
        cb=cm.BoundBox;assert cb.XLength+10<=256 and cb.YLength+10<=256 and cb.ZLength<=256
        cm.translate(-cb.XMin,-cb.YMin,-cb.ZMin);cm.write(str(CAD/'Cover_UNSELECTED_x1.stl'))""")
old = "assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values()); reopened = True"
source = source.replace(old, """cs=restored.SourceGripCoverFinished.Shape
            assert cs.isValid() and len(cs.Solids)==1 and not cs.check(True) and abs(cs.Volume-cv)<1e-5
            """+old)
source = source.replace('replacement_Carrier_quantity=1, added_print_quantity=0, new_fasteners=0,',
                        'replacement_Carrier_quantity=1, replacement_Cover_quantity=1, cover_removed_mm3=cover_removed.Volume, added_print_quantity=0, new_fasteners=0,')
# The first execution saved completed Carrier/Cover before a receiver-name
# error. Recover those native objects, not another reconstruction of the same
# booleans. Re-run parameter restoration, BOP and all pending contact/export
# checks; a saved document alone is never a passed receipt.
cad = ROOT/'hardware/cad/studies/w5-source-grips-native-r2/SourceCarrierInsulationGrips.FCStd'
if cad.exists():
    start = source.index('    parent = A.openDocument(str(PARENT))')
    end = source.index('    owners, pins = current_owners(A, Part)')
    recovery = """    target=CAD/'SourceCarrierInsulationGrips.FCStd'
    d=A.openDocument(str(target));d.recompute()
    final=d.SourceGripsFinished;link=d.ReceivedCarrier;parameters=d.GripParameters
    assert abs(parameters.GrooveAllowance.Value-.2)<1e-7 and abs(parameters.CoverAllowance.Value-.5)<1e-7
    assert final.Shape.isValid() and len(final.Shape.Solids)==1 and not final.Shape.check(True)
    nominal=final.Shape.Volume;parameters.GrooveAllowance=.3;d.recompute();assert final.Shape.Volume<nominal
    parameters.GrooveAllowance=.2;d.recompute();assert abs(final.Shape.Volume-nominal)<1e-5
    added=final.Shape.cut(link.Shape);assert added.Volume>0 and link.Shape.cut(final.Shape).Volume<1e-5
    for wire in SEATS:assert d.getObject(wire+'OpenSeat').Shape.common(link.Shape).Volume>1e-5
    bands={wire+'_T18I':Part.read(str(OUT/(wire+'_T18I_WORLD.brep'))) for wire in SEATS}
    cover_parent_path=ROOT/'hardware/cad/studies/w5-source-cover-passages-native-r1/SourceCoverCurvedPassages.FCStd'
    cover=d.SourceGripCoverFinished;cover_link=d.ReceivedSourceCover
    assert cover.Shape.isValid() and len(cover.Shape.Solids)==1 and not cover.Shape.check(True)
    cover_removed=cover_link.Shape.cut(cover.Shape);assert cover_removed.BoundBox.ZMin>125
    cv=cover.Shape.Volume;parameters.CoverAllowance=.6;d.recompute();assert cover.Shape.Volume<cv
    parameters.CoverAllowance=.5;d.recompute();assert abs(cover.Shape.Volume-cv)<1e-5;d.save()
    print('SOURCE_GRIPS_SAVED_NATIVE_RECOVERED',flush=True)
"""
    source = source[:start] + recovery + source[end:]
namespace = dict(__file__=str(Path(__file__).resolve()), __name__='source_grips_r2')
exec(compile(source, str(Path(__file__).resolve()), 'exec'), namespace)
if __name__ == '__main__': namespace['main']()

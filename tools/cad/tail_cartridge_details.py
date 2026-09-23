"""Local feature equivalence, screw/tool envelopes, and reference horn play."""
import json
from pathlib import Path
import pilot
from tail_cartridge_study import OUT, TARGET, PRINTS, HOLES


def main():
    import FreeCAD as A
    import Part
    assert not A.GuiUp and not A.listDocuments()
    def common(a,b):
        return abs(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.
    def cyl(r,h,z,x=171,y=-6):
        return Part.makeCylinder(r,h,A.Vector(x,y,z))
    try:
        d=A.openDocument(str(TARGET));d.recompute()
        shapes={n:pilot.global_shape(d.getObject(n)) for n in PRINTS}
        # Independent intended solids catch auto-reversed MCP pockets.
        def outline(z,h):
            return cyl(13.5,h,z).fuse(Part.makeBox(8.2,32,h,A.Vector(166.9,-19,z)))
        lower=outline(88,2).cut(cyl(3.8,10,86))
        upper=outline(90,4).cut(cyl(4,10,86))
        upper=upper.cut(Part.makeBox(4.6,28.4,2.35,A.Vector(168.7,-17.2,90)))
        upper=upper.cut(Part.makeBox(17.1,4.25,2.35,A.Vector(162.45,-8.125,90)))
        for x,y in HOLES:
            lower=lower.fuse(cyl(3.1,2.2,90,x,y)).cut(cyl(1.2,10,86,x,y)).cut(cyl(2.3,2.2,88,x,y))
            upper=upper.cut(cyl(1.2,10,86,x,y)).cut(cyl(3.3,2.2,90,x,y))
        source=pilot.document(A,pilot.CAD/'modules/tail/TailSupport.FCStd')
        old=pilot.global_shape(source.getObject('SupportedRoot34'))
        root=old.fuse(cyl(11.8,2,96).cut(cyl(5.5,2,96))).cut(cyl(14,2,92))
        for x,y in HOLES:root=root.cut(cyl(1.2,4,94,x,y))
        intended=dict(zip(PRINTS,[lower,upper,root]))
        comparisons={n:[s.cut(intended[n]).Volume,intended[n].cut(s).Volume] for n,s in shapes.items()}
        assert all(abs(v)<1e-5 for row in comparisons.values() for v in row),comparisons
        for o in d.Objects:
            if o.Name.startswith(('CartridgeBolt','CartridgeNut','CommunityHorn')):
                o.Shape.check(True)
                assert o.Shape.isValid() and len(o.Shape.Solids)==1
        # This OD6 probe is explicitly only pre-root access, not a real screwdriver.
        driver=cyl(3,30,93.05)
        pre_root={n:common(driver,s) for n,s in shapes.items() if n!='SupportedRoot34'}
        assert all(v<.001 for v in pre_root.values())
        assembled_block=common(driver,shapes['SupportedRoot34'])
        assert assembled_block>1
        horn=d.getObject('CommunityHornEnvelope').Shape.copy()
        play=[]
        for i in range(-20,21):
            angle=i/10
            h=horn.copy();h.rotate(A.Vector(171,-6,0),A.Vector(0,0,1),angle)
            play.append({'relative_angle_deg':angle,'upper_overlap_mm3':common(h,upper)})
        report={'study_sha256':pilot.sha(TARGET),'tool_sha256':pilot.sha(Path(__file__)),
            'expected_boolean_difference_mm3':comparisons,
            'nominal_fasteners_and_reference_strict_bop':True,
            'pre_root_OD6_tool_intersections_mm3':pre_root,
            'assembled_root_blocks_OD6_tool_mm3':assembled_block,
            'tool_access_scope':'Nominal OD6 envelope before root only; assembled root blocks it. No full service approval or real tool specification.',
            'relative_horn_play_samples':play,
            'play_scope':'Geometric free play of approximate cross horn, not servo backlash, stiffness, contact force or measured fit.',
            'nominal_wall_mm':{'long_arm_roof':1.65,'upper_roof_over_boss':1.8,'boss_wall_at_head_recess':.8,'upper_web_between_boss_pocket_and_long_arm':.9,'root_outer_annulus_after_undercut':2},
            'print_orientations_proposed':{'LowerRetainerPETG':'Z88 face on bed; head recess needs bridging/support trial','UpperCarrierPETG':'Z94 flat face on bed; flip so cross pockets face upward','SupportedRoot34':'Unresolved: underside step, cantilevered tail tongue, spindle load direction'},
            'nominal_boss_radial_clearance_mm':.2,'print_ready':False,'cad_saved':False}
        (OUT/'cartridge-details.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n')
        print(json.dumps({'booleans':comparisons,'tool_block':assembled_block,'play_first_contacts':[r for r in play if .001<r['upper_overlap_mm3']<1]}),flush=True)
    finally:
        for n in list(A.listDocuments()):A.closeDocument(n)


if __name__=='__main__':main()

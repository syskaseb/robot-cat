"""Native rib with a clearance notch matching the retained bracket bounds.

Preserve failed R4/R5 evidence. Do not move the entire rib again: notch only
the bracket corner with0.5mm nominal allowance and retain the outer rib web.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_feed_reliefs_native_r5.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r5'", "OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r6'")
replace("CAD = ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r5'", "CAD = ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r6'")
replace("            union=d.addObject('Part::MultiFuse','FeedReliefTools');union.Shapes=tools;union.Refine=False", """            if len(tools)==1:
                union=tools[0]  # OCCT MultiFuse requires at least two operands.
            else:
                union=d.addObject('Part::MultiFuse','FeedReliefTools');union.Shapes=tools;union.Refine=False""")
replace("                unionfinal=d.addObject('Part::Fuse','FeedReliefsFinished');", """                bracket_path=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1/CoverBracket_-84_1.brep'
                bracket=load(bracket_path);bb=bracket.BoundBox
                notch=d.addObject('Part::Box','BracketClearanceTool')
                notch.Length=bb.XLength+1;notch.Width=bb.YLength+1;notch.Height=bb.ZLength+1
                notch.Placement.Base=A.Vector(bb.XMin-.5,bb.YMin-.5,bb.ZMin-.5)
                cutrib=d.addObject('Part::Cut','NotchedFrontLeftLipBridge');cutrib.Base=rib;cutrib.Tool=notch;cutrib.Refine=False
                rib.Visibility=False;notch.Visibility=False;rib=cutrib;d.recompute()
                assert rib.Shape.isValid() and len(rib.Shape.Solids)==1 and rib.Shape.Volume>250
                unionfinal=d.addObject('Part::Fuse','FeedReliefsFinished');""")
replace("    pins = {'tools/electronics/servo_fuse_feed_reliefs_native_r4.py'", """    pins = {'tools/electronics/servo_fuse_feed_reliefs_native_r5.py':sha(ROOT/'tools/electronics/servo_fuse_feed_reliefs_native_r5.py'),
            'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r5/bridge-fit.json':sha(ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r5/bridge-fit.json'),
            'tools/electronics/servo_fuse_feed_reliefs_native_r4.py'""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

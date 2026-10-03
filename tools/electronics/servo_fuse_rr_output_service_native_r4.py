"""Connect to the real raised bank pillar with one supported overhead frame.

R3's floor-only bridge had zero main-bank embed. Actual material is the
pillarX-59..-55/Y-97..-95.35 aboveZ124.2. Connect to it atZ128..130,
then down the west side outside both upright lever sectors and body.
This is one coherent bracket, not guessed support from a bounding box.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_output_service_native_r3.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-rr-output-service-native-r3','servo-fuse-rr-output-service-native-r4')
code=code.replace("    previous=ROOT/", "    pin(ROOT/'tools/electronics/servo_fuse_rr_output_service_native_r3.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-service-native-r3/bridge-root-failure.json')\n    previous=ROOT/",1)
a=code.index("        bridge=d.addObject('Part::Box'");b=code.index('        d.recompute()',a)
code=code[:a]+'''        bridgeparts=[]
        for name,b in [('RRWestSupportColumn',[-70.2,-97,109.35,-67.2,-95.35,130]),
                       ('RRServiceOverheadArm',[-70.2,-97,128,-55,-95.35,130])]:
            o=d.addObject('Part::Box',name)
            o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=A.Vector(*b[:3]);bridgeparts.append(o)
        bridge=d.addObject('Part::MultiFuse','RRIndependentServiceFrame');bridge.Shapes=bridgeparts;bridge.Refine=False
''' +code[b:]
exec(compile(code,str(Path(__file__).resolve()),'exec'))

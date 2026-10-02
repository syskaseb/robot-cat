"""R2 detached rear skirt: one integral30x5x4bridge on its inside edge."""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_cover_native_r2.py')
code=base.read_text(encoding='utf-8').replace('servo-fuse-cover-native-r2','servo-fuse-cover-native-r3')
# R2 is a source wrapper; inject into the base source before it is executed.
code=code.replace("exec(compile(code,str(Path(__file__).resolve()),'exec'))", """
code=code.replace('d.recompute();s=previous.Shape.copy()', '''
        sk=d.addObject('Sketcher::SketchObject','RearBridgeProfile');sk.Placement.Base.z=136
        rect(sk,110,84,30,5);sketches.append(sk)
        bridge=d.addObject('Part::Extrusion','RearSkirtBridge');bridge.Base=sk;bridge.Dir=A.Vector(0,0,4);bridge.Solid=True
        fused=d.addObject('Part::MultiFuse','BankCoverConnected');fused.Shapes=[previous,bridge];fused.Refine=True
        previous.Visibility=False;bridge.Visibility=False;sk.Visibility=False;previous=fused
        d.recompute();s=previous.Shape.copy()''')
code=code.replace('cuts_mm=cuts,preserve=', 'cuts_mm=cuts,adds_mm=[[110,84,136,140,89,140]],preserve=')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

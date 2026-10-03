"""Keep the main-bank/tray connection; cut only the three proven witnesses.

R1's whole approach box severed the tray (2solids). Preserve that failure.
The approach outsideY=-98 is already clear in R2. No reason to cut the
supporting bank there: subtract only measured obstructing native material
plus the stated clearance, in three editable boxes.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_output_service_native_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-rr-output-service-native-r1','servo-fuse-rr-output-service-native-r2')
code=code.replace("    previous=ROOT/", "    pin(ROOT/'tools/electronics/servo_fuse_rr_output_service_native_r1.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-service-native-r1/failure.json')\n    previous=ROOT/",1)
a=code.index("        tool=d.addObject('Part::Box'");b=code.index("        f=d.addObject('Part::Cut'",a)
code=code[:a]+'''        tools=[]
        for k,hit in enumerate(proof['hits']):
            lo=hit['bounds_mm'][:3];hi=hit['bounds_mm'][3:]
            tool=d.addObject('Part::Box','RRLeverWitnessOpening'+str(k))
            tool.Placement.Base=A.Vector(*(v-.2 for v in lo))
            for prop,axis in [('Length',0),('Width',1),('Height',2)]:
                tool.setExpression(prop,f'{hi[axis]-lo[axis]:.12f} mm + 2 * RRServiceParameters.Clearance')
            tools.append(tool)
        tool=d.addObject('Part::Compound','RRLeverServiceOpenings');tool.Links=tools
''' +code[b:]
exec(compile(code,str(Path(__file__).resolve()),'exec'))

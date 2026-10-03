"""FR lap has real straight insulation under both9mm sleeve overlaps.

The unexecuted R5 factory tangent was only0.164mm long and was not a valid
straight sleeve model. Keep OD9/26mm sleeve, R20/R25.2, strip8 and nominal
factory100mm. W042 alone has2mm rework reserve (project allowance, not a
supplier requirement). The west return extends7mm for the other9mm overlap.
Exterior cover passage/protection is explicitly still OPEN, no selection.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r5.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r5'", "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r6'")
replace("f.line([-62.1,-36,cz])", "f.line([-71.5,-36,cz])")
replace("            e.arc(-X,south,25.2)\n            west_x=e.p.x;assert west_x < -107", "            e.line([e.p.x-7,e.p.y,e.p.z]);e.arc(-X,south,25.2)\n            west_x=e.p.x;assert west_x < -114")
replace("e.line([-70.1,-36,cz]);lap(leg,in_id,f,e,-X,X,X)", """e.line([-79.5,-36,cz])
            assert f.edges[-1].Length>=9 and e.edges[-1].Length>=9
            lap(leg,in_id,f,e,-X,X,X)""")
replace("        total=path.Length+strip+10", "        reserve=2 if name=='W042_factory' else 10\n        total=path.Length+strip+reserve")
replace("rework_assumption_mm=10,minimum_blank_with_allowance_mm=total", "rework_assumption_mm=reserve,minimum_blank_with_allowance_mm=total")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r4.py')", "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r4.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r5.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

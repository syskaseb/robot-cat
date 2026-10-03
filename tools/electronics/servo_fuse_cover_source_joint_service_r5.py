"""Join the full service arch to the measured upper wall section at Z175.

R4 longitudinal beam was outside the wall: two solids. One transverse
native beam now reaches the actual wall at X-69.5/Y-47.5, above W042.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_source_joint_service_r4.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='arch_r4_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-cover-source-joint-service-r4','servo-fuse-cover-source-joint-service-r5')
old="""    bridge=d.addObject('Part::Fuse','FrontLeftMountServiceArch')
    bridge.Base=column;bridge.Tool=beam;bridge.Refine=False"""
new="""    crossbeam=d.addObject('Part::Box','FrontLeftServiceArchWallBeam')
    crossbeam.Length=30;crossbeam.Width=6;crossbeam.Height=4;crossbeam.Placement.Base=A.Vector(-92,-50,174)
    bridge=d.addObject('Part::MultiFuse','FrontLeftMountServiceArch')
    bridge.Shapes=[column,beam,crossbeam];bridge.Refine=False"""
assert old in code;code=code.replace(old,new)
code=code.replace('native_service_arch_boxes_mm=[[-92,-100,123,7,3,55],[-92,-100,174,7,60,4]]',
    'native_service_arch_boxes_mm=[[-92,-100,123,7,3,55],[-92,-100,174,7,60,4],[-92,-50,174,30,6,4]]')
exec(compile(code,str(Path(__file__).resolve()),'exec'))

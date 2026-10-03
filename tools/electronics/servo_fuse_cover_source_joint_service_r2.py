"""Same full insulated passages with one short native mount-to-wall bridge.

R1 split off the original front-left mount. Keep that mount and connect it
on the left of the entire W042 sleeve passage, not through the wire space.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_source_joint_service_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-cover-source-joint-service-r1','servo-fuse-cover-source-joint-service-r2')
marker="    final=d.addObject('Part::Cut','CoverSourceJointServiceFinished')"
assert marker in code
code=code.replace(marker,"""    bridge=d.addObject('Part::Box','FrontLeftMountServiceBridge')
    bridge.Length=8;bridge.Width=12;bridge.Height=4;bridge.Placement.Base=A.Vector(-91,-100,130)
    servicebase=d.addObject('Part::Fuse','CoverWithMountServiceBridge')
    servicebase.Base=parent;servicebase.Tool=bridge;servicebase.Refine=False
    final=d.addObject('Part::Cut','CoverSourceJointServiceFinished')""")
code=code.replace('final.Base=parent; final.Tool=compound','final.Base=servicebase; final.Tool=compound')
code=code.replace('v=s.Volume; assert removed.Volume>0 and v<parent.Shape.Volume','v=s.Volume; bridgeadded=bridge.Shape.cut(parent.Shape).Volume; assert removed.Volume>0')
code=code.replace('subtractive_by_native_construction=True','subtractive_by_native_construction=False,native_union_bridge_mm=[-91,-100,130,8,12,4],bridge_added_mm3=bridgeadded')
code=code.replace("status='NATIVE_COVER_INSULATED_SOURCE_JOINT_PASSAGES_COMPLETE_SHARED_REMOVAL_OPEN'","status='NATIVE_COVER_SOURCE_JOINT_PASSAGES_AND_MOUNT_BRIDGE_COMPLETE_SHARED_REMOVAL_OPEN'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

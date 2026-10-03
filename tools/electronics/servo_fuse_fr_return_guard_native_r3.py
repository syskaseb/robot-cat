"""Add the exact remaining socket-head clearance, retaining the tab seat.

R2 shared fit had only4.457mm3 Screw0/Guard contact. Clear the5.5x3mm
DIN912 head with6mm diameter/3.3mm tall native tool starting at149.5,
NOT below the bearing face. Keep R2 panel fit, source capture and hardware.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_fr_return_guard_native_r2.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-return-guard-native-r2'","OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-return-guard-native-r3'")
replace("CAD=ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r2'","CAD=ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r3'")
replace("pocket.Placement.Base=V(x,-94,141.7);gtools.append(pocket)",
        """pocket.Placement.Base=V(x,-94,141.7);gtools.append(pocket)
            cap=guarddoc.addObject('Part::Cylinder','GuardHeadClearance'+str(i));cap.Radius=3;cap.Height=3.3;cap.Placement.Base=V(x,-94,149.5);gtools.append(cap)""")
replace("    pins={};V=A.Vector", """    pins={};V=A.Vector
    pins['tools/electronics/servo_fuse_fr_return_guard_native_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_fr_return_guard_native_r2.py')
    pins['hardware/electronics/full-cat/servo-fuse-fr-return-guard-native-r2/fit.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-fr-return-guard-native-r2/fit.json')""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

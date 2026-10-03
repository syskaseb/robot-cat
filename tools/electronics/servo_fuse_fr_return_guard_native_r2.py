"""Fit the channel to existing casing/panel without changing their shape.

R1 captured all external source wire but six installation contacts remained.
The actual panel underside is144.5, not144.7; use its measured2mm thickness.
Trim ONLY the channel at the Cover/bank seam, retain the complete attachment
tab and bearing rings. Full-depth guard holes/nut pockets clear hardware.
R1 failed evidence is preserved; no external dimensions are invented.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_fr_return_guard_native_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-fr-return-guard-native-r1','servo-fuse-fr-return-guard-native-r2')
def replace(old,new):
    global code
    assert code.count(old)==1,old[:100]
    code=code.replace(old,new)
replace("    pins={};V=A.Vector", """    pins={};V=A.Vector
    pins['tools/electronics/servo_fuse_fr_return_guard_native_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_fr_return_guard_native_r1.py')
    pins['hardware/electronics/full-cat/servo-fuse-fr-return-guard-native-r1/fit.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-fr-return-guard-native-r1/fit.json')""")
replace("gu=guarddoc.addObject('Part::MultiFuse','GuardStock');gu.Shapes=stocks;gu.Refine=False",
        """channel=guarddoc.addObject('Part::MultiFuse','ChannelStock');channel.Shapes=stocks[:-1];channel.Refine=False
        case=nbox(guarddoc,'ExistingCoverSeamClearance',[-98.5,-95.78,132,-94.5,85.5,145.98])
        panel=nbox(guarddoc,'ExistingBankSeamClearance',[-97.3,-97.3,144.2,-94.7,-94.7,146.8])
        seamtools=guarddoc.addObject('Part::MultiFuse','ChannelSeamTools');seamtools.Shapes=[case,panel]
        trimmed=guarddoc.addObject('Part::Cut','FittedChannel');trimmed.Base=channel;trimmed.Tool=seamtools;trimmed.Refine=False
        gu=guarddoc.addObject('Part::Fuse','GuardStock');gu.Base=trimmed;gu.Tool=stocks[-1];gu.Refine=False""")
replace("o.Height=10;o.Placement.Base=V(x,-94,140)",
        "o.Height=40 if d==guarddoc else 10;o.Placement.Base=V(x,-94,130 if d==guarddoc else 140)")
replace("            shank=Part.makeCylinder", """            pocket=guarddoc.addObject('Part::Cylinder','GuardNutClearance'+str(i));pocket.Radius=3.5;pocket.Height=3.4;pocket.Placement.Base=V(x,-94,141.7);gtools.append(pocket)
            shank=Part.makeCylinder""")
replace("-94+rad*math.sin(math.pi/6+k*math.pi/3),142.3)","-94+rad*math.sin(math.pi/6+k*math.pi/3),142.1)")
replace("V(x,-94,142.2)","V(x,-94,142)")
replace("bank_panel_mm=1.8","bank_panel_mm=2")
replace("nominal_thread_beyond_nut_mm=.8","nominal_thread_beyond_nut_mm=.6")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""Make the new cantilever stop lips integral, retaining the R2 shared layout.

The lips had a lateral0.5mm body clearance but no web to their roof. Add a
0.8mm-thick underlying bridge for each lip; it never enters the body. This
is a native attachment correction, not another holder-position search.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_cradles_native_r2.py')
code=parent.read_text(encoding='utf-8')


def replace(old,new):
    global code
    assert code.count(old)==1,old[:80]
    code=code.replace(old,new)


replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r2'", "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r3'")
replace("CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r2'", "CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r3'")
replace("    owners=retained_owners(pin,load,Part)", "    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r2.py')\n    owners=retained_owners(pin,load,Part)")
replace("fy0,fy1=(-95,-92) if leg=='RR'", "fy0,fy1=(-94,-92) if leg=='RR'")
replace("            integral.append((leg+'Stop'+str(j),lip,None,thick));parts[leg+'_Stop_'+str(j)]=box(lip)", """            integral.append((leg+'Stop'+str(j),lip,None,thick));parts[leg+'_Stop_'+str(j)]=box(lip)
            ya,yb=(b[1]-1.5,b[1]+.2) if j==0 else (b[4]-.2,b[4]+1.5)
            web=[roof[0],ya,b[2]-.8,roof[3],yb,b[2]]
            integral.append((leg+'StopWeb'+str(j),web,None,thick));parts[leg+'_StopWeb_'+str(j)]=box(web)""")
replace("    # Persist actual editable native construction even if shared fit is rejected.", """    save(OUT/'static-fit.json',dict(hits=hits,errors=errors,pairs=pairs,mounts=mount,source_sha256=pins,script_sha256=sha(Path(__file__))))
    # Persist actual editable native construction even if shared fit is rejected.""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

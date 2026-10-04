"""Go around rear terminal bodies, not over the occupied centre fuse family.

R1/R2 flights above central x64 cut installed source/head wires and F_AUX.
Keep113.5mm elevation; the outer rear approach clears blocks before entering
the x93 gap. Two low grips atY+/-20 avoid the ground blocks and centre fuses.
"""
from pathlib import Path
import w5_xa05_joint_repair_r2 as J
source=J.source


def replace(a,b):
    global source
    assert source.count(a)==1,a
    source=source.replace(a,b)


replace("w5-xa05-joint-repair-r2'","w5-xa05-joint-repair-r3'")
begin=source.index('def layout():')
end=source.index('\n\ndef main():',begin)
source=source[:begin]+'''def layout():
    c=Path15([123,9.5,113.5],Y)
    c.arc(X);c.arc(Y)
    c.line([153,55,113.5]);c.arc(mul(X,-1))
    c.line([108,70,113.5]);c.arc(mul(Y,-1))
    c.line([93,-42,113.5]);c.arc(X)
    c.line([110.5,-57,113.5])
    assert math.dist(c.p,[110.5,-57,113.5])<1e-7
    return dict(wire='XA05',a='P0G2.5',b='G_AUX.1',edges=c.edges,
        wire_SKU='HELU23501',OD_mm=2.5,min_fixed_R_mm=15,
        path_mm=sum(e['length_mm'] for e in c.edges),actual_cut_mm=None,
        nominal_trial_blank_mm=math.ceil((sum(e['length_mm'] for e in c.edges)+82)/10)*10,
        ends_preserved=True,blocks_unchanged=True,selected=False,physical_pass=False)
''' +source[end:]
replace("for name,y in [('North',27.05),('South',-24.5)]", "for name,y in [('North',20),('South',-20)]")
replace('raw=[60.7,y-3.3,108.8,67.3,y+3.3,135.7]', 'raw=[89.7,y-3.3,108.8,96.3,y+3.3,114.2]')
replace('A.Vector(64,y-3.4,135)', 'A.Vector(93,y-3.4,113.5)')
replace('left,right=59.9,68.1;bottom=109.5;top=137.2', 'left,right=88.9,97.1;bottom=109.5;top=114.75')
replace('y+1.6,138.5', 'y+1.6,116.1')
replace('box([right-1.4,y-2.5,bottom-.1,right+3.6,y+2.5,bottom+3.9])',
        'box([right+.1,y-2.5,bottom-.1,right+5.1,y+2.5,bottom+3.9])')
replace('groove_centre=[64,y,135]', 'groove_centre=[93,y,113.5]')
replace("tie_SKU='111-03110 T18I'", "tie_SKU='111-02370 T18I-PA66-BK'")
replace("    finish=datetime.now(timezone.utc)", "    finish=datetime.now(timezone.utc)\n    pins.append(Path(J.__file__))")
exec(compile(source,str(Path(__file__).resolve()),'exec'))

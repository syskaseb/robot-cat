"""One diagonal departure clears the existing RL_P band, not the other nets.

The band ends atX56.1. WithOD3, shift the downwardR10 bend3mm east
at its end. This keeps it below the G1 departures, unlike R2's high east
bend. All geometry down to the original MAIN pad is checked together.
"""
from pathlib import Path
import math
import w5_main_ground_low_return as base
from w5_s1_source_layout_r2 import CentreLine
from w5_parallel_connection import connect


def recipe(family):
    start=family['ends']['W060']['edges'][0]['start']
    c=CentreLine(start,[0,1,0]);c.line([start[0],start[1]+6,start[2]])
    c.arc([.3,0,-math.sqrt(.91)],radius=10)
    angle=math.acos(.3)
    c.arc([math.sqrt(.91),0,.3],angle=angle,radius=10)
    pre_tail=[122.5,0,105]
    c.edges.extend(connect(c.p,pre_tail,[1,0,0],10));c.p=pre_tail;c.t=[1,0,0]
    c.arc([0,0,-1],radius=10)
    assert math.dist(c.p,[132.5,0,95])<1e-7 and math.dist(c.t,[0,0,-1])<1e-7
    return dict(wire='W060',edges=c.edges,OD_mm=3,radius_mm=10,
        start=start,target=c.p,radius_supplier_qualified=False,
        retained_tail_radius_bound_mm=6,retained_tail_not_R10=True,
        diagonal_first_bend_offset_mm=3,retained_RL_P_band=True)


source=Path(base.__file__).read_text(encoding='utf-8')
source=source.replace("w5-main-ground-low-return-r1'","w5-main-ground-low-return-r3'")
source=source.replace('pins += [Path(__file__),','pins += [Path(__file__),Path(parent_source_path),')
ctx=dict(__name__='main_ground_r3_definition',__file__=__file__,parent_source_path=base.__file__)
exec(compile(source,__file__,'exec'),ctx)
ctx['recipe']=recipe
if __name__=='__main__':ctx['main']()

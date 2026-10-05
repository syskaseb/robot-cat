"""Retain R2's rear clearance and the previously clear upper AUX cage bend.

R2's new low slope crosses XA04. Terminate the west flight with aR15
downward bend and the reversed existingR15 upper cage bend, not that slope.
Six millimetres at the cage remain straight; the middle join is tangent.
"""
from pathlib import Path
import math
import w5_aux_diagonal_loop as base
import w5_aux_diagonal_loop_r2 as upper
from w5_four_low_returns import reverse_edges
from w5_s1_source_layout_r2 import CentreLine


def recipe(family,target):
    row=upper.recipe(family,target)
    retained=row['edges'][:-5]
    start=retained[-1]['end']
    assert math.dist(start,[target[0]-55,target[1],145.5])<1e-7
    b=CentreLine(target,[-1,0,0]);b.line([target[0]-6,target[1],target[2]])
    b.arc([0,0,1],radius=15)
    c=CentreLine(start,[1,0,0]);c.line([b.p[0]-15,start[1],start[2]])
    c.arc([0,0,-1],radius=15);c.line(b.p)
    row['edges']=retained+c.edges+reverse_edges(b.edges)
    row['body_mm']=sum(e['length_mm'] for e in row['edges'])
    row['nominal_mm']=row['body_mm']+22
    row['trial_blank_mm']=math.ceil((row['nominal_mm']+30)/10)*10
    row['upper_AUX_cage_bend_retained']=True
    return row


source=Path(base.__file__).read_text(encoding='utf-8')
source=source.replace("w5-aux-diagonal-loop-r1'","w5-aux-diagonal-loop-r3'")
source=source.replace('pins += [Path(__file__),','pins += [Path(__file__),Path(parent_source_path),Path(r2_source_path),scope.ROOT/\'tools/electronics/w5_four_low_returns.py\',')
ctx=dict(__name__='aux_r3_definition',__file__=__file__,parent_source_path=base.__file__,r2_source_path=upper.__file__)
exec(compile(source,__file__,'exec'),ctx)
ctx['recipe']=recipe
if __name__=='__main__':ctx['main']()

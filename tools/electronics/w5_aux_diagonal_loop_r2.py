"""Keep AUX below151.5mm Pi wires, above the received W061 cage arc.

R1's first diagonal ends at[135.5,5.5,122.5], only3mm above
the W061 arc at thatX/Y. A60/80 diagonal and10mm straight instead
end at[135.5,2.5,125.5] and put the west flight at145.5mm.
This is one joint interface correction, not another height search.
"""
from pathlib import Path
import w5_aux_diagonal_loop as base

source=Path(base.__file__).read_text(encoding='utf-8')
for old,new in (
    ("w5-aux-diagonal-loop-r1'","w5-aux-diagonal-loop-r2'"),
    ("c.arc([0,.8,.6],radius=15);c.line(add(c.p,mul(c.t,15)))",
     "c.arc([0,.6,.8],radius=15);c.line(add(c.p,mul(c.t,10)))"),
    ("pins += [Path(__file__),","pins += [Path(__file__),Path(parent_source_path),")):
    assert old in source
    source=source.replace(old,new)
ctx=dict(__name__='aux_r2_definition',__file__=__file__,parent_source_path=base.__file__)
exec(compile(source,__file__,'exec'),ctx)
recipe=ctx['recipe']
if __name__=='__main__':ctx['main']()

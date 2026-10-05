"""Leave the RL_P right band before descending, preserving the complete tail.

The right band occupiesX54..56.1/Y32.75..35.25/Z103.8..119.2.
R1 descends atX57 with a1.5mm envelope and touches it. Turn east first:
the descent is atX67..77, not another small shift against that band.
"""
from pathlib import Path
import w5_main_ground_low_return as base

source=Path(base.__file__).read_text(encoding='utf-8')
old='c.arc([0,0,-1],radius=10);c.arc([1,0,0],radius=10)'
new='c.arc([1,0,0],radius=10);c.arc([0,0,-1],radius=10);c.arc([1,0,0],radius=10)'
assert old in source;source=source.replace(old,new)
source=source.replace("w5-main-ground-low-return-r1'","w5-main-ground-low-return-r2'")
source=source.replace('pins += [Path(__file__),','pins += [Path(__file__),Path(parent_source_path),')
ctx=dict(__name__='main_ground_r2_definition',__file__=__file__,parent_source_path=base.__file__)
exec(compile(source,__file__,'exec'),ctx)
recipe=ctx['recipe']
if __name__=='__main__':ctx['main']()

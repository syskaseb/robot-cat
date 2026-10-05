"""Retain the clear whole FR flight; put FL west crossing south of AUX/strap.

R1 intersects XA02/XA04 only atX13..19/Y-1..2.6/Z161..166 and
W065_band atX46..51/Y0..4/Z160..164. Move the WHOLE west corridor
toY-36.5, not successive small offsets around those three crossings.
Both outer leg turns remainR21, with6mm at their cages.
"""
from pathlib import Path
import w5_front_paired_flights as base

source=Path(base.__file__).read_text(encoding='utf-8')
old='''            c.arc([-1,0,0],radius=21)
            before_turn=[target[0]-6,c.p[1],target[2]]'''
new='''            c.line([c.p[0],-15.5,c.p[2]])
            c.arc([-1,0,0],radius=21)
            before_turn=[target[0]-6,c.p[1],target[2]]'''
assert old in source;source=source.replace(old,new)
old='''            radius=(target[1]-c.p[1])/2
            assert radius>=21
            c.arc([0,1,0],radius=radius);c.arc([1,0,0],radius=radius)'''
new='''            c.arc([0,1,0],radius=21)
            c.line([c.p[0],target[1]-21,c.p[2]])
            c.arc([1,0,0],radius=21)'''
assert old in source;source=source.replace(old,new)
source=source.replace("w5-front-paired-flights-r1'","w5-front-paired-flights-r2'")
source=source.replace('pins += [Path(__file__),','pins += [Path(__file__),Path(parent_source_path),')
ctx=dict(__name__='front_r2_definition',__file__=__file__,parent_source_path=base.__file__)
exec(compile(source,__file__,'exec'),ctx)
recipes=ctx['recipes']
if __name__=='__main__':ctx['main']()

"""Whole source/end/support correction from the R4 contact witnesses.

Keep the clear east bypass; west flight avoids the PWM outlet, one low grip
stays past DATA anchors, and the outrigger attaches at the documented empty
north-east patch instead of the populated positive-source inlet.
"""
from pathlib import Path
BASE=Path(__file__).with_name('w5_xa05_outer_support_r4.py')
source=BASE.read_text(encoding='utf-8')


def replace(a,b):
    global source
    assert source.count(a)==1,a
    source=source.replace(a,b)


replace("w5-xa05-outer-support-r4'","w5-xa05-outer-support-r5'")
replace('c.shift([0,0,7.5]);c.line([153,-12,121]);c.arc(mul(X,-1))',
        'c.shift([0,0,7.5]);c.line([153,-18,121]);c.arc(mul(X,-1))')
replace('c.line([90.5,-27,121]);c.arc(mul(Y,-1));c.arc(X)',
        'c.line([88,-33,121]);c.arc(mul(Y,-1));c.arc(X)')
replace('c.shift([0,0,-7.5]);c.line([110.5,-57,113.5])',
        'c.shift([0,6,-7.5]);c.line([110.5,-57,113.5])')
replace('raw=box([116.7,-30.3,108.8,123.3,-23.7,121.7])',
        'raw=box([132,-36.3,108.8,136,-29.7,121.7])')
replace('groove=cyl([116.6,-27,121],1.5,6.8,(1,0,0))',
        'groove=cyl([131.9,-33,121],1.5,4.2,(1,0,0))')
replace('slots=[box([118.4,y-.8,108.8,121.6,y+.8,123.6]) for y in (-31.1,-22.9)]',
        'slots=[box([132.4,y-.8,108.8,135.6,y+.8,123.6]) for y in (-37.1,-28.9)]')
replace('tunnel=box([118.4,-32.1,109.4,121.6,-21.9,110.8])',
        'tunnel=box([132.4,-38.1,109.4,135.6,-27.9,110.8])')
replace('foot=box([126.5,-17,109,135.5,-1,112])',
        'foot=box([126.5,32,109,135.5,48,112])')
replace('stem=box([132.5,-13.4,111.8,135.5,-6.4,119])',
        'stem=box([132.5,35.6,111.8,135.5,42.6,119])')
replace('bridge=box([133,-13.4,116,156.3,-6.4,119.8])',
        'bridge=box([133,35.6,116,156.3,42.6,119.8]).fuse(box([149.7,-17.5,116,156.3,42.6,119.5]))')
replace('outer_seat=box([149.7,-13.2,119.5,156.3,-6.6,121.7])',
        'outer_seat=box([149.7,-17.3,119.3,156.3,-10.7,121.7])')
assert source.count('(-5,-13)')==3
source=source.replace('(-5,-13)','(44,36)')
replace('cyl([153,-13.3,121],1.5,6.8,(0,1,0))',
        'cyl([153,-17.4,121],1.5,6.8,(0,1,0))')
replace('box([147.9,-11.5,116.3,158.1,-8.3,117.7])',
        'box([147.9,-15.6,115.9,158.1,-12.4,117.7])')
replace('box([x-.8,-11.5,115.9,x+.8,-8.3,123.6])',
        'box([x-.8,-15.6,115.9,x+.8,-12.4,123.6])')
replace('inner.translate(A.Vector(120,-27,0))','inner.translate(A.Vector(134,-33,0))')
replace('outer=band_xz(153,-9.9,122.25,116.4)',
        'outer=band_xz(153,-14,122.25,116.4)')
replace('pins += [Path(__file__),','pins += [BASE,Path(__file__),')
exec(compile(source,str(Path(__file__).resolve()),'exec'))

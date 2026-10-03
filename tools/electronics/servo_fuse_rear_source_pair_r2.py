"""Rear pair below carrier, with separated inner lap joints and straight grips.

R1 outward/upper returns are rejected: carrier, ATO and opposing-end
conflicts. Restore under-carrier routing but lower/shift RL away from W060
and raise RR sleeve clear of RR_G. Both complete sources change together.
"""
from pathlib import Path
src=Path(__file__).with_name('servo_fuse_rear_source_pair_r1.py')
code=src.read_text(encoding='utf-8')
code=code.replace("servo-fuse-rear-source-pair-r1'","servo-fuse-rear-source-pair-r2'")
a=code.index('        normal=Y*.5+Z*math.sqrt(.75)')
b=code.index('        a=f.p;b=e.p;',a)
code=code[:a]+'''        tilt=-.075 if leg=='RL' else .2
        normal=-Y*math.sqrt(1-tilt*tilt)+Z*tilt
        f=Route([right,cy,cz]);f.arc(X,normal,20)
        angle=math.asin(abs(tilt))
        # Flatten tangent to -Y without a hidden kink in the full pipe.
        f.arc(normal,-Y*abs(tilt)-Z*math.copysign(math.sqrt(1-tilt*tilt),tilt),20,angle)
        jx=f.p.x;jz=f.p.z;factory_y=36 if leg=='RL' else -48
        factory_straight=abs(f.p.y-factory_y);assert factory_straight>=14
        f.line([jx,factory_y,jz])
        e=Route([32,sy,129]);delta=Z*(jz-129)
        travel=2*25.2*math.sin(math.acos(1-delta.Length/(2*25.2)))
        assert jx-25.2-32>=travel
        e.line([jx-25.2-travel,sy,129]);e.shift(X,delta,25.2);e.arc(X,Y,25.2)
        ext_y=factory_y-side*8
        assert side*(ext_y-e.p.y)>=14
        e.line([jx,ext_y,jz])
        jy=(factory_y+ext_y)*.5
''' +code[b:]
code=code.replace('centre=(a+b)*.5;axis=-X;','centre=(a+b)*.5;axis=Y;')
code=code.replace('barestart+V(0,dy,0),axis','barestart+X*dy,axis')
code=code.replace("factory_grip_centre_mm=[fx+12,jy,jz],extension_grip_centre_mm=[fx-20,jy,jz]",
                  "factory_grip_centre_mm=list(a+Y*12),extension_grip_centre_mm=list(b-Y*12)")
code=code.replace("    prior=ROOT/", "    pin(src);pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r1/checks.json')\n    prior=ROOT/")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

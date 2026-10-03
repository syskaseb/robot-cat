"""One RL east-return corridor and RR short inner source.

R3 fails against fixed signal/source conductors. Turn RL's joint along X
instead of forcing it between two Y bends. Its full extension uses an east
return, needing an explicit local removable casing if shared fit is clear.
RR removes the unnecessary10mm pre-bend, moving its complete joint/route
away from W078 and PWM. Front/source topology and MTA bodies stay fixed.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rear_source_pair_r3.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rear-source-pair-r3'","servo-fuse-rear-source-pair-r4'")
a=code.index('        tilt=-.2');b=code.index('        a=f.p;b=e.p;',a)
code=code[:a]+'''        if leg=='RL':
            tilt=-.2;normal=-Y*math.sqrt(1-tilt*tilt)+Z*tilt
            f=Route([right,cy,cz]);f.arc(X,normal,20)
            f.arc(normal,-Y*abs(tilt)+Z*math.sqrt(1-tilt*tilt),20,math.asin(abs(tilt)))
            f.arc(-Y,X,20);jz=f.p.z;jy=f.p.y
            f.line([f.p.x+14,jy,jz]);a=f.p
            e=Route([32,sy,129]);e.arc(X,Y,25.2)
            e.line([e.p.x,jy+25.2,129]);e.arc(Y,X,25.2)
            e.shift(X,Z*(jz-129),25.2)
            e.line([a.x+8+14,jy+50.4,jz]);e.arc(X,-Y,25.2,math.pi)
            e.line([a.x+8,jy,jz]);axis=X
            factory_grip=list(a-X*12);extension_grip=list(e.p+X*12)
        else:
            tilt=.2;normal=-Y*math.sqrt(1-tilt*tilt)+Z*tilt
            f=Route([right,cy,cz]);f.arc(X,normal,20)
            f.arc(normal,-Y*abs(tilt)-Z*math.sqrt(1-tilt*tilt),20,math.asin(abs(tilt)))
            jx=f.p.x;jz=f.p.z;factory_y=-47
            assert abs(f.p.y-factory_y)>=14
            f.line([jx,factory_y,jz])
            e=Route([32,sy,129]);delta=Z*(jz-129)
            travel=2*25.2*math.sin(math.acos(1-delta.Length/(2*25.2)))
            assert jx-25.2-32>=travel
            e.line([jx-25.2-travel,sy,129]);e.shift(X,delta,25.2);e.arc(X,Y,25.2)
            assert side*(factory_y-side*8-e.p.y)>=14
            e.line([jx,factory_y-side*8,jz]);axis=Y
            jy=(factory_y+e.p.y)*.5
            factory_grip=list(f.p+Y*12);extension_grip=list(e.p-Y*12)
''' +code[b:]
code=code.replace('centre=(a+b)*.5;axis=Y;', 'centre=(a+b)*.5;')
code=code.replace('barestart+X*dy,axis', "barestart+(Y if leg=='RL' else X)*dy,axis")
code=code.replace('factory_grip_centre_mm=list(a+Y*12),extension_grip_centre_mm=list(b-Y*12)',
                  'factory_grip_centre_mm=factory_grip,extension_grip_centre_mm=extension_grip')
code=code.replace("    pin(parent);pin(src);", "    pin(parent);pin(src);pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r3/checks.json');")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

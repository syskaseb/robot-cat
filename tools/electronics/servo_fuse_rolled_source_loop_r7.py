"""Complete FR feed: rise outside FL cages before the west return.

The R6 horizontal corner crossed FL_P/FL_G below their118mm top.
Use a simultaneous east/up S-offset to stay outside FL_G until clear,
then rise to145mm outside the FL holder before the westward bend.
Factory half-turn is tilted down8.2mm so its return clears F_PI;
the opposed lap has9mm straight insulation on both sides atY-36.
The2mm W042 rework allowance and100mm usable factory lead remain
PROJECT assumptions; no supplier/physical fit or exterior casing PASS.
"""
from pathlib import Path

parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r6.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r6'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r7'")
old="""            north=V(0,1,0);south=-north
            f=Route([right,cy,cz]);f.arc(X,north,20,math.pi)
            f.shift(-X,south*4,20);assert f.p.x>=-62.1
            f.line([-71.5,-36,cz])
            e=Route([-24,11,113.5]);e.line([-24,17,113.5])
            e.arc(north,-X,25.2);e.shift(-X,Z*12.5,25.2)
            e.line([e.p.x-7,e.p.y,e.p.z]);e.arc(-X,south,25.2)
            west_x=e.p.x;assert west_x < -114
            e.line([west_x,-10.8,cz]);e.arc(south,X,25.2)
            e.line([-79.5,-36,cz])
            assert f.edges[-1].Length>=9 and e.edges[-1].Length>=9
            lap(leg,in_id,f,e,-X,X,X)"""
new="""            north=V(0,1,0);south=-north
            tilt=math.asin(8.2/40)
            normal=north*math.cos(tilt)-Z*math.sin(tilt)
            f=Route([right,cy,cz]);f.arc(X,normal,20,math.pi)
            joint_z=117.8
            assert abs(f.p.z-joint_z)<1e-6
            f.shift(-X,south*(f.p.y+36),20)
            f.line([-69.5,-36,joint_z])
            # AtY30.5 the cable is above118mm, before entering FL_G's Xspan.
            e=Route([-24,11,113.5]);e.shift(north,V(6,0,12.5),25.2)
            e.shift(north,Z*19,25.2)
            e.arc(north,-X,25.2);e.line([-88.3,e.p.y,145])
            e.arc(-X,south,25.2);assert abs(e.p.x+113.5)<1e-6
            e.shift(south,-Z*(145-joint_z),25.2)
            assert e.p.y > -10.8
            e.line([-113.5,-10.8,joint_z]);e.arc(south,X,25.2)
            e.line([-77.5,-36,joint_z])
            assert f.edges[-1].Length>=9 and e.edges[-1].Length>=9
            lap(leg,in_id,f,e,-X,X,X)"""
replace(old,new)
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r5.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r5.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r6.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

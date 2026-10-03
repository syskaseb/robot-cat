"""Shared below-carrier rear bay: offset RL before turning; raise RR first.

R4 is rejected, not patched pointwise. Each entire factory/source pair now
stays in one low plane, has opposed Y lap ends, at least14mm straight grip
land each side, and no extra outside-body return. Keep the original100mm
factory assumption,8mm strip and10mm reserve. Only shared-fit result counts.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rear_source_pair_r4.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rear-source-pair-r4'","servo-fuse-rear-source-pair-r5'")
a=code.index("        if leg=='RL':");b=code.index('        a=f.p;b=e.p;',a)
code=code[:a]+'''        f=Route([right,cy,cz])
        if leg=='RL':
            f.shift(X,V(0,13,1.5),20);factory_y=48
        else:
            f.shift(X,Z*13,20);factory_y=-49
        f.arc(X,-Y,20);jx=f.p.x;jz=f.p.z
        assert side*(f.p.y-factory_y)>=14
        f.line([jx,factory_y,jz])
        e=Route([32,sy,129]);delta=Z*(jz-129)
        travel=2*25.2*math.sin(math.acos(1-delta.Length/(2*25.2)))
        assert jx-25.2-32>=travel
        e.line([jx-25.2-travel,sy,129]);e.shift(X,delta,25.2);e.arc(X,Y,25.2)
        ext_y=factory_y-side*8;assert side*(ext_y-e.p.y)>=14
        e.line([jx,ext_y,jz]);axis=Y;jy=(factory_y+ext_y)*.5
        factory_grip=list(f.p+Y*12);extension_grip=list(e.p-Y*12)
''' +code[b:]
code=code.replace("barestart+(Y if leg=='RL' else X)*dy,axis", 'barestart+X*dy,axis')
code=code.replace("    pin(parent);pin(src);", "    pin(parent);pin(src);pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r4/checks.json');")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

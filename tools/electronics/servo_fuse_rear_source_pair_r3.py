"""Complete rear corridors with minimum14mm straight insulation at each lap.

R2 stopped before exports: RL factory/extension straight grips could not
both fit between the bends. Lengthen the initial factory tangent within the
same100mm stock assumption and offset RL's source toward the unused south
space. RR first tangent moves its bend east. Not micro-shifting bare ends.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rear_source_pair_r2.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rear-source-pair-r2'","servo-fuse-rear-source-pair-r3'")
code=code.replace("tilt=-.075 if leg=='RL' else .2","tilt=-.2 if leg=='RL' else .2")
code=code.replace('f=Route([right,cy,cz]);f.arc(X,normal,20)',
                  "f=Route([right,cy,cz]);f.line([right+(26 if leg=='RL' else 10),cy,cz]);f.arc(X,normal,20)")
code=code.replace("factory_y=36 if leg=='RL' else -48","factory_y=33 if leg=='RL' else -47")
code=code.replace('delta=Z*(jz-129)','delta=Z*(jz-129)+(V(0,-8,0) if leg==\'RL\' else V(0,0,0))')
code=code.replace("    pin(src);", "    pin(parent);pin(src);")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""Clear purchased AUX/G_TAIL before descending factory output tails.

R6 descended inside purchased blocks. Retain the four MTA positions; first
travel west past the blocks, then lower both joint cages outside them.
Extensions descend at X25.5 before turning, not through AUX/G_TAIL.
All contacts, including other actual outputs, remain failures, not waived.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_output_returns_complete_r6.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r6_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace("servo-fuse-output-returns-complete-r6'", "servo-fuse-output-returns-complete-r7'")
code=code.replace("    native=ROOT/", "    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r6.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r6/checks.json')\n    native=ROOT/",1)
a=code.index('    for leg,ident,left,cy,cz,tx,target_y,factory_z,extension_z in [')
b=code.index('        lowy=target_y-4;lowz=extension_z-3.25',a)
code=code[:a]+'''    for leg,ident,left,cy,cz,drop,tx,target_y,factory_z,extension_z,clear_x in [
        ('RL','W045',16.5,72,130,16,-55,82,118,111.5,-4),
        ('RR','W053',28.5,-86,121.5,17,-47,-94,111,104.5,-3.5)]:
        side=1 if leg=='RL' else -1;Y=V(0,side,0)
        e=Route([25.5,side*49.5,113.5]);e.line([25.5,side*53.5,113.5])
        e.shift(Y,-Z*drop,25.2);e.arc(Y,-X,25.2)
        e.shift(-X,V(0,target_y-e.p.y,extension_z-e.p.z),25.2)
        straight=e.p.x-tx;assert straight>=4,dict(leg=leg,straight=straight)
        e.line([tx,target_y,extension_z])
        f=Route([left,cy,cz]);f.line([clear_x,cy,cz])
        f.shift(-X,V(0,target_y-cy,factory_z-cz),20)
        assert f.p.x>=tx;f.line([tx,target_y,factory_z])
        for r in (f,e):
            assert (r.edges[-1].tangentAt(r.edges[-1].LastParameter)+X).Length<1e-7
            assert abs(r.p.x-tx)<1e-7 and abs(r.p.y-target_y)<1e-7
        assert abs((f.p-e.p).Length-6.5)<1e-7
''' +code[b:]
exec(compile(code,str(Path(__file__).resolve()),'exec'))

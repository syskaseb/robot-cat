"""Coupled rear return INTO the clear gap before the twelve fuse holders.

R4 wrongly placed west-facing connector bodies IN the fuse rows. Keep the
same four main bodies and all accepted sources. Factory S-offsets end at
Y82/-91, not in the rows. The HELU west return offsets Y and Z together,
stays below AUX/ground and then enters each EAST face tangentially. RR drops
below the PWM-ground shelf. All remaining native casing contacts are OPEN.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_output_returns_complete_r4.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r4_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace("servo-fuse-output-returns-complete-r4'","servo-fuse-output-returns-complete-r5'")
code=code.replace('    native=ROOT/', "    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r4.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r4/checks.json')\n    p=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r5/checks.json';pin(p)\n    frstation=json.loads(p.read_text(encoding='utf-8'));assert frstation['native']['closed_STL'] and not frstation['hits']\n    native=ROOT/",1)
code=code.replace("servo-fuse-fr-return-guard-native-r3/Guard_WORLD.brep'", "servo-fuse-fr-output-station-native-r5/Guard_WORLD.brep'")
a=code.index('    for leg,ident,left,cy,cz,drop,tx,factory_z,extension_z in [')
b=code.index("        lowy=target_y-4;lowz=extension_z-3.25",a)
code=code[:a]+'''    for leg,ident,left,cy,cz,drop,tx,target_y,factory_z,extension_z in [
        ('RL','W045',16.5,72,130,8,-51,82,130,123.5),
        ('RR','W053',28.5,-86,121.5,14,-49,-91,121.5,115)]:
        side=1 if leg=='RL' else -1;Y=V(0,side,0)
        e=Route([25.5,side*49.5,113.5]);e.line([25.5,side*53.5,113.5])
        e.shift(Y,-Z*drop,25.2);e.arc(Y,-X,25.2)
        # One three-dimensional offset, not a diagonal through a body or
        # another impossible final tangent. Mouth stays on the east face.
        e.shift(-X,V(0,target_y-e.p.y,extension_z-e.p.z),25.2)
        straight=e.p.x-tx;assert straight>=4,dict(leg=leg,straight=straight)
        e.line([tx,target_y,extension_z])
        f=Route([left,cy,cz]);f.shift(-X,V(0,target_y-cy,factory_z-cz),20)
        assert f.p.x>=tx;f.line([tx,target_y,factory_z])
        for r in (f,e):
            assert (r.edges[-1].tangentAt(r.edges[-1].LastParameter)+X).Length<1e-7
            assert abs(r.p.x-tx)<1e-7 and abs(r.p.y-target_y)<1e-7
        assert abs((f.p-e.p).Length-6.5)<1e-7
''' +code[b:]
exec(compile(code,str(Path(__file__).resolve()),'exec'))

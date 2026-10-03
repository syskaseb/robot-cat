"""Use actual tessellated contact extents, not oversized curved-surface BBoxes.

R2's conservative contact box cut too much material and disconnected cover.
The saved failed geometry is retained. Exact BRep intersections verify the
resulting native slots; meshing only sizes tools with1mm nominal allowance.
"""
from pathlib import Path

parent=Path(__file__).with_name('servo_fuse_feed_reliefs_native_r2.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-feed-reliefs-native-r2','servo-fuse-feed-reliefs-native-r3')
old="                b=bounds(hit);zbottom=base.BoundBox.ZMin-1"
new="""                verts,_=hit.tessellate(.02)
                assert verts
                b=[min(getattr(v,k) for v in verts) for k in ('x','y','z')]+[max(getattr(v,k) for v in verts) for k in ('x','y','z')]
                zbottom=base.BoundBox.ZMin-1"""
assert code.count(old)==1;code=code.replace(old,new)
old="    pins = {}; result = []"
new="""    dependency=ROOT/'tools/electronics/servo_fuse_feed_reliefs_native_r2.py'
    pins = {dependency.relative_to(ROOT).as_posix():sha(dependency),
            'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r2/fault.json':sha(ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r2/fault.json')}; result = []"""
assert code.count(old)==1;code=code.replace(old,new)
exec(compile(code,str(Path(__file__).resolve()),'exec'))

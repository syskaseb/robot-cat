"""Replace the rejected FR high hairpin with one west-side source return.

Only W042 changes. Exact unchanged geometry and its failures are inherited
from output-wago-r3. The new factory half-turn/short lap fits the unchanged
100mm usable-lead assumption with the original10mm reserve. No selection.
"""
from pathlib import Path

parent = Path(__file__).with_name('servo_fuse_rolled_output_wago_r3.py')
wrapper = parent.read_text(encoding='utf-8')
tail = "exec(compile(code, str(Path(__file__).resolve()), 'exec'))"
assert wrapper.count(tail) == 1
exec(compile(wrapper.replace(tail, ''), str(parent), 'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-output-wago-r3'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r4'")
replace("prior_path=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-full-feeds-r1/checks.json'",
        "prior_path=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-output-wago-r3/checks.json'")
replace("source_ids=('W041','W042','W044','W052')",
        "source_ids=('W026','W037','W045','W053','W041','W044','W052')")
replace("old=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-full-feeds-r1'/(n+'_DESIGN.brep')",
        "old=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-output-wago-r3'/(n+'_DESIGN.brep')")
replace("if r['part'].startswith(source_ids) and not r['owner'].startswith(output_ids)",
        "if not r['part'].startswith('W042') and not r['owner'].startswith('W042')")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_output_wago_r2.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_output_wago_r2.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_output_wago_r3.py')")
old = """            f=Route([right,cy,cz]);f.arc(X,-Y,20);f.line([right+20,-41,cz])
            e=Route([-24,11,113.5]);e.line([-24,17,113.5]);e.shift(V(0,1,0),Z*12.5,25.2)
            e.arc(V(0,1,0),X,25.2)
            # One upper hairpin, not the rejected long R8 perimeter loop.
            e.arc(X,Z,25.2,math.pi)
            e.line([.7,e.p.y,e.p.z]);e.arc(-X,V(0,-1,0),25.2)
            e.shift(V(0,-1,0),-Z*50.4,30);assert e.p.y>=-33
            e.line([-24.5,-33,cz]);lap(leg,in_id,f,e,V(0,1,0),V(0,-1,0),V(0,1,0))"""
new = """            north=V(0,1,0);south=-north
            f=Route([right,cy,cz]);f.arc(X,north,20,math.pi)
            f.line([-56.4,-32,cz])
            e=Route([-24,11,113.5]);e.line([-24,17,113.5])
            e.shift(north,Z*23.5,25.2)
            e.arc(north,-X,25.2);e.line([e.p.x-25.2,e.p.y,e.p.z])
            e.arc(-X,south,25.2)
            assert abs(e.p.x+99.6)<1e-6
            e.shift(south,-Z*11,25.2)
            assert e.p.y>=-6.8
            e.line([-99.6,-6.8,cz]);e.arc(south,X,25.2)
            e.line([-64.4,-32,cz]);lap(leg,in_id,f,e,-X,X,X)"""
replace(old, new)
replace("start+X*dx,axis", "start+(V(0,1,0) if abs(axis.x)>.5 else X)*dx,axis")
exec(compile(code, str(Path(__file__).resolve()), 'exec'))

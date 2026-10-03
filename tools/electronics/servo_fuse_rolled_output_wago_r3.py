"""One coherent output correction: separate cages vertically, retain source failures.

The rear-left joint is inward of the bank wall and the factory bend is shorter.
Factory reserves and bend radii are not reduced to manufacture a pass. The
front-left route is retained; the other three WAGO housings are rolled90deg.
Vendor nominal envelope, cage datums and100mm factory lead are assumptions.
"""
from pathlib import Path

parent = Path(__file__).with_name('servo_fuse_rolled_output_wago_r2.py')
wrapper = parent.read_text(encoding='utf-8')
tail = "exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.count(tail) == 1
wrapper = wrapper.replace(tail, '')
exec(compile(wrapper, str(parent), 'exec'))

replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-output-wago-r2'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-output-wago-r3'")
replace("extra=22.5 if leg=='RL' else 0", "extra=19.5 if leg=='RL' else 0")
replace("end_y=dict(FL=105,FR=-111,RL=120,RR=-117)[leg]",
        "end_y=dict(FL=105,FR=-111,RL=106,RR=-117)[leg]")
replace("cage_delta=-6.5 if leg=='RL' else 6.5",
        "cage_delta=6.5 if leg=='FL' else 0\n        cage_z=cz if leg=='FL' else cz-6.5")
replace("e.line([mx,side*55.5,113.5])",
        "e.line([mx,side*(53.5 if leg=='RL' else 55.5),113.5])")
replace("e.shift(Y,V(target_x+cage_delta-mx,0,cz-113.5),radius)",
        "e.shift(Y,V(target_x+cage_delta-mx,0,cage_z-113.5),radius)")
replace("radius=31 if leg=='RL' else 25.2", "radius=25.2")
replace("end=V(target_x+cage_delta,end_y,cz)",
        "end=V(target_x+cage_delta,end_y,cage_z)")
replace("n=out_id+'_221412';changed[n]=Part.makeBox(13,18.3,8.15,V(lowx,lowy,cz-4))",
        """n=out_id+'_221412'
        if leg=='FL':
            lowz=cz-4; dims=[13,18.3,8.15]
        else:
            lowx=target_x-4; lowz=cage_z-3.25; dims=[8.15,18.3,13]
        changed[n]=Part.makeBox(*dims,V(lowx,lowy,lowz))""")
replace("ports_mm=[[target_x,end_y,cz],[target_x+cage_delta,end_y,cz]],",
        "ports_mm=[[target_x,end_y,cz],[target_x+cage_delta,end_y,cage_z]],")
replace("body_bounds_mm=[lowx,lowy,cz-4,lowx+13,lowy+18.3,cz+4.15],",
        "body_bounds_mm=[lowx,lowy,lowz,lowx+dims[0],lowy+dims[1],lowz+dims[2]],")
replace("cage_strip_mm=11,dimensions_mm=[13,18.3,8.15],",
        "cage_strip_mm=11,dimensions_mm=dims,rolled_cages=leg!='FL',")
replace("hits=[dict(r,inherited=True) for r in prior['hits'] if r['part'].startswith(source_ids)]",
        """# A source/output pair is affected by changed output geometry. Do not
    # inherit it and then count it again in the changed-pair loop.
    output_ids=('W026','W037','W045','W053')
    hits=[dict(r,inherited=True) for r in prior['hits']
          if r['part'].startswith(source_ids) and not r['owner'].startswith(output_ids)]""")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_full_feeds_r1.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_full_feeds_r1.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_output_wago_r2.py')")
exec(compile(code, str(Path(__file__).resolve()), 'exec'))

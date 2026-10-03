"""Correct four parallel output approaches with commercial221412 cages.

R1 inline output laps were wrong: both insulation ends approached in the
same direction. Use separate bare, UNTINNED cages on one connector face.
Source geometry/failures are inherited by exact file hashes, not reaudited.
This does not accept the rejected cradle or the three source extensions.
"""
from pathlib import Path
import json
parent=Path(__file__).with_name('servo_fuse_rolled_full_feeds_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-rolled-full-feeds-r1','servo-fuse-rolled-output-wago-r2')


def replace(old,new):
    global code
    assert code.count(old)==1,old[:80]
    code=code.replace(old,new)


replace("    changed={};paths={};rows=[];joints=[];intended=set();factory_failures=[]", """    prior_path=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-full-feeds-r1/checks.json';pin(prior_path);pin(ROOT/'tools/electronics/servo_fuse_rolled_full_feeds_r1.py')
    prior=json.loads(prior_path.read_text(encoding='utf-8'))
    assert not prior['errors'] and not prior['factory_failures']
    source_ids=('W041','W042','W044','W052')
    changed={};paths={};rows=[];joints=[];intended=set();factory_failures=[]""")
replace("        target_x=left-extra-20", "        target_x=left-extra-20\n        cage_delta=-6.5 if leg=='RL' else 6.5")
replace("        radius=30 if leg=='RL' else 25.2", "        radius=31 if leg=='RL' else 25.2")
replace("        e.shift(Y,V(target_x-mx,0,cz-113.5),radius)", "        e.shift(Y,V(target_x+cage_delta-mx,0,cz-113.5),radius)")
replace("        end=V(target_x,end_y+side*8,cz)", "        end=V(target_x+cage_delta,end_y,cz)")
replace("        e.line(end);lap(leg,out_id,f,e,Y,-Y,Y)", """        e.line(end)
        assert (f.edges[-1].tangentAt(f.edges[-1].LastParameter)-Y).Length<1e-6
        assert (e.edges[-1].tangentAt(e.edges[-1].LastParameter)-Y).Length<1e-6
        lowx=min(target_x,target_x+cage_delta)-3.25
        lowy=min(end_y,end_y+side*18.3)
        n=out_id+'_221412';changed[n]=Part.makeBox(13,18.3,8.15,V(lowx,lowy,cz-4))
        wire(out_id+'_factory',f,5,f.edges[0].tangentAt(f.edges[0].FirstParameter),'MTA_factory',11,leg)
        wire(out_id+'_extension',e,4.2,Y,'HELU23802',14+11,leg)
        # Both ends have distinct nominal cage centres, same housing face.
        joints.append(dict(id=out_id,leg=leg,kind='WAGO221-412',manufacturer_part='221-412',
            ports_mm=[[target_x,end_y,cz],[target_x+cage_delta,end_y,cz]],
            body_bounds_mm=[lowx,lowy,cz-4,lowx+13,lowy+18.3,cz+4.15],
            cage_strip_mm=11,dimensions_mm=[13,18.3,8.15],supplier_facts='parent-fuse-extensions-2026-10-03/facts.json',
            recipe='Bench prewire removed unpowered Deck, separate UNTINNED bare4mm2 Cu ends in two cages on SAME face. Close levers before mounting. Native cradle and insulation grips/lever handling/removal still OPEN.',
            selected=False,physical_pass=False))""")
replace("        assert abs(ftangent.dot(etangent)+1)<1e-7", """        assert abs(ftangent.dot(etangent)+1)<1e-7
        assert (factory.edges[-1].tangentAt(factory.edges[-1].LastParameter)-ftangent).Length<1e-6
        assert (ext.edges[-1].tangentAt(ext.edges[-1].LastParameter)-etangent).Length<1e-6""")
replace("solder_joints=len(joints),TE3_8_installed_blank_mm=26*len(joints),additional_WAGO221412=0", "solder_joints=3,TE3_8_installed_blank_mm=78,additional_WAGO221412=4")
replace("    hits=[];errors=[];pairs=0", """    # Preserve exact source geometry and its known failures. No green flag
    # from rerouting outputs; complete module remains OPEN.
    for n in changed:
        if n.startswith(source_ids):
            q=OUT/(n+'_DESIGN.brep');changed[n].exportBrep(str(q))
            old=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-full-feeds-r1'/(n+'_DESIGN.brep')
            pin(old);assert sha(q)==sha(old),'Unchanged source geometry changed: '+n
    hits=[dict(r,inherited=True) for r in prior['hits'] if r['part'].startswith(source_ids)]
    errors=[];pairs=0""")
replace("        for m,t in owners.items():check(n,s,m,t)", "        if not n.startswith(source_ids):\n            for m,t in owners.items():check(n,s,m,t)")
replace("            if frozenset((n,m)) not in intended:check(n,s,m,t)", "            if n.startswith(source_ids) and m.startswith(source_ids):continue\n            if frozenset((n,m)) not in intended:check(n,s,m,t)")
replace("        selected=False,physical_pass=False,W5_complete=False,routes=rows,joints=joints,factory_failures=factory_failures,", "        selected=False,physical_pass=False,W5_complete=False,routes=rows,joints=joints,factory_failures=factory_failures,\n        inherited_source_failures=True,output_parallel_laps_replaced_by_distinct_WAGO_cages=True,")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""Resolve the forced front-feed crossing by swapping two same-net cages.

Both W041/W042 terminate at the SAME selected P_FRONT221-615 bus, one
conductor per cage. Interchange project labels2/3 without moving the block,
MTA bodies, factory/lap or any unrelated wire. R11's source dx solver proved
the old crossed assignment has no clear offset. This changes both affected
routes and retests them against all actual owners, not just the last hit.
The W041/head contacts and exterior protection remain explicitly open.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_source_loop_r11.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r11'",
        "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r1'")
replace("source_ids=('W026','W037','W045','W053','W041','W044','W052')",
        "source_ids=('W026','W037','W045','W053','W044','W052')")
replace("if not r['part'].startswith('W042') and not r['owner'].startswith('W042')",
        "if not r['part'].startswith(('W041','W042')) and not r['owner'].startswith(('W041','W042'))")
replace("f.shift(-Y,V(-7,0,-12.5),20);assert f.p.y>=11",
        "f.shift(-Y,V(.5,0,-12.5),20);assert f.p.y>=11")
replace("f.line([-31.5,11,113.5]);wire(in_id+'_factory_direct'",
        "f.line([-24,11,113.5]);wire(in_id+'_factory_direct'")
replace("e=Route([-24,11,113.5]);e.shift(north,V(6,0,24),25.2)",
        "e=Route([-31.5,11,113.5]);e.shift(north,Z*24,25.2)")
replace("    save(OUT/'intent.json',", """    # These labels are project cage positions, not manufacturer numbers.
    h=json.loads(ledger.read_text(encoding='utf-8'))
    records=h['conductors']
    front={r['id']:r for r in records if r['id'] in ('W041','W042')}
    assert set(front)=={'W041','W042'}
    assert all(r['net']=='P_FRONT' and any(e.get('sku')=='221-615' for e in r['ends']) for r in front.values())
    save(OUT/'port-permutation.json',dict(selected=False,physical_pass=False,
        connector='P_FRONT',SKU='221-615',same_net='P_FRONT',topology_changed=False,
        one_conductor_per_cage=True,manufacturer_cage_numbers=False,
        changes=[dict(wire='W041',prior_label=front['W041']['b'],candidate_label='P_FRONT.3',entry_mm=[-24,11,113.5]),
                 dict(wire='W042',prior_label=front['W042']['b'],candidate_label='P_FRONT.2',entry_mm=[-31.5,11,113.5])],
        selection_rule='Relabel both endpoints/assembly ledger together ONLY when the entire bank candidate is selected. R51 and its original ledger remain unchanged now.'))
    save(OUT/'intent.json',""")
replace("pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r10.py')",
        "pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r10.py');pin(ROOT/'tools/electronics/servo_fuse_rolled_source_loop_r11.py');pin(ROOT/'hardware/electronics/full-cat/servo-fuse-fr-source-corridor-solver-r1/checks.json')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

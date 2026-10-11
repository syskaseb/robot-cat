"""Read-only common source-bay material map before designing local protection.

S0 family cylinder and terminal datums remain provisional, not real SKU metal.
No new protection geometry, native mutation, clearance waiver or M4 credit.
"""
import json,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA

def run():
    tick=time.monotonic()
    from current_complete_harness_context import context,W
    reader,pins,targets,wires=context();pins.add(Path(__file__))
    zone=[-125,-35,45,-20,65,115]
    def bounds(shape):
        b=shape.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    def inside(b):return all(b[j]<=zone[j+3] and b[j+3]>=zone[j] for j in range(3))
    source={n:bounds(s) for n,s in targets.items() if n.startswith('S0_')}
    neighbors={n:bounds(s) for n,s in targets.items() if not n.startswith('S0_') and s.Solids and inside(bounds(s))}
    routes={n:dict(bounds_mm=bounds(c),project_insulation_radius_mm=r) for n,(c,r) in wires.items() if inside(bounds(c))}
    manifest=dict(status='SOURCE_PROTECTION_SPACE_ONLY_NOT_GUARD_FIT',
        zone_mm=zone,S0_family_envelope_and_provisional_terminal_bounds_mm=source,
        actual_retained_neighbors_mm=neighbors,retained_wire_bounds_for_pair_selection_only=routes,
        mounting_pattern=dict(centre_mm=[-77,16,105],central_hole_mm=24,mount_holes_mm=6.5,
            mount_centres_relative_mm=[[-19,0],[19,0]],manufacturer_pattern_known=True,
            exact_SKU_terminal_case_stud_pitch_stack_unknown=True),
        delivery_gates=['Exact6EK002843-002 casing/terminal bay/stud pitch and seating',
            'Actual lug metal and insulation/tool approach','Physical source isolation; no power in this work'],
        rejected_approaches=['Tight boot cut around the opaque family cylinder',
            'Treat family-envelope overlap as a real short or invent a manufacturer terminal pocket'],
        selected=False,M4_complete=False,W5_complete=False,native_changed=False,physical_pass=False,
        worker_seconds=time.monotonic()-tick,
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}})
    (OUT/'source-protection-space.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=manifest['status'],source=source,neighbors=neighbors,
        worker_seconds=manifest['worker_seconds'])),flush=True)
    return manifest

if __name__=='__main__':run()

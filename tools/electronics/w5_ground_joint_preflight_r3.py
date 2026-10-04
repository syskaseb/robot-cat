"""Preflight the coupled ground side exits against unchanged DATA/source."""
from pathlib import Path
import json
import w5_ground_joint_preflight_r1 as checker
import w5_ground_joint_layout_r3 as layout
from servo_fuse_inputs_r1 import save, sha
OUT = layout.ROOT / 'hardware/electronics/full-cat/w5-ground-joint-preflight-r3'


def main():
    checker.OUT, checker.BLOCKS = OUT, layout.BLOCKS
    checker.ports, checker.attached_ends, checker.placement = layout.ports, layout.attached_ends, layout.placement
    checker.main()
    p = OUT / 'checks.json'
    receipt = json.loads(p.read_text(encoding='utf-8'))
    receipt.update(raised_layout_r1_rejected=True, unshifted_r2_DATA_contacts_rejected=True,
                   retained_body_underside_mm=109, central_translation_mm=[0, 8, 0],
                   central_exit_axis=[1, 0, 0], leg_exit_rule='outward along +/-Y')
    # Explicit owner dependencies, not a substring-based contact waiver.
    dependent = {'R53BUS/G2shared/' + s: ['W003', 'W061'] for s in ('left', 'right', 'top', 'bottom')}
    receipt['owner_dependencies'] = dependent
    receipt['contacts_requiring_ground_interface_rebuild'] = [h for h in receipt['hits']
        if h['category'] == 'affected_wire_or_restraint_requires_rebuild' or h['owner'] in dependent]
    receipt['other_contacts_still_open'] = [h for h in receipt['hits']
        if h not in receipt['contacts_requiring_ground_interface_rebuild']]
    receipt['fixed_wire_or_bought_body_contacts'] = [h for h in receipt['other_contacts_still_open']
        if h['category'] in ('fixed_obstacle', 'purchased_body')]
    receipt['native_and_attached_wire_rebuild_required'] = True
    for src in (Path(__file__), Path(layout.__file__), layout.ROOT / 'tools/electronics/w5_ground_joint_layout_r2.py'):
        receipt['source_sha256'][src.relative_to(layout.ROOT).as_posix()] = sha(src)
    save(p, receipt)


if __name__ == '__main__': main()

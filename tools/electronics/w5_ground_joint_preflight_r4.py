"""Receive the balanced ground rail, without waiving any old-end contact."""
from pathlib import Path
import json
import w5_ground_joint_preflight_r3 as wrapper
import w5_ground_joint_layout_r4 as layout
from servo_fuse_inputs_r1 import save, sha
OUT = layout.ROOT / 'hardware/electronics/full-cat/w5-ground-joint-preflight-r4'


def main():
    wrapper.OUT, wrapper.layout = OUT, layout
    wrapper.main()
    p = OUT / 'checks.json'
    receipt = json.loads(p.read_text(encoding='utf-8'))
    receipt['central_translation_mm'] = [0, layout.CENTRAL_Y, 0]
    receipt['datum_derivation'] = dict(received_W011_upper_Y_mm=-11.4,
        received_W012_lower_Y_mm=22.4, rotated_G2_half_depth_mm=15,
        feasible_centre_Y_interval_mm=[3.6, 7.4], selected_midpoint_mm=5.5,
        nominal_strap_clearance_each_mm=1.9)
    receipt['previous_r3_DATA_tie_contact_not_waived'] = True
    receipt['source_sha256'][Path(wrapper.__file__).relative_to(layout.ROOT).as_posix()] = sha(Path(wrapper.__file__))
    save(p, receipt)


if __name__ == '__main__': main()

"""Receive the complete unraised/side-exit ground-body layout preflight."""
from pathlib import Path
import json
import w5_ground_joint_preflight_r1 as checker
import w5_ground_joint_layout_r2 as layout
from servo_fuse_inputs_r1 import save, sha

OUT = layout.ROOT / 'hardware/electronics/full-cat/w5-ground-joint-preflight-r2'


def main():
    checker.OUT = OUT
    checker.BLOCKS = layout.BLOCKS
    checker.ports = layout.ports
    checker.attached_ends = layout.attached_ends
    checker.placement = layout.placement
    checker.main()
    receipt = json.loads((OUT / 'checks.json').read_text(encoding='utf-8'))
    receipt.update(raised_layout_r1_rejected=True, retained_body_underside_mm=109,
                   central_exit_axis=[1, 0, 0], leg_exit_rule='outward along +/-Y')
    for p in (Path(__file__), Path(layout.__file__)):
        receipt['source_sha256'][p.relative_to(layout.ROOT).as_posix()] = sha(p)
    save(OUT / 'checks.json', receipt)


if __name__ == '__main__': main()

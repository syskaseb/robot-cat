"""Full retained BRep scene for below-body wiring, without changing old gates.

The body-fanout planning cache deliberately clips objects wholly belowZ-30.
Do not use that bounded loader unchanged for low flexes or ground clearance.
Only its temporary instance-inclusion bounds are disabled; all saved geometry,
placements, stages and sampled motion remain the identical existing loader.
Historical source files and the1539-instance body proof remain untouched.
"""
from pathlib import Path
import numpy as np
import current_body_fanout_material as M


def load():
    previous=(M.S.LOW,M.S.HIGH)
    try:
        M.S.LOW=np.full(3,-np.inf);M.S.HIGH=np.full(3,np.inf)
        targets,wires,pins=M.load()
    finally:M.S.LOW,M.S.HIGH=previous
    pins[Path(__file__).relative_to(M.P.ROOT).as_posix()]=M.P.SHA(Path(__file__))
    return targets,wires,pins

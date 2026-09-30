"""Single corrected fixed yaw seat: clear JR end and real insulation slots."""
import json
from pathlib import Path
import head_fixed_yaw_feed_r2 as W
F=W.F
F.OUT=F.ROOT/'hardware/cad/studies/head-fixed-yaw-feed-r3'
# Splice seat begins at the actual reserved connector end, not2mm inside it.
# Widen only the factory-insulation floor so both tie holes pierce material.
F.EXTRA_ADDS=[[-105,-66,52.2,-65,-47.6,56.2],[-75,-61,56.2,-65,-52.6,57.2],[-149,-68,52.2,-139,-45.6,55.2]]
def main():
    W.main()
    checks=json.loads((F.OUT/'checks.json').read_text());plan=json.loads((F.OUT/'plan.json').read_text())
    s=F.B.load(F.OUT/'YawCarrierJRSeat.brep');slot_checks=[]
    # Every designated pair must pierce a real floor, not empty air outside it.
    solid_floor=F.R.box([-149,-68,52.2,-97,-45.6,55.2]).fuse(F.R.box([-105,-66,52.2,-65,-47.6,55.2]))
    for b in plan['cuts_mm']:
        p=F.R.box([b[0]+.1,b[1]+.1,51.5,b[3]-.1,b[4]-.1,58])
        removed=F.R.volume(p.common(solid_floor));hit=F.R.volume(p.common(s))
        assert removed>1e-4 and hit<1e-6,(b,removed,hit)
        slot_checks.append(dict(slot_bbox_mm=b,reference_floor_mm3=removed,new_carrier_hit_mm3=hit,through_floor=True))
    checks.update(slot_checks=slot_checks,script_sha256=F.R.sha(Path(__file__)))
    F.dump('checks.json',checks)
    print(json.dumps(dict(status=checks['status'],pairs=len(checks['rows']),hits=checks['hits'],real_tie_slots=len(slot_checks))),flush=True)
if __name__=='__main__':main()

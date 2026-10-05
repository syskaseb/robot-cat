"""BUS bypass from measured obstacle envelopes, keeping the facing pair.

Move the source ascent inward from FL_G Y30.5 edge, then pass above F_AUX
Z142 and XS23 Z139.762. W001/W061 are unchanged, not a new ground layout.
"""
from pathlib import Path
import json
import w5_central_ground_routes as base
from servo_fuse_inputs_r1 import save,sha

original=base.recipes
def recipes():
    rows=original()
    row=next(r for r in rows if r['wire']=='W003')
    src=row['middle'][0];tip=row['middle'][-1]
    row['middle']=[src,[src[0],17,src[2]],[src[0],17,144],[tip[0],tip[1],144],tip]
    return rows

def main():
    base.OUT=base.ROOT/'hardware/electronics/full-cat/w5-central-ground-routes-r2'
    base.recipes=recipes
    base.main()
    path=base.OUT/'checks.json';proof=json.loads(path.read_text(encoding='utf-8'))
    proof['source_sha256'][Path(__file__).relative_to(base.ROOT).as_posix()]=sha(Path(__file__))
    proof['BUS_corridor_basis']=dict(FL_G_inner_edge_Y=30.5,ascent_Y=17,
        F_AUX_top_Z=142,head_feed_top_Z=139.76243556529823,horizontal_level_Z=144,
        cable_radius_mm=1,nominal_top_clearance_mm=1)
    save(path,proof)

if __name__=='__main__':main()

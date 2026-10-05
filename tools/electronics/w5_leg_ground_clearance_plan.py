"""Use the spare FL cage and clearance-derived RR stand-off.

Inward FL/RR exits failed on fixed source/data components. Preserve outward
orientation; change FL logical .4 to the previously NC fifth physical cage.
RR rises4.5mm: 115.153 input-wire top +2.1 cable radius +0.5 clearance
requires portZ>=117.753; select118.0. All four RR ends rise together.
"""
import json
from pathlib import Path
import w5_egress_space as survey
from servo_fuse_inputs_r1 import save,sha

received=survey.attached_ends
def ends(graph):
    rows=[]
    for row in received(graph):
        block=row['end'].split('.')[0]
        if row['end']=='FL_G.4':
            row['point_mm'][0]=-45;row['physical_cage_before_rotation']=5;rows.append(row)
        elif block=='RR_G':
            row['point_mm'][2]+=4.5;rows.append(row)
    assert len(rows)==5
    return rows

def main():
    survey.OUT=survey.ROOT/'hardware/electronics/full-cat/w5-leg-ground-clearance-plan-r1'
    survey.OUT.mkdir(parents=True,exist_ok=True)
    survey.attached_ends=ends
    survey.main()
    p=survey.OUT/'egress.json';r=json.loads(p.read_text(encoding='utf-8'))
    r['source_sha256'][Path(__file__).relative_to(survey.ROOT).as_posix()]=sha(Path(__file__))
    r['mapping_changes']={'FL_G.4':'previously NC physical cage5','FL_G.5':'NC physical cage4'}
    r['RR_standoff_mm']=4.5
    r['RR_body_and_native_check_pending']=True
    r['clearance_basis']={'input_top_Z':115.1528313460505,'max_ground_radius_mm':2.1,
        'minimum_planned_clearance_mm':0.5,'new_centre_Z':118.0}
    save(p,r)

if __name__=='__main__':main()

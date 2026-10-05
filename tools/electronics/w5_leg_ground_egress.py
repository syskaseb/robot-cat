"""Resolve the FL/RR exits blocked by their fixed outer feeds.

Rotate only these two ground connectors within their existing rectangular
reservations. All four attached ends move together; native retention open.
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
        if block not in ('FL_G','RR_G'):continue
        cx,cy=(-33,40) if block=='FL_G' else (75,-40)
        x,y,z=row['point_mm'];row['point_mm']=[2*cx-x,2*cy-y,z]
        row['outward_axis']=[-v for v in row['outward_axis']]
        rows.append(row)
    assert len(rows)==8
    return rows

def main():
    survey.OUT=survey.ROOT/'hardware/electronics/full-cat/w5-leg-ground-inward-plan-r1'
    survey.OUT.mkdir(parents=True,exist_ok=True)
    survey.attached_ends=ends
    survey.main()
    p=survey.OUT/'egress.json';r=json.loads(p.read_text(encoding='utf-8'))
    r['source_sha256'][Path(__file__).relative_to(survey.ROOT).as_posix()]=sha(Path(__file__))
    r['changed_blocks']=['FL_G','RR_G']
    r['why']='Outer exits blocked by retained W041/W029 and XB13/W058; inward exits preserve block footprint and nets.'
    r['native_retention_pending']=True
    save(p,r)

if __name__=='__main__':main()

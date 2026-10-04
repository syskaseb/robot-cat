"""Separate the two source inlets using the received W066 crossing witness.

Keep both terminal mouths, the factory wire, and W066 unchanged. Start the
F_PI upward bend closer to its end face, leaving the riser east of W066.
The fuse casing remains in the actual collision census; no waived owner.
"""
from pathlib import Path
import json,math
import w5_source_inlet_joint_r1 as received
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul,X,Y,Z
from servo_fuse_inputs_r1 import save,sha

ROOT=received.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-source-inlet-joint-r2'

def factory_path():
    c=CentreLine([-73,-21,115],mul(X,-1))
    c.line([-73.5,-21,115]);c.arc(Z,radius=6)
    c.line([-79.5,-21,129.5]);c.arc(Y,radius=6)
    angle=math.acos(1-3/12);c.arc(X,angle,radius=6)
    c.arc(add(mul(Y,math.sin(angle)),mul(X,-math.cos(angle))),angle,radius=6)
    c.line([-76.5,7,135.5])
    row=received.factory_path()
    row.update(edges=c.edges,exposed_path_mm=sum(e['length_mm'] for e in c.edges))
    assert row['exposed_path_mm']+24<=80<=84.5
    return row

def main():
    parent=received.OUT/'checks.json'
    old=json.loads(parent.read_text(encoding='utf-8'))
    assert len(old['hits'])==2 and not old['errors']
    assert all(h['owner']=='jointSource/W066' for h in old['hits'])
    row=factory_path()
    received.factory_path=lambda:row
    received.OUT=OUT
    received.main()
    path=OUT/'checks.json';result=json.loads(path.read_text(encoding='utf-8'))
    result['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),parent]})
    result['changed_interface']='W043 riser/upper bend east of the received W066 crossing; no terminal relocation or extension.'
    save(path,result)

if __name__=='__main__':main()

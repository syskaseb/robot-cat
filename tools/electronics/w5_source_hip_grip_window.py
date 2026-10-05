"""Finish allocated hip root with an integral passage for its own top strap.

R2 has no P0 collisions; four identical contacts occur at the bridge riser.
Widen that riser to preserve1.25mm side webs around a2.9x1.4mm tie channel.
No strap station, cable route or P0 body is moved.
"""
from pathlib import Path
import json
import w5_source_hip_grips_allocated as R2
from servo_fuse_inputs_r1 import save,sha
ROOT=R2.ROOT;BASE=R2.BASE;OUT=BASE/'w5-source-hip-grips-r3'


def proposed(A,Part):
    parts,s=R2.proposed(A,Part);axis=s['common_allocated_band_axis_x_PCB_mm']
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    riser=[axis-2.7,-26.8,15.05,axis+2.7,-25,22.5]
    slot=[axis-1.45,-26.9,16.45,axis+1.45,-24.9,17.85]
    parts['Clip']=parts['Clip'].fuse(box(riser)).cut(box(slot))
    assert parts['Clip'].isValid() and len(parts['Clip'].Solids)==1
    assert not (parts['Clip'].check(True) or [])
    s['root_boxes_mm']['BridgeRiser']=riser
    s.update(top_body_tie_window_mm=slot,minimum_bridge_side_web_mm=1.25,
        strap_passage_repair='R2 four contacts only with own top strap at BridgeRiser. Add a dimensioned channel and wider side webs; keep all wire paths and strap positions.')
    return parts,s


def main():
    prior=json.loads((R2.OUT/'checks.json').read_text(encoding='utf-8'))
    assert len(prior['hits'])==4 and not prior['errors']
    assert all(h['part'].endswith('BodyBand') and h['owner'].endswith('Clip') for h in prior['hits'])
    R2.H.OUT=OUT;R2.H.proposed=proposed;R2.H.main()
    p=OUT/'checks.json';proof=json.loads(p.read_text(encoding='utf-8'))
    for q in (Path(__file__),Path(R2.__file__),R2.LANE,R2.SECTION,R2.OUT/'checks.json'):
        proof['source_sha256'][q.relative_to(ROOT).as_posix()]=sha(q)
    save(p,proof)


if __name__=='__main__':main()

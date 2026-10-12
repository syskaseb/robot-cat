"""Actual rejected Knee loop witnesses, without allocating any new support."""
import json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import check_low_hip_loom_layout as P


def run():
    tick=time.monotonic();gf=P.OUT/'low-hip-shared-layout.json';gate=json.loads(gf.read_text())
    family=json.loads((P.OUT/'low-joint-family-plan.json').read_text())
    axes=json.loads((P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    archive=P.OUT.parent/'current-view-60-20261012.zip';result=[]
    with zipfile.ZipFile(archive) as z:
        entries={q['label']:q for q in json.loads(z.read('index.json'))['entries']}
        for c in gate['contacts']:
            if not c['a'].endswith('/Knee'):continue
            r=next(r for r in family['knees'] if r['section']==c['a']);pose=c['pose']
            parts=P.scene_parts(r,pose['Hip'],pose['Knee'],axes);curve=P.wire(parts)
            e=entries[c['b']];s=Part.Shape();s.importBrepFromString(z.read(e['file']).decode())
            gap,pairs,info=curve.distToShape(s)
            row=dict(contact=c,parts=parts,gap_mm=gap,target_radius_mm=e.get('radius_mm',0),
                witnesses=[dict(cable_mm=list(a),target_mm=list(b)) for a,b in pairs],
                per_edge_gaps_mm=[ed.distToShape(s)[0] for ed in curve.Edges])
            result.append(row)
    report=dict(status='REJECTED_KNEE_FULL_ROUTE_WITNESSES_ONLY',witnesses=result,selected=False,physical_pass=False,
        source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (gf,archive,Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'joint-loop-contact-witness.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':run()

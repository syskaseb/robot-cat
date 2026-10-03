"""Qualify only five affected RR retained wires and their saved intersections."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-witness-sources-r1'


def main():
    import FreeCAD
    import Part
    started=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r1'
    p=folder/'checks.json';report=json.loads(p.read_text(encoding='utf-8'));pins={p.relative_to(ROOT).as_posix():sha(p)}
    sanity=ROOT/'hardware/electronics/full-cat/servo-fuse-contact-witness-sanity-r1/checks.json'
    pins[sanity.relative_to(ROOT).as_posix()]=sha(sanity)
    invalid=json.loads(sanity.read_text(encoding='utf-8'))['invalid']
    uncertain={r['index'] for r in invalid if r['report']==folder.name}
    def qualify(path,role):
        pins[path.relative_to(ROOT).as_posix()]=sha(path);s=Part.read(str(path))
        try:strict=s.check(True)
        except ValueError as exc:strict=[str(exc)]
        return dict(role=role,path=path.relative_to(ROOT).as_posix(),valid=s.isValid(),
            solids=len(s.Solids),volume_mm3=s.Volume,strict_BOP=strict,
            bounds_mm=[getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')])
    body=qualify(folder/'RR_MTA_BODY.brep','changed_RR_body');rows=[]
    save(OUT/'progress.json',dict(body=body,rows=rows,selected=False))
    for i,hit in enumerate(report['hits'],1):
        assert hit['part']=='RR'
        source=qualify(ROOT/hit['owner'],'retained_wire')
        witness=qualify(folder/f'HIT_{i}.brep','saved_Boolean_intersection')
        rows.append(dict(index=i,owner=hit['owner'],impossible_bbox_witness=i in uncertain,
            source=source,witness=witness))
        save(OUT/'progress.json',dict(body=body,rows=rows,selected=False,physical_pass=False))
        print('RR_SOURCE_WITNESS_QUALIFIED',i,flush=True)
    ended=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='LOCAL_BOOLEAN_QUALIFICATION_ONLY',body=body,rows=rows,
        selected=False,physical_pass=False,W5_complete=False,
        remaining='Do not treat impossible intersections as real contacts or clearance; correct affected collision method/representation only. Other unchanged interfaces not reaudited.',
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=started.isoformat(),
        finished_utc=ended.isoformat(),worker_wall_seconds=(ended-started).total_seconds()))


if __name__=='__main__':main()

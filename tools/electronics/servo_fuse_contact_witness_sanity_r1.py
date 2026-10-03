"""Reject impossible BOP contact witnesses, without rerunning collision pairs.

An intersection must be contained in BOTH operand bounding boxes. Failure is
an uncertain/invalid Boolean witness, NOT evidence that the parts are clear.
Native Deck topology qualification remains separate from retained wire BOP.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-contact-witness-sanity-r1'


def main():
    import FreeCAD
    import Part
    started=datetime.now(timezone.utc);pins={}
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    def read(p):
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
        return json.loads(p.read_text(encoding='utf-8'))
    def bounds(p):
        pins[p.relative_to(ROOT).as_posix()]=sha(p);s=Part.read(str(p))
        return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    cache=read(ROOT/'hardware/electronics/full-cat/servo-fuse-main-space-plan-r1/owners.json')
    owners={row['id']:row['bounds_mm'] for row in cache['owners']}
    owners['RetainedCoverR4']=cache['cover_bounds_mm'];owners['ModifiableCoverR4']=cache['cover_bounds_mm']
    owners['CandidateDeck']=bounds(ROOT/'hardware/cad/studies/servo-fuse-parent-complete-layout-r8/Deck_WORLD.brep')
    rows=[];unknown=[];invalid=[];margin=.001
    for folder,kind in [('servo-fuse-parent-complete-layout-r8','r8'),('servo-fuse-main-joint-layout-r1','joint')]:
        path=ROOT/'hardware/electronics/full-cat'/folder;r=read(path/'checks.json');parts={}
        for p in path.glob('*_DESIGN.brep'):parts[p.stem.removesuffix('_DESIGN')]=bounds(p)
        for p in path.glob('*_MTA_BODY.brep'):parts[p.stem.removesuffix('_MTA_BODY')]=bounds(p)
        for i,hit in enumerate(r['hits'],1):
            a=parts.get(hit['part']);b=owners.get(hit['owner'],parts.get(hit['owner']))
            if a is None or b is None:
                unknown.append(dict(report=folder,index=i,part=hit['part'],owner=hit['owner']));continue
            h=hit.get('bounds_mm');violations=[]
            for operand,name in [(a,'part'),(b,'owner')]:
                for axis in range(3):
                    if h[axis]<operand[axis]-margin:violations.append(dict(operand=name,axis=axis,side='min',outside_mm=operand[axis]-h[axis]))
                    if h[axis+3]>operand[axis+3]+margin:violations.append(dict(operand=name,axis=axis,side='max',outside_mm=h[axis+3]-operand[axis+3]))
            row=dict(report=folder,index=i,part=hit['part'],owner=hit['owner'],
                part_bounds_mm=a,owner_bounds_mm=b,witness_bounds_mm=h,
                impossible_intersection=bool(violations),violations=violations,
                meaning='INVALID/UNCERTAIN Boolean witness, do not infer clearance' if violations else 'Necessary bounding containment holds; not independent BOP validation')
            rows.append(row)
            if violations:invalid.append(row)
    ended=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='INVALID_CONTACT_WITNESSES' if invalid else 'NECESSARY_CONTAINMENT_HOLDS',
        selected=False,physical_pass=False,checked=len(rows),unknown=unknown,invalid=invalid,
        remaining='Resolve affected retained wire/Boolean representation before changing parts based on these contacts. Do not rerun all closed interfaces.',
        started_utc=started.isoformat(),finished_utc=ended.isoformat(),worker_wall_seconds=(ended-started).total_seconds(),
        source_sha256=pins,script_sha256=sha(Path(__file__))))
    print(json.dumps(dict(checked=len(rows),invalid=len(invalid),unknown=len(unknown))))


if __name__=='__main__':main()

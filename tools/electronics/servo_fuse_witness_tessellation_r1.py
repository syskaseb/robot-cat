"""Resolve conservative BREP bounds using actual witness surface sampling.

R1 bbox-containment inference is NOT a proof: OCCT boxes of trimmed curved
surfaces may include geometry beyond the trim. Do not discard contacts on it.
Tessellated bounds here are diagnostic, with explicit deflection allowance.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-witness-tessellation-r1'


def main():
    import FreeCAD
    import Part,MeshPart
    started=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    src=ROOT/'hardware/electronics/full-cat/servo-fuse-contact-witness-sanity-r1/checks.json'
    data=json.loads(src.read_text(encoding='utf-8'));pins={src.relative_to(ROOT).as_posix():sha(src)};rows=[]
    for row in data['invalid']:
        p=ROOT/'hardware/electronics/full-cat'/row['report']/f"HIT_{row['index']}.brep"
        pins[p.relative_to(ROOT).as_posix()]=sha(p);s=Part.read(str(p))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
        bb=mesh.BoundBox;mb=[getattr(bb,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
        violations=[]
        for op in ('part','owner'):
            b=row[op+'_bounds_mm']
            for i in range(3):
                if mb[i]<b[i]-.05 or mb[i+3]>b[i+3]+.05:violations.append(op+':'+str(i))
        vertices=[v.Point for v in s.Vertexes]
        rows.append(dict(report=row['report'],index=row['index'],part=row['part'],owner=row['owner'],
            mesh_bounds_mm=mb,linear_deflection_mm=.02,comparison_allowance_mm=.05,
            sampled_surface_outside_operand_bounds=violations,
            conservative_BREP_bbox_excess_only=not violations))
        save(OUT/'progress.json',dict(rows=rows,selected=False,physical_pass=False))
    ended=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='BOUNDING_BOX_INFERENCE_CORRECTED',
        supersedes='contact-witness-sanity-r1 invalidity inference: a BREP BoundBox is not guaranteed tight to trimmed curved surfaces. It does NOT prove an invalid intersection.',
        sampled=len(rows),surface_excess_count=sum(bool(r['sampled_surface_outside_operand_bounds']) for r in rows),rows=rows,
        selected=False,physical_pass=False,source_sha256=pins,script_sha256=sha(Path(__file__)),
        started_utc=started.isoformat(),finished_utc=ended.isoformat(),worker_wall_seconds=(ended-started).total_seconds()))
    print(json.dumps(dict(sampled=len(rows),surface_excess=sum(bool(r['sampled_surface_outside_operand_bounds']) for r in rows))))


if __name__=='__main__':main()

"""One source platform placement before another expensive cable build.

Lowered P_SYS hit preserved P0 supports. Raise the same block22mm instead;
W043/W066 must be redesigned together, not silently retained as qualified.
This tests the bought body only, not supports, levers or the six-wire family.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-psys-platform-preflight-r1'


def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    rejected_file=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r2/checks.json'
    rejected=json.loads(rejected_file.read_text(encoding='utf-8'))
    assert rejected['status']=='JOINT_SOURCE_REJECTED'
    assert any(h['wire']=='P_SYS_DISPLACED_BODY' and h['owner']=='P0Support0' for h in rejected['hits'])
    assert all(sha(ROOT/k)==v for k,v in {**rejected['source_sha256'],**rejected['files']}.items())
    intent=dict(displacement_mm=[0,0,22],new_wire_mouth_z_mm=135.5,
        wires_reopened=['W043','W066'],W043_factory_blank_candidate_mm=60,
        W043_supplier_minimum_factory_mm=84.5,W043_actual_cut_mm=None,
        source_selection_unchanged=True,P0_supports_unchanged=True,
        conditions=['Platform/retention/tool access NOT constructed.',
            'Body-only clearance cannot qualify the six source wires.',
            'W04360mm is candidate only; route+strip/reserve must fit before allocation.',
            'Do not preserve old W043/W066 readiness after selecting a displacement.'],
        selected=False,native_supports_ready=False,W5_complete=False,physical_pass=False)
    save(OUT/'intent.json',intent)
    owners,pins,_=installed(A,Part);body=owners.pop('P_SYS_design').copy()
    body.translate(A.Vector(*intent['displacement_mm']))
    geometry=OUT/'P_SYS_CANDIDATE_WORLD.brep';body.exportBrep(str(geometry))
    hits=[];errors=[];pairs=0
    for key,other in owners.items():
        if not body.BoundBox.intersect(other.BoundBox):continue
        pairs+=1
        try:
            common=body.common(other)
            if common.Volume>1e-5:
                b=common.BoundBox
                hits.append(dict(owner=key,mm3=common.Volume,bounds_mm=[getattr(b,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as exc:errors.append(dict(owner=key,error=str(exc)))
    # Establish whether the two R5 ground-body contacts were introduced by
    # rotation or already exist in the same selected reference envelope.
    original_ground=[]
    aux=owners['hardware/electronics/full-cat/xa05-main-aux-return-r2/XA05_DESIGN.brep']
    for key in ('RL_G_design','RR_G_design'):
        s=owners[key];volume=s.common(aux).Volume
        original_ground.append(dict(owner=key,unchanged_reference_contact_mm3=volume,
            physical_contact_verified=False,diagnostic_only=True))
    finish=datetime.now(timezone.utc);pins += [Path(__file__),rejected_file]
    save(OUT/'checks.json',dict(status='BOUGHT_BODY_PLACEMENT_REJECTED' if hits or errors else 'BOUGHT_BODY_ONLY_CLEAR_PLATFORM_AND_SIX_WIRES_OPEN',
        hits=hits,errors=errors,pairs=pairs,unchanged_ground_reference_observations=original_ground,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in (geometry,OUT/'intent.json')},
        selected=False,native_supports_ready=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('PLATFORM_PREFLIGHT',pairs,len(hits),len(errors),flush=True)


if __name__=='__main__':main()

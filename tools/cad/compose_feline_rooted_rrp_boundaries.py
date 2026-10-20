"""Current four RR_P boundaries plus received planning root/access evidence."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_rrp_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates
from feline_rrp_rooted_context import received


def current():
    base,rows,files=parent();f,r=received()
    af=OUT/'n01-RRP-assembly-access.json';assembly=json.loads(af.read_text())
    assert assembly['status']=='RRP_CONSTRUCTIVE_ASSEMBLY_ACCESS_RECEIVED_WITH_GATES' and not assembly['failures']
    for p,h in assembly['source_sha256'].items():assert sha(ROOT/p)==h,p
    updates={e['id']:dict(support_load_path_OPEN=False,constructive_RRP_assembly_received=True,
        support_root_receipt=f.relative_to(ROOT).as_posix(),support_root_sha256=sha(f),
        assembly_receipt=af.relative_to(ROOT).as_posix(),assembly_sha256=sha(af),
        native_manufacture_and_force_NOT_physically_qualified=True,own_mating_continuous_access_gate_OPEN=True)
        for e in rows if e.get('prefix_geometry_owner','').startswith('EarlyRR:')}
    assert len(updates)==4
    return base,apply_updates(rows,updates),(*files,f,af)

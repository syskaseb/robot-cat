"""Explain the bounded common-layout failure from saved domains, no new scan."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
import numpy as np
from feline_flat_station_templates import build,compatible

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


def main():
    tick=time.monotonic();gallery='--gallery' in sys.argv
    path=OUT/('n01-coupled-power-galleries.json' if gallery else 'n01-flat20-domains-joint.json');doc=json.loads(path.read_text())
    assert doc['joint_assignment'] is None and doc['search_nodes']==3 and not doc['errors']
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text())
    names=['P_SYS','P_REAR','G1','P_FRONT'] if gallery else [n for n,v in doc['domains'].items() if len(v)<=3];assert len(names)==4
    domains={}
    for n in names:
        station=next(s for s in plan['stations'] if s['ref']==n)
        domains[n]=[build(station,r['family'],r['side'],r['departure_X'],r['centre_mm'][0],
            r.get('centre_y_override_mm'),r.get('bend_mode','OUTWARD_CONCENTRIC')) for r in doc['domains'][n]]
    def possible(group):
        for choice in itertools.product(*(range(len(domains[n])) for n in group)):
            if all(compatible(domains[a][choice[i]],domains[b][choice[j]]) for i,a in enumerate(group) for j,b in enumerate(group) if i<j):return True
        return False
    core=None
    for size in range(2,len(names)+1):
        for group in itertools.combinations(names,size):
            if not possible(group):core=group;break
        if core:break
    assert core,'The three-node failure must be explained, not guessed'
    witnesses=[]
    for a,b in itertools.combinations(core,2):
        for i,aa in enumerate(domains[a]):
            for j,bb in enumerate(domains[b]):
                if compatible(aa,bb):continue
                ca=next(r for r in aa['boxes'] if r['kind']==0)['bounds']
                cb=next(r for r in bb['boxes'] if r['kind']==0)['bounds']
                overlap=np.maximum(0,np.minimum(ca[1],cb[1])-np.maximum(ca[0],cb[0]))
                witnesses.append(dict(a=a,a_domain=i,b=b,b_domain=j,
                    a_centre=aa['centre_mm'],b_centre=bb['centre_mm'],
                    nominal_full_source_box_overlap_mm3=float(np.prod(overlap)),
                    source_case_is_valid_full_nominal_box_not_precise_vendor_mesh=True,
                    whole_module_numeric_incompatibility=True))
    result=dict(status='BOUNDED_FLAT_FAMILY_MINIMAL_COUPLED_CONFLICT',
        selected=False,N01_complete=False,physical_pass=False,
        minimal_core=list(core),every_proper_subset_has_joint_choice=True,
        domain_counts={n:len(domains[n]) for n in core},witnesses=witnesses,
        no_global_infeasibility_claim=True,no_CAD_or_manufacturer_collision_claim_from_samples=True,
        unchanged19_received_domains_not_rescanned=True,
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (path,planfile,Path(__file__),ROOT/'tools/cad/feline_flat_station_templates.py')},
        next='Change shared row/height/module allocation including real clamps; no individual source-clock or scalar D_FL correction.',
        worker_seconds=round(time.monotonic()-tick,3))
    dest=OUT/('n01-coupled-power-gallery-conflict.json' if gallery else 'n01-flat20-coupled-conflict.json');assert not dest.exists()
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(core=list(core),counts=result['domain_counts'],witnesses=len(witnesses),seconds=result['worker_seconds'])))


if __name__=='__main__':main()

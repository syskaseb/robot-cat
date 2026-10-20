"""One shortest-link material proof for the entire surviving positive domain.

Longer portalX means the identical fixed lower straight only gets longer.
An intersection of this shortest segment rejects this topology's entire
received positive crown domain, NOT every possible route or the whole robot.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_atomic_save import save_json
from plan_feline_n01_shared import pipe


def main():
    tick=time.monotonic();sf=OUT/'n01-MTA-tight-crown-domain.json';r=json.loads(sf.read_text())
    assert r['status'] in ('SHARED_FOUR_CROWN_CONSERVATIVE_DOMAIN_CURRENT_WHOLE_SCENE','NO_CONSERVATIVE_SHARED_CROWN_DOMAIN_NOT_GLOBAL_IMPOSSIBLE')
    assert r['domains_X_mm']['positive']
    import math
    for n in ('CustomPrefix:W041','CustomPrefix:W042'):
        b=pipe(r['plans'][n]['crown_at_portalX0'],2.1).BoundBox
        assert all(n+':'+str(float(z)) in r['completed_slabs'] for z in range(math.floor(b.ZMin),math.ceil(b.ZMax),2)),n
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    of=OUT/'n01-rooted-end-bays-caps.json';output=json.loads(of.read_text());parts=load(output)
    minimum=min(a for a,b in r['domains_X_mm']['positive']);rows=[]
    for n,w in (('CustomPrefix:W041','W045'),('CustomPrefix:W042','W053')):
        q=r['plans'][n]['stem_end_mm'];length=minimum-25.2-q[0];assert length>0
        line=Part.makeCylinder(2.1,length,A.Vector(*q),A.Vector(1,0,0));other='EndBay:CaseBase:'+w+'_Joint'
        common=line.common(parts[other]);assert common.isNull() or common.isValid()
        gap,points,_=line.distToShape(parts[other])
        rows.append(dict(wire=n,source=other,shortest_positive_portalX_mm=minimum,
            straight_start_mm=q,shortest_straight_length_mm=length,
            actual_gap_mm=gap,actual_overlap_mm3=common.Volume,
            witness_mm=[[list(a),list(b)] for a,b in points[:1]],
            invalidates_entire_received_positive_domain=common.Volume>1e-5,
            reason='Every larger admissible portal contains this identical lower straight'))
    result=dict(status='LOWER_LINK_TOPOLOGY_HOLD' if any(p['invalidates_entire_received_positive_domain'] for p in rows) else 'LOWER_LINK_NAMED_PAIR_CLEAR_NOT_FULL_SCENE',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (sf,of,ROOT/output['bundle'],Path(__file__))},
        lower_links=rows,worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,native_changed=False,
        global_impossibility_NOT_proved=True)
    save_json(OUT/'n01-MTA-lower-link-topology.json',result)
    print(json.dumps(result,separators=(',',':')),flush=True)


if __name__=='__main__':main()

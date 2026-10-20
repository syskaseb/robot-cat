"""Receive ALL source restraint witnesses before another topology change.

Reuse already received exact pairs. No geometry generation or motion run.
This is a blocker map, not an N01 acceptance or production detail model.
"""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from feline_source_restraint_plan import source
from receive_feline_rrp_shared_height import load
from receive_feline_source_restraints import local_limit
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();sf=OUT/'n01-source-restraints-whole-r3.json';r=json.loads(sf.read_text())
    dest=OUT/'n01-source-restraints-static-witnesses.json'
    assert not dest.exists(),'Receive saved whole blocker map, do not repeat'
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    world,parts,meta,pins,docs=compose();mf=OUT/'n01-MTA-low-stop-cradles.json';m=json.loads(mf.read_text())
    effective={n:s for n,s in parts.items() if n not in m['retired']};effective.update(load(m))
    base,_,_,_=source();new=load(r);effective.update(base);effective.update(new)
    ameta={row['name']:row for row in r['geometry']}
    old=json.loads(gzip.decompress((ROOT/r['pair_rows']).read_bytes()))
    rows={k:v for k,v in old.items() if '|' in k};reused=len(rows);done=[];query=SolidQueries()
    def save():
        out=dict(status='ALL_CHANGED_SOURCE_STATIC_WITNESSES_NOT_APPROVAL',source=sf.relative_to(ROOT).as_posix(),
            source_sha256={**pins,sf.relative_to(ROOT).as_posix():sha(sf),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
            completed=done,checks=rows,reused_exact_pairs=reused,
            failures={k:v for k,v in rows.items() if not v['ok']},
            N01_complete=False,native_changed=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,out)
    for n,s in new.items():
        for other,t in {**effective,**{'rest:'+k:v for k,v in world.rest.items()}}.items():
            if other==n or other in new and list(new).index(other)>list(new).index(n):continue
            key=n+'|'+other
            if key in rows:continue
            if any(n in members and other in members for members in r['print_groups'].values()):continue
            limit=local_limit(n,other,ameta,r['print_groups'],r['independent_grips'],r['case_bonds'])
            if limit is None:continue
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            a=s;b=t
            if other==world.bus['name']:a=s.copy();a.Placement=docs['inverse']*a.Placement;b=world.bus['original']
            if not b.Solids:
                md=meta.get(other,{});radius=md.get('nominal_profile_radius_mm') or md.get('radius_mm')
                row=profile_gap(a,b,radius,limit) if radius else dict(ok=False,unreceived_curve_profile=True)
            else:
                gap=query.distance(a,b);common=a.common(b).Volume if limit==0 else 0.
                row=dict(ok=gap>=limit-1e-6 and common<1e-5,gap_mm=gap,minimum_mm=limit,common_mm3=common)
                if not row['ok']:
                    row['witness_mm']=[[list(x),list(y)] for x,y in a.distToShape(b)[1][:1]]
            rows[key]=row
            if not row['ok']:print('WITNESS',key,row,flush=True)
        done.append(n);save();print('MAPPED',n,flush=True)
    save();print('ALL_MAPPED',len(done),len(rows),reused,round(time.monotonic()-tick,3),flush=True)


if __name__=='__main__':main()

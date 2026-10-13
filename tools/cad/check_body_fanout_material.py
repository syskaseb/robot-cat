"""Exact current fanout curve/radius gate, with durable per-pair checkpoints.

May qualify a received PARTIAL route set for reuse; only36 routes can complete
this scoped gate. Even a full clear gate does not qualify absent grip material,
stock, complete wiring or physical hardware.
"""
import json
import math
import time
from pathlib import Path
import numpy as np
import current_body_fanout_material as M
from immutable_bounds import ImmutableBounds
from exact_pair_receipts import PairReceipts
from plan_current_mta_interfaces import line

P=M.P


class AtomicPairs(PairReceipts):
    def save(self):
        tmp=self.path.with_suffix('.tmp')
        tmp.write_text(json.dumps(dict(checker_sha256=self.revision,records=self.records),separators=(',',':'))+'\n')
        tmp.replace(self.path)


def terminal_trim(parts,amount=1.5):
    """Only the explicitly mated contact mouth, never the whole receiving leg."""
    last=parts[-1];assert last['kind']=='line' and last['length_mm']>amount
    ratio=amount/last['length_mm']
    end=[b+(a-b)*ratio for a,b in zip(last['start'],last['end'])]
    return [*parts[:-1],line(last['start'],end)]


def mate_names(row):
    role=row['receiver_role']
    if row['core'] in ('D','G'):return {role.split('.')[0]}
    leg=role.removeprefix('F_').split('.')[0]
    side='L' if leg[:2] in ('FL','RL') else 'R'
    position=int(leg[-1])+(3 if leg[:2] in ('RL','RR') else 0)
    return {f'F_{side}{position}_CP2_OUT',f'F_{side}{position}_CP2_Housing'}


def run():
    tick=time.monotonic();file=P.OUT/'body-fanout-layout.json'
    plan=json.loads(file.read_text());assert plan['routes']
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,old,pins=M.load()
    scene=json.loads((P.OUT/'body-fanout-scene.json').read_text())
    archive=P.ROOT/scene['scene'];assert P.SHA(archive)==scene['sha256']
    with np.load(archive,allow_pickle=False) as mesh:
        assert set(map(str,mesh['material_names']))<=set(targets),'Exact loader omitted a planned material instance'
    rows={r['wire']:r for r in plan['rows']};curves={};without_mouth={};after_breakout={}
    for name,r in plan['routes'].items():
        parts=r['parts'];row=rows[name]
        assert math.dist(parts[0]['start'],row['start'])<1e-8
        assert math.dist(parts[-1]['end'],row['receiver_point_mm'])<1e-8
        curves[name]=P.wire(parts);without_mouth[name]=P.wire(terminal_trim(parts))
        assert abs(parts[0]['length_mm']-5)<1e-8
        after_breakout[name]=P.wire(parts[1:])
    bounds=ImmutableBounds();cache=AtomicPairs(P.OUT/'body-fanout-exact-pair-cache.json',bounds.near)
    contacts=[];errors=[];pairs=0;last_save=time.monotonic();completed=[]
    def check(name,curve,target,other,radius=0):
        nonlocal pairs,last_save
        required=1.25+radius
        if not bounds.near(curve,other,required):return
        pairs+=1
        try:
            # Include the project margin in the component broad phase too.
            # Calling the cache with radius1 then testing1.25 would lose pairs.
            gap,_=cache.check(curve,other,1.25,radius)
            if gap<required-1e-6:contacts.append(dict(wire=name,target=target,gap_mm=gap,required_project_mm=required))
        except (AssertionError,ValueError) as e:errors.append(dict(wire=name,target=target,error=str(e)))
        if time.monotonic()-last_save>20:
            cache.save();last_save=time.monotonic()
            print('exact fanout',name,'pairs',pairs,'contacts',len(contacts),'errors',len(errors),flush=True)
    def save():
        result=dict(status='REJECTED_CURRENT_FANOUT_MATERIAL' if contacts or errors else
            'PARTIAL_CURRENT_FANOUT_EXACT_CLEAR_REMAINING_OPEN' if len(curves)<36 else 'CURRENT36FANOUT_CURVES_EXACT_CLEAR_GRIP_MATERIAL_OPEN',
            routes=list(curves),completed_routes=completed,pairs=pairs,contacts=contacts,errors=errors,
            material_instances=len(targets),retained_wire_instances=len(old),project_core_OD_mm=2,
            project_radial_margin_mm=.25,source_jacket_mate_excluded_first_mm=5,
            named_receiving_mate_mouth_excluded_last_mm=1.5,
            exclusion_scope='Only same-loom retained jacket for first5mm; only named physical receiver casing/OUT contact for last1.5mm. All other pair curves are whole.',
            excluded_new_grip_material='Not designed yet; this gate cannot accept receiver/midspan grips or wholeW5.',
            source_sha256={**pins,file.relative_to(P.ROOT).as_posix():P.SHA(file),
                Path(__file__).relative_to(P.ROOT).as_posix():P.SHA(Path(__file__))},
            computed_pairs=cache.computed,reused_pairs=cache.reused,worker_seconds=round(time.monotonic()-tick,3),
            selected=False,W5_complete=False,physical_pass=False,continuous_motion_sweep=False)
        dest=P.OUT/'body-fanout-material.json';tmp=dest.with_suffix('.tmp')
        tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(dest);cache.save()
        return result
    names=list(curves)
    for i,name in enumerate(names):
        row=rows[name];mates=mate_names(row)
        for target,shape in targets.items():
            stem=target.split('/')[0]
            curve=without_mouth[name] if stem in mates else curves[name]
            check(name,curve,target,shape)
        for target,(shape,radius) in old.items():
            curve=after_breakout[name] if target.startswith('leg/'+row['loom']+'/') else curves[name]
            check(name,curve,target,shape,radius)
        for other in names[:i]:check(name,curves[name],'new/'+other,curves[other],1)
        completed.append(name);result=save()
        print('received exact fanout',name,'completed',len(completed),'pairs',pairs,'contacts',len(contacts),'errors',len(errors),flush=True)
    print(json.dumps({k:result[k] for k in ('status','worker_seconds','pairs','computed_pairs','reused_pairs')}),flush=True)


if __name__=='__main__':run()

"""One cause change after e3ddcac; reuse unaffected actual-solid checks.

Separate front MTA/source planes, place AUX in a measured free cell, start
all three source fanouts together, and exchange FR with an unused same-bus
port. Existing support contacts remain failures until native replacement.
"""
from pathlib import Path
import copy, json, math, sys
import open_prototype_receiving_gallery as G
from open_prototype_bundle_spines import add, mul
from open_prototype_distribution_allocation import input_recipe

PLAN=G.OUT/'receiving-gallery-recovery-plan.json'
PROOF=G.OUT/'receiving-gallery-recovery-checks.json'


def build():
    old=G.read(G.PLAN); plan=copy.deepcopy(old)
    proof=G.read(G.PROOF)
    for path,h in proof['source_sha256'].items():
        # Original generating source is preserved by e3ddcac; the refactored
        # runner is now pinned separately. All geometry inputs must match.
        if path!='tools/cad/open_prototype_receiving_gallery.py':assert G.sha(G.ROOT/path)==h,path
    for row in plan['mts']:
        if row['native'] in ('MTA_FL_CP2','MTA_FR_CP2'):
            row['old_centre_mm']=row['centre_mm'][:];row['centre_mm'][2]=116
    by_port={r['role']:r for r in plan['ports']}
    assert by_port['P_FRONT.3']['occupied'] and not by_port['P_FRONT.5']['occupied']
    by_port['P_FRONT.3']['occupied']=False;by_port['P_FRONT.5']['occupied']=True
    plan['main_targets']['W042']='P_FRONT.5'
    plan['same_bus_port_exchange']={'wire':'W042','old':'P_FRONT.3','new':'P_FRONT.5','old_new_net_identical':True,'new_old_occupant':'NC'}
    changed={'MTA_FL_CP2','MTA_FR_CP2','W042/entry9mm'}
    for row in plan['holders']:
        n=row['holder']
        if n=='F_AUX':
            row['input_mm'][1]+=10;row['output_mm'][1]+=10;row['cut_mm'][1]+=10
            for part in row['output_parts']:
                for k in ('start','mid','end'):
                    if k in part:part[k][1]+=10
            recipe=input_recipe(row['input_mm'],by_port[row['target']]['point_mm'],mul(row['axis'],-1),6)
            row['input_parts']=recipe['segments'];row['input_centreline_mm']=recipe['centreline_mm']
            row['input_blank_mm']=recipe['centreline_mm']+14
            changed.update(n+'/'+s for s in ('case','input','output','sleeve','new_insulation','ATO_tool_budget'))
        if n in ('F_HY','F_HP','F_TY'):
            parts=row['input_parts'];direction=mul(row['axis'],-1)
            first=math.dist(parts[0]['start'],parts[0]['end']);shift=mul(direction,3-first)
            parts[0]['end']=add(parts[0]['start'],mul(direction,3))
            for part in parts[1:-1]:
                for k in ('start','mid','end'):
                    if k in part:part[k]=add(part[k],shift)
            parts[-1]['start']=add(parts[-1]['start'],shift)
            assert math.dist(parts[-1]['start'],parts[-1]['end'])>=9-1e-7
            changed.add(n+'/input')
        assert row['input_blank_mm']<=row['input_limit_mm'],n
    assert len(plan['ports'])==100 and sum(r['occupied'] for r in plan['ports'])==86
    plan['preserved']=[r for r in plan['preserved'] if not r.startswith('Four MTA')]
    plan['preserved'].append('Rear MTA casings/poses; front source and output full routes OPEN')
    plan['invalidated'].extend(['Both front MTA native seats/load paths and both tails',
        'Front FR WAGO landing .3 to NC .5; every affected map must be propagated before selection'])
    plan['cause_change']=['Front MTA plane116 below source intake138',
        'AUX body Y-40 with2.625mm nominal clearance to retained G_AUX case',
        'Three source fanouts share3mm onset, preserved R6 and minimum9mm grip',
        'FR feed receives at NC .5 instead of intersecting TY output at .3']
    plan['changed_names']=sorted(changed)
    plan['source_sha256'].pop('tools/cad/open_prototype_receiving_gallery.py',None)
    for p in (Path(G.__file__),Path(__file__),G.PLAN,G.PROOF):
        plan['source_sha256'][p.relative_to(G.ROOT).as_posix()]=G.sha(p)
    return plan,proof,changed


if __name__=='__main__':
    plan,proof,changed=build()
    print(json.dumps({'inputs':[(r['holder'],r['input_blank_mm'],r['input_limit_mm']) for r in plan['holders']],
        'ports':len(plan['ports']),'occupied':sum(p['occupied'] for p in plan['ports']),
        'changed':sorted(changed)}),flush=True)
    if '--preflight' not in sys.argv:G.main(plan,PLAN,PROOF,proof,changed)

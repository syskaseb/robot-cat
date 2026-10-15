"""Solve received36 exact positive domains without rechecking old whole wires.

Every candidate already passed all20 retained curves during static preflight.
Only NEW prefixes require wire/grip or wire/wire mutual checks here. The20
received full curves are immutable, so their old pair gates are reused.
"""
import copy,json,time
from pathlib import Path
import core_receiver_port as T
from plan_body36_receiver_space import P,C


def run():
    tick=time.monotonic();file=P.OUT/'body36-global-receiver-space.json';contractfile=P.OUT/'body36-current-contract.json'
    preflight,contract=[json.loads(f.read_text()) for f in (file,contractfile)]
    for n,h in preflight['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    assert len(preflight['qualified_options'])==36 and all(preflight['qualified_options'].values())
    missing=set(contract['remaining_wire_ids']);domains={}
    for name,records in preflight['qualified_options'].items():
        options=[]
        for i,record in enumerate(records):
            q=copy.deepcopy(record);profile=T.build(q['land'],q['normal'],q['offset']);goal=profile['arrival_world_mm']
            q.update(profile=profile,seed=P.box([v-2 for v in goal]+[v+2 for v in goal]),identity=(name,i),
                wire=P.wire(q['row']['receiving_parts']) if name in missing else None)
            options.append(q)
        domains[name]=options
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'body36-global-receiver-pairs.json',bounds.near)
    checks=0;memo={};witnesses=[];last=time.monotonic();nodes=0;selected={};timed_out=False
    def hit(a,b,ra=0,rb=0):
        nonlocal checks,last
        if not bounds.near(a,b,ra+rb+.0001):return False
        checks+=1;gap,vol=cache.check(a,b,ra,rb)
        if time.monotonic()-last>20:cache.save();last=time.monotonic()
        return vol>1e-5 or ((ra or rb) and gap<ra+rb-1e-6)
    def fits(q,p):
        key=tuple(sorted((q['identity'],p['identity'])))
        if key in memo:return memo[key]
        witness=None
        for ka,a in (('body',q['profile']['body']),('band',q['profile']['band']),('seed',q['seed'])):
            for kb,b in (('body',p['profile']['body']),('band',p['profile']['band']),('seed',p['seed'])):
                if q['owner']==p['owner'] and ka!='band' and kb!='band':continue
                if hit(a,b):witness=(ka,kb);break
            if witness:break
        if not witness and q['wire'] is not None and p['wire'] is not None and hit(q['wire'],p['wire'],1.25,1):witness=('prefix','prefix')
        if not witness:
            for a,b in ((q,p),(p,q)):
                if a['wire'] is None:continue # All retained whole wires already checked in every grip's preflight.
                for kind,s in (('body',b['profile']['body']),('band',b['profile']['band']),('seed',b['seed'])):
                    if hit(a['wire'],s,1.25):witness=('prefix',kind);break
                if witness:break
        memo[key]=witness is None
        if witness and len(witnesses)<80:witnesses.append(dict(pair=key,kind=witness))
        return memo[key]
    until=time.monotonic()+300
    def solve():
        nonlocal nodes,timed_out
        nodes+=1
        if len(selected)==36:return True
        if time.monotonic()>until or nodes>20000:timed_out=True;return False
        available={n:[q for q in d if all(fits(q,p) for p in selected.values())] for n,d in domains.items() if n not in selected}
        name=min(available,key=lambda n:len(available[n]))
        for q in available[name]:
            selected[name]=q
            if solve():return True
            selected.pop(name)
            if timed_out:return False
        return False
    solved=solve()
    def pack(q):return {k:v for k,v in q.items() if k not in ('profile','seed','wire','identity')}
    result=dict(status='GLOBAL36_RECEIVER_PREFIX_GRIPS_JOINT_CLEAR_16MIDDLES_OPEN' if solved else
        ('RECEIVER36_SOLVE_BUDGET_EXHAUSTED_NOT_GEOMETRIC_IMPOSSIBILITY' if timed_out else 'RECEIVER36_RECEIVED_DOMAINS_INCOMPATIBLE'),
        grips={n:pack(q) for n,q in selected.items()},checks=checks,search_nodes=nodes,pair_options_memoized=len(memo),
        conflict_examples=witnesses,worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={file.relative_to(P.ROOT).as_posix():P.SHA(file),contractfile.relative_to(P.ROOT).as_posix():P.SHA(contractfile),
            Path(__file__).relative_to(P.ROOT).as_posix():P.SHA(Path(__file__))},
        inherited_whole_wire_pair_checks_reused=True,selected=False,W5_complete=False,physical_pass=False)
    out=P.OUT/'body36-receiver-selected.json';out.write_text(json.dumps(result,indent=2)+'\n');cache.save()
    print(result['status'],'nodes',nodes,'pairs',checks,'seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':run()

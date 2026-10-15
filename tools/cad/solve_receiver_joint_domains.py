"""Solve pinned prequalified22domains without rebuilding the robot scene."""
import copy,itertools,json,sys,time
from pathlib import Path
from plan_bolted_receiver_layout import material
from plan_body36_receiver_space import P,C
from csg_bore_clearance import prove as prove_bores
from receiver_domain_solver import solve


def run():
    tick=time.monotonic();source=P.OUT/'bolted-receiver-layout.json';receipt=json.loads(source.read_text())
    assert receipt['status']=='BOLTED_RECEIVER_LAYOUT_OPEN' and not receipt['rejections'] and not receipt['errors']
    for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    extra_files=[]
    if '--parallel' in sys.argv:
        extension=P.OUT/'parallel-fuse-receiver-domains.json';new=json.loads(extension.read_text())
        assert new['status']=='PARALLEL_FL_FUSE_DOMAINS_CLEAR_JOINT_OPEN' and not new['errors']
        assert new['parent_domains']==source.relative_to(P.ROOT).as_posix()
        for n,h in new['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
        receipt=copy.deepcopy(receipt);receipt['qualified_options'].update(new['replacement_options'])
        receipt['source_sha256'].update(new['source_sha256']);extra_files.append(extension)
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'bolted-receiver-layout-pairs.json',bounds.near)
    domains={};records={};registry={};memo={};checks=0;conflicts=[];errors=[]
    def hit(a,b,ra=0,rb=0):
        nonlocal checks
        if not bounds.near(a,b,ra+rb+.0001):return False
        if not ra and rb and id(a) in registry:
            recipe,kind=registry[id(a)]
            if prove_bores(recipe,kind,b,rb):return False
        if ra and not rb and id(b) in registry:
            recipe,kind=registry[id(b)]
            if prove_bores(recipe,kind,a,ra):return False
        if rb and not b.Solids and len(b.Edges)>1:return any(hit(a,e,ra,rb) for e in b.Edges)
        checks+=1
        try:gap,volume=cache.check(a,b,ra,rb)
        except RuntimeError as e:errors.append(str(e));return True
        return volume>1e-5 or ((ra or rb) and gap<ra+rb-1e-6)
    for name,options in receipt['qualified_options'].items():
        domains[name]=list(range(len(options)))
        for index,q in enumerate(options):
            p,parts=material(q)
            if 'recipe' in q:
                assert json.dumps(p['recipe'],sort_keys=True)==json.dumps(q['recipe'],sort_keys=True),(name,index,'Recipe changed since environment acceptance')
            else:
                # RR record stores its complete builder inputs, whose exact
                # builder file is pinned by the accepted environment receipt.
                assert q['kind']=='single' or (q.get('retainer')=='M2_cap' and name=='RR_G')
                builder='core_receiver_port.py' if q['kind']=='single' else 'bolted_rail_pressure_bridge.py'
                assert P.SHA(Path(__file__).with_name(builder))==receipt['source_sha256']['tools/cad/'+builder]
            if q['kind']=='triple':
                for kind in ('body','cap'):registry[id(parts[kind])]=(p['recipe'],kind)
            prefixes={row['wire']:P.wire(row['receiving_parts']) for row in q['rows'] if row['wire'] in receipt['changed_wire_ids']}
            records[name,index]=dict(owner=q['owner'],parts=parts,prefixes=prefixes)
    def compatible(a,x,b,y):
        key=tuple(sorted(((a,x),(b,y))))
        if key in memo:return memo[key]
        q,p=records[a,x],records[b,y];witness=None
        for ka,s in q['parts'].items():
            for kb,t in p['parts'].items():
                if q['owner']==p['owner'] and ka in ('body','seed') and kb in ('body','seed'):continue
                if hit(s,t):witness=[ka,kb];break
            if witness:break
        if not witness:
            for first,second in ((q,p),(p,q)):
                for name,wire in first['prefixes'].items():
                    for kind,s in second['parts'].items():
                        if hit(wire,s,1.25):witness=['prefix/'+name,kind];break
                    if witness:break
                if witness:break
        if not witness:
            for na,s in q['prefixes'].items():
                for nb,t in p['prefixes'].items():
                    if hit(s,t,1.25,1):witness=['prefix/'+na,'prefix/'+nb];break
                if witness:break
        memo[key]=not witness
        if witness:conflicts.append(dict(a=a,option_a=x,b=b,option_b=y,components=witness))
        return memo[key]
    selection,stats=solve(domains,compatible,seconds=120,max_nodes=50000)
    if selection is not None:
        assert all(compatible(a,selection[a],b,selection[b]) for a,b in itertools.combinations(selection,2))
    result=dict(status='BOLTED22_RECEIVER_JOINT_SELECTION_CLEAR_MIDDLES_OPEN' if selection is not None else 'RECEIVER_JOINT_SELECTION_OPEN',
        selected_options=selection,domain_receipt=source.relative_to(P.ROOT).as_posix(),solver=stats,
        override_receipt=extra_files[0].relative_to(P.ROOT).as_posix() if extra_files else None,
        compatibility_queries=len(memo),material_queries=checks,conflicts=conflicts,errors=errors,
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
        source_sha256={**receipt['source_sha256'],**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in
            (source,Path(__file__),Path(__file__).with_name('receiver_domain_solver.py'),*extra_files)}})
    out=P.OUT/'receiver-joint-selection.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save()
    print('Receiver joint selection',stats,'queries',len(memo),'material',checks,flush=True)


if __name__=='__main__':run()

"""Identity-level W5 end coverage; never infer completeness from counts alone.

Coordinates come from current route endpoints. Old local OPEN flags are not
rewritten: their later native/root proofs are joined explicitly here.
"""
import json,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def exact_cover(expected,rows):
    ids=[r['id'] for r in rows]
    assert len(ids)==len(set(ids)),('Duplicate end',ids)
    assert set(ids)==set(expected),dict(missing=sorted(set(expected)-set(ids)),extra=sorted(set(ids)-set(expected)))


def compose_fixed(allocation,space,oldroots,newroots,source,retained,bindings,feeds):
    source_roles={}
    for g in source['groups']:
        assert g['root_subset_verified']
        for role in g['recipe']['bound_ends']:
            key=(g['recipe']['wire'],role);assert key not in source_roles
            owner='SourceGripRail' if g['id'] in ('W066_0_15','W043_P_SYS','W067_P_SYS','W068_P_SYS') else g['owner']
            source_roles[key]=dict(group=g['id'],owner=owner,proof='local-source-retention-roots.json',native_proof='operating-supports-native/manifest.json' if owner=='SourceGripRail' else 'local-source-retention-native/manifest.json')
    roots={g['id']:g for g in oldroots['groups'] if g['owner']!='UpperCarrier001'}
    roots.update({g['id']:g for g in newroots['groups'] if g['kind']=='wire_saddle'})
    groups={g['id']:g for g in space['spatial_groups']};by_end={}
    assert len(groups)==54 and set(groups)==set(roots)
    for gid,g in groups.items():
        for end in g['ends']:
            assert end not in by_end
            by_end[end]=dict(group=gid,owner=roots[gid]['owner'],proof='current-upper-operating-roots.json' if roots[gid]['owner']=='UpperCarrier001' else 'remaining25-saddle-roots.json',native_proof='current-operating-native-composition.json')
    rows=[]
    for e in allocation['ends']:
        support=source_roles.get((e['wire'],e['role'])) if e['already_native_source_group'] else by_end.get(e['id'])
        assert support,('Missing remaining25 end',e['id'],e['role'])
        rows.append(dict(id=e['id'],wire=e['wire'],segment=e['segment'],side=e['side'],role=e['role'],point_world_mm=e['point_world_mm'],restraint=support))
    assert len(rows)==66 and len(by_end)==63
    exact_cover([e['id'] for e in allocation['ends']],rows)
    retained_rows=[]
    for r in retained['rows']:
        wid=r['wire'];b=bindings['bindings'][wid]
        for e in r['nominal_geometry_endpoints']:
            i=e['segment_index'];side=e['side']
            if wid=='W076':role={ (0,'start'):'F0.out',(0,'end'):'POST_F0.1',(1,'start'):'POST_F0.2',(1,'end'):'S0.in'}[i,side]
            else:
                bound=b['ends'][0 if side=='start' else 1]
                assert bound['point_world_mm']==e['point_world_mm'],(wid,side,'Binding is not current route endpoint')
                role=bound['current_physical_role']
            support=source_roles.get((wid,role))
            if not support and role.startswith('G1.'):
                support=dict(group='G1/five',owner='UpperCarrier001',proof='g1-rooted-carrier-plan.json',native_proof='current-operating-native-composition.json')
            if not support and role.startswith('G2.'):
                support=dict(group='BUS_G' if wid=='W003' else 'Heavy3',owner='UpperCarrier001',proof='remaining-fixed-feed-checks.json',native_proof='current-operating-native-composition.json')
            if not support:
                matched=[x for x in feeds['restraints'] if x['wire']==wid and role.startswith(x['group']+'.')]
                if matched:
                    assert len(matched)==1 and matched[0]['accepted_in_this_scope']
                    x=matched[0];support=dict(group=x['group'],owner=x['owner'],proof='retained-feed-restraints-checks.json',native_proof='current-operating-native-composition.json')
            if not support and wid=='W025' and role.startswith('FL_G.'):
                support=dict(group='FL_G',owner='FrontLeftFixedCarrier',proof='remaining-fixed-feed-checks.json',native_proof='current-operating-native-composition.json')
            if not support and wid in ('W060','W078','W079','W080') and role.startswith(('MAIN.','PI_USB_C.')):
                support=dict(group='MAIN/USB',owner='E1_current_native',proof='u1-power-grips-checks.json',native_proof='u1-power-grips-native.json')
            if not support and wid in ('W002','W003') and role.startswith('BUS.'):
                support=dict(group='BUS paired source',owner='BUSCarrierCurrent',proof='BUS-routes-checks.json',native_proof='BUS-native-checks.json')
            assert support,('Uncovered retained end',wid,i,side,role)
            retained_rows.append(dict(id=f'{wid}/retained{i}/{side}',wire=wid,segment=i,side=side,role=role,point_world_mm=e['point_world_mm'],restraint=support))
    expected=[f"{r['wire']}/retained{e['segment_index']}/{e['side']}" for r in retained['rows'] for e in r['nominal_geometry_endpoints']]
    exact_cover(expected,retained_rows);assert len(retained_rows)==40
    return rows+retained_rows


def run():
    tick=time.monotonic();files={};data={}
    def read(name):
        f=OUT/(name+'.json');files[name]=f;data[name]=json.loads(f.read_text());return data[name]
    names=['remaining25-interface-allocation','remaining25-restraint-space','remaining25-saddle-roots','current-upper-operating-roots',
        'local-source-retention-roots','current-retained-endpoints','retained19-current-end-bindings','retained-feed-restraints-checks']
    args=[read(n) for n in names]
    assert not args[1]['errors'] and not args[1]['failed_groups']
    assert args[3]['accepted']==38 and not args[3]['errors']
    assert not args[4]['errors'] and not args[7]['errors']
    fixed=compose_fixed(*args)
    contract=read('body36-current-contract');macro=read('body36-shared-macro-layout');base=read('body36-recovery-layout')
    assert not macro['remaining_wire_ids'] and all(not a['contacts'] and not a['errors'] for a in macro['attempts'])
    rows={r['wire']:r for r in contract['rows']};rows.update({r['wire']:r for r in macro['changed_rows']})
    routes={n:base['routes'][n] for n in macro['retained_route_ids']};routes.update(macro['qualified_changed_routes'])
    assert set(rows)==set(routes) and len(rows)==36
    body=[]
    for wid,r in sorted(rows.items()):
        route=routes[wid];p=route['parts']
        body.extend([dict(id=wid+'/body/start',wire=wid,role=r['loom']+'/fixed_boundary',point_world_mm=p[0]['start'],
            restraint=dict(group=r['existing_bundle_land'],owner=r['existing_fixed_support'],native_proof='current-source-supports.json')),
            dict(id=wid+'/body/end',wire=wid,role=r['receiver_role'],point_world_mm=p[-1]['end'],
            restraint=dict(group=r['receiver_role'].split('.')[0],owner=r['existing_fixed_support'],native_proof='current-operating-native-composition.json'))])
    register=read('harness-interfaces-plan');ids={r['id'] for r in register['body_conductors']}
    assert {r['wire'] for r in fixed+body}==ids and len(ids)==80
    for n in ['g1-rooted-carrier-plan','remaining-fixed-feed-checks','body36-fixed-restraint-coverage','current-source-supports',
        'current-operating-native-composition','local-source-retention-native/manifest','remaining-frame-saddles-native/manifest',
        'receiver-supports/manifest','u1-power-grips-checks','u1-power-grips-native','BUS-routes-checks','BUS-native-checks']:
        read(n)
    # Later native receipts replace declared old parents, not their wire paths.
    comp=data['current-operating-native-composition'];assert comp['physical_print_quantity']==14
    native=data['local-source-retention-native/manifest'];assert len(native['parts'])==5
    result=dict(status='ALL80_BODY_NETS_CURRENT_GUIDE_END_RESTRAINT_IDENTITY_MAP',fixed_net_count=44,body_fanout_net_count=36,
        logical_end_count=160,fixed_physical_guide_ends=fixed,body_fixed_boundary_ends=body,
        fixed_physical_guide_end_count=106,body_fixed_boundary_end_count=72,
        distinction='Body start boundaries are not extra cut ends. Moving factory portions and source-owned donor joins remain in their existing qualified loom recipes; physical cut ends are composed separately.',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in list(files.values())+[Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
        open=['Current assembled snapshot and local mounting sequence','Nominal scope stock selection','Final receipt/source integrity verification'])
    (OUT/'w5-current-end-coverage.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(nets=80,fixed_guide_ends=len(fixed),body_boundaries=len(body),seconds=result['worker_seconds'])))


if __name__=='__main__':run()

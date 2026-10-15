"""Compose unchanged-component and changed-curve evidence without reruns.

Old33whole curves were in both G1/5feed component gates. The three NEW whole
curves were tested against all12 same geometries by the current macro gate.
The ten other feeds have their own fresh full36 gate. Native/stock/W5 open.
"""
import hashlib,json,subprocess,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def unchanged_routes(old,current,base):
    def routes(m):
        q={n:base['routes'][n] for n in m['retained_route_ids']}
        return {**q,**m['qualified_changed_routes']}
    before,after=routes(old),routes(current)
    assert len(before)==33 and len(after)==36
    assert all(after[n]['parts']==r['parts'] for n,r in before.items()),'Changed inherited whole curve'
    added=set(after)-set(before)
    assert added=={'W004','W022','W069'}
    assert {r['wire'] for r in current['attempts']}==added
    assert all(not r['contacts'] and not r['errors'] for r in current['attempts'])
    return sorted(before),sorted(added)


def run():
    tick=time.monotonic();mf=OUT/'body36-shared-macro-layout.json';current=json.loads(mf.read_text())
    assert not current['remaining_wire_ids']
    parent=current['inherited_qualified_receipt']['git_commit'];path=mf.relative_to(ROOT).as_posix()
    raw=subprocess.check_output(['git','show',parent+':'+path],cwd=ROOT)
    variants={hashlib.sha256(b).hexdigest():b for b in (raw,raw.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))}
    old=json.loads(raw);bf=ROOT/current['inherited_receipt'];base=json.loads(bf.read_text())
    inherited,added=unchanged_routes(old,current,base)
    scopes=[];files=[mf,bf,Path(__file__)]
    for filename,status in [('g1-rooted-carrier-plan.json','G1_ROOTED_COMPONENT_GATE_CLEAR'),
                             ('remaining-fixed-feed-checks.json','FIVE_REMAINING_FIXED_FEEDS_COMPONENT_GATE_CLEAR')]:
        f=OUT/filename;q=json.loads(f.read_text());files.append(f)
        assert q['status']==status and not q['errors']
        assert len(q['components'])==6
        assert all(not r.get('contact') and not r.get('contacts') for r in q['components'])
        assert q['source_sha256'][path] in variants,'Historical raw scene bytes not recovered exactly'
        for n,h in q['source_sha256'].items():
            if n==path:continue
            assert SHA(ROOT/n)==h,('Changed component scope input',n)
        assert current['source_sha256'][f.relative_to(ROOT).as_posix()]==SHA(f),'Changed material proof used by macro'
        scopes.append(dict(receipt=f.relative_to(ROOT).as_posix(),raw_source_macro_sha256=q['source_sha256'][path],
                           historical_source_commit=parent,raw_digest_recovered_exactly=True,old33whole_covered=True))
    for f in (OUT/'retained-feed-restraints-checks.json',OUT/'upper-fixed-feed-supports/manifest.json'):
        files.append(f)
    feeds=json.loads(files[-2].read_text());native=json.loads(files[-1].read_text())
    assert feeds['status']=='TEN_FEED_COMMON_COMPONENT_GATE_COMPLETE' and feeds['full_body_curves_accepted']
    assert len(feeds['restraints'])==10 and all(r['accepted_in_this_scope'] for r in feeds['restraints']) and not feeds['errors']
    assert feeds['source_sha256'][path]==SHA(mf)
    assert native['status']=='CURRENT_UPPER_FEED_NATIVE_COMPONENT_COMPLETE'
    assert SHA(ROOT/native['native'])==native['native_sha256']
    for receipt in (current,feeds,native):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    result=dict(status='CURRENT36_AND_TWENTY_RETAINED_ENDS_GEOMETRY_COVERAGE_COMPOSED',
        inherited_whole_ids=inherited,new_whole_ids=added,component_scopes=scopes,
        all12_new_support_components_used_in_changed_curve_gate=True,
        current_ten_feed_gate=True,retained_body_end_coverage_count=20,
        upper_native_complete=True,receiver_native_complete=False,full_stock_complete=False,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
        scope='Geometry coverage ONLY: old33+new3 curves, G1fiveends/G2fourends/FL_Goneend/tenrailfeeds. Other10 retained ends,25guide interfaces/native/stock/service still OPEN.')
    (OUT/'body36-fixed-restraint-coverage.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['worker_seconds'])


if __name__=='__main__':run()

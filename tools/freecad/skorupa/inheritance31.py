"""Compare 260 inherited v30/v31 BReps, excluding four intentional changes."""
import json
from inheritance30 import ROOT, compare_text, sha


def main():
    old,new=(ROOT/'hardware/skorupa'/r for r in ['v30','v31'])
    plans=[json.loads((p/'assembly-plan.json').read_text()) for p in [old,new]]
    for p,plan in zip([old,new],plans):
        assert sha(p/plan['cad_filename'])==plan['source_sha256']
        assert json.loads((p/'shape-cache/index.json').read_text())['source_sha256']==plan['source_sha256']
    names={r['name'] for r in plans[0]['components']}-{'Pololu','Part__Feature038','ShellMounted20','TailBridge29'}
    assert len(names)==260
    rows=[]
    for name in sorted(names):
        files=[p/'shape-cache'/(name+'.brep') for p in [old,new]]
        result=compare_text(*(p.read_text(encoding='ascii') for p in files))
        rows.append(dict(name=name,source_BRep_sha256=sha(files[0]),target_BRep_sha256=sha(files[1]),**result))
    report=dict(source_sha256=plans[1]['source_sha256'],inherited_from_sha256=plans[0]['source_sha256'],verified=True,
        absolute_tolerance=1e-9,relative_tolerance=1e-12,byte_identical=sum(r['byte_identical'] for r in rows),
        max_absolute_delta=max(r['max_absolute_delta'] for r in rows),inherited_parts=len(rows),parts=rows,scope=__doc__)
    (new/'inheritance-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2))


if __name__=='__main__':main()

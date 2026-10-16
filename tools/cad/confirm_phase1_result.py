"""Confirm one complete nominal result; fixed denominator and previous evidence.

Electrical E3 is deliberately not admitted by this packaging-only confirmer.
"""
import argparse,json,time
from datetime import datetime,timezone
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from release_check import verify


ALLOWED={'K1','K2','K3','M4','A2','A3'}


def validate_score(score,result):
    assert result in ALLOWED and score['fixed_total']==20
    ids=score['confirmed_result_ids'];assert len(ids)==len(set(ids))==score['result_count']
    assert score['result_percent']==5*len(ids) and result not in ids
    return ids+[result]


def run(result,file):
    file=file.resolve();assert file.is_relative_to(ROOT.resolve())
    tick=time.monotonic();score_file=BASE/'current-phase1-score.json';score=json.loads(score_file.read_text())
    assert SHA(ROOT/score['evidence'])==score['evidence_sha256'],'Previous confirmed result evidence changed'
    ids=validate_score(score,result);manifest=json.loads(file.read_text())
    assert manifest['result_id']==result and manifest[result+'_complete'] and manifest['selected']
    assert manifest['readiness']=='prototype' and manifest['physical_pass'] is False
    receipt=verify(ROOT,manifest);assert receipt['integrity_ok'],receipt
    selection=json.loads((ROOT/manifest['selection']).read_text())
    assert selection['result_id']==result and selection[result+'_complete'] and selection['selected']
    old={k:score[k] for k in ('new_result','evidence','evidence_sha256')}
    score.update(confirmed_result_ids=ids,result_count=len(ids),result_percent=5*len(ids),change_pp=5,new_result=result,
        previous_evidence=old,evidence=file.relative_to(ROOT).as_posix(),evidence_sha256=SHA(file),
        checked_utc=datetime.now(timezone.utc).isoformat(),verification_seconds=round(time.monotonic()-tick,3),
        verification_basis=manifest['scope']+' Required file hashes verified; nominal prototype preparation, NOT physical PASS.')
    score_file.write_text(json.dumps(score,indent=2)+'\n')
    print(json.dumps(dict(result=result,count=len(ids),fixed_total=20,percent=score['result_percent'],seconds=score['verification_seconds'])))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('result',choices=sorted(ALLOWED));p.add_argument('manifest',type=Path);a=p.parse_args();run(a.result,a.manifest)

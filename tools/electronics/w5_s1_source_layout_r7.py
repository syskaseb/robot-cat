"""Separate whole terminal approaches, preserving all received bus mouths.

R6's upper left/down and right/down arcs crossed each other. Turn the RL
source downward at the outer north lane before turning toward its terminal;
give the right return a separate east column with a late inward S offset.
Carrier entries, the short AUX branch, exact TE datums and P0 do not move.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math
import w5_s1_source_layout_r6 as parent
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import X,Y,Z,mul,norm
from servo_fuse_inputs_r1 import save,sha
ROOT=parent.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r7'

def layout():
    rows=parent.layout()
    c=CentreLine([-69,7,135.5],mul(Y,-1))
    c.arc(Z);c.line([-69,-18.2,182]);c.arc(mul(X,-1))
    c.line([-101.8,-18.2,207.2]);c.arc(Y);c.line([-127,107.2,207.2]);c.arc(X)
    c.line([parent.LEFT-50.4,132.4,207.2]);c.arc(mul(Z,-1))
    c.line([parent.LEFT-25.2,132.4,166.5]);c.arc(mul(Y,-1));c.arc(mul(Z,-1))
    c.line([parent.LEFT-25.2,82,parent.EZ+25.2]);c.arc(X)
    paths={'W067':c}
    c=CentreLine([-61.5,7,135.5],mul(Y,-1))
    c.arc(X);c.arc(Z);c.line([-11.1,-18.2,174]);c.arc(X)
    c.line([parent.RIGHT+12,-18.2,199.2]);c.arc(Y)
    c.line([parent.RIGHT+37.2,56.8,199.2]);c.arc(mul(Z,-1))
    c.shift([-12,0,0]);c.line([parent.RIGHT+25.2,82,parent.EZ+25.2]);c.arc(mul(X,-1))
    paths['W068']=c
    for row in rows:
        if row['wire'] not in paths:continue
        c=paths[row['wire']]
        assert norm([x-y for x,y in zip(c.p,row['end'])])<1e-7
        row['edges']=c.edges;row['exposed_path_mm']=sum(e['length_mm'] for e in c.edges)
        row['nominal_trial_blank_mm']=math.ceil((row['exposed_path_mm']+52.73)/10)*10
    return rows

def main():
    begin=datetime.now(timezone.utc)
    p=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r6/checks.json'
    r=json.loads(p.read_text(encoding='utf-8'))
    assert len(r['hits'])==15 and not r['errors']
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    source=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r6/intent.json'
    record=json.loads(source.read_text(encoding='utf-8'))
    record.update(routes=layout(),new_four_S1_trial_mm=sum(q['nominal_trial_blank_mm'] for q in layout()[:4]),
        status='SHARED_TERMINAL_APPROACHES_CANDIDATE_UNSELECTED',
        received_parent={'receipt':p.relative_to(ROOT).as_posix(),'pairs':130,'hits':15,'worker_wall_seconds':r['worker_wall_seconds']})
    record['source_sha256'].update({q.relative_to(ROOT).as_posix():sha(q) for q in [Path(__file__),source,p,
        ROOT/'tools/electronics/w5_s1_source_layout_r6.py']})
    end=datetime.now(timezone.utc)
    record.update(started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds())
    assert not (OUT/'intent.json').exists();OUT.mkdir(parents=True,exist_ok=True);save(OUT/'intent.json',record)
    print('SHARED_SOURCE_TERMINAL_APPROACHES',[(r['wire'],r['nominal_trial_blank_mm']) for r in layout()],flush=True)

if __name__=='__main__':main()

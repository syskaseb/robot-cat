"""One diagonal left approach avoids the actual RL holder and W064.

Keep R7's received carrier entries and clear right approach. The left upper
turn uses a distinct X column; a diagonal X/Y offset reaches the final
column north of W064 before the shared lower S bend. No fuse holder moves.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math
import w5_s1_source_layout_r7 as parent
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import X,Y,Z,mul,norm
from servo_fuse_inputs_r1 import save,sha
ROOT=parent.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r8'

def layout():
    rows=parent.layout();left=parent.parent.LEFT;ez=parent.parent.EZ
    c=CentreLine([-69,7,135.5],mul(Y,-1))
    c.arc(Z);c.line([-69,-18.2,182]);c.arc(mul(X,-1))
    c.line([-101.8,-18.2,207.2]);c.arc(Y);c.line([-127,107.2,207.2]);c.arc(X)
    c.line([left-62.4,132.4,207.2]);c.arc(mul(Y,-1));c.arc(mul(Z,-1))
    c.shift([12,10,0]);c.line([left-25.2,92,128]);c.shift([0,-10,0])
    c.line([left-25.2,82,ez+25.2]);c.arc(X)
    row=rows[2];assert norm([x-y for x,y in zip(c.p,row['end'])])<1e-7
    row['edges']=c.edges;row['exposed_path_mm']=sum(e['length_mm'] for e in c.edges)
    row['nominal_trial_blank_mm']=math.ceil((row['exposed_path_mm']+52.73)/10)*10
    return rows

def main():
    begin=datetime.now(timezone.utc)
    p=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r7/checks.json'
    r=json.loads(p.read_text(encoding='utf-8'));assert len(r['hits'])==11 and not r['errors']
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    source=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r7/intent.json'
    record=json.loads(source.read_text(encoding='utf-8'))
    record.update(routes=layout(),new_four_S1_trial_mm=sum(q['nominal_trial_blank_mm'] for q in layout()[:4]),
        status='DIAGONAL_TERMINAL_APPROACH_CANDIDATE_UNSELECTED',
        received_parent={'receipt':p.relative_to(ROOT).as_posix(),'pairs':r['pairs'],'hits':11,'worker_wall_seconds':r['worker_wall_seconds']})
    record['source_sha256'].update({q.relative_to(ROOT).as_posix():sha(q) for q in [Path(__file__),source,p,
        ROOT/'tools/electronics/w5_s1_source_layout_r7.py']})
    end=datetime.now(timezone.utc);record.update(started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds())
    assert not (OUT/'intent.json').exists();OUT.mkdir(parents=True,exist_ok=True);save(OUT/'intent.json',record)
    print('SOURCE_DIAGONAL_APPROACH',[(q['wire'],q['nominal_trial_blank_mm']) for q in layout()],flush=True)

if __name__=='__main__':main()

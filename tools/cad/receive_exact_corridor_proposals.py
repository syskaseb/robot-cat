"""Full whole-route receipt for the three saved proposals, not a reroute.

The saved interrupted planning receipt is candidate geometry only. Require a
new complete actual-world gate before any whole route/native/phase credit.
"""
import copy,hashlib,json,subprocess
from pathlib import Path
from shared_body36_macro_routes import packed_front_prefixes
from plan_body36_receiver_space import P
import check_shared_body36_macro as receiver
import joint_clearance_corridors as dispatch

def run(commit):
    ff=P.OUT/'exact-corridor-plan.json';path=ff.relative_to(P.ROOT).as_posix()
    raw=subprocess.check_output(['git','show',commit+':'+path],cwd=P.ROOT)
    assert hashlib.sha256(raw).hexdigest()==P.SHA(ff),'Saved proposal geometry changed'
    saved=json.loads(raw);assert set(saved['candidates'])=={'W019','W022','W030'}
    original=receiver.prepare
    def prepare():
        targets,wires,pins,grips=original()
        pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (ff,Path(__file__))})
        return targets,wires,pins,grips
    def choose(parent,base):
        rows={r['wire']:copy.deepcopy(r) for r in base['rows']}
        rows.update({r['wire']:copy.deepcopy(r) for r in parent['changed_rows']})
        front=packed_front_prefixes(rows)
        for n in ('W004','W019','W030'):
            source=rows[n].get('source_parts') or [rows[n]['source_land']]
            after=rows[n].get('source_after_jacket_first5_mm',source[1:])
            rows[n]['source_after_jacket_first5_mm']=[*after,*front[n][len(source):]]
            rows[n]['source_parts']=front[n];rows[n]['free_start']=front[n][-1]['end'];rows[n]['source_free_axis']=[0,0,1]
        return rows,saved['candidates'],saved['failures']
    receiver.prepare=prepare;dispatch.plan=choose
    receiver.run(saved['parent_commit'],joint_clearance=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--proposal-commit',required=True);run(p.parse_args().proposal_commit)

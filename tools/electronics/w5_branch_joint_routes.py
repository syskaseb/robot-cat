"""Route the jointly allocated leg departures, reopening only affected nets.

The upstream reservations are planning keep-outs, not physical conductors.
Unchanged accepted paths remain pinned; five unresolved central nets stay open.
"""
from pathlib import Path
import json
import w5_coupled_corridors_r3 as prior

ROOT=prior.base.ROOT
PLAN=ROOT/'hardware/electronics/full-cat/w5-branch-space-plan-r1/checks.json'
OLD=ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r3/checks.json'
plan=json.loads(PLAN.read_text(encoding='utf-8'))
old=json.loads(OLD.read_text(encoding='utf-8'))
assert plan['success'] and len(plan['choices'])==24
old_by={r['wire']:r for r in old['accepted']}
changed_prefix={w for w,c in plan['choices'].items() if w in old_by and c['prefix']!=old_by[w]['a']}
todo=set(plan['reopen_accepted_routes'])|changed_prefix|{w for w in plan['choices'] if w not in old_by}
retained=[r for r in old['accepted'] if r['wire'] not in todo]

source=prior.source
source=source.replace("    aa=[prefix(row['a_datum'],row['wire'],o) for o in (['up'] if upper else ['up','down','left','right'])]",
    "    aa=[PLAN_CHOICES[row['wire']]['prefix']] if row['wire'] in PLAN_CHOICES else [prefix(row['a_datum'],row['wire'],o) for o in (['up'] if upper else ['up','down','left','right'])]")
source=source.replace('    checks=0', '    current_wire=None\n    checks=0')
source=source.replace('            if key in skip or not shape.BoundBox.intersect(other.BoundBox):continue',
    "            if key in skip or key=='RESERVED/'+str(current_wire) or not shape.BoundBox.intersect(other.BoundBox):continue")
source=source.replace('    accepted=[]; unresolved=[]; errors=[]', '''    pins += [PLAN,OLD,WRAPPER]
    for r in RETAINED:
        p=OLD.parent/(r['wire']+'_WORLD.brep');fixed[r['wire']]=Part.read(str(p));pins.append(p)
    for w in PLAN_CHOICES:
        p=PLAN.parent/(w+'_RESERVATION.brep');fixed['RESERVED/'+w]=Part.read(str(p));pins.append(p)
    save(OUT/'allocation.json',dict(reopened=sorted(TODO),changed_prefix=sorted(CHANGED_PREFIX),
        retained=[r['wire'] for r in RETAINED],choices=PLAN_CHOICES,
        reservation_hits_are_planning_constraints_not_material_collisions=True))
    accepted=list(RETAINED); unresolved=[]; errors=[]''')
source=source.replace('    for row in ([] if body_hits else rows):',
    "    for row in ([] if body_hits else [r for r in rows if r['wire'] in TODO]):\n        current_wire=row['wire']")
source=source.replace("status='COUPLED49_CORRIDOR_PLANNING_NOT_SELECTED'", "status='JOINT_BRANCH_ROUTES_NOT_SELECTED'")
ctx=dict(__name__='branch_joint_definition',__file__=prior.base.__file__,
    PLAN_CHOICES=plan['choices'],PLAN=PLAN,OLD=OLD,WRAPPER=Path(__file__),
    RETAINED=retained,TODO=todo,CHANGED_PREFIX=changed_prefix)
exec(compile(source,prior.base.__file__,'exec'),ctx)
ctx['contract']=prior.contract
ctx['OUT']=ROOT/'hardware/electronics/full-cat/w5-branch-joint-routes-r1'
if __name__=='__main__':ctx['main']()

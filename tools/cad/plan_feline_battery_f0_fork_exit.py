"""Separate the two POST branches instead of converging them near F0.

Only custom exit changes: inwardY plus foreX, away from both RL_G's
X50.75/Y58 witness and the incoming factory branch atX89.66.
"""
import itertools,math
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_battery_f0_inward_exit import construction as previous
from plan_feline_battery_f0_joint import path
from plan_feline_n01_shared import pipe
from receive_feline_source_joint import receive


def construction(parts,ends):
    actors,recipes,bad,names,datums,extra=previous(parts,ends)
    assert [k for k,v in bad.items() if not v['ok']]==['W076_factory|W076_custom_prefix']
    p=datums['POST2'];direction=[-math.cos(math.pi/6),-math.sin(math.pi/6),0]
    recipes['W076_custom_prefix']=path(p,[0,0,-1],[('turn',direction),('line',9)],25.2)
    actors['W076_custom_prefix']=pipe(recipes['W076_custom_prefix']['parts'],2.1)
    own={}
    for a,b in itertools.combinations(actors,2):
        minimum=bad[a+'|'+b]['minimum_mm'];s,t=actors[a],actors[b]
        gap=s.distToShape(t)[0];c=s.common(t);assert c.isNull() or c.isValid()
        own[a+'|'+b]=dict(bad[a+'|'+b],ok=gap>=minimum-1e-6 and c.Volume<1e-5,gap_mm=gap,common_mm3=c.Volume)
    extra.pop('custom_exit_clock')
    extra.update(rejected_converging_branch_pair='W076_factory|W076_custom_prefix',
        custom_exit_direction=direction,full_R25_2_and9mm_retained=True,
        builder_dependency_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (
            ROOT/'tools/cad/plan_feline_battery_f0_inward_exit.py',ROOT/'tools/cad/plan_feline_battery_f0_joint.py')})
    return actors,recipes,own,names,datums,extra


if __name__=='__main__':receive(construction,Path(__file__),'n01-BAT-F0-fork-exit.json')

"""Resume refinement without repeating completed poses or sweeping overlength.

Analytical fillet length is exact for the same line/arc construction. Only
length-feasible wires receive a solid sweep and material intersection check.
Bound the joint endpoint assignment as well as the outer search loop.
"""
from pathlib import Path
from itertools import product
import json
import w5_central_space_solver_r3 as prior
from w5_path_length import recipe_length

ROOT=prior.ROOT
PROGRESS=ROOT/'hardware/electronics/full-cat/w5-central-space-solver-r3/progress.json'

def placements(targets):
    old=json.loads(PROGRESS.read_text(encoding='utf-8'))
    key=lambda p:(tuple(p['g1_centre']),tuple(p['g2_centre']),p['floor'],p['direction'])
    visited={key(r['placement']) for r in old['attempts']}
    return [p for p in prior.placements(targets) if key(p) not in visited]

source=prior.source
needle='                path,whole=from_recipe(A,Part,recipe_full)'
assert needle in source
source=source.replace(needle,'''                if recipe_length(recipe_full)+19>150:
                    last_reasons.append('nominal_above150mm');continue
                path,whole=from_recipe(A,Part,recipe_full)
                assert abs(path.Length-recipe_length(recipe_full))<1e-6''')
source=source.replace('            def joint(i):\n                if i==len(ordered):return True',
    '            joint_nodes=0\n            def joint(i):\n                nonlocal joint_nodes\n                joint_nodes+=1\n                if joint_nodes>512 or time.monotonic()-tic>480:return False\n                if i==len(ordered):return True')
source=source.replace("blocked='no_mutually_clear_end_assignment'", "blocked='joint_search_bound' if joint_nodes>512 or time.monotonic()-tic>480 else 'no_mutually_clear_end_assignment'")
source=source.replace("pins += [", "pins += [ROOT/'tools/electronics/w5_central_space_solver_r4.py',ROOT/'tools/electronics/w5_path_length.py',ROOT/'tools/electronics/w5_rounded_path.py',ROOT/'hardware/electronics/full-cat/w5-central-space-solver-r3/progress.json',",1)
ctx=dict(__name__='central_space_r4_definition',__file__=prior.prior.base.__file__,product=product,recipe_length=recipe_length)
exec(compile(source,prior.prior.base.__file__,'exec'),ctx)
ctx['placements']=placements
ctx['OUT']=ROOT/'hardware/electronics/full-cat/w5-central-space-solver-r4'
if __name__=='__main__':ctx['main']()

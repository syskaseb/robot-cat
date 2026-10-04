"""Separate the two front knee corridors from their ankle corridors.

Only FL2/FR2 move to the parallel outer lane; inherit the other ten complete
R2 corridors and their owner checks. Recheck changed-to-all mutual pairs.
"""
from pathlib import Path
parent = Path(__file__).with_name('w5_leg_corridors_r2.py')
wrapper = parent.read_text(encoding='utf-8')
tail = "exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns = dict(__file__=str(parent),__name__='r2_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code = ns['code'].replace("w5-leg-corridors-r2'", "w5-leg-corridors-r3'", 1)
old="x=min(-140,lead.x-25) if front else max(182,lead.x+25)"
assert code.count(old)==1
code=code.replace(old,old+"\n        if row['loom'] in ('FL2','FR2'):x=-152")
code=code.replace("previous_folder=ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r1'",
                  "previous_folder=ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r2'")
code=code.replace("assert len(previous['hits'])==4 and all(h['loom'].endswith('1') for h in previous['hits'])",
                  "assert len(previous['hits'])==2 and {h['loom'] for h in previous['hits']}=={'FL2','FR2'}")
code=code.replace("assert len(previous['errors'])==4 and all(h['loom'].endswith('2') for h in previous['errors'])",
                  "assert not previous['errors']")
code=code.replace("len(previous['routes'])==8", "len(previous['routes'])==12")
code=code.replace("if r['loom'].endswith('3'):","if r['loom'] not in ('FL2','FR2'):")
code=code.replace("if row['loom'].endswith('3'):","if row['loom'] not in ('FL2','FR2'):")
code=code.replace("if rows[i]['loom'].endswith('3') and rows[j]['loom'].endswith('3'):continue",
                  "if rows[i]['loom'] not in ('FL2','FR2') and rows[j]['loom'] not in ('FL2','FR2'):continue")
code=code.replace("inherited_unchanged_looms=['FL3','FR3','RL3','RR3']",
                  "inherited_unchanged_looms=[r['loom'] for r in planned if r['loom'] not in ('FL2','FR2')]")
code=code.replace("pins += [ROOT/'tools/electronics/w5_leg_corridors_r1.py',",
                  "pins += [ROOT/'tools/electronics/w5_leg_corridors_r1.py',ROOT/'tools/electronics/w5_leg_corridors_r2.py',")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

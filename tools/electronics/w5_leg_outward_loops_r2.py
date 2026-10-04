"""Turn above Deck/P0 after the original six-mm straight cage entries.

R1 was stopped on an exact P0 bridge collision. This is a single whole-family
change, not another trial of the same under-Deck geometry. All checked owners,
real R10 half-turns, unchanged V paths and mutual checks remain in the builder.
"""
from pathlib import Path
import json
import w5_leg_outward_loops_r1 as previous
from servo_fuse_inputs_r1 import save, sha

ROOT=previous.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-leg-outward-loops-r2'
source=Path(previous.__file__).read_text(encoding='utf-8')
assert source.count('-20*math.sin(theta)')==1
assert source.count('-10*math.sin(theta)')==2
source=source.replace('-20*math.sin(theta)','+20*math.sin(theta)')
source=source.replace('-10*math.sin(theta)','+10*math.sin(theta)')
assert source.count('high=(137 if')==1
source=source.replace('high=(137 if','high=(147 if').replace("else 149)+3*rank","else 159)+3*rank")
context=dict(__file__=previous.__file__,__name__='upward_loop_definition')
exec(compile(source,previous.__file__,'exec'),context)
context['OUT']=OUT
plan=context['plan']


def main():
    context['main']()
    p=OUT/'checks.json'
    receipt=json.loads(p.read_text(encoding='utf-8'))
    receipt['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    receipt['upward_half_turn']=True
    receipt['rejected_predecessor']='w5-leg-outward-loops-r1/execution-observation.json'
    receipt['source_sha256']['hardware/electronics/full-cat/w5-leg-outward-loops-r1/execution-observation.json']=sha(
        ROOT/'hardware/electronics/full-cat/w5-leg-outward-loops-r1/execution-observation.json')
    save(p,receipt)


if __name__=='__main__': main()

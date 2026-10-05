"""BUS flight149.5 clears the received AUX witness ending at146.75.

Same registered ports and whole900mm factory cable. R2's actual common
at X44.68..47.78/Y13.05..15.96 determines this2mm correction.
"""
import json
import math
from pathlib import Path
import w5_bus_factory900 as B
from w5_bus_factory900_r2 import recipe as previous

OUT=B.scope.ROOT/'hardware/electronics/full-cat/w5-bus-factory900-r3'


def recipe(family,source):
    row=previous(family,source)
    # Raise only the flight and the connecting vertical straights. End ports stay.
    for i,e in enumerate(row['edges']):
        if i==2:
            e['end'][2]+=2;e['length_mm']+=2
        elif 3<=i<len(row['edges'])-1:
            e['start'][2]+=2;e['end'][2]+=2
            if 'center' in e:e['center'][2]+=2
            if 'mid' in e:e['mid'][2]+=2
        elif i==len(row['edges'])-1:
            e['start'][2]+=2;e['length_mm']+=2
    row['body_mm']+=4;row['nominal_mm']+=4
    row['trial_blank_mm']=math.ceil((row['body_mm']+71)/10)*10
    row['remaining_nominal900_mm']=900-row['trial_blank_mm']
    row['source_end_straight_mm']+=2
    return row


def main():
    B.OUT=OUT;B.recipe=recipe;B.main()
    p=OUT/'checks.json';proof=json.loads(p.read_text(encoding='utf-8'))
    for s in (Path(__file__),B.scope.ROOT/'tools/electronics/w5_bus_factory900_r2.py'):
        proof['source_sha256'][s.relative_to(B.scope.ROOT).as_posix()]=B.sha(s)
    proof['changed_interface']='BUS flight149.5mm; actual AUX witness, ports unchanged'
    B.save(p,proof)


if __name__=='__main__':main()

"""One BUS corridor between AUX146.75 and head feeds150.45.

2mm OD centre148.6 leaves nominal0.85mm on each side of these actual
material limits. This is a prototype clearance, not delivered cable fit.
"""
import json
import math
from pathlib import Path
import w5_bus_factory900 as B
from w5_bus_factory900_r2 import recipe as previous

OUT=B.scope.ROOT/'hardware/electronics/full-cat/w5-bus-factory900-r4'


def recipe(family,source):
    row=previous(family,source);rise=1.1
    for i,e in enumerate(row['edges']):
        if i==2:
            e['end'][2]+=rise;e['length_mm']+=rise
        elif 3<=i<len(row['edges'])-1:
            for key in ('start','end','mid'):
                if key in e:e[key][2]+=rise
        elif i==len(row['edges'])-1:
            e['start'][2]+=rise;e['length_mm']+=rise
    row['body_mm']+=2*rise;row['nominal_mm']+=2*rise
    row['trial_blank_mm']=math.ceil((row['body_mm']+71)/10)*10
    row['remaining_nominal900_mm']=900-row['trial_blank_mm']
    row['source_end_straight_mm']+=rise
    return row


def main():
    B.OUT=OUT;B.recipe=recipe;B.main()
    p=OUT/'checks.json';proof=json.loads(p.read_text(encoding='utf-8'))
    for s in (Path(__file__),B.scope.ROOT/'tools/electronics/w5_bus_factory900_r2.py'):
        proof['source_sha256'][s.relative_to(B.scope.ROOT).as_posix()]=B.sha(s)
    proof['corridor']=dict(lower_material_limit_mm=146.75,upper_material_limit_mm=150.45,
        centre_z_mm=148.6,nominal_diameter_mm=2,nominal_margin_each_side_mm=.85,
        delivered_OD_unknown=True,physical_pass=False)
    B.save(p,proof)


if __name__=='__main__':main()

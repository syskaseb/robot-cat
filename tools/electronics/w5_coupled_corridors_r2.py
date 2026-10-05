"""Use the measured saved W067 envelope to reserve the full DATA row.

The first row ended at Y=-20; W067 reaches -20.3 there. Move both DATA
rows outward3mm, leaving a2.7mm nominal envelope gap, without changing Z.
No completed routing solution exists in r1; its body-conflict result is kept.
"""
from pathlib import Path
import w5_coupled_corridors as base

original=base.contract
def contract():
    bodies,rows,preserved,pins=original()
    for name,box in bodies.items():
        if name.startswith('D_'):
            dy=3 if name.endswith('L') else -3
            box[1]+=dy;box[4]+=dy
    for row in rows:
        for side in ('a','b'):
            if row[side+'_end'].startswith('D_'):
                p=row[side+'_datum']['point_mm'];p[1]+=3 if p[1]>0 else -3
    pins += [Path(__file__),base.ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r1/checks.json',
             base.ROOT/'hardware/electronics/full-cat/w5-space-plan-inputs-r1/space.json']
    return bodies,rows,preserved,pins

base.contract=contract
base.OUT=base.ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r2'
if __name__=='__main__':base.main()

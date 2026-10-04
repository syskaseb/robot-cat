"""Whole D/G escape at cage height, rising beyond crowded central material.

The lower-family attempt struck immutable P0 supports and was stopped early.
Keep all bought blocks, DATA grips, 12V and loom-end datums. Do not repeat the
below-Pi traverses. Actual contacts with Deck/Cover remain rejected, not waived.
"""
from pathlib import Path
import json
import w5_leg_lower_fanouts_r1 as base
import w5_source_grips_native_r1 as owners_module
from servo_fuse_inputs_r1 import save, sha
ROOT=base.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-leg-escape-fanouts-r1'


def plan(rows):
    result=[]
    for old in rows:
        row=dict(old)
        if row['role']=='V': result.append(row); continue
        leg=row['loom'][:2]; side=1 if leg.endswith('L') else -1
        outward=-1 if leg.startswith('F') else 1
        peers=sorted((q for q in rows if q['loom'][:2]==leg and q['role']==row['role']),key=lambda q:q['waypoints_mm'][0][0])
        index=next(i for i,q in enumerate(peers) if q['wire']==row['wire'])
        rank=index if outward<0 else 2-index
        end=list(row['waypoints_mm'][0]); end[1]=side*30.5
        tail=list(row['waypoints_mm'][-1])
        lane=side*(14.5 if row['role']=='D' else 8.5)
        escape=tail[0]-outward*25
        high=(137 if row['role']=='D' else 149)+3*rank
        row['waypoints_mm']=[end,[end[0],lane,end[2]],[escape,lane,end[2]],
            [escape,lane,high],[tail[0],lane,high],[tail[0],tail[1],high],tail]
        row['body_entry_tangent']=[0,-side,0]
        row['ground_orientation_180_same_footprint']=False
        result.append(row)
    assert len(result)==36
    return result


def main():
    original=owners_module.current_owners
    def with_hoods(A,Part):
        owners,pins=original(A,Part)
        for label,rel in (
            ('SourceWestHood','hardware/electronics/full-cat/w5-source-roof-native-r3/WestHood_WORLD.brep'),
            ('SourceEastHood','hardware/electronics/full-cat/w5-source-roof-native-r5/EastHood_WORLD.brep')):
            p=ROOT/rel; assert p.is_file(); owners[label]=Part.read(str(p)); pins.append(p)
        for p in (ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r3').glob('*WORLD.brep'):
            if p.name.startswith(('Bolt','Nut','Washers')):
                owners['SourceHoodHardware/'+p.stem]=Part.read(str(p)); pins.append(p)
        return owners,pins
    owners_module.current_owners=with_hoods
    base.OUT=OUT; base.plan=plan
    base.main()
    p=OUT/'checks.json'; receipt=json.loads(p.read_text(encoding='utf-8'))
    receipt['status']=receipt['status'].replace('LOWER_FANOUT','ESCAPE_FANOUT')
    receipt['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    receipt['all_new_source_hoods_included']=True
    receipt['earlier_lower_attempt_rejected_without_full_check']=True
    save(p,receipt)


if __name__=='__main__': main()

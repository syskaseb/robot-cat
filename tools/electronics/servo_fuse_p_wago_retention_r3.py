"""Retain three clear R1 straps and the clear changed RL R2 strap.

Do not repeat their geometry checks or retain the new rejected FL R2 head.
Mixed whole strap bounding envelopes are disjoint, so the retained clear
body/Deck/route checks cover the mixed configuration without pair waivers.
All lever contacts remain explicit bench-first/removable-strap constraints.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,itertools
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    start=datetime.now(timezone.utc);pins={}
    def read(rel):p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    source={i:read(f'hardware/electronics/full-cat/servo-fuse-p-wago-retention-r{i}/checks.json') for i in (1,2)}
    mapping=read('hardware/electronics/full-cat/servo-fuse-wago-map-r1/interface.json')
    assert len(source[1]['hits'])==4 and all(r['part'].startswith('RL_P_') for r in source[1]['hits'])
    assert len(source[2]['hits'])==1 and source[2]['hits'][0]['part']=='FL_P_Head'
    assert all(not j['errors'] for j in source.values())
    rows=[];boxes={};pairs=[]
    for block in mapping['blocks']:
        ident=block['id'];rev=2 if ident=='RL_P' else 1;j=source[rev]
        assert not any(r['part'].startswith(ident+'_') for r in j['hits'])
        row=next(r for r in j['blocks'] if r['id']==ident).copy()
        folder=f'hardware/electronics/full-cat/servo-fuse-p-wago-retention-r{rev}'
        shapes=[]
        for part in ('Bottom','Top','Left','Right','Head'):
            rel=f'{folder}/{ident}_{part}_DESIGN.brep';pins[rel]=sha(ROOT/rel);shapes.append(rel)
        row.update(static_source=f'{folder}/checks.json',geometry=shapes,static_contacts=0,
            actual_lever_motion_qualified=False,
            assembly='With power absent, strip and connect the four named wires on the loose block, fifthportNC empty. Close levers; position on Deck; thread/tighten body strap through both existing slots; dress source feed/input fans afterwards. Cut body strap before any later lever opening. Delivered lever seating/band tension inspected in phase2.',
            bank_removal='No WAGO lever opening or removal of this body strap. Keep all4conductors connected; use the explicit33TE/output-tie release sequence after its shared fit is accepted.')
        x,y,z=block['center_mm'];sy=row['plane_y_mm']
        boxes[ident]=[x-18,sy-2.25,103.8,x+18,sy+2.25,122.7]
        rows.append(row)
        for rel,h in j['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in pins:assert pins[rel]==h
            pins[rel]=h
        script=f'tools/electronics/servo_fuse_p_wago_retention_r{rev}.py';pins[script]=sha(ROOT/script)
    for left,right in itertools.combinations(boxes,2):
        a,b=boxes[left],boxes[right]
        disjoint=any(a[i+3]<=b[i] or b[i+3]<=a[i] for i in range(3))
        assert disjoint,(left,right)
        pairs.append(dict(first=left,second=right,bounded_whole_straps_disjoint=True))
    end=datetime.now(timezone.utc);out=ROOT/'hardware/electronics/full-cat/servo-fuse-p-wago-retention-r3'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'checks.json').exists()
    save(out/'checks.json',dict(status='FOUR_NATIVE_SLOT_STRAPS_STATIC_CLEAR_WITH_BENCH_PORT_SEQUENCE',
        selected=False,physical_pass=False,W5_complete=False,blocks=rows,ports=20,connected_ports=16,NC=4,
        changed_cross_strap_envelopes=boxes,changed_cross_strap_checks=pairs,static_contacts=0,errors=[],
        native_existing_slots=8,added_prints=0,added_fasteners=0,body_straps_installed=4,
        same_existing_fixed_lower_feed_grips=4,same_bank_insulation_grips=24,
        lever_contacts_preserved=True,whole_installed_lever_access_qualified=False,
        strap_removal_before_lever_operation=True,retained_configurations=['FL_P:R1','FR_P:R1','RL_P:R2','RR_P:R1'],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('P_WAGO_MIXED_FOUR_STATIC_CLEAR',len(pins),flush=True)

if __name__=='__main__':main()

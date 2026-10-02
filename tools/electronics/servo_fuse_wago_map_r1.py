"""All five project-labelled ports on four turned P junctions, no net remap.

Port1 parent factory lead remains an open routed interface. Mapping does
not silently count that route or full W5 as complete.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math
ROOT=Path(__file__).resolve().parents[2]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-wago-map-r1'
def main():
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'interface.json').exists()
    sources=[ROOT/'hardware/electronics/power-platform/leg-distribution-p0.json',
             ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json',
             ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11/checks.json',
             ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json']
    distribution,ledger,routes,quantities=[json.loads(p.read_text(encoding='utf-8')) for p in sources]
    assert distribution['connector']['sku']=='221-415' and distribution['connector']['ports']==5
    assert not routes['hits'] and not routes['errors'];byid={r['id']:r for r in ledger['conductors']}
    blocks=[];used=set()
    for leg in ('FL','FR','RL','RR'):
        spec=next(b for b in distribution['blocks'] if b['id']==leg+'_P')
        assert spec['net']==leg+'_P' and [r['slot'] for r in spec['ports']]==[1,2,3,4]
        base=-69 if leg.startswith('F') else 39;side=1 if leg.endswith('L') else -1
        ports=[]
        for slot in range(1,6):
            end=next((r['endpoint'] for r in spec['ports'] if r['slot']==slot),None)
            coordinate=[base+(slot-3)*6.75,side*49.5,113.5]
            connected=[r for r in ledger['conductors'] if leg+'_P.'+str(slot) in (r['a'],r['b'])]
            assert len(connected)==(1 if end else 0)
            row=connected[0] if connected else None
            if row:
                assert end in (row['a'],row['b']);assert row['id'] not in used;used.add(row['id'])
                wago_end=row['ends'][0 if row['a'].startswith(leg+'_P.') else 1]
                assert wago_end['sku']=='221-415' and not wago_end['double_wire_allowed'] and not wago_end['tin_allowed']
            if slot in (2,3,4):
                actual=routes['placements'][row['id']]['start']
                assert max(abs(a-b) for a,b in zip(actual,coordinate))<1e-7
            ports.append(dict(project_slot=slot,physical_position='world X ascending',prior_physical_slot=6-slot,
                entry_mm=coordinate,endpoint=end or 'NC',wire_id=row['id'] if row else None,
                routed_interface='servo-fuse-side-bank-r11' if slot in (2,3,4) else 'OPEN factory parent feed' if slot==1 else 'EMPTY',
                one_conductor=True,do_not_tin=True,strip_to_delivered_221415_marking=True))
        blocks.append(dict(id=leg+'_P',rotation_z_deg=180,center_mm=[base,side*40,113.5],
            labels='Project labels only, not printed manufacturer cage numbers. Relabel before inserting any lead.',ports=ports))
    assert len(blocks)==4 and len(used)==16 and sum(p['endpoint']=='NC' for b in blocks for p in b['ports'])==4
    tie=next(r for r in quantities['lines'] if r['id']=='tie:111-02370')
    cable=next(r for r in quantities['lines'] if r['id']=='p0:WIRE-INLET-BLACK12-P0')
    battery=byid['W001'];assert battery['nominal_selected_blank_mm']==140
    nominal=routes['planned_required_blank_mm']+battery['nominal_selected_blank_mm']
    assert nominal==2180 and cable['planning_quantity']==2 and cable['unit']=='m'
    end=datetime.now(timezone.utc)
    save(OUT/'interface.json',dict(status='PORT_MAP_COMPLETE_PARENT_FEEDS_OPEN',selected=False,W5_complete=False,physical_pass=False,
        connector='WAGO221-415',all_ports=20,connected_ports=16,unused_ports=4,blocks=blocks,
        open_parent_feeds=['W026','W037','W045','W053'],
        stock=dict(LAPP0107001_bank_blanks_mm=2040,battery_blank_mm=140,minimum_nominal_total_mm=nominal,
            selected_purchase_mm=2000,selected_stock_insufficient=True,candidate_purchase_m=math.ceil(nominal/1000),
            candidate_purchase_selected=False,actual_cuts_mm=None,T18I_selected_qty=tie['planning_quantity'],
            previous_installed_working=tie['installed'],new_bank_ties=24,provisional_working_total=tie['installed']+24,
            prior_working_count_not_final_census=True),
        assembly=['Disconnect battery first.','Turn each P block in place and relabel all five cages with this world-coordinate map.',
            'One unsoldered conductor per cage. Port5 stays empty; lever access and parent feed routing remain open.',
            'Do not reuse the old100mm branch limit. Dry-fit before cutting; electrical length assumptions must be updated on selection.'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},script_sha256=sha(Path(__file__)),
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(ports=20,connected=16,empty=4,nominal_LAPP_mm=nominal,parent_feeds_open=4)),flush=True)
if __name__=='__main__':main()

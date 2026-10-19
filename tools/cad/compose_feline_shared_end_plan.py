"""Overlay received shared mouths/grips without inventing unseen pinouts.

No final middle-route or cut-length approval. The four P309 balance branches
are explicitly separate from the123-portions/246-ends harness register.
"""
import copy
import json
import math
import time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def plus(a,b):return [x+y for x,y in zip(a,b)]
def scale(a,k):return [x*k for x in a]
def mv(r,p):return [sum(x*y for x,y in zip(row,p)) for row in r]


def station_ends(rows,models):
    bykey={(r['endpoint'],r['wire']):r for r in rows if r['group'].startswith('WAGO:')}
    count=0
    for ref,wires in models.items():
        for w in wires:
            r=bykey[w['endpoint'],w['wire']]
            r.update(point_mm=w['point_mm'],departure_axis=w['departure_axis'],jacket_grip9_mm=[w['grip_start_mm'],w['grip_end_mm']],
                minimum_R_mm=w['minimum_R_mm'],pose_status='CURRENT_SHARED_STATION_MOUTH_AND_FULL_GRIP',
                current_pose_basis='Complete shared54 static/mutual selection; project mouth, not supplier guarantee',
                received_prefix_R_mm=w.get('received_prefix_R_mm'),grip_length_mm=9,
                full_middle_route_accepted=False,supplier_datum_guaranteed=False)
            count+=1
    assert count==len(bykey) and len({(r['endpoint'],r['wire']) for r in rows if r['group'].startswith('WAGO:')})==count
    return count


def bank_end(row,recipe):
    q=recipe['point_mm'];d=recipe['departure_axis'];start=q;axis=d
    if recipe.get('grip_site')=='AFTER_BEND':
        start=plus(plus(q,scale(d,recipe['first_mm']+recipe['R_mm'])),scale(recipe['bend_unit'],recipe['R_mm']))
        axis=recipe['bend_unit']
    row.update(point_mm=q,departure_axis=d,jacket_grip9_mm=[start,plus(start,scale(axis,9))],
        minimum_R_mm=recipe['R_mm'],received_prefix_R_mm=recipe['R_mm'],
        pose_status='CURRENT_SHARED_BANK_MOUTH_FULL_GRIP',supplier_datum_guaranteed=False,
        full_middle_route_accepted=False,grip_length_mm=9)


def inline_end(row,recipe,sign):
    rotation=recipe['rotation_rows'];centre=recipe['centre_mm'];axis=mv(rotation,[sign,0,0]);mouth=plus(centre,mv(rotation,[21*sign,0,0]))
    assert row['point_mm'] is None,'Internal accounting end must not become an invented contact'
    row.update(jacket_routing_point_mm=mouth,jacket_departure_axis=axis,jacket_grip9_mm=[mouth,plus(mouth,scale(axis,9))],
        pose_status='CURRENT_SHARED_INLINE_JACKET_INTERNAL_ACCOUNTING_SEPARATE',supplier_datum_guaranteed=False,
        full_middle_route_accepted=False,grip_length_mm=9)


def balance_contract(ecad):
    rows=copy.deepcopy(ecad['balance_interface'])
    assert len(rows)==4 and {r['tap'] for r in rows}=={'BAT.B0','BAT.B1','BAT.B2','BAT.B3'}
    assert all(r['physical_GTech_cavity'] is None and r['ID_must_not_be_used'] for r in rows)
    return dict(branches=rows,not_in_existing_123_portions_or_246_ends=True,
        selected_alarm_unchanged=True,physical_GTech_pinout_assigned=False,
        branch_length_and_connector_envelope_known=False,delivery_measurement_required=True,
        routing_capacity_and_retention_not_yet_accepted=True)


def main():
    tick=time.monotonic();files=dict(base=OUT/'n01-current-246-end-register.json',shared=OUT/'n01-shared54-current.json',
        ecad=ROOT/'hardware/electronics/kicad-current/design.json')
    docs={n:json.loads(p.read_text()) for n,p in files.items()};shared=docs['shared']
    assert len(shared['chosen'])==54 and shared['current_occupied_station_end_count']==86
    for n,h in shared['source_sha256'].items():assert sha(ROOT/n)==h,n
    result=copy.deepcopy(docs['base']);rows=result['endpoints'];byid={r['id']:r for r in rows}
    assert len(rows)==246 and len(byid)==246
    count=station_ends(rows,shared['current_station_wire_ends']);assert count==86
    bank=[]
    for group,choice in shared['chosen'].items():
        if group.startswith('Bank:'):
            row=byid[group[5:]];bank_end(row,choice['recipe']);bank.append(row['id'])
    assert len(bank)==24
    for endpoint,sign in (('F_PWM.in',-1),('F_PWM.out',1)):
        matches=[r for r in rows if r['endpoint']==endpoint];assert len(matches)==1
        inline_end(matches[0],shared['chosen']['F_PWM_whole']['recipe'],sign)
    assert all(len(ids)==2 for ids in result['portions'].values())
    result.update(status='SHARED54_WAGO_BANK_INLINE_ENDS_RECONCILED_OTHER_INTERFACES_OPEN',selected=False,N01_complete=False,
        physical_pass=False,shared_station_updated=count,shared_bank_updated=bank,shared_inline_jackets_updated=2,
        balance_factory_contract=balance_contract(docs['ecad']),
        current_endpoint_pose_counts={status:sum(r['pose_status']==status for r in rows) for status in {r['pose_status'] for r in rows}},
        open=['Remaining source/bare/jacket boundaries and full grips','Common structural load paths and installation','All factory corridor capacities including separate four-tap P309 bundle'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-shared-end-plan.json',result)
    print(json.dumps(dict(station_ends=count,bank_ends=len(bank),inline_jackets=2,status=result['status'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()

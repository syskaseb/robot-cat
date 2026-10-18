"""All20selected distribution casings/occupied cavities, not only80body nets.

Seventeen current faces calibrated by multiple pinned CAD endpoints. Three
extra faces transfer exact legacy guides only after checking their source
casing face. Current KiCad physical labels take precedence over historical.
No full-route/stock/native or supplier-mouth acceptance follows from this map.
"""
import json
import math
import re
import time
from pathlib import Path
from compose_feline_n01_allocation import ROOT,OUT,sha


def compose():
    tick=time.monotonic();files={k:p for k,p in dict(packet=OUT/'n01-current-endpoint-packet-r3.json',
        modules=OUT/'n01-module-plan-r5.json',aux=OUT.parent/'aux-wiring-checkpoint/whole-layout-plan.json',
        ecad=ROOT/'hardware/electronics/kicad-current/design.json',
        stations=OUT.parent/'body-harness-checkpoint/leg-stations-plan.json').items()}
    p={k:json.loads(f.read_text()) for k,f in files.items()};groups={g['role']:g for g in p['modules']['groups']}
    aliases={'P_AUX':'P_AUX_CP2','G_AUX':'W3Ref_G_AUX_case','G1':'G1_CP2','G2':'G2_CP2','P_FRONT':'P_FRONT_new','P_SYS':'P_SYS_new'}
    refs=('D_FL','D_FR','D_RL','D_RR','FL_P','FL_G','FR_P','FR_G','RL_P','RL_G','RR_P','RR_G',
        'P_FRONT','P_REAR','P_SYS','G1','G2','P_AUX','G_AUX','G_TAIL')
    byref={ref:[] for ref in refs};body={}
    for e in p['packet']['endpoints']:
        if not e['group'].startswith('WAGO:'):continue
        ref=e['role'].rsplit('.',1)[0];assert ref in byref,ref
        body.setdefault(ref,[]).append(e)
    prototypes={};source_transfers=[]
    def physical(ref,number):
        # These2power rails deliberately retain logical port1 at physical5.
        # The map describes their already-transferred coordinates; use it for
        # calibration/index lookup ONCE, never move those coordinates again.
        mapping=p['stations']['stations'].get(ref,{}).get('logical_to_physical_common_rail_cavity',{})
        return int(mapping.get(str(number),number))
    for ref,es in body.items():
        es=sorted(es,key=lambda e:physical(ref,int(e['role'].rsplit('.',1)[1])));a,b=es[0],es[1]
        ia,ib=[physical(ref,int(e['role'].rsplit('.',1)[1])) for e in (a,b)]
        step=[(y-x)/(ib-ia) for x,y in zip(a['point_mm'],b['point_mm'])]
        pitch=math.sqrt(sum(v*v for v in step));assert min(abs(pitch-v) for v in (4.75,6.5))<1e-5,ref
        origin=[x-(ia-1)*v for x,v in zip(a['point_mm'],step)]
        for e in es:
            number=physical(ref,int(e['role'].rsplit('.',1)[1]));q=[x+(number-1)*v for x,v in zip(origin,step)]
            assert math.dist(q,e['point_mm'])<1e-5,(ref,e['id'])
            assert math.dist(e['departure_axis'],a['departure_axis'])<1e-5,ref
        prototypes[ref]=dict(first_port_mm=origin,port_pitch_vector_mm=step,departure_axis=a['departure_axis'],
            basis='Multiple current project CAD ends, not manufacturer guaranteed mouth coordinates',
            calibration_endpoint_ids=[e['id'] for e in es])
    assert len(prototypes)==17
    for ref,wire,port in (('P_AUX','XA03',2),('G_AUX','XA04',2),('G_TAIL','XA06',1)):
        g=groups['WAGO:'+aliases.get(ref,ref)];old=p['aux']['routes'][wire]['parts'][-1]['end']
        lo,hi=g['current_bounds_mm'];assert abs(old[0]-hi[0])<1e-4 and lo[1]<=old[1]<=hi[1]
        assert abs(old[2]-(lo[2]+hi[2])/2)<1e-4,(ref,'GUIDE not on known source case face')
        R=g['rotation_rows'];t=g['translation_mm'];q=[sum(R[i][j]*old[j] for j in range(3))+t[i] for i in range(3)]
        d=[R[i][0] for i in range(3)];step=[-4.75*R[i][1] for i in range(3)]
        base=[x-(port-1)*v for x,v in zip(q,step)]
        prototypes[ref]=dict(first_port_mm=base,port_pitch_vector_mm=step,departure_axis=d,
            basis='Exact named legacy guide on source case + current group rotation ONCE, still project datum',
            calibrated_source_wire=wire,source_port=port,source_point_mm=old)
        source_transfers.append(dict(ref=ref,group=g['role'],old_point_mm=old,new_point_mm=q,
            source_face_checked=True,rotation_applied_once=True))
    occupied=set();physical_occupied=set();external=[]
    for wire in p['ecad']['wires']:
        if not wire['id'].startswith('W0'):external.append(wire)
        for side in ('a','b'):
            endpoint=wire[side];ref,number=endpoint.rsplit('.',1) if '.' in endpoint else (endpoint,None)
            if ref not in byref:continue
            assert number.isdigit() and 1<=int(number)<=5,endpoint
            assert endpoint not in occupied,(endpoint,'Two physical conductors assigned one cavity')
            occupied.add(endpoint);number=int(number);pr=prototypes[ref];cavity=physical(ref,number)
            assert (ref,cavity) not in physical_occupied;physical_occupied.add((ref,cavity))
            q=[a+(cavity-1)*v for a,v in zip(pr['first_port_mm'],pr['port_pitch_vector_mm'])]
            byref[ref].append(dict(wire=wire['id'],endpoint=endpoint,schematic_port=number,physical_port=cavity,side=side,
                point_mm=q,departure_axis=pr['departure_axis'],minimum_jacket_land_mm=9,
                supplier_port_verified=False,full_route_or_grip_or_stock_verified=False))
    stations=[]
    for ref in refs:
        rows=sorted(byref[ref],key=lambda r:r['physical_port']);assert rows,ref
        stations.append(dict(ref=ref,current_group='WAGO:'+aliases.get(ref,ref),
            occupied_ports=rows,unused_ports=[n for n in range(1,6) if (ref,n) not in physical_occupied],
            schematic_to_physical_common_rail_map={str(n):physical(ref,n) for n in range(1,6)},
            prototype=prototypes[ref],independent_wire_grip_complete=False,
            current_power_comb_material_scope_only=ref=='P_SYS'))
    assert len(stations)==20
    return dict(status='TWENTY_DISTRIBUTION_CAVITIES_RECONCILED_NOT_COMPLETE_N01_OR_WIRING',selected=False,
        N01_complete=False,physical_pass=False,station_count=20,occupied_cavities=len(occupied),
        schematic_wire_segments=len(p['ecad']['wires']),outside_body80_schematic_segments=len(external),
        body_logical_net_count=80,body_physical_segment_count=89,body_endpoint_count=178,
        these_are_different_counters=True,stations=stations,three_extra_face_transfers=source_transfers,
        additional_schematic_segments=external,all_selected_external_pinouts_or_routes_verified=False,
        untouched_selected_parts_and_ECAD=True,
        next='Use ALL20comb/strap/lever/assembly spaces and all extra circuit endpoints in common layout. Input PSU/PCB/JPWM/servo endpoint frames and full current W1/W3/W4 traces remain to reconcile; do not duplicate factory leads or claim89segments cover all134schematic sections.',
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,4))


def main():
    dest=OUT/'n01-twenty-wago-port-contract.json';assert not dest.exists();p=compose()
    dest.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(p['status'],p['station_count'],p['occupied_cavities'],p['outside_body80_schematic_segments'],p['worker_seconds'])


if __name__=='__main__':main()

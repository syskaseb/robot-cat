"""Joint four-source replacement using the exact TE wire-entry datum.

Keep P0, ring seats/net identities and the received P_SYS platform. Route
around the bridge instead of through it. Housing relief/guards are explicit
later construction, not an assertion that this candidate fits unchanged E6.
"""
from pathlib import Path
from datetime import datetime, timezone
import math, json
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add, mul, norm, X, Y, Z
from servo_fuse_inputs_r1 import save, sha
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r4'
SEAT=62.0
ENTRY_Z=SEAT+2.8067
ENTRY_LEFT=117-22.1234
ENTRY_RIGHT=129+22.1234

def layout():
    rows=[]
    def finish(w,a,b,c,end):
        assert norm([x-y for x,y in zip(c.p,end)])<1e-7
        assert norm([x-y for x,y in zip(c.t,X if w in ('W064','W067') else mul(X,-1))])<1e-7
        length=sum(e['length_mm'] for e in c.edges)
        rows.append(dict(wire=w,a=a,b=b,start=c.edges[0]['start'],end=list(c.p),edges=c.edges,
            wire_sku='HELU23802',OD_mm=4.2,minimum_static_radius_mm=25.2,
            exposed_path_mm=length,nominal_trial_blank_mm=math.ceil((length+22.73+30)/10)*10,
            strip_allowance_mm=22.73,trial_reserve_mm=30,actual_cut_mm=None,
            ring_seating_Z_provisional_mm=SEAT,wire_entry_from_exact_TE_STEP=True,
            selected=False,physical_pass=False))
    c=CentreLine([-39,11,113.5],Y)
    c.arc(mul(Z,-1));c.arc(mul(X,-1));c.shift([0,0,ENTRY_Z-c.p[2]])
    c.line([-81.8,36.2,ENTRY_Z]);c.arc(Y);c.line([-107,95.2,ENTRY_Z]);c.arc(X)
    c.line([ENTRY_LEFT-50.4,120.4,ENTRY_Z]);c.arc(mul(Y,-1));c.arc(X)
    finish('W064','P_FRONT.1','S1.3',c,[ENTRY_LEFT,70,ENTRY_Z])
    c=CentreLine([32,13.6,129],X)
    c.arc(mul(Y,-1));c.line([57.2,-100.2,129]);c.arc(mul(Z,-1))
    c.line([57.2,-125.4,ENTRY_Z+25.2]);c.arc(X)
    c.line([ENTRY_RIGHT,-125.4,ENTRY_Z]);c.arc(Y)
    c.line([ENTRY_RIGHT+25.2,44.8,ENTRY_Z]);c.arc(mul(X,-1))
    finish('W065','P_REAR.1','S1.6',c,[ENTRY_RIGHT,70,ENTRY_Z])
    c=CentreLine([-69,7,135.5],mul(Y,-1))
    c.arc(mul(X,-1));c.line([-101.8,-18.2,135.5]);c.arc(Y)
    c.line([-127,107.2,135.5]);c.arc(mul(Z,-1))
    c.line([-127,132.4,ENTRY_Z+25.2]);c.arc(X)
    c.line([ENTRY_LEFT-50.4,132.4,ENTRY_Z]);c.arc(mul(Y,-1));c.arc(X)
    finish('W067','P_SYS.3','S1.2',c,[ENTRY_LEFT,82,ENTRY_Z])
    c=CentreLine([-61.5,7,135.5],mul(Y,-1))
    c.line([-61.5,-.5,135.5]);c.arc(mul(X,-1));c.line([-114,-25.7,135.5]);c.arc(Y)
    c.line([-139.2,119.2,135.5]);c.arc(mul(Z,-1))
    c.line([-139.2,144.4,ENTRY_Z+25.2]);c.arc(X)
    c.line([ENTRY_RIGHT,144.4,ENTRY_Z]);c.arc(mul(Y,-1))
    c.line([ENTRY_RIGHT+25.2,107.2,ENTRY_Z]);c.arc(mul(X,-1))
    finish('W068','P_SYS.4','S1.5',c,[ENTRY_RIGHT,82,ENTRY_Z])
    return rows

def main():
    begin=datetime.now(timezone.utc);assert not (OUT/'intent.json').exists()
    rows=layout();graph=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'
    nets={r['id']:r for r in json.loads(graph.read_text(encoding='utf-8'))['conductors']}
    for r in rows: assert {r['a'],r['b']}=={nets[r['wire']]['a'],nets[r['wire']]['b']}
    ref=ROOT/'hardware/reference/source-terminal-2026-10-04/received.json'
    source=json.loads(ref.read_text(encoding='utf-8'));assert source['valid'] and source['solids']==1
    assert all(sha(ROOT/k)==v for k,v in {**source['source_sha256'],**source['files']}.items())
    pins=[Path(__file__),Path(__file__).with_name('w5_s1_source_layout_r2.py'),
        Path(__file__).with_name('w5_s1_source_layout_r1.py'),graph,ref,
        ROOT/'hardware/electronics/full-cat/w5-source-platform-native-r4/checks.json',
        ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r3/checks.json']
    end=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'intent.json',dict(status='FOUR_SOURCE_JOINT_TE_DATUM_CANDIDATE_UNSELECTED',routes=rows,
        S1_ring_seat_centres={'S1.3':[117,70,SEAT],'S1.6':[129,70,SEAT],
                              'S1.2':[117,82,SEAT],'S1.5':[129,82,SEAT]},
        S1_ring_direction='Unchanged west/east; barrel axis+2.8067Z from received STEP.',
        legacy_four_S1_mm=920,new_four_S1_trial_mm=sum(r['nominal_trial_blank_mm'] for r in rows),
        P0_changes=0,new_electrical_connections=0,new_electrical_SKUs=0,
        preserve=['SourceInletPlatform nativeR4','W066 sourceR3','W043 inletR2','Selected R53 until whole source family qualifies'],
        assumptions=['S1 seating Z62 and casing/lug stack remain prototype datums, not physical measurements.',
            'TE STEP is uncrimped. Exact crimp/pocket/strain relief must be dry fitted in phase2.',
            'NKK official S821 CAD selected successfully; download requires business-email account. No login or account created.',
            'NKK drawing says terminal numbers ARE on switch; compare physical clocking before connecting.',
            'Outer routes require simultaneous PETG reliefs/guards, supports, stock and assembly; not selected yet.'],
        selected=False,native_supports_ready=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('FOUR_SOURCE_TE_DATUM',[(r['wire'],r['nominal_trial_blank_mm']) for r in rows],flush=True)

if __name__=='__main__':main()

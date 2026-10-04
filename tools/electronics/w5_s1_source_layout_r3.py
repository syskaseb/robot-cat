"""One six-lead source family, retaining S0/P0 and exact electrical nets.

Raise P_SYS22 and move it north18 to allow the short factory F_PI lead.
Four S1 rings use their original separated left/right directions. Source
routes go around, not through, the head feeds, MAIN and Pi cooling volume.
This is one unselected joint candidate; no support or collision claims.
"""
from datetime import datetime,timezone
from pathlib import Path
import math,json
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul,norm,X,Y,Z
from servo_fuse_inputs_r1 import save,sha
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r3'

def layout():
    rows=[]
    def finish(w,a,b,c,od,radius,strip,sku):
        length=sum(e['length_mm'] for e in c.edges)
        rows.append(dict(wire=w,a=a,b=b,start=c.edges[0]['start'],end=list(c.p),edges=c.edges,
            wire_sku=sku,OD_mm=od,minimum_static_radius_mm=radius,exposed_path_mm=length,
            nominal_trial_blank_mm=math.ceil((length+strip+30)/10)*10,
            strip_allowance_mm=strip,trial_reserve_mm=30,actual_cut_mm=None,selected=False,physical_pass=False))
    c=CentreLine([-39,11,113.5],Y)
    c.line([-39,25,113.5]);c.arc(mul(Z,-1));c.line([c.p[0],c.p[1],70.2]);c.arc(X)
    c.shift([0,70-c.p[1],0]);c.line([51,70,45]);c.shift([0,0,17]);c.line([94.877,70,62])
    finish('W064','P_FRONT.1','S1.3',c,4.2,25.2,22.73,'HELU23802')
    c=CentreLine([32,13.6,129],X)
    c.arc(mul(Y,-1));c.line([57.2,-55,129]);c.arc(mul(Z,-1));c.line([57.2,-80.2,70.2]);c.arc(X)
    c.line([155.2,-80.2,45]);c.arc(Y);c.shift([0,0,17]);c.line([180.4,44.8,62]);c.arc(mul(X,-1));c.line([151.123,70,62])
    finish('W065','P_REAR.1','S1.6',c,4.2,25.2,22.73,'HELU23802')
    c=CentreLine([-69,7,135.5],mul(Y,-1))
    c.line([-69,-88,135.5]);c.arc(mul(Z,-1));c.line([-69,-113.2,70.2]);c.arc(mul(X,-1));c.arc(Y)
    c.line([-119.4,106.8,45]);c.arc(X);c.line([-31,132,45]);c.shift([0,-50,0]);c.shift([0,0,17]);c.line([94.877,82,62])
    finish('W067','P_SYS.3','S1.2',c,4.2,25.2,22.73,'HELU23802')
    c=CentreLine([-61.5,7,135.5],mul(Y,-1))
    c.line([-61.5,-80.5,135.5]);c.arc(mul(Z,-1));c.line([-61.5,-105.7,77.7]);c.arc(X)
    c.line([162.7,-105.7,52.5]);c.arc(Y);c.shift([0,0,9.5]);c.line([187.9,56.8,62]);c.arc(mul(X,-1));c.line([151.123,82,62])
    finish('W068','P_SYS.4','S1.5',c,4.2,25.2,22.73,'HELU23802')
    # Preserve the already selected S0 ring/clocking and lower W066 loop.
    out=[-61.5-12/math.sqrt(2),70,43+12/math.sqrt(2)]
    alpha=math.acos((out[0]+90.5)/52.1);u=[-math.cos(alpha),0,math.sin(alpha)]
    c=CentreLine(add(out,mul(u,26.9)),u);c.arc(mul(Y,-1));c.shift([0,0,71-c.p[2]])
    c.line([-90.5,-65,71]);c.arc(Z,math.pi);c.line([-90.5,-47,121.4]);c.shift([6.5,0,14.1]);c.line([-84,7,135.5])
    finish('W066','S0.out','P_SYS.1',c,4.2,25.2,32.73,'HELU23802')
    # Factory F_PI wire, no made-up long pigtail or hidden extension.
    c=CentreLine([-76.5,7,135.5],mul(Y,-1));c.line([-76.5,-9,135.5])
    delta=[3.5,0,-20.5];h=norm(delta);u=mul(delta,1/h)
    c.arc(u,radius=6);c.line(add(c.p,mul(u,h-12)));c.arc(mul(Y,-1),radius=6)
    assert norm([a-b for a,b in zip(c.p,[-73,-21,115])])<1e-7
    finish('W043','P_SYS.2','F_PI.in',c,3.4,6,14,'Intact FHAC0001ZXJ16AWG factory')
    rows[-1].update(trial_reserve_mm=15,nominal_trial_blank_mm=80,factory_minimum_mm=84.5,
        factory_OD_and_bend_radius_provisional=True)
    return rows

def main():
    start=datetime.now(timezone.utc);assert not (OUT/'intent.json').exists()
    rows=layout();graph=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'
    nets={r['id']:r for r in json.loads(graph.read_text(encoding='utf-8'))['conductors']}
    for r in rows:assert {r['a'],r['b']}=={nets[r['wire']]['a'],nets[r['wire']]['b']}
    f=rows[-1];assert f['nominal_trial_blank_mm']>=f['exposed_path_mm']+f['strip_allowance_mm']+f['trial_reserve_mm']
    assert f['nominal_trial_blank_mm']<=f['factory_minimum_mm']
    OUT.mkdir(parents=True,exist_ok=True);finish=datetime.now(timezone.utc)
    pins=[Path(__file__),Path(__file__).with_name('w5_s1_source_layout_r2.py'),Path(__file__).with_name('w5_s1_source_layout_r1.py'),
        graph,ROOT/'hardware/electronics/full-cat/w5-psys-platform-preflight-r1/intent.json',
        ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r2/checks.json',ROOT/'hardware/electronics/power-platform/switch-terminations-p0.json']
    save(OUT/'intent.json',dict(status='ONE_SIX_LEAD_SOURCE_FAMILY_UNSELECTED',routes=rows,
        P_SYS_displacement_mm=[0,18,22],P_SYS_new_body_bounds_mm=[-87.5,7,131,-50.5,29,142],
        source_qualified_wires_reopened=['W043','W066'],S1_ring_orientation='Original left-west/right-east, unchanged centres/fasteners/nets.',
        legacy_four_S1_mm=920,new_four_S1_trial_mm=sum(r['nominal_trial_blank_mm'] for r in rows if r['wire'] in ('W064','W065','W067','W068')),
        P0_changes=0,new_electrical_connections=0,new_electrical_SKUs=0,
        remaining=['Actual simultaneous body/6wire/ring checks, including current source and head feeds.',
            'Raised/north-shifted P_SYS retention and all six insulation restraints.',
            'Outer route guards/cover as needed; do not infer that original E6 encloses this candidate.',
            'Shared assembly/tool/stock selection. Preserve original selected source until all gates pass.'],
        selected=False,native_supports_ready=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},started_utc=start.isoformat(),
        finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('SIX_SOURCE_LEADS',[(r['wire'],r['nominal_trial_blank_mm']) for r in rows],flush=True)

if __name__=='__main__':main()

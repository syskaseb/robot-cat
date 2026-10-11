"""Shared four-pad MAIN/Pi proposal, no invented external U1 connections.

Two USB free pigtail exits are project routing datums, NOT USB contact pins.
Retain the sealed keyed K1474 plug. Concentric pair bends preserve spacing.
"""
import json,math,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,E,W,N,S,U,D,line,curve,add,mul,reverse,SHA
from open_prototype_source_group import check_path
R=11.1

def straight(q,p):
    a=q[-1]['end']
    if math.dist(a,p)>1e-8:q.append(line(a,p))

def turn(q,u,v,r=R):
    a=q[-1]['end'];k=math.sqrt(.5)
    q.append(curve(a,add(add(a,mul(u,r)),mul(v,r)),
      add(add(a,mul(u,r*k)),mul(v,r*(1-k))),r,math.pi/2))

def pad(x,direction,jacket_land=3):
    #3mm bare rise followed by3mm jacket before the first R11.1 bend.
    # Actual pad/solder/insulation lengths remain delivered board fit gates.
    bare=[line([x,21.289,48.0948],[x,21.289,51.0948])]
    q=[line(bare[-1]['end'],[x,21.289,51.0948+jacket_land])];turn(q,U,direction)
    return bare,q

def plan():
    routes={};bare={}
    # Both protected output cores share one flat paired route below the neck
    # floor. Concentric turns, NOT equal-radius translated crossing bends.
    usb={};output_top=45.2+2*R+1
    for wid,x,endx,first,last in [('W079',-48.68,-9.1,14.6,14.6),('W080',-45.18,-12.6,11.1,11.1)]:
        # North-side complete pair avoids the S0 nominal stud/case envelope.
        # R14.3 starts below Z65, clears its east tangent before entering it.
        bare[wid],q=pad(x,N,output_top-14.3-51.0948)
        q=[line([x,21.289,51.0948],[x,21.289,output_top-14.3])]
        turn(q,U,N,14.3);turn(q,N,E,first)
        straight(q,[-23.7,q[-1]['end'][1],output_top]);turn(q,E,S,last)
        mouth=[endx,-53,45.2];tail=[line(mouth,[endx,-62,45.2])]
        turn(tail,S,U);straight(tail,[endx,-73.1,output_top-R]);turn(tail,U,N)
        straight(q,tail[-1]['end']);q+=reverse(tail)
        routes[wid]=q;usb[wid]=dict(point_mm=mouth,departure=S,
          basis='Nominal loose K1474 two-core pigtail routing allowance at sealed USB-C plug; NOT USB internal pads/pinout. Actual boot/exit fit gate.')
    # MAIN input return: separate NORTH entry at G1, below retained neck floor.
    top=65.1948;bare['W060'],tail=pad(-41.68,S)
    straight(tail,[-41.68,1.189,top]);turn(tail,S,W)
    # Shared G1 rail port4 replaces port2, which lies directly in retained
    # XB12. Swap the unfinished FRreturn to2; no ground net/topology change.
    q=[line([-69.5,-73.75,100.99],[-69.5,-64.75,100.99])]
    turn(q,N,D);straight(q,[-69.5,-53.65,top+R]);turn(q,D,N)
    straight(q,[-69.5,tail[-1]['end'][1]-R,top]);turn(q,N,E)
    straight(q,tail[-1]['end']);q+=reverse(tail);routes['W060']=q
    # Standing F_PI case is unchanged. The west prefix entered F_HP, while
    # east required >150mm18AWG. SOUTH uses the clear x19 aisle and a full
    # protected factory/custom overlap, preserving both cases and input.
    # The qualified old EAST prefix never proved this remaining continuation.
    prefix=[line([19,85.5,97.9],[19,85.5,94.9])];turn(prefix,D,S,6)
    straight(prefix,[19,72.589,88.9]);routes['W077']=prefix
    bare['W078'],tail=pad(-38.18,N)
    straight(tail,[-38.18,41.389,top]);turn(tail,N,E)
    q=[line([19,80.589,88.9],[19,63.589,88.9])];turn(q,S,D)
    straight(q,[19,tail[-1]['end'][1],top+R]);turn(q,D,W)
    straight(q,tail[-1]['end'])
    q+=reverse(tail);routes['W078']=q
    result={}
    for n,parts in routes.items():
        check_path(parts,min_radius=6 if n=='W077' else R)
        result[n]=dict(parts=parts,radius_mm=2 if n=='W077' else 1.05,
          guide_mm=sum(p['length_mm'] for p in parts),
          SKU='FHAC0001ZXJ supplied16AWG' if n=='W077' else 'Joy-IT K-1474 retained18AWG',actual_cut_mm=None)
    assert result['W078']['guide_mm']+3<=150
    assert result['W060']['guide_mm']+3+14<=300
    assert max(result[n]['guide_mm']+3 for n in ('W079','W080'))<=250
    assert result['W077']['guide_mm']+8<=100
    return dict(status='SHARED_MAIN_PI_FOUR_PAD_PLAN_ONLY',selected=False,W5_complete=False,physical_pass=False,
      routes=result,bare_pad_parts=bare,usb_pigtail_datums=usb,
      factory_custom_overlap=dict(factory_tip_mm=[19,72.589,88.9],custom_tip_mm=[19,80.589,88.9],
        strip_each_mm=8,sleeve_bounds_mm=[16.6,66.589,86.5,21.4,86.589,91.3],
        SKU='RNF-100-3/16-0-STK',raw_blank_mm=20),
      supersedes=['Only W077_PREFIX and F_PI_sleeve from source-receiving plan, not F_PI case or protected input',
        'Old paired free-pigtail project coordinates, not USB contact pins or electrical polarity'],
      end_preparation={'MAIN':'Delivered4853 markings and family1.524mm drilled pads; bare3mm/project, actual solder/fit gate. No terminal2444 or full jacket in aPCB bore.',
        'W060_G1':'untinned12..14mm, use14 nominal','USB':'Retain sealed factory plug; test both insertion orientations only in phase2'},
      grips='One independent4core insulation comb on fixed MAIN mount, plus paired Pi grip before sealed boot and both sides of protected16/18 splice. Exact9mm grip stations after bends; solder/PCB never the load path. Native grips OPEN.',
      gates=['Current valid material/retained curves and own four-wire distances',
        'Native independent retention, screw/trimmer/service access and delivered fit',
        'Joint/pigtail recipe supersession, whole stock and E3 coordination'],
      source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (Path(__file__),OUT/'harness-interfaces-plan.json',
        ROOT/'hardware/electronics/power-platform/MAIN-INPUT-P0.md',ROOT/'hardware/electronics/power-platform/PI-CABLE-P0.md')})

if __name__=='__main__':
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'main-pi-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:round(r['guide_mm'],3) for k,r in p['routes'].items()}))

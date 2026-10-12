"""One allocated full11wire topology, not eleven independent shortest paths.

North lanes carry GPIO/U1 links; south return carries3V3; finePWM uses
separated low-current tiers. Existing terminal prefixes remain explicit.
Fixed prototype routing only. Native restraint/service gates remain open.
"""
import math,json,sys
from pathlib import Path
import plan_current_main_pi_wiring as M
from plan_current_main_sources import ROOT,SHA
from open_prototype_source_group import check_path


def complete(p):
    if '--free' in sys.argv:
        f=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/u1-free-channels-plan.json'
        current=json.loads(f.read_text())
        assert current['status']=='COMMON_U1_CHANNELS_SAMPLED_ONLY_ACTUAL_GATE_OPEN' and not current['search_failures']
        assert len(current['complete_routes'])==11 and set(current['changed_MAIN_pair'])=={'W079','W080'}
        for n,h in current['source_sha256'].items():assert SHA(ROOT/n)==h,('Changed allocation input',n)
        current['source_sha256'][f.relative_to(ROOT).as_posix()]=SHA(f)
        current['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=SHA(Path(__file__))
        return current
    rows={}
    for wid,top in [('XL05',115),('XL06',119),('XL01',123),('XL07',127),('XL10',135),('XL08',139)]:
        r=p['routes'][wid];a=r['ends']['a']['end_mm'];b=r['ends']['b']['end_mm']
        radius=6 if wid=='XL08' else 10
        east=b[0]>a[0];direction=M.E if east else M.W
        q=[M.line(a,[a[0],a[1],top-radius])];M.turn(q,M.U,M.N,radius)
        north=max(a[1]+radius,b[1]+radius*2)+13
        M.straight(q,[a[0],north,top]);M.turn(q,M.N,direction,radius)
        M.straight(q,[b[0]-radius*(1 if east else -1),q[-1]['end'][1],top])
        M.turn(q,direction,M.S,radius)
        M.straight(q,[b[0],b[1]+radius,top]);M.turn(q,M.S,M.D,radius)
        M.straight(q,b);rows[wid]=q
    r=p['routes']['XL02'];a=r['ends']['a']['end_mm'];b=r['ends']['b']['end_mm'];top=145
    q=[M.line(a,[a[0],a[1]-3,a[2]])];M.turn(q,M.S,M.U,6)
    M.straight(q,[q[-1]['end'][0],q[-1]['end'][1],top-6]);M.turn(q,M.U,M.W,6)
    M.straight(q,[b[0]+6,q[-1]['end'][1],top]);M.turn(q,M.W,M.N,6)
    M.straight(q,[b[0],b[1]-6,top]);M.turn(q,M.N,M.D,6);M.straight(q,b);rows['XL02']=q
    r=p['routes']['XL09'];a=r['ends']['a']['end_mm'];b=r['ends']['b']['end_mm']
    q=[M.line(a,[a[0],a[1],112])];M.turn(q,M.U,M.S,6)
    M.straight(q,[a[0],b[1]+6,118]);M.turn(q,M.S,M.E,6)
    M.turn(q,M.E,M.D,6);M.turn(q,M.D,M.W,6)
    M.straight(q,[b[0]+6,b[1],106]);M.turn(q,M.W,M.U,6);M.straight(q,b);rows['XL09']=q
    for i,wid in enumerate(('XS11','XS21','XS31')):
        r=p['routes'][wid];a=r['ends']['a']['end_mm'];b=r['ends']['b']['end_mm'];top=105+2*i
        q=[M.line(a,[a[0],a[1],top-.5])];M.turn(q,M.U,M.E,.5)
        M.straight(q,[56.5,a[1],top]);M.turn(q,M.E,M.N,.5)
        M.straight(q,[57,b[1]-.5,top]);M.turn(q,M.N,M.D,.5)
        M.straight(q,[57,b[1],b[2]+.5]);M.turn(q,M.D,M.E,.5);M.straight(q,b);rows[wid]=q
    assert set(rows)==set(p['routes']) and len(rows)==11
    p['complete_routes']={}
    for wid,middle in rows.items():
        r=p['routes'][wid];radius=.5 if wid.startswith('XS') else 6 if wid in ('XL02','XL08','XL09') else 10
        check_path(middle,start=r['ends']['a']['end_mm'],end=r['ends']['b']['end_mm'],min_radius=radius)
        full=r['ends']['a']['parts']+middle+M.reverse(r['ends']['b']['parts'])
        length=check_path(full,min_radius=radius)
        # No new splice. Five factory600mm GPIO jumpers retain Pi housing;
        # cut only U1 end, with30mm service and6mm preparation allowance.
        cut=math.ceil(length+36) if r['source'].get('AWG')==26 else math.ceil(length+6)
        if r['source'].get('AWG')==26:assert cut<=600,(wid,cut)
        p['complete_routes'][wid]=dict(parts=full,middle_parts=middle,radius=r['ends']['a']['radius'],
            guide_mm=length,nominal_blank_mm=cut,actual_cut_mm=None,min_fixed_radius_mm=radius,
            source=r['source'],native_grips_open=True,physical_pass=False)
    p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=SHA(Path(__file__))
    p['status']='WHOLE11WIRE_AND_MAIN_COUPLED_PLAN_NATIVE_OPEN'
    return p

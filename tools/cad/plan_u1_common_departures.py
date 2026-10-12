"""One coupled Pi/U1 departure plan, preserving the first rejected receipt.

Plan the full GPIO portal, paired USB route and all22 ends together. Geometry
cut is planning-only; no native source, selection or score is changed here.
"""
import json,math,time,sys
from pathlib import Path
import FreeCAD as A
import Part
import plan_u1_external_fan as F
import plan_current_main_pi_wiring as M
from current_prototype_harness_scene import wire
from u1_socket_current_context import context
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_joined_leg_looms import exact_quarter
from plan_current_mta_interfaces import line
from plan_u1_socket_passives import rounded
sys.path.insert(0,str(ROOT/'tools/electronics'))
import plan_u1_socket_carrier as U
import pi_wiring_complete_r1 as P

PORTAL=[-13.5,20.5,74.62,40.5,28.5,77.82]


def build():
    p=F.build();pins,datums=P.j8()
    for row in p['routes'].values():
        for e in ('a','b'):
            t=row['source'][e]
            if t['kind']=='project40pin_housing_wire_exit':
                n=int(t['ref'].split('H')[1]);point=pins[n]
                assert math.dist(point[:2],t['world_mm'][:2])<1e-6
    p['GPIO_source_datum']=dict(source_historical_datums=datums,XY_verified_against_current5ends=True,
        current_board_underside_mm=47.72,wire_exit_assumed_z_mm=65.32,
        current_board_to_world_translation_mm=[-19,-28,47.72],
        current_housing_bounds_mm=[-12.05,21.95,51.32,39.05,27.05,65.57],
        mated_height_and_12mm_withdrawal_are_project_delivery_gates=True)
    q=json.loads((OUT/'u1-socket-carrier-plan.json').read_text())
    for t in q['terminals']:
        if t['ref']=='OE.in':t['y']=6.35
    q['terminals'].append(dict(ref='PCA3V3.out',x=-17.78,y=-3.81,net='LOGIC3V3'))
    U.check(q)
    p['terminal_rebindings']={'OE.in':dict(old_local=[-12.7,8.89],new_local=[-12.7,6.35]),
                             'PCA3V3.out':dict(old_local=[12.7,6.35],new_local=[-17.78,-3.81])}
    for wid,side,xy in [('XL07','b',[78.89,6.35]),('XL02','a',[73.81,-3.81])]:
        r=p['routes'][wid];r['source'][side]['world_mm'][:2]=xy
        e=r['ends'][side];x,y,z=r['source'][side]['world_mm']
        e['parts']=[line([x,y,z+1],[x,y,z+10])];e['end_mm']=e['parts'][-1]['end']
        p['bare'][wid+'/'+side]['parts']=[line([x,y,81.2202],[x,y,z+1])]
    for wid,i in [('XS11',0),('XS21',1),('XS31',2)]:
        e=p['routes'][wid]['ends']['b'];x,y,z=p['routes'][wid]['source']['b']['world_mm']
        yy=-6.35-1.27*i
        e['parts']=F.parts(rounded([[x,y,z+.5],[x,y,90.3],[x,yy,90.3],
                                    [61,yy,90.3],[61,yy,93]],.5))
        e['end_mm']=e['parts'][-1]['end']
    # Supported fixed LAPP profile, not a relaxation of a moving cable.
    for wid in ('XL02','XL08','XL09'):p['routes'][wid]['source']['project_radius_mm']=6
    e=p['routes']['XL09']['ends']['b'];a=p['routes']['XL09']['source']['b']['world_mm'];x,y,z=a
    seg=[line(a,[x+9,y,z])];seg.append(exact_quarter(seg[-1]['end'],[1,0,0],[0,0,-1],6))
    seg.append(line(seg[-1]['end'],[x+15,y,z-15]));e['parts']=seg;e['end_mm']=seg[-1]['end']
    # Whole paired MAIN output moves to the WEST side of J8. Same first
    # north departure and concentric bends: no S0 east-tangent recrossing.
    main=M.plan();p['changed_MAIN_pair']={}
    for wid,x,endx,first,last in [('W079',-48.68,-18.5,14.6,14.6),('W080',-45.18,-22,11.1,11.1)]:
        top=68.4;q=[line([x,21.289,51.0948],[x,21.289,54.1])]
        M.turn(q,M.U,M.N,14.3);M.turn(q,M.N,M.E,first)
        M.straight(q,[-33.1,q[-1]['end'][1],top]);M.turn(q,M.E,M.S,last)
        mouth=[endx,-53,45.2];tail=[line(mouth,[endx,-62,45.2])]
        M.turn(tail,M.S,M.U);M.straight(tail,[endx,-73.1,top-M.R]);M.turn(tail,M.U,M.N)
        M.straight(q,tail[-1]['end']);q+=M.reverse(tail)
        M.check_path(q,min_radius=M.R)
        r=dict(main['routes'][wid],parts=q,guide_mm=sum(s['length_mm'] for s in q))
        assert r['guide_mm']+3<=250
        p['changed_MAIN_pair'][wid]=r
    for l in p['grip_lands']:
        wid,s=l['wire'],l['side'];e=p['routes'][wid]['ends'][s]
        if (wid,s) in [('XL07','b'),('XL02','a')]:l['line_mm']=[e['parts'][0]['start'],e['parts'][0]['end']]
        if wid in ('XS11','XS21','XS31') and s=='b':
            yy=-6.35-1.27*(['XS11','XS21','XS31'].index(wid));l['line_mm']=[[62,yy,90.3],[71,yy,90.3]]
    p['GPIO_carrier_portal_world_mm']=PORTAL
    p['limits']='Fixed LAPP0.25 nominalOD1.3/staticR5.2: projectR6/OD<=1.4. Fine1446R0.5 fixed only. Pi26AWG remainsR10. Portal and USB fit are project gates.'
    p['status']='COUPLED_GPIO_MAIN_U1_PREFIX_LAYOUT_ONLY'
    p['source_sha256'].update({f.relative_to(ROOT).as_posix():SHA(f) for f in
        (Path(__file__),ROOT/'tools/electronics/pi_wiring_complete_r1.py',P.REF/'pi4-mechanical.dxf',ROOT/'tools/cad/plan_current_main_pi_wiring.py')})
    return p


def run():
    tick=time.monotonic();p=build();reader,pins,targets,old=context()
    print('Common Pi/U1 context ready',round(time.monotonic()-tick,2),flush=True)
    previous_file=OUT/'u1-external-fan-checks.json';previous=json.loads(previous_file.read_text())
    for n,h in previous['source_sha256'].items():assert SHA(ROOT/n)==h,('Changed reused source',n)
    assert not previous['errors']
    changed={'XL07/b','XL07/b/bare','XL02/a','XL02/a/bare','XL09/b',
             'XS11/b','XS21/b','XS31/b','W079','W080'}
    original=targets['UpperCarrier001'];b=PORTAL
    tool=Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    final=original.cut(tool)
    assert final.isValid() and len(final.Solids)==1 and not final.check(True),'GPIO portal damages carrier'
    removed=original.Volume-final.Volume;assert removed>0
    targets['UpperCarrier001']=final
    # The original closed G_TAIL reference has no bored cavities. Check the
    # exact known entry face after only the wire-radius axial engagement is
    # removed; do not exempt the connector case or its adjacent wires.
    curves={}
    for wid,r in p['routes'].items():
        for s,e in r['ends'].items():curves[wid+'/'+s]=(wire(e['parts']),e['radius'])
    curves.update({n+'/bare':(wire(e['parts']),e['radius']) for n,e in p['bare'].items()})
    for wid,r in p['changed_MAIN_pair'].items():
        assert wid in old,wid;old.pop(wid);curves[wid]=(wire(r['parts']),r['radius_mm'])
    result=dict(status='PENDING',pairs=0,material_resolutions=[],wire_contacts=[],errors=[],
        GPIO_portal=dict(bounds_mm=b,remaining_solids=1,strict_BOP_errors=0,removed_mm3=removed,native_open=True),
        selected=False,E1_complete=False,W5_complete=False,physical_pass=False)
    result['unchanged_prefix_evidence']=dict(receipt=previous_file.relative_to(ROOT).as_posix(),
        sha256=SHA(previous_file),all_source_hashes_verified=True,
        rule='Only changed curves need whole context. Unchanged curves recheck carrier subtraction; new USB pair participates in every mutual candidate. Original13 unresolved pairs belong to changed curves/carrier/USB.')
    def near(s,t,r):
        b=s.BoundBox;b.enlarge(r);return b.intersect(t.BoundBox)
    for n,(c,r) in curves.items():
        for other,s in targets.items():
            if n not in changed and other!='UpperCarrier001':continue
            cc=c
            if n=='XL09/b' and other=='G_TAIL':
                seg=json.loads(json.dumps(p['routes']['XL09']['ends']['b']['parts']))
                seg[0]=line([seg[0]['start'][0]+r+.01,*seg[0]['start'][1:]],seg[0]['end']);cc=wire(seg)
            if not near(cc,s,r):continue
            result['pairs']+=1
            try:
                d=cc.distToShape(s)[0]
                if d<r-1e-5:result['material_resolutions'].append(dict(a=n,b=other,distance_mm=d,required_mm=r))
            except Exception as ex:result['errors'].append(dict(a=n,b=other,error=str(ex)))
        for other,(w,rr) in old.items():
            if n not in changed:continue
            if not near(c,w,r+rr):continue
            result['pairs']+=1
            try:
                d=c.distToShape(w)[0]
                if d<r+rr-1e-5:result['wire_contacts'].append(dict(a=n,b=other,distance_mm=d,required_mm=r+rr))
            except Exception as ex:result['errors'].append(dict(a=n,b=other,error=str(ex)))
        print(n,'pairs',result['pairs'],'issues',len(result['material_resolutions'])+len(result['wire_contacts']),round(time.monotonic()-tick,2),flush=True)
    names=list(curves)
    for i,n in enumerate(names):
        c,r=curves[n]
        for m in names[i+1:]:
            if n.split('/')[0]==m.split('/')[0]:continue
            if n not in changed and m not in changed:continue
            d,rr=curves[m]
            if not near(c,d,r+rr):continue
            result['pairs']+=1;gap=c.distToShape(d)[0]
            if gap<r+rr-1e-5:result['wire_contacts'].append(dict(a=n,b=m,distance_mm=gap,required_mm=r+rr))
    result['status']='COMMON_DEPARTURES_REQUIRE_RESOLUTION' if any(result[k] for k in ('material_resolutions','wire_contacts','errors')) else 'COMMON_DEPARTURES_CLEAR_MIDDLES_NATIVE_OPEN'
    p['source_sha256'].update(F.E.build()['source_sha256'])
    (OUT/'u1-common-departures-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    result['source_sha256']={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins},**p['source_sha256']}
    result['plan_sha256']=SHA(OUT/'u1-common-departures-plan.json');result['worker_seconds']=round(time.monotonic()-tick,3)
    (OUT/'u1-common-departures-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)


if __name__=='__main__':run()

"""One coupled Pi/U1 departure plan, preserving the first rejected receipt.

Plan the full GPIO portal, current Pi USB receiver and all22 ends together. Geometry
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
USB_RELIEF=[-14.8,-42.75,46.42,8.2,-28.75,55.42]


def ne_to_e(q,r):
    a=q[-1]['end'];theta=math.atan2(.8,.6)
    q.append(M.curve(a,[a[0]+.8*r,a[1]+.4*r,a[2]],
        [a[0]+(.8-math.sin(theta/2))*r,a[1]+(math.cos(theta/2)-.6)*r,a[2]],r,theta))


def usb_receiver():
    rows=[v for k,v in P.dxf_entities(P.REF/'pi4-mechanical.dxf')
          if k=='LWPOLYLINE' and dict(v).get('5')=='234']
    assert len(rows)==1
    xx=[float(v) for c,v in rows[0] if c=='10'];yy=[float(v) for c,v in rows[0] if c=='20']
    assert [min(xx),min(yy),max(xx),max(yy)]==[6.875,-1.25,15.525,6.15]
    return dict(SKU='Delock60047',quantity=1,selected=False,
        manufacturer_source='https://www.delock.com/produkt/60047/pdf.html?sprache=en',
        manufacturer_approx_dimensions_mm=[22,13,8],manufacturer_max_current_A=5,
        manufacturer_material='metal',manufacturer_orientation='left/right',
        official_Pi_USB_C_shell_board_xy_mm=[min(xx),min(yy),max(xx),max(yy)],
        mating_front_world_mm=[-7.8,-29.25,50.92],
        current_Pi_PCB_bottom_mm=47.72,USB_centre_above_PCB_assumed_mm=3.2,
        reservations_mm={'AdapterBody':[-14.3,-42.25,46.92,7.7,-29.25,54.92],
                         'RetainedK1474Boot':[7.7,-45.9,46.92,32.7,-31.9,54.92]},
        free_wire_mouths_mm={'W079':[32.7,-37.15,50.92],'W080':[32.7,-40.65,50.92]},
        assumptions=['Only supplier overall dimensions/rating/orientation and official Pi shellXY are facts.',
            'Adapter male engagement, female face, centreZ and K1474 boot/mouths are explicit PROJECT fit reservations, not a reverse-engineered supplier model.',
            'Keep sealed K1474 and use passive adapter only; no PD trigger or alternative PiGPIO power.',
            'Insulate metal body from carrier/boards and support plug plus cable independently. Added two contact interfaces require delivered voltage/temperature checks.',
            'If delivered adapter/boot exceeds these allocations, replace this reservation/layout before selection. No geometric or electrical physicalPASS.'])


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
    q['terminals'].append(dict(ref='PCA3V3.out',x=-15.24,y=-13.97,net='LOGIC3V3'))
    U.check(q)
    p['terminal_rebindings']={'OE.in':dict(old_local=[-12.7,8.89],new_local=[-12.7,6.35]),
                             'PCA3V3.out':dict(old_local=[12.7,6.35],new_local=[-15.24,-13.97])}
    for wid,side,xy in [('XL07','b',[78.89,6.35]),('XL02','a',[76.35,-13.97])]:
        r=p['routes'][wid];r['source'][side]['world_mm'][:2]=xy
        e=r['ends'][side];x,y,z=r['source'][side]['world_mm']
        e['parts']=[line([x,y,z+1],[x,y,z+10])];e['end_mm']=e['parts'][-1]['end']
        p['bare'][wid+'/'+side]['parts']=[line([x,y,81.2202],[x,y,z+1])]
    # The under-adapter terminal must ESCAPE before the PCB above it; a
    # vertical prefix ending below that PCB cannot continue magically UP.
    e=p['routes']['XL02']['ends']['a'];x,y,z=p['routes']['XL02']['source']['a']['world_mm']
    e['parts']=[exact_quarter([x,y,z+1],[0,0,1],[0,-1,0],6)]
    e['parts'].append(line(e['parts'][-1]['end'],[x,y-15,z+7]))
    e['end_mm']=e['parts'][-1]['end'];e['end_axis']=[0,-1,0]
    for wid,i in [('XS11',0),('XS21',1),('XS31',2)]:
        e=p['routes'][wid]['ends']['b'];x,y,z=p['routes'][wid]['source']['b']['world_mm']
        yy=-6.35-1.27*i
        e['parts']=F.parts(rounded([[x,y,z+.5],[x,y,90.3],[x,yy,90.3],
                                    [58,yy,90.3]],.5))
        e['end_mm']=e['parts'][-1]['end'];e['end_axis']=[-1,0,0]
    # Supported fixed LAPP profile, not a relaxation of a moving cable.
    for wid in ('XL02','XL08','XL09'):p['routes'][wid]['source']['project_radius_mm']=6
    e=p['routes']['XL09']['ends']['b'];a=p['routes']['XL09']['source']['b']['world_mm'];x,y,z=a
    seg=[line(a,[x+9,y,z])];seg.append(exact_quarter(seg[-1]['end'],[1,0,0],[0,0,-1],6))
    seg.append(line(seg[-1]['end'],[x+15,y,z-15]));e['parts']=seg;e['end_mm']=seg[-1]['end']
    # Bind current PCB/shell datum BEFORE the paired route. Old free ends
    # inside F0 are not retained ports. Whole Pi/M5 remain unchanged.
    main=M.plan();p['changed_MAIN_pair']={};p['USB_receiver']=usb_receiver()
    for wid,x,first,east,mouthy,bend in [('W079',-48.68,14.6,52,-37.15,19.85),('W080',-45.18,11.1,48.5,-40.65,11.1)]:
        top=73.12;q=[line([x,21.289,51.0948],[x,21.289,top-14.3])]
        # East component clears the round S0 body before rising past Z65.
        # Differing NE->E radii allocate3.5mm separated east lanes; equal
        # translated arcs would merge. Return WEST of BUS and PiUSB-A.
        M.turn(q,M.U,[.6,.8,0],14.3);ne_to_e(q,bend)
        M.straight(q,[east-first,q[-1]['end'][1],top]);M.turn(q,M.E,M.S,first)
        M.straight(q,[east,mouthy+M.R,top]);M.turn(q,M.S,M.D)
        M.straight(q,[east,mouthy,50.92+M.R]);M.turn(q,M.D,M.W)
        M.straight(q,p['USB_receiver']['free_wire_mouths_mm'][wid])
        M.check_path(q,min_radius=M.R)
        r=dict(main['routes'][wid],parts=q,guide_mm=sum(s['length_mm'] for s in q))
        assert r['guide_mm']+3<=450
        p['changed_MAIN_pair'][wid]=r
    for l in p['grip_lands']:
        wid,s=l['wire'],l['side'];e=p['routes'][wid]['ends'][s]
        if (wid,s)==('XL07','b'):l['line_mm']=[e['parts'][0]['start'],e['parts'][0]['end']]
        if (wid,s)==('XL02','a'):l['line_mm']=[e['parts'][1]['start'],e['parts'][1]['end']]
        if wid in ('XS11','XS21','XS31') and s=='b':
            yy=-6.35-1.27*(['XS11','XS21','XS31'].index(wid));l['line_mm']=[[62,yy,90.3],[71,yy,90.3]]
    p['GPIO_carrier_portal_world_mm']=PORTAL
    p['USB_lower_carrier_relief_world_mm']=USB_RELIEF
    longest=max(r['guide_mm']+3 for r in p['changed_MAIN_pair'].values())
    source_offcut=max(main['routes'][n]['guide_mm']+3+(14 if n=='W060' else 0) for n in ('W060','W078'))
    rho60=.0175*(1+.00393*40);loop=rho60*2*longest/1000/.823
    p['PI_CABLE_P0_proposed_routing_cap_supersession']=dict(
        historical_project_cap_mm=250,new_project_cap_mm=450,
        reason='Same supplier1m K1474 and18AWG pair; current receiver datum plus passive60047 rightangle adapter replaces old blocked free endpoints. No splice or purchase; one new candidate connector and its losses explicitly included.',
        longest_required_mm=longest,remaining_single1m_cut_after_output_and_INPUT_offcut_mm=1000-longest-source_offcut,
        conditional_copper_loop_60C_ohm=loop,conditional_drop_3A_V=3*loop,
        conditional_remaining_total_loop_budget_ohm=(5.08-4.95)/3-loop,
        assumptions='Copper rho/temperature, MAIN minimum5.08V and Pi3A are project scenarios, not guarantees. Contact/solder/PCB losses and E3 remainOPEN.',
        selected=False,physical_pass=False)
    p['limits']='Fixed LAPP0.25 nominalOD1.3/staticR5.2: projectR6/OD<=1.4. Fine1446R0.5 fixed only. Pi26AWG remainsR10. Portal and USB fit are project gates.'
    p['status']='COUPLED_GPIO_MAIN_U1_PREFIX_LAYOUT_ONLY'
    p['source_sha256'].update({f.relative_to(ROOT).as_posix():SHA(f) for f in
        (Path(__file__),ROOT/'tools/electronics/pi_wiring_complete_r1.py',P.REF/'pi4-mechanical.dxf',ROOT/'tools/cad/plan_current_main_pi_wiring.py')})
    return p


def run():
    tick=time.monotonic();p=build();full='--full' in sys.argv
    if full:
        from plan_u1_common_middles import complete
        p=complete(p)
    reader,pins,targets,old=context()
    print('Common Pi/U1 context ready',round(time.monotonic()-tick,2),flush=True)
    previous_file=OUT/'u1-external-fan-checks.json';previous=json.loads(previous_file.read_text())
    for n,h in previous['source_sha256'].items():assert SHA(ROOT/n)==h,('Changed reused source',n)
    assert not previous['errors']
    changed={'XL07/b','XL07/b/bare','XL02/a','XL02/a/bare','XL09/b',
             'XS11/b','XS21/b','XS31/b','W079','W080'}
    if full:changed=set(p['complete_routes'])|{'W079','W080'}
    original=targets['UpperCarrier001'];b=PORTAL
    tool=Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    final=original.cut(tool)
    assert final.isValid() and len(final.Solids)==1 and not final.check(True),'GPIO portal damages carrier'
    removed=original.Volume-final.Volume;assert removed>0
    targets['UpperCarrier001']=final
    original_lower=targets['LowerCarrier001'];b=USB_RELIEF
    usb_tool=Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    lower=original_lower.cut(usb_tool)
    assert lower.isValid() and len(lower.Solids)==1 and not lower.check(True),'USB relief damages Pi carrier'
    targets['LowerCarrier001']=lower
    b=PORTAL
    # The original closed G_TAIL reference has no bored cavities. Check the
    # exact known entry face after only the wire-radius axial engagement is
    # removed; do not exempt the connector case or its adjacent wires.
    curves={}
    if full:
        for wid,r in p['complete_routes'].items():
            curves[wid]=(wire(r['parts']),r['radius']);old.pop(wid,None)
    else:
        for wid,r in p['routes'].items():
            for s,e in r['ends'].items():curves[wid+'/'+s]=(wire(e['parts']),e['radius'])
    curves.update({n+'/bare':(wire(e['parts']),e['radius']) for n,e in p['bare'].items()})
    for wid,r in p['changed_MAIN_pair'].items():
        assert wid in old,wid;old.pop(wid);curves[wid]=(wire(r['parts']),r['radius_mm'])
    result=dict(status='PENDING',pairs=0,material_resolutions=[],wire_contacts=[],errors=[],
        USB_fit_reservations=[],
        GPIO_portal=dict(bounds_mm=b,remaining_solids=1,strict_BOP_errors=0,removed_mm3=removed,native_open=True),
        USB_lower_relief=dict(bounds_mm=USB_RELIEF,remaining_solids=1,strict_BOP_errors=0,
            removed_mm3=original_lower.Volume-lower.Volume,native_open=True),
        selected=False,E1_complete=False,W5_complete=False,physical_pass=False)
    result['unchanged_prefix_evidence']=dict(receipt=previous_file.relative_to(ROOT).as_posix(),
        sha256=SHA(previous_file),all_source_hashes_verified=True,
        rule='Only changed curves need whole context. Unchanged curves recheck carrier subtraction; new USB pair participates in every mutual candidate. Original13 unresolved pairs belong to changed curves/carrier/USB.')
    if '--space-only' in sys.argv:
        boxes=[]
        for name,s in targets.items():
            if not s.Solids:continue
            assert s.isValid(),name
            if name in ('Foundation','UpperCarrier001','LowerCarrier001','E2Fixture'):
                # A planar face WITH holes still has one large bounding
                # rectangle. Tessellated surface tiles preserve those holes
                # for conservative search; never call a tile hit contact.
                nodes,tris=s.tessellate(.2)
                pending=[[list(nodes[i]) for i in tri] for tri in tris]
                while pending:
                    tri=pending.pop();pairs=((0,1),(1,2),(2,0));a,c=max(pairs,key=lambda ij:math.dist(tri[ij[0]],tri[ij[1]]))
                    if math.dist(tri[a],tri[c])>3:
                        mid=[(x+y)/2 for x,y in zip(tri[a],tri[c])];other=3-a-c
                        pending.extend(([tri[a],mid,tri[other]],[mid,tri[c],tri[other]]));continue
                    boxes.append(dict(owner=name,bounds_mm=[min(v[j] for v in tri) for j in range(3)]+[max(v[j] for v in tri) for j in range(3)]))
                continue
            for face in s.Faces:
                bb=face.BoundBox
                boxes.append(dict(owner=name,bounds_mm=[getattr(bb,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        for name,bb in p['USB_receiver']['reservations_mm'].items():boxes.append(dict(owner='USB/'+name,bounds_mm=bb))
        sampled=[]
        for name,(shape,radius) in old.items():
            if name in ('W079','W080'):continue
            parts=[]
            for edge in shape.Edges:
                points=edge.discretize(Distance=.7)
                parts.extend(line(list(a),list(b)) for a,b in zip(points,points[1:]) if (b-a).Length>1e-7)
            sampled.append(dict(wire=name,OD_mm=radius*2,segments=parts))
        p['source_sha256'].update(F.E.build()['source_sha256'])
        spatial=dict(status='CURRENT_U1_ACTUAL_SURFACES_CONSERVATIVE_PLANNING_ONLY',boxes=boxes,retained_wires=sampled,
            source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins},**p['source_sha256']},
            geometry=dict(GPIO_portal=PORTAL,USB_relief=USB_RELIEF,USB_receiver=p['USB_receiver']),
            worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False,
            note='Native structural surfaces use<=3mm tessellated triangle tiles, preserving planar-face holes. Other face bounds and sampled retained centrelines are conservative search obstacles, never actual contact proof.')
        (OUT/'u1-current-routing-space.json').write_text(json.dumps(spatial,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(dict(status=spatial['status'],faces=len(boxes),wires=len(sampled),seconds=spatial['worker_seconds'])),flush=True)
        return
    def near(s,t,r):
        b=s.BoundBox;b.enlarge(r);return b.intersect(t.BoundBox)
    # Full conservative supplier/boot budgets are reservations, NOT claimed
    # actual BReps. Empty intersection proves space; overlap is a fit question.
    for name,budget in p['USB_receiver']['reservations_mm'].items():
        shape=Part.makeBox(*(budget[i+3]-budget[i] for i in range(3)),A.Vector(*budget[:3]))
        for other,s in targets.items():
            if not shape.BoundBox.intersect(s.BoundBox):continue
            result['pairs']+=1
            try:
                hit=shape.common(s)
                if hit.Volume>1e-5:result['USB_fit_reservations'].append(dict(reservation=name,other=other,volume_mm3=hit.Volume))
            except Exception as ex:result['errors'].append(dict(a=name,b=other,error=str(ex)))
        for other,(w,rr) in old.items():
            if other in ('W079','W080') or not near(w,shape,rr):continue
            result['pairs']+=1;gap=w.distToShape(shape)[0]
            if gap<rr-1e-5:result['USB_fit_reservations'].append(dict(reservation=name,other=other,distance_mm=gap,required_mm=rr))
    for n,(c,r) in curves.items():
        for other,s in targets.items():
            if n not in changed and other not in ('UpperCarrier001','LowerCarrier001'):continue
            cc=c
            if n in ('XL09/b','XL09') and other=='G_TAIL':
                seg=json.loads(json.dumps(p['routes']['XL09']['ends']['b']['parts']))
                seg[0]=line([seg[0]['start'][0]+r+.01,*seg[0]['start'][1:]],seg[0]['end'])
                if full:seg=p['routes']['XL09']['ends']['a']['parts']+p['complete_routes']['XL09']['middle_parts']+M.reverse(seg)
                cc=wire(seg)
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
    result['status']='COMMON_DEPARTURES_REQUIRE_RESOLUTION' if any(result[k] for k in ('material_resolutions','wire_contacts','USB_fit_reservations','errors')) else 'COMMON_DEPARTURES_CLEAR_MIDDLES_NATIVE_OPEN'
    p['source_sha256'].update(F.E.build()['source_sha256'])
    tag='u1-common-wiring' if full else 'u1-common-departures'
    (OUT/(tag+'-plan.json')).write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    result['source_sha256']={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins},**p['source_sha256']}
    result['plan_sha256']=SHA(OUT/(tag+'-plan.json'));result['worker_seconds']=round(time.monotonic()-tick,3)
    (OUT/(tag+'-checks.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)


if __name__=='__main__':run()

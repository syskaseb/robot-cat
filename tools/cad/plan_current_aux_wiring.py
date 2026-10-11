"""One current fixed AUX/platform layout; no historical route acceptance.

The first operation inventories only changed endpoint owners from their saved
native shapes. It does not recompute, move or save any source CAD.
"""
import json, time, math, argparse
from pathlib import Path
import finish_current_head_anchor as F
from check_main_p0_placement import SavedShapes, sha, prop

A, Part, ROOT, BASE = F.A, F.Part, F.ROOT, F.BASE
OUT = BASE / 'aux-wiring-checkpoint'
from plan_current_pwm_branch import line, arc, near, box
from plan_current_tail_wiring import shift
from plan_current_head_bundle import makewire
from plan_current_head_supply import recipe

def save(name, value):
    OUT.mkdir(exist_ok=True)
    (OUT/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')

def bounds(s):
    return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]

def inventory():
    tick=time.monotonic(); reader=SavedShapes()
    targets,_=F.physical_scene(reader)
    names=[n for n in targets if any(q in n for q in ('AUX','G2','F_AUX','P_AUX','S0','S1'))]
    rows={n:dict(bounds_mm=bounds(targets[n]),valid=targets[n].isValid(),solids=len(targets[n].Solids)) for n in names}
    current=BASE/'head-supply-checkpoint/HeadSupplyCurrent.FCStd'
    for n in ('Foundation','UpperCarrier001'):
        rows[n]=dict(bounds_mm=bounds(reader.shape(current,n)),native=current.relative_to(ROOT).as_posix())
    save('endpoint-owner-inventory.json',dict(status='READ_ONLY_CURRENT_OWNER_INVENTORY',objects=rows,
         source_sha256=reader.hashes,worker_seconds=round(time.monotonic()-tick,3),physical_pass=False))
    print(json.dumps(rows),flush=True)

def straight(q, p):
    if (A.Vector(*q[-1]['end'])-A.Vector(*p)).Length>1e-7:q.append(line(q[-1]['end'],p))

def turn(q, c, p):q.append(arc(c,q[-1]['end'],p))

def offset(q, axis, delta, r=15):
    v=A.Vector(*delta);d=v.Length
    if d<1e-7:return
    u=A.Vector(*axis);v.normalize();a=A.Vector(*q[-1]['end'])
    if d<=2*r:
        q.extend(shift(list(a),axis,list(v),d,r));return
    b=a+u*r+v*r;turn(q,list(a+v*r),list(b))
    c=b+v*(d-2*r);straight(q,list(c))
    turn(q,list(c+u*r),list(c+u*r+v*r))

def build():
    """A single allocation of all six W1 feeds plus both F_AUX sides.

    The F_AUX pose, pad fanout, accessible service joints and common return
    lanes are planned together. No path, case or stock is selected here.
    """
    z=123.39378221735;routes={}
    def put(n,q,r=1.25):routes[n]=dict(parts=q,radius=r)
    # Complete horizontal holder ABOVE the E2 receiving plate, not through
    # AUX PCB/carrier or through the two already qualified input tie heads.
    # P_REAR.1 is same positive rail, previously reserved for unfinishedW5.
    q=[line([29,13,138],[38,13,138])];offset(q,[1,0,0],[0,1.5,11],6)
    input_x=q[-1]['end'][0]+9;straight(q,[input_x,14.5,149]);put('XA01_factory',q,2)
    output_x=input_x+51;column_x=output_x+15
    # Output exits DOWN. The custom 1mm2 splice is a supported vertical lap,
    # not a fictitious full conductor pushed through the 1.02mm PCB drill.
    q=[line([output_x,14.5,149],[output_x+9,14.5,149])]
    turn(q,[output_x+9,8.5,149],[column_x,8.5,149]);straight(q,[column_x,-27,149])
    turn(q,[column_x,-27,143],[column_x,-33,143]);straight(q,[column_x,-33,130]);put('F_AUX_factory_out',q,2)
    # Opposed END strips share exactly130..138mm, not just an arbitrary
    # overlap of two long centreline segments away from their stripped tips.
    q=[line([column_x,-33,138],[column_x,-33,123.5])]
    turn(q,[column_x-15,-33,123.5],[column_x-15,-33,108.5]);offset(q,[-1,0,0],[0,0,16.82])
    straight(q,[76.27,-33,125.32]);turn(q,[76.27,-18,125.32],[61.27,-18,125.32]);straight(q,[61.27,-16.27,125.32])
    turn(q,[46.27,-16.27,125.32],[46.27,-1.27,125.32])
    turn(q,[46.27,-1.27,110.32],[31.27,-1.27,110.32])
    straight(q,[31.27,-1.27,91.32]);put('XA02',q)
    put('XA02_sleeve',[line([column_x,-33,125],[column_x,-33,143])],2.4)
    # VOUT climbs before the bank, then uses the two ATO inter-module gaps.
    # P_AUX is a complete elevated EAST-entry module, not the old low cage.
    # Bypass the entire E2 receiving plate on its WEST, below its underside,
    # before rising above the bank. No new hole/cutout in a retained plate.
    # The upper eastward lane is NORTH of the XB11 upper return quarter.
    q=[line([36.27,6.35,91.32],[36.27,6.35,108.32])]
    turn(q,[21.27,6.35,108.32],[21.27,6.35,123.32]);straight(q,[-12,6.35,123.32])
    turn(q,[-12,6.35,138.32],[-27,6.35,138.32]);straight(q,[-27,6.35,160])
    turn(q,[-27,21.35,160],[-27,21.35,175]);turn(q,[-12,21.35,175],[-12,36.35,175])
    straight(q,[67,36.35,175]);turn(q,[67,21.35,175],[82,21.35,175]);straight(q,[82,-80.5,175])
    turn(q,[67,-80.5,175],[67,-95.5,175]);turn(q,[67,-80.5,175],[52,-80.5,175])
    straight(q,[52,-45.25-math.sqrt(800),175]);offset(q,[0,1,0],[0,0,-20])
    turn(q,[37,-45.25,155],[37,-30.25,155]);straight(q,[28,-30.25,155]);put('XA03',q)
    # Power return to G_AUX.2, kept separate from platform/signal returns.
    q=[line([41.27,1.27,91.32],[41.27,1.27,105.32])]
    # Rise east of the WHOLE south lid-removal space, not at its near edge.
    # This separates the wire topology from the fuse service operation.
    turn(q,[56.27,1.27,105.32],[56.27,1.27,120.32]);straight(q,[121.27,1.27,120.32])
    turn(q,[121.27,-13.73,120.32],[136.27,-13.73,120.32])
    turn(q,[136.27,-13.73,135.32],[136.27,-28.73,135.32]);straight(q,[136.27,-28.73,150])
    turn(q,[121.27,-28.73,150],[121.27,-28.73,165]);offset(q,[-1,0,0],[0,7.68,0])
    straight(q,[-78,-21.05,165]);offset(q,[-1,0,0],[0,0,z-165])
    straight(q,[-117,-21.05,z]);put('XA04',q)
    # Main ground feed uses the open top, then drops before the ground fanout.
    q=[line([101.5,53.5,155],[125.5,53.5,155])]
    turn(q,[125.5,53.5,170],[140.5,53.5,170]);turn(q,[125.5,53.5,170],[125.5,53.5,185])
    straight(q,[-30,53.5,185]);turn(q,[-30,38.5,185],[-45,38.5,185]);straight(q,[-45,-1.3,185])
    turn(q,[-60,-1.3,185],[-60,-16.3,185]);straight(q,[-78,-16.3,185]);offset(q,[-1,0,0],[0,0,z-185])
    straight(q,[-117,-16.3,z]);put('XA05',q)
    # G_TAIL.1 uses the open top, outside the retained F_TY source approach.
    q=[line([-117,-35.3,z],[-80,-35.3,z])]
    turn(q,[-80,-35.3,z+15],[-65,-35.3,z+15]);straight(q,[-65,-35.3,156])
    turn(q,[-50,-35.3,156],[-50,-35.3,171]);offset(q,[1,0,0],[0,9.8,0]);straight(q,[46.5,-25.5,171])
    turn(q,[46.5,-25.5,156],[61.5,-25.5,156]);turn(q,[46.5,-25.5,156],[46.5,-25.5,141])
    straight(q,[37.5,-25.5,141]);put('XA06',q)
    # Custom + genuine FHAC factory input. A straight, supported eight-mm
    # lap with 20mm finished sleeve, not an unexplained extension.
    # Fan outward to the NORTH of both the VOUT entry and G_TAIL approach
    # before changing levels. Two crossing XZ U-turns in the same Y plane
    # cannot be resolved by nudging their radii or heads.
    q=[line([28,-25.5,155],[37,-25.5,155])]
    turn(q,[37,-10.5,155],[52,-10.5,155]);turn(q,[52,-10.5,170],[52,4.5,170])
    turn(q,[37,4.5,170],[37,4.5,185]);straight(q,[-20,4.5,185])
    turn(q,[-20,-10.5,185],[-35,-10.5,185]);straight(q,[-35,-70.125,185])
    turn(q,[-35,-70.125,170],[-35,-85.125,170]);straight(q,[-35,-85.125,135])
    turn(q,[-50,-85.125,135],[-50,-85.125,120]);straight(q,[-78,-85.125,120]);put('XB11',q)
    put('F_HY_factory_in',[line([-115,-85.125,120],[-70,-85.125,120])],2)
    put('XB11_sleeve',[line([-84,-85.125,120],[-64,-85.125,120])],2.4)
    # Separate formed copper fanouts before full jacket diameter. Individually
    # insulated above the assigned component-side solder land, no pad/PCB
    # exception for a full1mm2 conductor through a1.02mm drill.
    for n,y,dx in [('XA02',-1.27,-5),('XA04',1.27,5)]:
        sign=1 if dx>0 else -1
        b=[36.27,y,84.32];q=[line(b,[36.27,y,86.32])]
        turn(q,[36.27+sign,y,86.32],[36.27+sign,y,87.32]);straight(q,[36.27+dx-sign,y,87.32])
        turn(q,[36.27+dx-sign,y,88.32],[36.27+dx,y,88.32]);straight(q,[36.27+dx,y,94.32]);put(n+'_bare',q,math.sqrt(1/math.pi))
    put('XA03_bare',[line([36.27,6.35,84.32],[36.27,6.35,94.32])],math.sqrt(1/math.pi))
    return dict(status='WHOLE_W1_CANDIDATE_NOT_SELECTED',selected=False,physical_pass=False,
      W1_complete=False,routes=routes,F_AUX_case_mm=[input_x,3.5,138.875,output_x,25.5,159.125],
      F_AUX_roll_deg=90,F_AUX_side_service_mm=[input_x+13.5,-31.5,146,output_x-15.5,3.5,156],
      F_AUX_input_port='P_REAR.1',P_REAR_port5='unselected W5 reservation, unchangedE2 port4',
      P_AUX_pose=dict(pivot_mm=[8,-84.75,99.99],yaw_deg=-90,translation_mm=[10.5,49.75,55.01]),
      G2_pose=dict(pivot_mm=[92,84.75,99.99],yaw_deg=90,translation_mm=[0,-40.75,55.01]),G_TAIL_XA06_port=1,
      W4_paired_ground_head_mm=[41.1,-40.325,143.325,45.9,-36.825,147.825],
      P_AUX_roles={'1':'XB11 F_HY source','2':'XA03 AUX VOUT','3':'W5 reserved','4':'W5 reserved','5':'W5 reserved'},
      tier_allocation_mm={'cases_entry':155,'AUX_GND_crossing':165,'G_TAIL_return':171,'long_free_arches':185},
      topology_change_after_two_rejects='Two elevated EAST-entry WAGO modules, entryZ155 and casing top159.5: P_AUX centre18.5/-35, G2centre92/39. No case over an ATO service opening. Horizontal F_AUX above E2 receiving plate, source on free same-positive P_REAR.1. VOUT crosses above both complete casings at175 then returns through the inter-module aisle. Retained E2/W3/W4 conductors stay fixed; shared W4 tie head goes on TOP of the same band, explicitly rechecked (bottom conflicts with actual E2 native receiver). Functional free wire arches185mm, upper cosmetic shell off, no torso-side widening.',
      pad_registration=dict(source='hardware/manufacturing/one-batch-prototype-r20/fixed-aux-interface.json',translation_mm=[19,0,-71.2802],basis='Same three supplier-drilled bearing coordinates and orientation as CurrentBoardMounts; component-side solder, not full1mm2 through drill',delivered_revision_gate=True),
      native_changes_required=['Matched carrier-rooted elevated WAGO receiving floors; F_AUX floor on existing E2 plate, no routing cutout through retained structural load paths','Independent AUX three-wire insulation comb on carrier, never on unknown pads','P_AUX1/2 separate insulation seat; G2.5 plate-rooted seat','G_AUX1/2/5 seats coordinated with retained3/4 relief','G_TAIL1 separate relief on E2 fixture','FHAC casing retention, both exit grips, two insulated splice grips'],
      assembly=['All power/USB absent; carrier passages and captive anchors before boards','Prepare measured factory/custom supported splices off PETG; no bare copper outside individual insulation','Component-side AUX pad joints only after supplier registration and delivered fit check','Lay all six circuits, then insulation grips, then casing restraints; levers and ATO lid remain accessible','Support soldered board ends when servicing; free WAGO ends and cut only designated ties'],
      assumptions=['FHACOD4/R6 and84.5mm usable factory lead are delivery assumptions, not catalogL140','HELU1mm2 OD2.5/fixedR15; nominal CAD length is dry-fit stock basis, not measured delivered length','Functional wires may rise above omitted upper cosmetic shell; fixed torso sides are not widened'],
      formed_end_insulation=dict(material='Temflex165',layers=2,added_radius_mm=.33,jacket_overlap_mm=3,delivery_solder_land_gate=True),
      factory_custom_joints={'XA02':dict(factory_tip_mm=[column_x,-33,130],custom_tip_mm=[column_x,-33,138],strip_each_mm=8,sleeve_raw_mm=18,sleeve_envelope_mm=[125,143]),'XB11':dict(factory_tip_mm=[-70,-85.125,120],custom_tip_mm=[-78,-85.125,120],strip_each_mm=8,sleeve_raw_mm=20,sleeve_envelope_mm=[-84,-64])},
      assigned_pairs=[['XA02','F_AUX_factory_out'],['XA02_sleeve','XA02'],['XA02_sleeve','F_AUX_factory_out'],['XB11','F_HY_factory_in'],['XB11_sleeve','XB11'],['XB11_sleeve','F_HY_factory_in']]+[[n,n+'_bare'] for n in ('XA02','XA03','XA04')])

def preflight():
    tick=time.monotonic();p=build();save('whole-layout-plan.json',p)
    paths={n:makewire(q['parts']) for n,q in p['routes'].items()}
    r=dict(status='PENDING',contacts=[],pairs=0,errors=[],lengths_mm={},minimum_radii_mm={},selected=False,physical_pass=False)
    for n,w in paths.items():
        r['lengths_mm'][n]=w.Length
        for a,b in zip(w.Edges,w.Edges[1:]):
            gap=(a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length
            dot=a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))
            if gap>1e-5 or dot<1-1e-5:r['errors'].append(dict(wire=n,gap=gap,dot=dot))
        radii=[e.Curve.Radius for e in w.Edges if hasattr(e.Curve,'Radius')]
        r['minimum_radii_mm'][n]=min(radii or [1e9])
    peers={}
    for folder,filename in [('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        old=json.loads((BASE/folder/filename).read_text())
        for n,q in old['routes'].items():
            if 'reserved' not in n and n!='F_HY_input_prefix':peers['retained/'+n]=(makewire(q['parts']),q['radius'])
    assigned={frozenset(v) for v in p['assigned_pairs']}
    for i,n in enumerate(paths):
        c=paths[n];rad=p['routes'][n]['radius']
        for m,(t,rr) in {**{k:(paths[k],p['routes'][k]['radius']) for k in list(paths)[i+1:]},**peers}.items():
            if frozenset((n,m)) in assigned or not near(c,t,rad+rr):continue
            r['pairs']+=1;distance=c.distToShape(t);d=distance[0]
            if d<rad+rr-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rad+rr,witness_mm=[list(v) for v in distance[1][0]]))
    r['factory_budgets']={n:dict(route_mm=paths[n].Length,minimum_usable_assumption_mm=84.5,margin_mm=84.5-paths[n].Length) for n in ('F_AUX_factory_out','F_HY_factory_in')}
    r['unfused_XA01_blank_mm']=paths['XA01_factory'].Length+11
    r.update(status='REJECTED_WHOLE_CURVE_ALLOCATION' if r['contacts'] or r['errors'] else 'CURVE_ALLOCATION_ONLY_NATIVE_AND_SOLID_GATES_OPEN',worker_seconds=round(time.monotonic()-tick,3),source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    save('whole-layout-preflight.json',r)
    print(json.dumps(r),flush=True)

def current_scene(reader,p):
    targets,torso=F.physical_scene(reader)
    source=BASE/'head-supply-checkpoint/HeadSupplyCurrent.FCStd'
    targets['UpperCarrier001']=reader.shape(source,'UpperCarrier001')
    foundation=reader.shape(source,'Foundation');foundation.translate(A.Vector(-42,0,25));targets['Foundation']=foundation
    for n in reader.doc(source):
        if n.startswith('W3Ref_'):
            s=reader.shape(source,n)
            if s.Solids:targets[n]=s
    mounts=BASE/'mounting-checkpoint/RetentionMountsAssembly.FCStd'
    for n in ('P_AUX_CP2','G2_CP2'):
        s=reader.shape(mounts,n)
        pose=p['P_AUX_pose' if n=='P_AUX_CP2' else 'G2_pose']
        s.rotate(A.Vector(*pose['pivot_mm']),A.Vector(0,0,1),pose['yaw_deg']);s.translate(A.Vector(*pose['translation_mm']))
        targets[n]=s
    targets['F_AUX_candidate_case']=box(p['F_AUX_case_mm'])
    # Same closed common band, locking head installed on the top run.
    # This frees port1; old W4 wires/native channels do not move. Its changed
    # purchased envelope still requires clearance/access, not a waiver.
    targets['W4_TieHead_PairedSourceGround']=box(p['W4_paired_ground_head_mm'])
    return targets,torso

def solid_gate():
    tick=time.monotonic();p=build();save('whole-layout-plan.json',p)
    reader=SavedShapes();targets,torso=current_scene(reader,p)
    save('current-obstacle-bounds.json',{n:bounds(s) for n,s in targets.items() if s.Solids})
    r=dict(status='PENDING',pairs=0,contacts=[],reservation_conflicts=[],errors=[],selected=False,physical_pass=False)
    def check(n,c,rr,m,t,pose=None,reservation=False):
        if not t.Solids or not near(c,t,rr):return
        if not t.isValid():r['errors'].append(dict(object=m,reason='invalid obstacle'));return
        r['pairs']+=1;result=c.distToShape(t);d=result[0]
        if d<rr-1e-4:
            hit=dict(a=n,b=m,distance_mm=d,required_mm=rr,witness_mm=[list(v) for v in result[1][0]],pose=pose)
            r['reservation_conflicts' if reservation else 'contacts'].append(hit)
    paths={n:makewire(q['parts']) for n,q in p['routes'].items()}
    mouths={('XA03','P_AUX_CP2'):'end',('XB11','P_AUX_CP2'):'start',('XA05','G2_CP2'):'start',
      ('XA01_factory','P_REAR'):'start',('XA06','G_TAIL'):'end',('XA04','W3Ref_G_AUX_case'):'end',
      ('XA05','W3Ref_G_AUX_case'):'end',('XA06','W3Ref_G_AUX_case'):'start',
      ('F_HY_factory_in','W3Ref_F_HY_case'):'start',('XA01_factory','F_AUX_candidate_case'):'end',('F_AUX_factory_out','F_AUX_candidate_case'):'start'}
    def outside_mouth(c,which):
        edges=list(c.Edges);i=0 if which=='start' else -1;e=edges[i]
        assert e.Length>=9-1e-6,('short assigned insulation prefix',e.Length)
        if abs(e.Length-9)<1e-6:edges.pop(i)
        else:
            u=e.getParameterByLength(9 if which=='start' else e.Length-9)
            edges[i]=e.Curve.toShape(u,e.LastParameter) if which=='start' else e.Curve.toShape(e.FirstParameter,u)
        return Part.Wire(edges)
    for n,c in paths.items():
        rr=p['routes'][n]['radius']
        for m,t in targets.items():
            if n.endswith('_bare') and m=='AUX4092NominalPCB':continue # Exact assigned component-side solder lands only.
            cc=outside_mouth(c,mouths[n,m]) if (n,m) in mouths else c
            check(n,cc,rr,m,t,reservation=m.endswith('_CP2') or 'NominalPCB' in m or m.endswith('_case'))
        print('W1 solid gate',n,'contacts',len(r['contacts']),'reservations',len(r['reservation_conflicts']),flush=True)
        save('whole-layout-solid-progress.json',r)
    for name in ('F_AUX_candidate_case','P_AUX_CP2','G2_CP2'):
        case=targets[name]
        assert case.isValid() and case.Solids,name
        for n,t in targets.items():
            if n==name or not t.Solids or not near(case,t,0):continue
            r['pairs']+=1;v=sum(a.common(b).Volume for a in case.Solids for b in t.Solids)
            if v>1e-5:r['contacts'].append(dict(a=name,b=n,volume_mm3=v))
    head=targets['W4_TieHead_PairedSourceGround']
    for n,t in targets.items():
        if n=='W4_TieHead_PairedSourceGround' or not t.Solids or not near(head,t,0):continue
        r['pairs']+=1;v=sum(a.common(b).Volume for a in head.Solids for b in t.Solids)
        if v>1e-5:r['contacts'].append(dict(a='changed_W4_tie_head',b=n,volume_mm3=v))
    # Do not spend a nine-pose movement gate on a statically rejected layout.
    if not r['contacts'] and not r['reservation_conflicts'] and not r['errors']:
        for y in (-15,0,15):
            for pitch in (-10,0,5):
                group=F.H.head(reader,y,pitch)
                for m,t in group.items():
                    if m=='Foundation':continue
                    for n,c in paths.items():check(n,c,p['routes'][n]['radius'],'head/'+m,t,[y,pitch])
    r.update(status='SOLID_CLEARANCE_ONLY_MOUNTS_OPEN' if not r['contacts'] and not r['reservation_conflicts'] and not r['errors'] else 'REJECTED_WHOLE_SOLID_ALLOCATION',worker_seconds=round(time.monotonic()-tick,3),source_sha256=reader.hashes)
    save('whole-layout-solid-checks.json',r)
    print(json.dumps({k:r[k] for k in ('status','contacts','reservation_conflicts','errors','pairs','worker_seconds')}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--inventory',action='store_true');parser.add_argument('--solids',action='store_true');args=parser.parse_args()
    inventory() if args.inventory else solid_gate() if args.solids else preflight()

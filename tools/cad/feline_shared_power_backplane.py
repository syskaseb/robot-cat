"""One shared upper-power/side-compute architecture inside the200mm body.

No battery/bank/drive/SKU change. S0 longitudinal high in the central lane;
Pi's complete44-part occupied-edge kit at the positive flank. Preserve S1
and PWM source geometry. Case/core gate precedes any new detailed mount.
"""
import hashlib
import itertools
import json
import math
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np

from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_candidate_collision_scene import Scene
from feline_pwm_board_shelf import build,source_inputs
from feline_fore_power_pair import SolidQueries,actual_s0_mouths,all_current_blockers


def fast_inputs():
    """Constructor guard from named source records, before heavy world load."""
    from types import SimpleNamespace
    file=OUT/'n01-full-material-scene.json';doc=json.loads(file.read_text());parts={};meta={}
    bundle=ROOT/doc['bundle'];assert sha(bundle)==doc['bundle_sha256']
    with zipfile.ZipFile(bundle) as z:
        for row in doc['parts']:
            if row.get('role')!='S0' and not row['name'].startswith(('Ref_Material_MAIN_','Ref_Material_Power_MAIN','MAIN_CommonRelief','MAINTie','Ref_Material_JPWM_')):continue
            blob=z.read(row['entry']);assert hashlib.sha256(blob).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(blob.decode());parts[row['name']]=s;meta[row['name']]=row
    plan=json.loads((OUT/'n01-flat-station-architecture.json').read_text())
    name=next(r for r in plan['stations'] if r['ref']=='P_SYS')['source_part_record']['name']
    found=None
    for filename in ('n01-full-material-scene.json','n01-lower-bay-world-probe.json','n01-common-restraint-world-probe.json','n01-remaining-selected-inventory.json'):
        d=json.loads((OUT/filename).read_text())
        for rr in d['parts']:
            if rr['name']==name:found=(ROOT/d['bundle'],rr)
    assert found,'Missing pinned P_SYS source record'
    bundle,row=found
    with zipfile.ZipFile(bundle) as z:blob=z.read(row['entry'])
    assert hashlib.sha256(blob).hexdigest()==row['sha256']
    s=Part.Shape();s.importBrepFromString(blob.decode());parts[row['name']]=s;meta[row['name']]=row
    _,pi,rows=packed(OUT/'n01-coupled-clocked-joints.json')
    for n,s in pi.items():
        if rows[n]['group']=='PiCoupled':parts[n]=s;meta[n]=rows[n]
    # Current relief/ties override the historical source with the same name.
    for filename in ('n01-lower-bay-world-probe.json','n01-common-restraint-world-probe.json','n01-remaining-selected-inventory.json'):
        d=json.loads((OUT/filename).read_text());bundle=ROOT/d['bundle'];assert sha(bundle)==d['bundle_sha256']
        with zipfile.ZipFile(bundle) as z:
            for row in d['parts']:
                if not row['name'].startswith(('MAIN_CommonRelief','MAINTie')):continue
                blob=z.read(row['entry']);assert hashlib.sha256(blob).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(blob.decode());parts[row['name']]=s;meta[row['name']]=row
    return SimpleNamespace(parts=parts,meta=meta,pins={},wire=lambda n:n.startswith(('PiGPIO:','PiPower:','PiUSBData')))


def proposal(world,fore_upper=False,shared_fore=False,supported_fore=False):
    source=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())
    _,_,s1,_=build(*source_inputs())
    s0={n:s.copy() for n,s in world.parts.items() if world.meta[n].get('role')=='S0'}
    assert len(s0)==11
    origin=s0['Ref_Material_S0_body_CP2_0_0'].BoundBox.Center
    original={n:s.copy() for n,s in s0.items()}
    # Both original M10 barrel mouths point UP and OUT,30deg above horizontal
    # in the final transverse plane. No change to ring, stud, nut or washer.
    clocks={'IN':60.,'OUT':-90.}
    for side,angle in clocks.items():
        name='Ref_Material_S0_ring_'+side+'_0_0';stud=s0['Ref_Material_S0_stud_'+side+'_0_0'].BoundBox.Center
        pivot=A.Vector(stud.x,-1,stud.z);rot=A.Rotation(A.Vector(0,1,0),angle)
        s0[name].Placement=A.Placement(pivot-rot.multVec(pivot),rot)*s0[name].Placement
    intrinsic=[];queries=SolidQueries()
    for side in ('IN','OUT'):
        n='Ref_Material_S0_ring_'+side+'_0_0';other='OUT' if side=='IN' else 'IN'
        for m in ('Ref_Material_S0_body_CP2_0_0',*(f'Ref_Material_S0_{part}_{other}_0_0' for part in ('ring','stud','washer','nut'))):
            gap=queries.distance(s0[n],s0[m]);v=None
            if gap<1e-6:
                common=s0[n].copy().common(s0[m].copy());assert common.isValid();v=common.Volume
            datum=dict(part=n,other=m,gap_mm=gap,positive_common_mm3=v,required_mm=0 if '_body_' in m else 1.25)
            if '_body_' in m and (v or 0)>1e-5:
                inherited=original[n].copy().common(original[m].copy());assert inherited.isValid()
                extra=common.cut(inherited);assert extra.isNull() or extra.isValid()
                datum.update(inherited_nominal_terminal_mate_mm3=inherited.Volume,
                             NEW_overlap_outside_inherited_mate_mm3=extra.Volume,
                             source_body_includes_nominal_terminal_interface_not_new_material_waiver=True)
                datum.update(classification='SUPPLIER_INTERFACE_HOLD',
                    basis='whole_cat_interior.py: S0 family reserve includes stud space, NOT exact HELLA casing; check_source_contact_insulation.py treats own nominal case/terminal pairs as supplier gates',
                    requires_delivered_terminal_recess_and_reclocking_fit=True,
                    physical_clearance_claimed=False)
            intrinsic.append(datum)
    rotation=A.Rotation(A.Vector(0,0,1),90 if fore_upper else -90)
    if shared_fore:rotation=A.Rotation(A.Vector(0,1,0),-10)*rotation
    local={}
    for n,s in s0.items():
        t=s.copy();t.Placement=A.Placement(-rotation.multVec(origin),rotation)*t.Placement;local[n]=t
    stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
    psys=world.parts[next(r for r in stations if r['ref']=='P_SYS')['source_part_record']['name']]
    body=local['Ref_Material_S0_body_CP2_0_0']
    target=A.Vector(psys.optimalBoundingBox().XMax+1.25-body.optimalBoundingBox().XMin,0,
                    112-4-max(s.optimalBoundingBox().ZMax for s in local.values()))
    if fore_upper:target.x=-141.5+4-body.optimalBoundingBox().XMin
    tf=A.Placement(target-rotation.multVec(origin),rotation)
    endpoints=json.loads((OUT/'n01-current-endpoint-packet-r3.json').read_text())['endpoints']
    mouths=actual_s0_mouths(s0,[r for r in endpoints if r['group']=='S0'],tf)
    for s in s0.values():s.Placement=tf*s.Placement
    s1change={}
    if shared_fore:
        from receive_feline_global_case_candidates import placement
        datum=json.loads((OUT/'n01-intrinsic-s1-whole-pose.json').read_text())
        old=source['fore_outboard_budget']['pose'];origin1=np.array(datum['centre_mm'])
        oldr=np.array(old['rotation_rows']);newr=np.array([[0,0,-1],[1,0,0],[0,-1,0]])
        lower=s1['Ref_Material_current_S1_body_CP2_0_0'].BoundBox.ZMin
        newcentre=np.array([old['centre_mm'][0],old['centre_mm'][1],lower+21])
        rel=placement(newr,newcentre-newr@origin1)*placement(oldr,np.array(old['centre_mm'])-oldr@origin1).inverse()
        for s in s1.values():s.Placement=rel*s.Placement
        if supported_fore:
            roll=A.Rotation(A.Vector(1,0,0),-135)
            spin=A.Placement(A.Vector(*newcentre)-roll.multVec(A.Vector(*newcentre)),roll)
            for s in s1.values():s.Placement=spin*s.Placement
            dz=39.77-min(s.optimalBoundingBox().ZMin for s in s1.values())
            for s in s1.values():s.translate(A.Vector(0,0,dz))
            newr=np.array([list(roll.multVec(A.Vector(*v))) for v in np.eye(3)]).T@newr
            newcentre[2]+=dz
        s1change=dict(centre_mm=newcentre.tolist(),rotation_rows=newr.tolist(),control_axis='+X',
                      immutable_purchased_pinwheel_preserved=True,old900_and36_receipts_NOT_reused=True)
    pi_path=OUT/'n01-coupled-clocked-joints.json';pi_doc,pi_all,pi_records=packed(pi_path)
    pi={n:(world.parts[n] if n in world.parts else s).copy() for n,s in pi_all.items() if pi_records[n]['group']=='PiCoupled'}
    assert len(pi)==44
    board='Ref_Material_Pi4NominalPCB_0_0';current=pi[board].BoundBox.Center
    # Recover the CURRENT physical board frame, not an older nominal tilt.
    # The board's long edge, occupied USB edge and GPIO housing select signs.
    planar=max((f for f in pi[board].Faces if type(f.Surface).__name__=='Plane'),key=lambda f:f.Area)
    normal=planar.normalAt(0,0);normal.normalize()
    if normal.dot(pi['PiBudget:GPIO_header'].BoundBox.Center-current)<0:normal=-normal
    edge=max((e for e in planar.OuterWire.Edges if type(e.Curve).__name__=='Line'),key=lambda e:e.Length)
    long=edge.Vertexes[-1].Point-edge.Vertexes[0].Point;long.normalize()
    if long.dot(pi['PiBudget:USB_A_data_boot'].BoundBox.Center-current)<0:long=-long
    across=normal.cross(long);across.normalize();matrix=A.Matrix()
    for i in range(3):
        for j,col in enumerate((long,across,normal)):setattr(matrix,f'A{i+1}{j+1}',col[i])
    oldrot=A.Rotation(matrix);newrot=A.Rotation(A.Vector(1,0,0),90)
    relative=newrot*oldrot.inverted()
    pi_tf=A.Placement(A.Vector(0,0,32)-relative.multVec(current),relative)
    for s in pi.values():s.Placement=pi_tf*s.Placement
    out=max(s.optimalBoundingBox().YMax for s in pi.values());plane_shift=100-4-out
    for s in pi.values():s.translate(A.Vector(0,plane_shift,0))
    pi_tf.Base=pi_tf.Base+A.Vector(0,plane_shift,0)
    if fore_upper:
        # Retain the already coupled, upper Pi board orientation. Only whole
        # translation follows S0's new key end and full bought USB boot edge.
        pi={n:(world.parts[n] if n in world.parts else s).copy() for n,s in pi_all.items() if pi_records[n]['group']=='PiCoupled'}
        usb=pi['PiBudget:USB_A_data_boot']
        dx=s0['Ref_Material_S0_key_CP2_0_0'].BoundBox.XMax+6-usb.BoundBox.XMin
        front_limit=dx
        if shared_fore:
            doc=json.loads((OUT/'n01-full-material-scene.json').read_text())
            busmin=min(r['bounds_mm'][0][0] for r in doc['parts'] if r['name'].startswith('Ref_Material_BUSsupplier'))
            rear_limit=busmin-1.25-max(s.optimalBoundingBox().XMax for s in pi.values())
            assert rear_limit>dx,'No complete Pi occupied-edge bay between front key and fixed BUS'
            # Use the centre of the shared WHOLE-kit bay, not a 0.15mm fix
            # to the first witness and not boot-only clearance as before.
            dx=(dx+rear_limit)/2
        pi_tf=A.Placement(A.Vector(dx,0,0),A.Rotation())
        for s in pi.values():s.Placement=pi_tf*s.Placement
    main={};mainfacts={}
    if fore_upper:
        main={n:s.copy() for n,s in world.parts.items() if n.startswith(('Ref_Material_MAIN_','Ref_Material_Power_MAIN','MAIN_CommonRelief','MAINTie'))}
        assert len(main)>=12
        mainboard=main['Ref_Material_MAIN_CurrentMainSupplierReference_0_0']
        # Reverse each COMPLETE selected M2 fastener stack at its actual hole,
        # then place the whole carrier above the bank (not into its TE row).
        for i in (0,1):
            names=[n for n in main if n.startswith('Ref_Material_MAIN_'+str(i)+'_')]
            assert len(names)==4
            pivot=main[f'Ref_Material_MAIN_{i}_shaft_0_0'].BoundBox.Center
            pivot.z=91;rot=A.Rotation(A.Vector(1,0,0),180)
            for n in names:main[n].Placement=A.Placement(pivot-rot.multVec(pivot),rot)*main[n].Placement
        dy=(-76-mainboard.BoundBox.Center.y) if shared_fore else math.ceil(s0['Ref_Material_S0_key_CP2_0_0'].BoundBox.YMax+1.25-mainboard.BoundBox.YMin)
        dx=(-20-mainboard.BoundBox.Center.x) if shared_fore else 0
        bankdoc=json.loads((OUT/'n01-full-material-scene.json').read_text())
        banktop=max(r['bounds_mm'][1][2] for r in bankdoc['parts'] if '_CP2_Housing_' in r['name'] and r['name'].startswith('Ref_Material_F_L'))
        dz=banktop+1.25-min(s.BoundBox.ZMin for s in main.values())
        mt=A.Placement(A.Vector(dx,dy,dz),A.Rotation())
        for s in main.values():s.Placement=mt*s.Placement
        from plan_feline_front_service_split import line_tube
        for e in endpoints:
            if e['group']!='MAIN':continue
            q=mt.multVec(A.Vector(*e['point_mm']));d=A.Vector(*e['departure_axis'])
            n='End:'+e['id'];main[n]=line_tube(list(q),list(q+d*12),1.05)
        # Old carrier/ties were on the wrong side of the now reversed screws.
        # Replace their planning budgets together, never waive those contacts.
        oldrelief=[n for n in main if n.startswith(('Ref_Material_Power_MAIN','MAIN_CommonRelief','MAINTie'))]
        for n in oldrelief:main.pop(n)
        lands=[s for n,s in main.items() if n.startswith('End:')]
        centres=sorted(s.BoundBox.Center.x for s in lands);y=lands[0].BoundBox.Center.y
        z0=min(s.BoundBox.ZMin for s in lands);lo,hi=centres[0]-1.25,centres[-1]+1.25
        comb=Part.makeBox(hi-lo,4.5,9,A.Vector(lo,y-1.25,z0))
        for x in centres:
            channel=Part.makeCylinder(1.25,11,A.Vector(x,y,z0-1))
            channel=channel.fuse(Part.makeBox(2.5,3,11,A.Vector(x-1.25,y-3,z0-1)))
            comb=comb.cut(channel)
        # Both selected tie budgets enclose the entire comb/four jackets.
        # Head blocks are provisional stock envelopes, not manufacturer CAD.
        for i,z in enumerate((z0+1,z0+5)):
            # Full-width front strap groove, .25mm axial/face allowance.
            # Without it the web between adjacent jackets cuts the strap.
            comb=comb.cut(Part.makeBox(hi-lo+2,.7,3,A.Vector(lo-1,y-1.5,z-.25)))
            outer=Part.makeBox(hi-lo+3,6.7,2.5,A.Vector(lo-1.5,y-2.25,z))
            inner=Part.makeBox(hi-lo+.6,4.3,4.5,A.Vector(lo-.3,y-1.05,z-1))
            main[f'MAINNewTie{i}']=outer.cut(inner)
            main[f'MAINNewTie{i}:head_budget']=Part.makeBox(5,6,3,A.Vector((lo+hi)/2-2.5,y+4.45,z-.25))
        main['MAINNewCommonComb']=comb.removeSplitter()
        mainfacts=dict(relative_translation_mm=[dx,dy,dz],complete_two_fastener_stacks_reversed=True,
            bank_top_mm=banktop,full_first12_jacket_lands_preserved=True,
            old_MAIN_middle_routes_invalidated_not_translated=True,root_to_frame_and_tools_OPEN=True)
        mainfacts.update(retired_old_relief_parts=oldrelief,new_shared_comb_and_two_full_tie_budgets=True,
                         own_relief_clearance_pending=True)
    actual_pi_mates=[]
    for n,s in world.parts.items():
        if n.startswith('CurrentBUS:USB') and 'Pi' in n and 'Overmould' in n:
            t=s.copy();t.Placement=pi_tf*t.Placement;pi[n]=t;actual_pi_mates.append(n)
    retired=set(s0)|set(pi)|set(main)
    if fore_upper:retired.update(oldrelief)
    invalid_wires={r['wire'] for r in endpoints if r['group'] in (('S0','Pi4','MAIN') if fore_upper else ('S0','Pi4'))}
    for n in world.parts:
        r=world.meta[n]
        if world.wire(n) and (r.get('wire_owner') in invalid_wires or any(w+'/' in n or n==w for w in invalid_wires)):retired.add(n)
        if r.get('role')=='ScaffoldPlanning' and any(x in n for x in ('S0','Pi4')):retired.add(n)
    pwm=json.loads((OUT/'n01-pwm-board-shelf.json').read_text());retired.update(pwm['retired_whole_owner'])
    if fore_upper:retired.add('RetainedMAINCutForeCap')
    parts={**s0,**s1,**pi,**main}
    groups={n:'S0' if n in s0 else 'S1' if n in s1 else 'MAINUpper' if n in main else 'PiUpper' if fore_upper else 'PiSide' for n in parts}
    kinds={n:pi_records.get(n,world.meta.get(n,{})).get('kind','actual_source') for n in parts}
    if fore_upper:
        for n in main:
            if n.startswith('End:'):kinds[n]='proposal_wire'
            elif n.startswith('MAINNewTie'):kinds[n]='project_stock_reservation'
            elif n=='MAINNewCommonComb':kinds[n]='proposal_material'
    extras={};extrafacts={}
    if shared_fore:
        extras,extragroups,extrakinds,extrafacts=shared_fore_extras(world,s0,s1,pi,supported_fore)
        retired.update(extrafacts['retired_parts'])
        parts.update(extras);groups.update(extragroups);kinds.update(extrakinds)
        usbparts,usbrec=pi_usb_escape(pi,{**parts,**packed(OUT/'n01-pwm-board-shelf.json')[1]})
        parts.update(usbparts);extrafacts['PiUSB_changed_profile']=usbrec
        if supported_fore:
            newroot,rootfacts=pwm_root_behind_control(s1)
            parts['ShelfPWM:carrier']=newroot;groups['ShelfPWM:carrier']='PWMRoot';kinds['ShelfPWM:carrier']='proposal_material'
            retired.add('ShelfPWM:carrier');extrafacts['PWM_changed_root']=rootfacts
    facts=dict(status='CONSTRUCTIVE_SHARED_POWER_BACKPLANE_PROPOSAL',selected=False,N01_complete=False,physical_pass=False,
        whole_power_core_gate_complete=False,S0_centre_mm=list(target),S0_rotation_quaternion=list(rotation.Q),
        functional_architecture='SHARED_FORE_S0_TILTED_S1_AXIAL_FHY_FLANK_MAIN_OPPOSITE' if shared_fore else 'FORE_S0_KEY_AFT_UPPER_PI_MAIN_OVER_BANK' if fore_upper else 'REJECTED_CENTRAL_S0_SIDE_PI',
        reuse_original_S1_pose=not shared_fore,S1_changed_pose=s1change,shared_fore_units=extrafacts,
        MAIN_whole_changed_unit=mainfacts,
        S0_source_clocks_degrees=clocks,S0_intrinsic_ring_receipts=intrinsic,source_S0_mouths=mouths,
        Pi_actual_PCB_centre_mm=list(pi[board].BoundBox.Center),Pi_selected_complete_kit_parts=len(pi),
        Pi_inherited5_GPIO_R10_and9_after_turn_and_both_USB_edges_preserved=True,
        Pi_relative_pose=dict(translation_mm=list(pi_tf.Base),rotation_quaternion=list(pi_tf.Rotation.Q)),
        Pi_whole_bay_translation_interval_mm=[front_limit,rear_limit] if shared_fore else None,
        Pi_current_frame_from_geometry=dict(long_axis=list(long),normal=list(normal),across=list(across)),
        Pi_extra_actual_data_mates=actual_pi_mates,retired_whole_owners=sorted(retired),
        invalidated_custom_wire_middles=sorted(invalid_wires),battery_bank_drives_unchanged=True,
        reserved_outer_budget_mm=dict(torso=[325,200,160],new_outer_extreme_margin_mm=4),
        planned_true_outer='Shared mid-flank refinement inside max200; actual containment remains required, not a boxed-shell PASS',
        open=['Whole case/port/motion gate','S0 supplier terminal/case fit remains an explicit delivery gate, not physical clearance','FR body bundle/oldW077 whole redesign',
              'Source6fullfans and new common roots/tool/removal sequence','Other47 variable kits/current123portions246ends/4MTA/full factory lengths','True contour before N01'],
        source_sha256={**world.pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (pi_path,OUT/'n01-source-saddles-whole-joint.json',
             OUT/'n01-pwm-board-shelf.json',OUT/'n01-current-endpoint-packet-r3.json',Path(__file__))}})
    return parts,groups,kinds,facts


def shared_fore_extras(world,s0,s1,pi,supported_fore=False):
    """Opposite fore fuse/under-PWM junction as complete source-owned units."""
    from plan_feline_front_bulkhead_architecture import tube
    from plan_feline_front_service_split import line_tube
    from feline_s1_flexible_fans import saddle_shapes
    old,source,rr=packed(OUT/'n01-fore-topology.json')
    original=source['ForeFHAC:case'];rot=A.Rotation(A.Vector(0,1,0),90)
    # First3 is a project cap transition plus a separate FULL9 factory grip.
    # Allocate it with the whole100mm blank and both joints, not just a box.
    R=12.4;first=12.;external=97.;jacket=1.7
    centre=A.Vector(-138.25+jacket+first+R+25.5,62.65,112-3.25-1.2-20.25/2)
    tf=A.Placement(centre-rot.multVec(original.BoundBox.Center),rot)
    case=original.copy();case.Placement=tf*case.Placement
    parts={'ForeFHAC:case':case};groups={};kinds={};facts=[]
    b=case.BoundBox
    # Nominal body saddle and one complete case tie, with a side head.
    parts['ForeFHAC:common_body_saddle']=Part.makeBox(b.XLength,b.YLength,2,A.Vector(b.XMin,b.YMin,b.ZMin-2))
    outer=Part.makeBox(2.5,b.YLength+2.4,b.ZLength+4.4,A.Vector(centre.x-1.25,b.YMin-1.2,b.ZMin-3.2))
    inner=Part.makeBox(4.5,b.YLength,b.ZLength+2,A.Vector(centre.x-2.25,b.YMin,b.ZMin-2))
    parts['ForeFHAC:case_tie_budget']=outer.cut(inner)
    parts['ForeFHAC:case_tie_head_budget']=Part.makeBox(6,6,6,A.Vector(centre.x-3,b.YMax+1.2,centre.z-3))
    for recipe in old['fore_recipes']:
        q=tf.multVec(A.Vector(*recipe['point_mm']));d=rot.multVec(A.Vector(*recipe['departure_axis']))
        assert abs(abs(d.x)-1)<1e-6
        bend=A.Vector(0,1,0) if d.x>0 else A.Vector(0,0,-1)
        a=q+d*first;end=a+bend*(2*R);mid=a+d*R+bend*R
        tip=end-d*(external-first-math.pi*R)
        spine=Part.Wire([Part.makeLine(q,a),Part.Arc(a,mid,end).toShape(),Part.makeLine(end,tip)])
        assert abs(spine.Length-external)<1e-5
        pre='ForeFHAC:'+recipe['side']
        parts[pre+':factory97']=tube(spine,jacket);kinds[pre+':factory97']='proposal_wire'
        parts[pre+':sleeve20']=line_tube(list(tip+d*14),list(tip-d*6),2.4);kinds[pre+':sleeve20']='proposal_wire'
        parts[pre+':custom26']=line_tube(list(tip+d*8),list(tip-d*18),1.55);kinds[pre+':custom26']='proposal_wire'
        for label,start,axis,radius in (('factory',q+d*3,d,jacket),('custom',tip-d*9,-d,1.55)):
            row=dict(grip_start_mm=list(start),grip_axis=list(axis),jacket_radius_mm=radius)
            for k,s in saddle_shapes(row,180,90).items():
                name=pre+':'+label+':'+k;parts[name]=s
                kinds[name]='proposal_material' if k=='saddle' else 'project_stock_reservation'
        facts.append(dict(side=recipe['side'],mouth_mm=list(q),axis=list(d),R_mm=R,
            first_project_transition_mm=3,first_full9_mm=[list(q+d*3),list(a)],external_factory_mm=spine.Length,internal_assumed_mm=3,
            nominal_factory_blank_mm=100,factory100_is_provisional=True,sleeve_mm=20,lap_mm=8,
            factory_end_mm=list(tip),custom_grip9_mm=[list(tip-d*9),list(tip-d*18)]))
    for n in parts:groups[n]='ForeFHAC';kinds.setdefault(n,'project_stock_reservation' if 'budget' in n else 'proposal_material' if 'saddle' in n else 'actual_source')
    retired={n for n,r in rr.items() if r['group']=='ForeFHAC'}
    # Nominal selected JPWM unit relocates as a whole; four guide registrations
    # remain explicitly separate from manufacturer mating geometry.
    name='Ref_Material_JPWM_0_0';original=world.parts[name];j=original.copy()
    pwm=json.loads((OUT/'n01-pwm-board-shelf.json').read_text())
    # PCB bottom comes from actual source board in the existing38part packet.
    _,pb,pr=packed(OUT/'n01-pwm-board-shelf.json')
    board=next(s for n,s in pb.items() if 'NominalPCB' in n)
    target=A.Vector(original.BoundBox.Center.x,-51,board.BoundBox.ZMin-1.25-original.BoundBox.ZLength/2)
    if supported_fore:
        target.y=s1['Ref_Material_current_S1_control_CP2_0_0'].BoundBox.YMin-1.25-original.BoundBox.YLength/2
    shift=target-original.BoundBox.Center;j.translate(shift)
    parts[name]=j;groups[name]='JPWM';kinds[name]='actual_source';retired.add(name)
    return parts,groups,kinds,dict(F_HY_case_centre_mm=list(centre),F_HY_full_factory_ports=facts,
        F_HY_unchanged_purchased_case_and_two_provisional100_blanks=True,JPWM_relative_translation_mm=list(shift),
        JPWM_four_guide_registration_and_full_relief_OPEN=True,retired_parts=sorted(retired),
        frame_roots_tools_whole_fore_shared_gate_OPEN=True)


def pwm_root_behind_control(s1):
    """Move the WHOLE load path behind the S1 control, retaining all37 peers."""
    from feline_pwm_board_shelf import box
    doc,parts,rows=packed(OUT/'n01-pwm-board-shelf.json')
    old=parts['ShelfPWM:carrier'];root=doc['shared_backbone_join']['root_bounds_mm'];x0=(root[0][0]+root[1][0])/2
    board=next(s for n,s in parts.items() if 'NominalPCB' in n);top=board.BoundBox.ZMin-1.25
    removed=box([x0-3,-60,34.69],[x0+3,-54,top])
    retained=old.cut(removed)
    # Negative bank is staggered12mm from positive bank. Use the ACTUAL
    # named R1/R2 gap recorded in the pinned source geometry, not L1's gap.
    data=json.loads((OUT/'n01-full-material-scene.json').read_text())
    bank={r['name']:r['bounds_mm'] for r in data['parts']}
    right=bank['Ref_Material_F_R1_CP2_Housing_0_0'][1][0]
    left=bank['Ref_Material_F_R2_CP2_Housing_0_0'][0][0]
    x=(right+left)/2;assert left-right>=8.5
    post=box([x-3,-60,34.7],[x+3,-54,top])
    # Outboard crossbeam avoids BOTH complete underside washer rows. A
    # short aft return reaches the finite rail behind the PCB/key, not
    # through the bought board or the S1 control.
    bridge=box([x0-3,-70.95,top-3],[x+3,-64.95,top])
    aftreturn=box([x-3,-70.95,top-3],[x+3,-54,top])
    new=retained.fuse(post).fuse(bridge).fuse(aftreturn).removeSplitter()
    assert new.isValid() and len(new.Solids)==1,('Invalid or disconnected root',new.isValid(),len(new.Solids))
    added=new.cut(old);assert added.isNull() or added.isValid()
    q=SolidQueries();checks=[]
    for n,t in parts.items():
        if n=='ShelfPWM:carrier':continue
        from feline_solid_distance import bbox_lower_bound
        if bbox_lower_bound(added.BoundBox,t.BoundBox)>=.2:continue
        gap=q.distance(added,t);checks.append(dict(other=n,gap_mm=gap,required_mm=.2))
    return new,dict(source_carrier_sha256=rows['ShelfPWM:carrier']['sha256'],root_centre_X_mm=x,
        named_R1_R2_full_case_gap_mm=[right,left],root_bounds_mm=[[x-3,-60,34.7],[x+3,-54,top]],
        root_mate='StructureReserve:BankBed-1',expected_shared_slab_union_mm3=108,
        unchanged_PWM_peers=37,added_material_own_checks=checks,
        own_failures=[r for r in checks if r['gap_mm']<.2-1e-6],old_key_crossing_column_removed=True,
        printed_shared_structure_union_is_not_a_purchased_or_wire_waiver=True)


def pi_usb_escape(pi,owned):
    """One source-pinned full R30/after9 profile, planned with ALL owned bays."""
    from plan_feline_front_bulkhead_architecture import tube
    from plan_feline_front_service_split import line_tube
    cap=min((f for f in pi['PiUSBData'].Faces if type(f.Surface).__name__=='Plane'),
            key=lambda f:(f.CenterOfMass-pi['PiBudget:USB_A_data_boot'].BoundBox.Center).Length)
    q=cap.CenterOfMass;d=-cap.normalAt(0,0);d.normalize()
    assert abs(cap.Area-math.pi*2.5**2)<1e-4
    n=A.Vector(0,1,0);n=n-d*n.dot(d);n.normalize();v=d.cross(n)
    gates=[];cache=SolidQueries()
    for clock in (0,90,45,-45,-90,135,-135,180):
        b=n*math.cos(math.radians(clock))+v*math.sin(math.radians(clock))
        a=q+d*3;mid=a+d*(30/math.sqrt(2))+b*(30*(1-1/math.sqrt(2)))
        end=a+d*30+b*30;tip=end+b*9
        wire=tube(Part.Wire([Part.makeLine(q,a),Part.Arc(a,mid,end).toShape()]),2.5)
        grip=line_tube(list(end),list(tip),2.5);fail=[]
        for name,s in (('PiUSBData',wire),('PiUSBData:grip',grip)):
            bb=s.optimalBoundingBox()
            if bb.ZMax>108.75+1e-6 or bb.ZMin< -44.75-1e-6 or bb.YMax>96.75+1e-6 or bb.YMin< -96.75-1e-6:
                fail.append(dict(part=name,kind='absolute_box_budget'));continue
            for other,t in owned.items():
                if other.startswith('PiUSBData') or other in ('PiBudget:USB_A_data_boot','PiBudget:USB_A_rear','PiBudget:USB_A_front'):continue
                minimum=.2 if other.startswith(('PiGPIO:','PiPower:','PWM:XS','PWM:XL','End:')) else 1.25
                from feline_solid_distance import bbox_lower_bound
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                gap=cache.distance(s,t)
                if gap<minimum-1e-6:fail.append(dict(part=name,other=other,gap_mm=gap,required_mm=minimum))
        gates.append(dict(clock_degrees=clock,failures=fail))
        if not fail:return dict(PiUSBData=wire,**{'PiUSBData:grip':grip}),dict(
            status='OWNED_BAYS_PROFILE_CLEAR_EXTERNAL_WORLD_STILL_OPEN',mouth_mm=list(q),departure_axis=list(d),
            R_mm=30,first_project_mm=3,bend_unit=list(b),grip9_mm=[list(end),list(tip)],
            source='Actual saved pipe cap adjacent to selected occupied USB boot; not new manufacturer data',
            candidates=gates,physical_pass=False)
    return {},dict(status='NO_PROFILE_IN_BOUNDED_EIGHT_CLOCK_FAMILY',candidates=gates,physical_pass=False)


def intrinsic_failures(receipts):
    """Own nominal supplier envelope is a HOLD, never a physical PASS.

    Continue independent external space planning as historical source policy
    permits. Real ring-to-other-terminal metal separation remains mandatory.
    """
    return [r for r in receipts if r.get('classification')!='SUPPLIER_INTERFACE_HOLD'
            and ((r['positive_common_mm3'] or 0)>1e-5 or r['gap_mm']<r['required_mm']-1e-6)]


def main_own_receipt(parts,groups,target='MAINUpper'):
    tick=time.monotonic();members=[(n,s) for n,s in parts.items() if groups[n]==target]
    rows=[];errors=[]
    for (n,s),(m,t) in itertools.combinations(members,2):
        if not s.BoundBox.intersect(t.BoundBox):continue
        try:
            c=s.copy().common(t.copy());assert c.isNull() or c.isValid()
            lap=(target=='ForeFHAC' and n.rsplit(':',1)[0]==m.rsplit(':',1)[0]
                 and {n.rsplit(':',1)[-1],m.rsplit(':',1)[-1]}<= {'factory97','sleeve20','custom26'})
            rows.append(dict(part=n,other=m,positive_common_mm3=c.Volume,
                             named_8mm_lap_or_filled_joint_budget=lap))
        except Exception as e:errors.append(dict(part=n,other=m,error=repr(e)))
    return dict(scope='All complete MAIN owned solids positive penetration; bearing contact allowed, no torque/strength or physical supplier fit claim',
                parts=len(members),pairs=rows,failures=[r for r in rows if r['positive_common_mm3']>1e-5 and not r['named_8mm_lap_or_filled_joint_budget']],
                errors=errors,worker_seconds=round(time.monotonic()-tick,3))


def reconcile_supported_root(packet_path=None):
    """Receive only wrongly externalized own mates; no external pair waived.

    Old105 own pairs remain valid on the retained SUBSET. Added material is
    independently .2mm clear of every one of the unchanged37 peers. Repair
    the slab datum from its actual pinned3mm BRep, not a lower rail recipe.
    """
    tick=time.monotonic();dest=packet_path or OUT/'n01-supported-fore-layout.json'
    doc,parts,records=packed(dest);pwm,peers,oldrows=packed(OUT/'n01-pwm-board-shelf.json')
    assert not pwm['internal_assembly']['failures'] and not pwm['internal_assembly']['errors']
    name='ShelfPWM:carrier';old=peers.pop(name);new=parts[name]
    assert oldrows[name]['sha256']==pwm['internal_assembly']['geometry_sha256'][name]
    added=new.cut(old);assert added.isValid() and added.Solids
    q=SolidQueries();checks=[]
    for n,t in peers.items():
        assert oldrows[n]['sha256']==pwm['internal_assembly']['geometry_sha256'][n]
        from feline_solid_distance import bbox_lower_bound
        lower=bbox_lower_bound(added.BoundBox,t.BoundBox)
        gap=lower if lower>=.2 else q.distance(added,t)
        assert gap>=.2-1e-6,(n,gap)
        checks.append(dict(other=n,certified_gap_lower_bound_mm=gap,broad_phase_separation=lower>=.2))
    rec=doc['all_current_blockers'];assert rec['status']=='ALL_CURRENT_POWER_BLOCKERS_RECEIVED_NOT_N01'
    mate='StructureReserve:BankBed-1'
    reportrow=next(r for r in rec['pairs'].values() if r['part']==name and r['other']==mate)
    if mate in parts:slab=parts[mate]
    else:
        data=json.loads((OUT/'n01-full-material-scene.json').read_text())
        rr=next(r for r in data['parts'] if r['name']==mate)
        assert rr['sha256']==reportrow['owner_meta']['sha256']
        with zipfile.ZipFile(ROOT/data['bundle']) as z:blob=z.read(rr['entry'])
        assert hashlib.sha256(blob).hexdigest()==rr['sha256'];slab=Part.Shape();slab.importBrepFromString(blob.decode())
    bb=slab.optimalBoundingBox();assert abs(bb.ZLength-3)<1e-5
    c=new.common(slab);assert c.isValid()
    lo,hi=doc['shared_fore_units']['PWM_changed_root']['root_bounds_mm']
    foot=Part.makeBox(hi[0]-lo[0],hi[1]-lo[1],3,A.Vector(lo[0],lo[1],bb.ZMin))
    outside=c.cut(foot);assert outside.isNull() or outside.isValid()
    assert outside.Volume<1e-5 and abs(c.Volume-108)<1e-5
    prior=[]
    for key,row in rec['pairs'].items():
        if row['part']!=name:continue
        if row['other'] in peers:
            prior.append(row.copy());row.update(kind='OWNED_CARRIER_SUBSET_PLUS_CLEAR_ADDITION',
                inherited_internal_105_pair_receipt='n01-pwm-board-shelf.json',minimum_external_NOT_applicable=True)
        elif row['other']==mate:
            prior.append(row.copy());row.pop('error',None)
            row.update(kind='NAMED_SHARED_STRUCTURE_UNION',positive_common_mm3=c.Volume,
                       actual_slab_Z_mm=[bb.ZMin,bb.ZMax],native_union_pending_N03=True)
    def corrected(row):return row.get('part')==name and (row.get('other') in peers or row.get('other')==mate)
    rec['failures']=[r for r in rec['failures'] if not corrected(r)]
    rec['errors']=[r for r in rec['errors'] if not corrected(r)]
    rec['immutable_S1_critical900_and_PWM380_pairs_reused']=False
    doc['PWM_root_ownership_reconciliation']=dict(prior_external_semantics_and_wrong_slab_rows=prior,
        unchanged_internal_pairs=105,all37_added_material_checks=checks,slab_union_mm3=c.Volume,
        actual_slab_Z_mm=[bb.ZMin,bb.ZMax],source_sha256={
            'n01-pwm-board-shelf.json':sha(OUT/'n01-pwm-board-shelf.json'),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,physical_pass=False)
    dest.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status='NAMED_OWNED_MATES_RECEIVED_NOT_EXTERNAL_CLEARANCE',seconds=round(time.monotonic()-tick,3),
        all37_added_checks=len(checks),slab_union=c.Volume,remaining_failures=len(rec['failures']),remaining_errors=rec['errors'])),flush=True)


def main():
    supported_fore='--supported-fore' in sys.argv
    shared_fore='--shared-fore' in sys.argv or supported_fore;fore_upper='--fore-upper' in sys.argv or shared_fore
    tick=time.monotonic();dest=OUT/('n01-supported-fore-layout.json' if supported_fore else 'n01-common-fore-layout.json' if shared_fore else 'n01-shared-power-backplane-fore.json' if fore_upper else 'n01-shared-power-backplane.json')
    assert not dest.exists(),'Receive existing shared architecture before another calculation'
    # Catch constructor and own-interface mistakes without reloading the
    # whole motion/static scene on every wrapper repair.
    pilotparts,pilotgroups,_,pilot=proposal(fast_inputs(),fore_upper,shared_fore,supported_fore)
    if supported_fore:assert not pilot['shared_fore_units']['PWM_changed_root']['own_failures'],pilot['shared_fore_units']['PWM_changed_root']['own_failures']
    bad=intrinsic_failures(pilot['S0_intrinsic_ring_receipts'])
    if bad:print(json.dumps(dict(status='S0_INTRINSIC_REJECTED_BEFORE_WORLD',failures=bad)),flush=True);return
    own=main_own_receipt(pilotparts,pilotgroups) if fore_upper else None
    if own and (own['failures'] or own['errors']):
        print(json.dumps(dict(status='MAIN_OWN_REJECTED_BEFORE_WORLD',receipt=own)),flush=True);return
    fhy=main_own_receipt(pilotparts,pilotgroups,'ForeFHAC') if shared_fore else None
    if fhy and (fhy['failures'] or fhy['errors']):
        print(json.dumps(dict(status='FHY_OWN_REJECTED_BEFORE_WORLD',receipt=fhy)),flush=True);return
    world=Scene();parts,groups,kinds,facts=proposal(world,fore_upper,shared_fore,supported_fore)
    if own:facts['MAIN_own_penetration_receipt']=own
    if fhy:facts['FHY_own_penetration_receipt']=fhy
    archive=dest.with_suffix('.breps.zip');records=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for i,(n,s) in enumerate(parts.items()):
            assert s.isValid() and s.Solids,n
            raw=s.exportBrepToString().encode();entry=f'{i:03d}.brep';z.writestr(entry,raw)
            records.append(dict(name=n,group=groups[n],kind=kinds[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    facts.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),parts=records,
                 worker_seconds=round(time.monotonic()-tick,3))
    if supported_fore:
        prior=OUT/'n01-common-fore-layout.json'
        facts.update(equivalent_prior_packet=prior.relative_to(ROOT).as_posix(),equivalent_prior_packet_sha256=sha(prior))
    dest.write_text(json.dumps(facts,indent=2)+'\n',encoding='utf-8',newline='\n')
    bad=intrinsic_failures(facts['S0_intrinsic_ring_receipts'])
    print(json.dumps(dict(parts=len(parts),S0_centre=facts['S0_centre_mm'],Pi_centre=facts['Pi_actual_PCB_centre_mm'],intrinsic_failures=bad)),flush=True)
    if not bad:all_current_blockers(dest,world)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True)
    if '--reconcile-root' in sys.argv:reconcile_supported_root()
    elif '--reconcile-receivers-root' in sys.argv:reconcile_supported_root(OUT/'n01-fore-receivers-integrated.json')
    else:main()

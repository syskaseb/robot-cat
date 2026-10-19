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
            if row.get('role')!='S0' and not row['name'].startswith(('Ref_Material_MAIN_','Ref_Material_Power_MAIN','MAIN_CommonRelief','MAINTie')):continue
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


def proposal(world,fore_upper=False):
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
        dy=math.ceil(s0['Ref_Material_S0_key_CP2_0_0'].BoundBox.YMax+1.25-mainboard.BoundBox.YMin)
        bankdoc=json.loads((OUT/'n01-full-material-scene.json').read_text())
        banktop=max(r['bounds_mm'][1][2] for r in bankdoc['parts'] if '_CP2_Housing_' in r['name'] and r['name'].startswith('Ref_Material_F_L'))
        dz=banktop+1.25-min(s.BoundBox.ZMin for s in main.values())
        mt=A.Placement(A.Vector(0,dy,dz),A.Rotation())
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
        mainfacts=dict(relative_translation_mm=[0,dy,dz],complete_two_fastener_stacks_reversed=True,
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
    facts=dict(status='CONSTRUCTIVE_SHARED_POWER_BACKPLANE_PROPOSAL',selected=False,N01_complete=False,physical_pass=False,
        whole_power_core_gate_complete=False,S0_centre_mm=list(target),S0_rotation_quaternion=list(rotation.Q),
        functional_architecture='FORE_S0_KEY_AFT_UPPER_PI_MAIN_OVER_BANK' if fore_upper else 'REJECTED_CENTRAL_S0_SIDE_PI',
        MAIN_whole_changed_unit=mainfacts,
        S0_source_clocks_degrees=clocks,S0_intrinsic_ring_receipts=intrinsic,source_S0_mouths=mouths,
        Pi_actual_PCB_centre_mm=list(pi[board].BoundBox.Center),Pi_selected_complete_kit_parts=len(pi),
        Pi_inherited5_GPIO_R10_and9_after_turn_and_both_USB_edges_preserved=True,
        Pi_relative_pose=dict(translation_mm=list(pi_tf.Base),rotation_quaternion=list(pi_tf.Rotation.Q)),
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


def intrinsic_failures(receipts):
    """Own nominal supplier envelope is a HOLD, never a physical PASS.

    Continue independent external space planning as historical source policy
    permits. Real ring-to-other-terminal metal separation remains mandatory.
    """
    return [r for r in receipts if r.get('classification')!='SUPPLIER_INTERFACE_HOLD'
            and ((r['positive_common_mm3'] or 0)>1e-5 or r['gap_mm']<r['required_mm']-1e-6)]


def main_own_receipt(parts,groups):
    tick=time.monotonic();members=[(n,s) for n,s in parts.items() if groups[n]=='MAINUpper']
    rows=[];errors=[]
    for (n,s),(m,t) in itertools.combinations(members,2):
        if not s.BoundBox.intersect(t.BoundBox):continue
        try:
            c=s.copy().common(t.copy());assert c.isNull() or c.isValid()
            rows.append(dict(part=n,other=m,positive_common_mm3=c.Volume))
        except Exception as e:errors.append(dict(part=n,other=m,error=repr(e)))
    return dict(scope='All complete MAIN owned solids positive penetration; bearing contact allowed, no torque/strength or physical supplier fit claim',
                parts=len(members),pairs=rows,failures=[r for r in rows if r['positive_common_mm3']>1e-5],
                errors=errors,worker_seconds=round(time.monotonic()-tick,3))


def main():
    fore_upper='--fore-upper' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-shared-power-backplane-fore.json' if fore_upper else 'n01-shared-power-backplane.json')
    assert not dest.exists(),'Receive existing shared architecture before another calculation'
    # Catch constructor and own-interface mistakes without reloading the
    # whole motion/static scene on every wrapper repair.
    pilotparts,pilotgroups,_,pilot=proposal(fast_inputs(),fore_upper)
    bad=intrinsic_failures(pilot['S0_intrinsic_ring_receipts'])
    if bad:print(json.dumps(dict(status='S0_INTRINSIC_REJECTED_BEFORE_WORLD',failures=bad)),flush=True);return
    own=main_own_receipt(pilotparts,pilotgroups) if fore_upper else None
    if own and (own['failures'] or own['errors']):
        print(json.dumps(dict(status='MAIN_OWN_REJECTED_BEFORE_WORLD',receipt=own)),flush=True);return
    world=Scene();parts,groups,kinds,facts=proposal(world,fore_upper)
    if own:facts['MAIN_own_penetration_receipt']=own
    archive=dest.with_suffix('.breps.zip');records=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for i,(n,s) in enumerate(parts.items()):
            assert s.isValid() and s.Solids,n
            raw=s.exportBrepToString().encode();entry=f'{i:03d}.brep';z.writestr(entry,raw)
            records.append(dict(name=n,group=groups[n],kind=kinds[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    facts.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),parts=records,
                 worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(facts,indent=2)+'\n',encoding='utf-8',newline='\n')
    bad=intrinsic_failures(facts['S0_intrinsic_ring_receipts'])
    print(json.dumps(dict(parts=len(parts),S0_centre=facts['S0_centre_mm'],Pi_centre=facts['Pi_actual_PCB_centre_mm'],intrinsic_failures=bad)),flush=True)
    if not bad:all_current_blockers(dest,world)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True)
    main()

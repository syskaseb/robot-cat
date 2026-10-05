"""One received-frame mounting/strap proposal before native construction.

Use exact existing supplier nominal M3x16/nut and T18I sizes. All eight axes
are planned together: innerY104 clears the cover/nut pocket; outerY112 retains
edge material. Wire routes and frame roots do not move. Slot allowance and
tightened belt paths are prototype assumptions, not delivered measurements.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math
from servo_fuse_inputs_r1 import save,sha
import w5_received_central_scope as S
import w5_harness_passages_native as N

ROOT=N.ROOT;BASE=N.BASE;PRIOR=BASE/'w5-loom-frames-received-r1'
OUT=BASE/'w5-loom-mount-hardware-r1'
CART=ROOT/'hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json'
TIE=ROOT/'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json'


def build(A,Part,bp,boltdim,nutdim,tiedim):
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    def half_ring(x,y,ri,ro,z,height,back):
        s=Part.makeCylinder(ro,height,A.Vector(x,y,z)).cut(Part.makeCylinder(ri,height+.2,A.Vector(x,y,z-.1)))
        return s.common(box([x if back>0 else x-ro-.1,y-ro-.1,z-.1,x+ro+.1 if back>0 else x,y+ro+.1,z+height+.1]))
    def hexagon(x,y,af,z,height):
        rad=af/math.sqrt(3);v=[A.Vector(x+rad*math.cos(k*math.pi/3),y+rad*math.sin(k*math.pi/3),z) for k in range(6)]
        return Part.Face(Part.makePolygon(v+[v[0]])).extrude(A.Vector(0,0,height))
    frames={};pads={};hardware={};tools={};bands={};spec={};grip_recipes=[];axes=[]
    for leg,group in bp['blueprints'].items():
        x,y=group['root_xy_mm'];side=1 if y>0 else -1;back=1 if leg.startswith('F') else -1
        raw=[box(b) for b in group['raw_boxes'].values()];cutters=[];native_tools=[]
        seat_shapes=[]
        for g in group['grooves']:
            gx,gy,gz=g['origin_mm'];name=g['name'];cz=89.5;lo=cz-1.25;hi=cz+1.25
            raw.append(Part.makeCylinder(g['outer_radius_mm'],g['height_mm'],A.Vector(gx,gy,gz)))
            cutter=Part.makeCylinder(g['inner_radius_mm'],18,A.Vector(gx,gy,76));cutters.extend([cutter,box(g['opening_box_mm'])])
            # Open-side belt touches only assumed cable insulation. Back belt
            # runs outside saddle; two corners and one back channel are freed
            # together while retaining >4mm beam depth below the tie station.
            rear=half_ring(gx,gy,5.5,6.7,lo,2.5,back)
            front=half_ring(gx,gy,2.75,3.95,lo,2.5,-back)
            bridges=[];slot_boxes=[]
            for sign in (-1,1):
                ya,yb=(2.75,6.7) if sign>0 else (-6.7,-2.75)
                bridges.append(box([gx-1.2 if back>0 else gx,gy+ya,lo,gx if back>0 else gx+1.2,gy+yb,hi]))
                ya,yb=(2.55,6.95) if sign>0 else (-6.95,-2.55)
                sb=[gx-1.45 if back>0 else gx-.25,gy+ya,lo-.25,gx+.25 if back>0 else gx+1.45,gy+yb,hi+.25]
                slot_boxes.append(sb);cutters.append(box(sb))
            back_tool=half_ring(gx,gy,5.25,6.95,lo-.25,3,back);cutters.append(back_tool)
            bands[name+'Belt']=Part.makeCompound([rear,front,*bridges])
            # Locking head faces the open north side, not down into the beam.
            # Tangential length4.8(X), radial height3.5(Y), band width4.5(Z).
            head=[gx-2.4,gy+5.8,cz-2.25,gx+2.4,gy+9.3,cz+2.25]
            bands[name+'Head']=box(head)
            grip_recipes.append(dict(loom=name,owner=leg+'FixedFrame',axis_mm=[gx,gy,85],
                belt_station_z_mm=cz,band_width_mm=tiedim['band_width_mm'],band_thickness_mm=tiedim['band_thickness_mm'],
                slot_boxes_mm=slot_boxes,back_channel=dict(inner_radius_mm=5.25,outer_radius_mm=6.95,z_mm=lo-.25,height_mm=3),
                head_box_mm=head,head_dimensions_xyz_mm=[4.8,3.5,4.5],nominal_bundle_OD_mm=5.5,
                clamp_path_provisional=True,pullout_or_creep_not_certified=True))
        # Apply only the received complete reliefs to newly introduced material.
        relief=bp['coupled_correction']['relief_specs']
        for row in relief.get(leg+'FixedFrame',[]):cutters.append(box(row['bounds_mm']))
        pad=box(group['landing_box_mm']);pad_cuts=[box(row['bounds_mm']) for row in relief.get(leg+'DeckLanding',[])]
        for yy in (side*104,side*112):
            label=leg+('_Inner' if abs(yy)==104 else '_Outer')
            bore=Part.makeCylinder(1.7,18,A.Vector(x,yy,94));cutters.append(bore);pad_cuts.append(bore)
            pocket=hexagon(x,yy,5.9,106.3,3);pad_cuts.append(pocket)
            shank=Part.makeCylinder(boltdim['d']/2,boltdim['L'],A.Vector(x,yy,95))
            head=Part.makeCylinder(boltdim['head_d']/2,boltdim['head_h'],A.Vector(x,yy,92))
            hardware[label+'Bolt']=shank.fuse(head)
            hardware[label+'Nut']=hexagon(x,yy,nutdim['AF'],106.3,nutdim['H']).cut(Part.makeCylinder(1.5,3,A.Vector(x,yy,106.2)))
            tools[label+'LowerKeyAccess']=Part.makeCylinder(3,37,A.Vector(x,yy,55))
            tools[label+'NutDrop']=hexagon(x,yy,5.5,106.3,22.7)
            axes.append(dict(leg=leg,axis_mm=[x,yy],frame_stack_mm=[95,101],landing_stack_mm=[101,109],
                bolt_underhead_z_mm=95,bolt_tip_z_mm=111,nut_z_mm=[106.3,108.7],full_nut_thread_engagement_mm=2.4,
                tip_beyond_nut_mm=2.3,captive_pocket_AF_mm=5.9,pocket_floor_z_mm=106.3,
                key_supplier_AF_mm=2.5,lower_access_envelope_diameter_mm=6,key_socket_depth_not_measured=True,
                candidate_screw_sku='SKL000625',candidate_nut_sku='SKL000383',washer_count=0))
        frame=raw[0].multiFuse(raw[1:]).cut(Part.makeCompound(cutters))
        pad=pad.cut(Part.makeCompound(pad_cuts))
        assert frame.isValid() and len(frame.Solids)==1 and pad.isValid() and len(pad.Solids)==1,leg
        frames[leg+'FixedFrame']=frame;pads[leg+'DeckLanding']=pad
        spec[leg]=dict(group,proper_axes_xy_mm=[[x,side*104],[x,side*112]],unused_old_X_holes_not_constructed=True,
                       tie_slot_and_belt_recipes=[r for r in grip_recipes if r['loom'].startswith(leg)])
    return frames,pads,hardware,tools,bands,spec,axes,grip_recipes


def main():
    import FreeCAD as A,Part
    from w5_exact_separation import separated
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    prior=read(PRIOR/'checks.json');assert prior['all_received_pairs_clear']
    assert all(sha(ROOT/k)==v for k,v in {**prior['source_sha256'],**prior['files']}.items())
    bp_path=PRIOR/'native-blueprint.json';bp=read(bp_path)
    cart=read(CART);bolt=next(r for r in cart['rows'] if r['supplier_sku']=='SKL000625')
    nut=next(r for r in cart['rows'] if r['supplier_sku']=='SKL000383');tie=read(TIE)
    assert bolt['dimensions_mm']==dict(d=3,L=16,b=16,head_d=5.5,head_h=3,key=2.5,pitch=.5)
    assert nut['dimensions_mm']['AF']==5.5 and nut['dimensions_mm']['H']==2.4
    assert [tie['band_width_mm'],tie['band_thickness_mm']]==[2.5,1.2]
    OUT.mkdir(parents=True,exist_ok=True)
    frames,pads,hardware,tools,bands,spec,axes,grips=build(A,Part,bp,bolt['dimensions_mm'],nut['dimensions_mm'],tie)
    pins=[Path(__file__),PRIOR/'checks.json',bp_path,CART,TIE]
    fixed,printed,_,_,_,loaded,_,_=S.load(A,Part);pins+=loaded
    for wire,row in read(N.CENTRAL)['routes'].items():
        p=ROOT/row['geometry'];fixed[wire]=Part.read(str(p));pins.append(p)
    for owner in ('SourceWestHood','SourceBankLeft'):
        p=ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1'/(owner+'_CANDIDATE_WORLD.brep')
        if p.exists():printed[owner]=Part.read(str(p));pins.append(p)
    for owner in ('SourceCarrier','SourceCover'):
        p=ROOT/'hardware/cad/studies/w5-side-retention-native-r1'/(owner+'_CANDIDATE_WORLD.brep')
        printed[owner]=Part.read(str(p));pins.append(p)
    p=ROOT/'hardware/cad/studies/w5-central-retention-native-r1/CentralRetentionDeck_CANDIDATE_WORLD.brep'
    printed['SourceDeck']=Part.read(str(p));pins.append(p)
    p=BASE/'w5-loom-common-layout-r3/EastHood_RL_FRAME_PASSAGE_UNSELECTED_WORLD.brep'
    printed['SourceEastHood']=Part.read(str(p));pins.append(p)
    for alias in N.OWNER_ALIASES:printed.pop(alias,None)
    old_file=PRIOR/'FOUR_FRAMES_AND_LANDINGS_RECEIVED_WORLD.brep'
    original=dict(zip(prior['proposal_roles'],Part.read(str(old_file)).childShapes()));pins.append(old_file)
    additions={};new_shapes={**frames,**pads,**hardware,**tools,**bands}
    for key,s in frames.items():
        additions[key]=s.cut(original[key])
        assert additions[key].isValid() and additions[key].Volume<250,(key,additions[key].Volume)
    names=list(new_shapes);p=OUT/'MOUNT_AND_STRAPS_PROPOSED_WORLD.brep'
    Part.makeCompound([new_shapes[k] for k in names]).exportBrep(str(p))
    save(OUT/'native-blueprint.json',dict(groups=spec,axes=axes,grips=grips,roles=names,
        assembly=['Preload8M3nuts from above into captive Deck pockets before installing the Deck.',
                  'Hold each frame under its pad; insert twoM3x16 from below. No washers in this nominal stack; hand adjustment only, clamp torque requires the PETG sample.',
                  'Lay continuous looms sideways into12open saddles, feed T18I through both corner tunnels, then tighten only on insulation; no new electrical joints.',
                  'Frame retention and planned tool access do not qualify joint travel, moving cable grips or whole bank/cover removal.'],
        stock_candidate=dict(installed_M3x16=8,installed_M3nuts=8,installed_T18I=12,new_fixed_frame_prints=4,selected=False),
        supplier_nominal=dict(bolt=bolt,nut=nut,tie=tie),selected=False,W1_complete=False,W5_complete=False,physical_pass=False))
    hits=[];errors=[];pairs=0
    def check(label,s,owner,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox) or separated(a,b):continue
                pairs+=1
                try:
                    common=a.common(b)
                    if common.Volume>1e-6:hits.append(dict(part=label,owner=owner,mm3=common.Volume,
                        bounds_mm=[getattr(common.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as e:errors.append(dict(part=label,owner=owner,error=str(e)))
    # Reuse the57clear received placement pairs. Only fillings from relocated
    # bores add frame material; all other frame changes are subtraction.
    external={**fixed,**printed}
    for key,s in additions.items():
        for owner,t in external.items():check(key+'OldHoleFill',s,owner,t)
    for key,s in {**hardware,**tools,**bands}.items():
        for owner,t in {**external,**frames,**pads}.items():
            if key.endswith('NutDrop') and owner.startswith(key.split('_')[0]+'DeckLanding'):continue
            check(key,s,owner,t)
        # Opposite tool/hardware interfaces are not blanket exemptions; the
        # driving key stops at the bolt's socket face. Nut-drop overlaps its
        # own final nut intentionally and is not tested as installed material.
        for owner,t in hardware.items():
            if owner==key or key.endswith('NutDrop') or key.endswith('LowerKeyAccess'):continue
            check(key,s,owner,t)
        save(OUT/'progress.json',dict(last_part=key,pairs=pairs,hits=hits,errors=errors,updated_utc=datetime.now(timezone.utc).isoformat()))
        print('LOOM_MOUNT',key,'pairs',pairs,'hits',len(hits),'errors',len(errors),flush=True)
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='ONE_FIXED_FRAME_HARDWARE_STRAP_CONTACT_RECEIPT',hits=hits,errors=errors,pairs=pairs,
        frame_fill_volumes_mm3={k:s.Volume for k,s in additions.items()},reused_received_clear_pairs=57,
        all_fastener_stacks_nominal=dict(installed=8,length_mm=16,grip_mm=14,nut_height_mm=2.4,tip_above_nut_mm=2.3),
        native_complete=False,whole_assembly_motion_complete=False,stock_selected=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in set(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [p,OUT/'native-blueprint.json']}))


if __name__=='__main__':main()

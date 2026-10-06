"""CP2 shared interior preflight, NOT printable supports or selected wiring.

One layout covers commercial roles together. Explicit bounding reservations
are not supplier solids. Retained P0/head/tail shapes are tested as actual BReps.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import itertools
import time
import math
import subprocess
import sys

# Preserve two failed shared MTA plans for diagnosis only. Default builds
# retain the good S1 candidate; do not rerun this flag unchanged.
MTA_REPACK = '--mta-candidate-rejected' in sys.argv

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging'
OUT = BASE / 'cp2'
NET = ROOT / 'hardware/electronics/full-cat/connection-map-e4-r1/netlist.json'
BUS = ROOT / 'hardware/electronics/full-cat/pi-bus-primary-r1/PCB.brep'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def splice_inventory():
    """Resolve installed roles vs spare from R53; never occupy spare stock."""
    selection_path=ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json'
    selected=json.loads(selection_path.read_text(encoding='utf-8'))
    stock_path=ROOT/selected['local_fuse_stock']
    catalog_path=selection_path.parent/'nonfastener-catalog.json'
    body_path=ROOT/selected['body_harness']
    stock=json.loads(stock_path.read_text(encoding='utf-8'))['WAGO221412']
    row=next(r for r in json.loads(catalog_path.read_text(encoding='utf-8'))['rows']
             if r['quantity_id']=='splice:WAGO221-412')
    expected={'XB11','W026_output','W037_output','W045_output','W053_output'}
    assert set(stock['installed_roles'])==expected and stock['installed']==5
    assert stock['spare']==1 and row['planning_quantity']==stock['installed']+stock['spare']==6
    assert row['manufacturer_part']=='221-412'
    wires={w['id']:w for w in json.loads(body_path.read_text(encoding='utf-8'))['conductors']}
    assert wires['W077']['b']=='SPLICE_PI.16' and wires['W078']['a']=='SPLICE_PI.18'
    slots=[('Splice_L1_CP2','XB11',['W077','W078']),
           ('Splice_L2_CP2','W026_output',['W026']),
           ('Splice_L3_CP2','W045_output',['W045']),
           ('Splice_R1_CP2','W037_output',['W037']),
           ('Splice_R2_CP2','W053_output',['W053'])]
    baseline=[]
    for slot,role,ids in slots:
        baseline.append(dict(native_slot=slot,electrical_role=role,sku='221-412',
            wires=[dict(id=i,a=wires[i]['a'],b=wires[i]['b']) for i in ids],
            allocation_basis='NEW CP2 identity allocation, old six boxes had NO circuit identity',
            old_mount_or_complete_wiring_qualified=False))
    return dict(status='R53_INSTALLED_ROLES_RECONCILED_CP2_NOT_SELECTED',selected=False,
        physical_pass=False,R53_quantity=6,R53_installed=5,R53_spare=1,
        spare_location='OFF_ROBOT; no native space reservation',
        removed_unbound_slot='Splice_R3_CP2',baseline=baseline,
        catalogue_dimensions_mm=[13,18.3,8.15],planning_reservation_mm=[14,19,9],
        ports_and_levers_supplier_verified=False,
        extra_post_F0_candidate=1,normal_CP2_installed_candidates=6,
        normal_CP2_quantity_candidate_including_spare=7,
        with_four_MTA_source_extensions_installed_candidate=10,
        with_four_MTA_source_extensions_quantity_candidate_including_spare=11,
        four_MTA_output_joints_are_replacements_not_additional=True,
        extra_source_joints_not_selected_purchase=True,full_stock_selection_open=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p)
                       for p in [selection_path,stock_path,catalog_path,body_path]},
        W1_complete=False,W5_complete=False,K3_complete=False)


def main():
    import FreeCAD as A
    import Part
    started = datetime.now(timezone.utc)
    tick = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=True)
    prior = json.loads((OUT/'checks.json').read_text(encoding='utf-8')) if (OUT/'checks.json').exists() else None
    pins = {p.relative_to(ROOT).as_posix(): digest(p) for p in
            [BASE/'WholeCatLayout.FCStd', BASE/'layout.json', NET,
             ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json', BUS,
             ROOT/'hardware/reference/u1-adapter-2026-09-26/source.json',
             ROOT/'hardware/reference/xt60-p0-2026-09-24/README.md',
             ROOT/'hardware/electronics/full-cat/protection-selection-r2/branch-protection.json',
             ROOT/'hardware/cad/studies/wago-p0/r1/dimensions.json',
             ROOT/'hardware/electronics/power-platform/PI-BRANCH.md',
             ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json',
             OUT/'post-f0-splice-source.json',
             ROOT/'tools/electronics/source_switch_layout_r6.py',
             ROOT/'tools/electronics/source_switch_mount_finish_r4.py',
             ROOT/'hardware/electronics/power-platform/switch-terminations-p0.json',
             ROOT/'hardware/reference/manual-stop-p0-2026-09-24/toggle_S.pdf',
             ROOT/'hardware/reference/manual-stop-p0-2026-09-24/130171-RS.pdf',
             ROOT/'hardware/reference/leg-distribution-p0-2026-09-24/README.md',
             ROOT/'hardware/reference/leg-distribution-p0-2026-09-24/MTA-catalogue.pdf']}
    d = A.openDocument(str(BASE/'WholeCatLayout.FCStd'))
    torso = d.getObject('TorsoEnvelope').Shape.copy()
    assert torso.isValid() and len(torso.Solids) == 1
    refs = []
    for ob in list(d.Objects):
        if 'Category' in ob.PropertiesList:
            if ob.Category == 'electronics':
                d.removeObject(ob.Name)
            elif ob.Name != 'BatteryNominal':
                refs.append((ob.Name, ob.Shape.copy(), ob.Category))
    # Replace only the Pi reservation; retained battery/chassis references stay.
    rows, shapes = [], {}
    g = d.addObject('App::DocumentObjectGroup', 'InteriorReservations')
    g.Label = 'CP2: wspólny układ, bryły rezerwacji NIE części do druku'

    def box(name, origin, size, group, basis, shell=True, rotation=None):
        o = d.addObject('Part::Box', name)
        o.Length, o.Width, o.Height = size
        o.Placement.Base = A.Vector(*origin)
        if rotation is not None:o.Placement.Rotation=rotation
        g.addObject(o)
        o.addProperty('App::PropertyString', 'DimensionBasis'); o.DimensionBasis = basis
        o.addProperty('App::PropertyString', 'Role'); o.Role = name
        d.recompute()
        shapes[name] = o.Shape.copy()
        bb=o.Shape.BoundBox
        rows.append(dict(name=name, origin_mm=[bb.XMin,bb.YMin,bb.ZMin],
                         size_mm=[bb.XLength,bb.YLength,bb.ZLength],group=group,
                         local_size_mm=size,placement_base_mm=origin,
                         rotation_quaternion=list(o.Placement.Rotation.Q),
                         dimension_basis=basis, require_internal_shell=shell))

    box('Pi4_CP2', [-31 if MTA_REPACK else -19,-28,42], [85,56,22], 'logic', '85x56 PCB; populated height22 prototype reserve; experimental move not mount qualification')
    box('MAIN4853_CP2', [-66,-5,42], [30.5,24,12], 'logic', '22.9x30.5x7.7 supplier board + solder reserve; rotated90Z beside source bay',
        rotation=A.Rotation(A.Vector(0,0,1),90))
    # Actual Waveshare vendor geometry, NOT the unrelated U1 SSOP/DIP adapter.
    old_layout=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
    bus_key=BUS.relative_to(ROOT).as_posix()
    if prior and prior['source_sha256'].get(bus_key)==pins[bus_key]:
        # Source and placement unchanged: reuse bounded evidence, not a costly
        # repeat of the same invalid vendor compound check.
        bus_reference_valid=prior['BUS_vendor_compound_valid']
        br=next(r for r in old_layout['components'] if r['name']=='BUS_CP2')
        bus_origin,bus_size=br['origin_mm'],br['size_mm']
    else:
        bs=Part.Shape();bs.read(str(BUS));assert len(bs.Solids)==117
        bus_reference_valid=bs.isValid()
        bs.Placement=A.Placement(A.Vector(103.0120752,-20.98790452,44.60000348467585),A.Rotation(A.Vector(0,0,1),90))
        bb=bs.BoundBox;bus_origin=[bb.XMin,bb.YMin,bb.ZMin];bus_size=[bb.XLength,bb.YLength,bb.ZLength]
    if MTA_REPACK:bus_origin=[110,bus_origin[1],bus_origin[2]]
    box('BUS_CP2',bus_origin,bus_size, 'logic',
        'Waveshare25514 full vendor envelope rotated90Z; cached117-solid compound invalid, envelope only NOT exact fit')
    box('Monitor_CP2', [-4 if MTA_REPACK else -44,30,50], [41,25,12], 'logic', 'P309 supplier41x25x12; pin exits/clip/lead still provisional')
    box('PWM9685_CP2', [-39,-12.7,78], [62.5,25.4,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    box('AUX4092_CP2', [35,-12.7,78], [18.8,25.4,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    box('PWM1608_CP2', [70,-25.4,78], [43.18,50.8,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    # Panel flange + TE assemblies + bend space are ONE envelope, not fictitious catalog depth.
    for side, y in [('L',58), ('R',-58)]:
        centres=[-53,-23,7,37,67,97] if side=='L' else [-53,-21,11,43,75,107]
        for i, x in enumerate(centres, 1):
            box(f'F_{side}{i}_CP2', [x-14,y-13,70], [28,26,64], 'fuses',
                'MTA0300330 flange28x15, below panel24.5; TE-IN23.749/OUT21.717; '
                'engagement e=0 provisional; remaining height is ATO/bend budget, NOT measured fit')
    names = [['FL_P','FL_G','D_FL','RL_P','RL_G'],
             ['FR_P','FR_G','D_FR','RR_P','RR_G'],
             ['P_SYS','P_FRONT','P_REAR','G1','G2'],
             ['D_RL','D_RR','P_AUX','G_AUX','G_TAIL']]
    wanted = {e['b'] for e in json.loads(NET.read_text(encoding='utf-8'))['edges'] if e['kind']=='internal_bus'}
    assert wanted == {n for r in names for n in r}, 'Every logical bus must have exactly one place'
    for y,ns in zip([79.5,-79.5],names[:2]):
        for x,name in zip([-45,-10,25,60,95],ns):
            box(name+'_CP2',[x-15,y-4.5,111 if MTA_REPACK else 75],[30,19,9],'wago',
                '221-41530x19x9 planning bounds; rotate-90X: both wire entries point DOWN; lever face needs side-cover access',
                rotation=A.Rotation(A.Vector(1,0,0),-90))
    central=[(22,[(-40,'P_FRONT'),(7,'P_SYS'),(47,'P_REAR'),(84,'D_RL'),(120,'G2')]),
             (-22,[(-40,'G1'),(0,'D_RR'),(40,'P_AUX'),(80,'G_AUX'),(120,'G_TAIL')])]
    for y,sites in central:
        for x,name in sites:
            size=[37,22,11] if name in ['P_SYS','P_FRONT','P_REAR','G1'] else [30,19,9]
            if name=='P_SYS':
                box('P_SYS_CP2',[-11.5,33.5,95],size,'wago',
                    '221-615 rotate+90X entries UP; nominal port2 local[13,22,5.5], NOT supplier pin datum',
                    rotation=A.Rotation(A.Vector(1,0,0),90))
            elif name=='G1':
                box('G1_CP2',[-56.1,-39.5,125.5],size,'wago',
                    '221-615 DOWN entry; nominal port1 local[5.5,22,5.5]; G1.1 battery role retained, physical datums provisional',
                    rotation=A.Rotation(A.Vector(1,0,0),-90))
            elif name=='P_FRONT':
                box('P_FRONT_CP2',[-58.5,33,130.2],size,'wago',
                    '221-615 entries DOWN at108.2; nominal port1[5.5,22,5.5]; shared S1 output approach, all physical datums provisional',
                    rotation=A.Rotation(A.Vector(1,0,0),-90))
            elif name=='P_REAR':
                box('P_REAR_CP2',[50.5,38.5,110],size,'wago',
                    '221-615 entries+X; nominal port1[5.5,22,5.5]; common S1 rear return, no old mount qualification',
                    rotation=A.Rotation(A.Vector(0,0,1),-90))
            else:
                by=-16 if name=='D_RR' else 0 if name in ['P_REAR','G2'] else y
                if name=='D_RL':x=94;by=0
                if name=='G2':x=129
                box(name+'_CP2',[x-size[0]/2,by-size[1]/2,110],size,'wago',
                    'SKU-specific221-615/415 planning bounds; G1 moved to front for battery minus; not an old qualified route')
    splice_roles=splice_inventory()
    pins.update(splice_roles['source_sha256'])
    allocations={r['native_slot']:r for r in splice_roles['baseline']}
    for y, prefix in [(55,'L'),(-55,'R')]:
        for i, x in enumerate([-43,0,43],1):
            name=f'Splice_{prefix}{i}_CP2'
            if name not in allocations:continue # Sixth purchased item is a spare.
            if MTA_REPACK and allocations[name]['electrical_role']!='XB11':continue # Output joints replace these roles.
            origin=([-94,-25,40] if i==1 else [-55,-12,40]) if prefix=='R' and i in [1,2] else [70,-64.5,40] if prefix=='R' and i==3 else [x-15,y-9.5,40]
            origin=[origin[0]+8,origin[1],origin[2]]
            box(name,origin,[14,19,9],'splices',
                '221-412 catalogue13x18.3x8.15, planning14x19x9; '+allocations[name]['electrical_role']+
                '; allocation NEW, full leads/old mount NOT qualified')
            ob=d.getObject(name);ob.Label=allocations[name]['electrical_role']+' CP2'
            ob.addProperty('App::PropertyString','ElectricalRole');ob.ElectricalRole=allocations[name]['electrical_role']
    box('PostF0Splice_CP2',[51.5,-54.3,12],[14,19,9],'splices',
        'Additional candidate221-412 AFTER F0; catalogue13x18.3x8.15/strip11; entriesUP; port/pitch/lever datums provisional',
        rotation=A.Rotation(A.Vector(1,0,0),90))
    mta_sites=[('FL',-45,38),('RL',70,38),('FR',-45,-38),('RR',70,-38)] if MTA_REPACK else []
    for name,x,y in mta_sites:
        box('MTA_'+name+'_CP2', [x+11,y-17.5,42], [35,22,16], 'inline',
            '0100335 family35x22x16 rotated90Z; BOTH exits alongY, centreZ50. '
            'Lower pair corridors beside battery; catalogue L140 is NOT100mm per side; original mounts unqualified',
            rotation=A.Rotation(A.Vector(0,0,1),90))
    if not MTA_REPACK:
        for name,x,y in [('FL',-35,84),('RL',55,84),('FR',-35,-84),('RR',55,-84)]:
            box('MTA_'+name+'_CP2',[x-17.5,y-11,80],[35,22,16],'inline',
                '0100335 rolled family budget35x22x16; BOTH exit faces retained; exact L140 length unknown')
    # Protection is the highest central layer. Both factory exits retained;
    # no WAGO tray must be removed merely to reach an ATO or inline cover.
    # Supplier51 max length/20.25 max width; thickness22 is an explicit prototype budget.
    fhac_sites = [('F_PI',-58.5,4.875),('F_AUX',61.5,4.875),
                  ('F_HY',-58.5,-25.125),('F_HP',1.5,-25.125),('F_TY',61.5,-25.125)]
    for name,x,y in fhac_sites:
        box(name+'_CP2', [x,y,125], [51,20.25,22], 'inline',
            'FHAC0001ZXJ length50+/-1,width20+/-0.25; horizontal X-axis lid UP; thickness22 ASSUMED; both leads89.5+/-5 incl strip6.35+/-2')
    box('F0_CP2', [-48,-68.925,39], [51,20.25,22], 'inline',
        'FHAC0002ZXJ horizontalX source bay; length51max/width20.25max; thickness22/lead11mm above floor/R10/OD4.5 ASSUMED')
    box('F_PWM_CP2', [15,8,128], [28,8,9], 'inline',
        '0242.100UAT1 axial fuse with insulation/strain relief;28x8x9 assembly budget NOT catalog dimension; no separate holder')
    box('XT60_CP2', [-96.9,-54.2,45.3], [23.9,16.4,9.2], 'inline',
        'AMASS own housing only, rotated90X; cups atworldX-73/Y-58.8/Z50,57 are PROVISIONAL pitch7. Read marked polarity; mate/release still OPEN',
        rotation=A.Rotation(A.Vector(1,0,0),90))
    # S0 family model includes stud space, NOT exact HELLA SKU casing.
    for name,z,r,h,shell in [('S0_body_CP2',65,28.5,40,True),
                              ('S0_neck_CP2',105,11,3,True),
                              ('S0_key_CP2',108,15,63.5,False)]:
        o=d.addObject('Part::Cylinder', name);o.Radius=r;o.Height=h
        o.Placement.Base=A.Vector(-77,16,z);g.addObject(o);d.recompute()
        shapes[name]=o.Shape.copy()
        rows.append(dict(name=name,origin_mm=[-77-r,16-r,z],size_mm=[2*r,2*r,h],group='switch',
                         dimension_basis='Existing HELLA family reserve rotated vertical; studs/lugs/opening conditional',
                         require_internal_shell=shell))
    box('S1_body_CP2', [114.2,37,64], [24,37,42], 'switch',
        'NKK S821 body24x42 with axial34+3 budget, axis+Y; terminal bearing offset4 ASSUMED, panel aperture OPEN')
    o=d.addObject('Part::Cylinder','S1_control_CP2');o.Radius=14;o.Height=34
    o.Placement=A.Placement(A.Vector(126.2,74,85),A.Rotation(A.Vector(1,0,0),-90));g.addObject(o);d.recompute()
    shapes[o.Name]=o.Shape.copy()
    rows.append(dict(name=o.Name,origin_mm=[112.2,74,71],size_mm=[28,34,28],group='switch',
                     rotation_quaternion=list(o.Placement.Rotation.Q),
                     dimension_basis='12mm bushing+22mm lever, +/-28deg conservative cylinder axis+Y; external operator/aperture OPEN, NOT wider belly',
                     require_internal_shell=False))
    print('Shared layout:',len(rows),'modules;20 buses,12 holders/24 ends,6 existing+1 candidate post-F0 splice,4 MTA,5 branch FHAC+F0+axial F_PWM',flush=True)

    access=[]
    ag=d.addObject('App::DocumentObjectGroup','ServiceReservations')
    ag.Label='CP2: nominalne przestrzenie narzędzi, NIE ruch zmierzony producenta'
    def service(name,target,origin,size,basis):
        o=d.addObject('Part::Box',name);o.Length,o.Width,o.Height=size
        o.Placement.Base=A.Vector(*origin);ag.addObject(o);d.recompute()
        o.addProperty('App::PropertyString','DimensionBasis');o.DimensionBasis=basis
        access.append(dict(name=name,target=target,origin_mm=origin,size_mm=size,
                           dimension_basis=basis,supplier_motion_verified=False))
    for r in rows:
        if r['group']=='fuses':
            x,y,z=r['origin_mm'];dx,dy,dz=r['size_mm']
            service('Access_'+r['name'],r['name'],[x,y,z+dz],[dx,dy,45],
                    '45mm straight upward extraction/tool planning reserve above complete fuse envelope; cover removed')
    for name,x,y in fhac_sites:
        service('Access_'+name,name+'_CP2',[x-2,y-2,147],[55,24.25,40],
                '40mm top access with2mm lateral budget; NOT exact supplier lid hinge or hand model')

    # Solve the short branch before creating supports. Exact two quarter arcs,
    # not sampled spline curvature or a bounding-box clearance claim.
    wg=d.getObject('P_SYS_CP2')
    entry=wg.Placement.multVec(A.Vector(13,22,5.5))
    fb=d.getObject('F_PI_CP2').Shape.BoundBox
    start=A.Vector(fb.XMax,(fb.YMin+fb.YMax)/2,fb.ZMin+10)
    radius=6.; first=3.; grip=12.; strip=14.; od=3.4
    assert abs(entry.x-start.x-first-radius)<1e-6
    assert abs(start.z-entry.z-grip-radius)<1e-6
    a=start+A.Vector(first,0,0)
    b=a+A.Vector(radius,radius,0)
    c=A.Vector(entry.x,entry.y-radius,start.z)
    e=A.Vector(entry.x,entry.y,entry.z+grip)
    assert c.y>b.y, 'A straight between bend planes must be positive'
    q=radius/math.sqrt(2)
    arc1=Part.Arc(a,A.Vector(a.x+q,a.y+radius-q,a.z),b).toShape()
    arc2=Part.Arc(c,A.Vector(c.x,c.y+q,c.z-radius+q),e).toShape()
    path=Part.Wire([Part.makeLine(start,a),arc1,Part.makeLine(b,c),arc2,Part.makeLine(e,entry)])
    circle=Part.Wire([Part.makeCircle(od/2,start,A.Vector(1,0,0))])
    lead=path.makePipeShell([circle],True,False)
    assert lead.isValid() and len(lead.Solids)==1
    blank=path.Length+strip
    assert blank<=50 and abs(path.Length-(first+math.pi*radius+(c-b).Length+grip))<1e-6
    hg=d.addObject('App::DocumentObjectGroup','HarnessCandidate')
    ob=d.addObject('Part::Feature','W043_FPI_CP2');ob.Shape=lead;hg.addObject(ob)
    ob.addProperty('App::PropertyString','Status');ob.Status='Nominal cable snapshot; physical lead/port/OD/R not measured'
    copper=d.addObject('Part::Feature','W043_strip_CP2')
    copper.Shape=Part.makeCylinder(.646,strip,entry,A.Vector(0,0,-1));hg.addObject(copper)
    fpi_wire=dict(id='W043',a='F_PI.in',b='P_SYS.2',input_factory_side='right+X',
                  centerline_length_mm=path.Length,maximum_strip_mm=strip,
                  nominal_blank_mm=blank,limit_mm=50,insulated_entry_straight_mm=grip,
                  holder_exit_straight_mm=first,bend_radii_mm=[radius,radius],OD_mm=od,
                  radius_OD_exit_height_port_coordinates_assumed=True,
                  supplier_verified_wago_strip_mm=[12,14],factory_lead_includes_strip=True,
                  exact_arcs_not_curvature_samples=True,physical_pass=False,
                  start_mm=list(start),entry_mm=list(entry),native_geometry='builder-owned snapshots')

    envelope=path.makePipeShell([Part.Wire([Part.makeCircle(od/2+2.4,start,A.Vector(1,0,0))])],True,False)
    wires=[dict(metadata=fpi_wire,shape=lead,enclosure_reserve=envelope,targets=['F_PI_CP2','P_SYS_CP2'])]
    def routed_wire(identifier,role_a,role_b,edges,diameter,targets,extra,limit,basis,entry_strip=None):
        p=Part.Wire(edges);point=edges[0].Vertexes[0].Point
        for one,two in zip(edges,edges[1:]):
            assert (one.valueAt(one.LastParameter)-two.valueAt(two.FirstParameter)).Length<1e-6
            assert (one.tangentAt(one.LastParameter)-two.tangentAt(two.FirstParameter)).Length<1e-6
        profile=Part.Wire([Part.makeCircle(diameter/2,point,edges[0].tangentAt(edges[0].FirstParameter))])
        shape=p.makePipeShell([profile],True,False)
        assert shape.isValid() and len(shape.Solids)==1
        length=p.Length+extra
        if limit is not None:assert length<=limit
        ob=d.addObject('Part::Feature',identifier+'_CP2');ob.Shape=shape;hg.addObject(ob)
        ob.addProperty('App::PropertyString','Status');ob.Status=basis
        if entry_strip:
            location,direction,mm,*radii=entry_strip
            ob=d.addObject('Part::Feature',identifier+'_strip_CP2')
            ob.Shape=Part.makeCylinder(radii[0] if radii else 1.02,mm,location,direction);hg.addObject(ob)
        meta=dict(id=identifier,a=role_a,b=role_b,centerline_length_mm=p.Length,
                  termination_allowance_in_blank_mm=extra,nominal_blank_mm=length,limit_mm=limit,
                  OD_mm=diameter,dimension_basis=basis,physical_pass=False,
                  geometry='builder-owned snapshot',factory_polarity_from_markings_not_left_right=True)
        envelope=p.makePipeShell([Part.Wire([Part.makeCircle(diameter/2+2.4,point,edges[0].tangentAt(edges[0].FirstParameter))])],True,False)
        assert envelope.isValid() and len(envelope.Solids)==1
        wires.append(dict(metadata=meta,shape=shape,enclosure_reserve=envelope,targets=targets))
    plus=A.Vector(-73,-58.8,50);f0=A.Vector(-48,-58.8,50)
    assert abs(d.getObject('F0_CP2').Shape.BoundBox.XMin-f0.x)<1e-6
    routed_wire('W075','BAT.plus','F0.in',[Part.makeLine(plus,f0)],
        4.5,['XT60_CP2','F0_CP2'],5,50,
        'Intact F0 factory12AWG; OD4.5/R10/exitheight11/pitch7 and solder allowance5 provisional; no prefuse intermediate joint')
    minus=A.Vector(-73,-58.8,57);n1=minus+A.Vector(10,0,0);r=12.4;q=r/math.sqrt(2)
    n2=n1+A.Vector(r,r,0);n3=n2+A.Vector(0,r,r)
    ground=d.getObject('G1_CP2').Placement.multVec(A.Vector(5.5,22,5.5))
    assert abs(n3.x-ground.x)<1e-6 and abs(n3.y-ground.y)<1e-6 and ground.z-n3.z>=9
    routed_wire('W001','BAT.minus','G1.1',[
        Part.makeLine(minus,n1),
        Part.Arc(n1,A.Vector(n1.x+q,n1.y+r-q,n1.z),n2).toShape(),
        Part.Arc(n2,A.Vector(n2.x,n2.y+q,n2.z+r-q),n3).toShape(),
        Part.makeLine(n3,ground)],3.1,['XT60_CP2','G1_CP2'],19,150,
        'LAPP0107001 supplierOD3.1/staticR12.4;14mm WAGO strip+5mm solder allowance; mouth/cup datums provisional;9+mm final insulation straight',
        entry_strip=(ground,A.Vector(0,0,1),14))

    # One common source-switch plan. Existing supplier/assumed distinction is
    # retained: family stud pitch24 and ring seating15mm above tips are NOT
    # verified HELLA datums. Additional splice is protected by F0, never before it.
    R=25.2
    def quarter(begin,u,v,radius):
        end=begin+(u+v)*radius
        mid=begin+u*(radius/math.sqrt(2))+v*(radius*(1-1/math.sqrt(2)))
        return Part.Arc(begin,mid,end).toShape(),end
    def s_shift(begin,axis,shift,radius):
        h=shift.Length;unit=shift/h;theta=math.acos(1-h/(2*radius))
        def point(t):
            if t<=theta:return begin+axis*(radius*math.sin(t))+unit*(radius*(1-math.cos(t)))
            q=t-theta
            return begin+axis*(2*radius*math.sin(theta)-radius*math.sin(theta-q))+unit*(radius*(1+math.cos(theta-q)-2*math.cos(theta)))
        return [Part.Arc(point(0),point(theta/2),point(theta)).toShape(),
                Part.Arc(point(theta),point(1.5*theta),point(2*theta)).toShape()],point(2*theta)
    X,Y,Z=A.Vector(1,0,0),A.Vector(0,1,0),A.Vector(0,0,1)
    splice=d.getObject('PostF0Splice_CP2')
    sin=splice.Placement.multVec(A.Vector(5.5,19,4.5))
    sout=splice.Placement.multVec(A.Vector(12.25,19,4.5))
    source=A.Vector(3,-58.8,50);a=A.Vector(sin.x-10,source.y,source.z)
    bend,b=quarter(a,X,-Z,10)
    assert (sin-b).dot(-Z)>=9-1e-6 and (sin-b).cross(Z).Length<1e-6
    routed_wire('W076_FACTORY','F0.out','POST_F0.1',
        [Part.makeLine(source,a),bend,Part.makeLine(b,sin)],4.5,
        ['F0_CP2','PostF0Splice_CP2'],11,84.5,
        'Original FHAC0002ZXJ12AWG; shortest supplied84.5 inclstrip; strip11 at221-412; OD4.5/R10/exitdatum provisional',
        entry_strip=(sin,-Z,11))
    # Second gate identified a crossing of the unchanged W001 riser. Change
    # the physical clocking of BOTH S0 terminals, not scalar wire offsets:
    # left IN/right OUT,24mm family pitch. S0 casing axis stays vertical.
    s0in=A.Vector(-89,16,80);s0out=A.Vector(-65,16,80)
    incoming=A.Vector(-.5,math.sqrt(3)/2,0)
    outgoing=A.Vector(math.sqrt(3)/2,.5,0)
    intip=s0in-incoming*26.9;outtip=s0out+outgoing*26.9
    a=sout+Z*9;arc,b=quarter(a,Z,-X,R)
    # Lower central corridor: turn below the fuse reserves atZ65.2; move
    # inside Y-40 BEFORE rising. No loop through outer leg WAGO atY-79.5.
    shifted,q=s_shift(b,-X,A.Vector(0,-40-b.y,0),R)
    raised,q2=s_shift(q,-X,A.Vector(0,0,intip.z-q.z),R)
    theta=math.pi/3
    final_straight=(intip.y-q2.y-R*(1-math.cos(theta)))/math.sin(theta)
    assert final_straight>=9
    arc_end=intip-incoming*final_straight
    corner=arc_end+A.Vector(R*math.sin(theta),-R*(1-math.cos(theta)),0)
    assert (corner-q2).dot(-X)>0 and abs(corner.y-q2.y)<1e-6
    def turn_point(t):return corner-X*(R*math.sin(t))+Y*(R*(1-math.cos(t)))
    turn=Part.Arc(corner,turn_point(theta/2),arc_end).toShape()
    routed_wire('W076_EXTENSION','POST_F0.2','S0.in',
        [Part.makeLine(sout,a),arc]+shifted+raised+[Part.makeLine(q2,corner),turn,Part.makeLine(arc_end,intip)],
        4.2,['PostF0Splice_CP2','S0_body_CP2'],11+15,None,
        'HELU23802 red4mm2/staticR25.2;11mm splice strip+15mm ring barrel allowance; ring/pitch/OD4.2 provisional; AFTER F0')
    target=d.getObject('P_SYS_CP2').Placement.multVec(A.Vector(5.5,22,5.5))
    # Ring-width gate: an axial OUT tongue touched the PCB reservation even
    # though its narrower wire was clear. Clock the entire barrel/lead30deg.
    angle=math.pi/6
    def flatten_point(t):
        return outtip+X*(R*(math.sin(angle)-math.sin(angle-t)))+Y*(R*(math.cos(angle-t)-math.cos(angle)))
    flat=flatten_point(angle)
    flatten=Part.Arc(outtip,flatten_point(angle/2),flat).toShape()
    transverse,aligned=s_shift(flat,X,A.Vector(0,target.y-flat.y,0),R)
    lower=A.Vector(target.x+2*R-R,target.y,outtip.z)
    rise,riser=quarter(lower,X,Z,R)
    top=riser+Z*(target.z+9-riser.z)
    high=top-X*R+Z*R;down=top-X*(2*R)
    assert abs((aligned-target).dot(Y))<1e-6 and (lower-aligned).dot(X)>0
    routed_wire('W066','S0.out','P_SYS.1',
        [flatten]+transverse+[Part.makeLine(aligned,lower),rise,Part.makeLine(riser,top),
         Part.Arc(top,high,down).toShape(),Part.makeLine(down,target)],
        4.2,['S0_body_CP2','P_SYS_CP2'],15+14,330,
        'HELU23802 red4mm2/staticR25.2;15mm TE130207 barrel+14mm WAGO strip; ring seating80/pitch24/OD4.2 provisional',
        entry_strip=(target,-Z,14,math.sqrt(4/math.pi)))
    # Purchased terminal/hardware snapshots, not fabricated print geometry.
    terminal_group=d.addObject('App::DocumentObjectGroup','S0TerminalCandidates')
    terminal_parts={}
    def terminal(name,shape):
        assert shape.isValid() and shape.Solids
        ob=d.addObject('Part::Feature',name);ob.Shape=shape;terminal_group.addObject(ob)
        terminal_parts[name]=shape
    def cylinder(point,radius,height):return Part.makeCylinder(radius,height,point,Z)
    for name,centre,direction in [('IN',s0in,-incoming),('OUT',s0out,outgoing)]:
        cross=Z.cross(direction)
        vertices=[centre+direction*u+cross*v-Z*1.05 for u,v in [(-6.9,-6.75),(26.9,-6.75),(26.9,6.75),(-6.9,6.75)]]
        tongue=Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(Z*1.05)
        tongue=tongue.cut(cylinder(centre-Z*1.15,5.02,1.25))
        barrel=Part.makeCylinder(3.2,15,centre+direction*11.9,direction)
        terminal('S0_ring_'+name,tongue.fuse(barrel))
        terminal('S0_stud_'+name,cylinder(centre-Z*15,5,15))
        terminal('S0_washer_'+name,cylinder(centre-Z*3.05,10,2).cut(cylinder(centre-Z*3.15,5.25,2.2)))
        vertices=[centre+A.Vector(17/math.sqrt(3)*math.cos(k*math.pi/3),17/math.sqrt(3)*math.sin(k*math.pi/3),-11.05) for k in range(6)]
        nut=Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(Z*8)
        terminal('S0_nut_'+name,nut.cut(cylinder(centre-Z*11.15,5,8.2)))
    source_switch_plan=dict(stud_centres_mm=[list(s0in),list(s0out)],stud_pitch_mm=24,
        clocking='IN left/OUT right; common terminal clocking changed to avoid W001 riser, NOT supplier datum',
        ring_barrel_directions=[list(-incoming),list(outgoing)],
        lug_seating_above_tip_mm=15,datums_supplier_verified=False,
        rings='Two existing TE130207 allocations, not extra rings',
        hardware='Two existing M10 nutsAF17/h8 and washersOD20/ID10.5/t2',
        W076_split='One logical W076, factory+protected extension, NOT two extra netlist nets',
        post_F0_splice_additional_candidate_qty=1,HELU_extension_selection_stock_open=True,
        access='Nut tool and switch mount assembly/removal still OPEN; no socket-down access claim over front frame',
        no_prefuse_joint=True,selected=False,physical_pass=False)

    # Common S1 plan: two upper supply routes, all four ring directions and
    # screw access BEFORE any supports. Output routes remain explicitly OPEN.
    # A sideways switch keeps its driver axes away from the rear hip bracket.
    # Manufacturer pitch/body are known; bearing/pocket and indexing are not.
    def arc_turn(begin,tangent,normal,theta,radius):
        def point(t):return begin+tangent*(radius*math.sin(t))+normal*(radius*(1-math.cos(t)))
        return Part.Arc(begin,point(theta/2),point(theta)).toShape(),point(theta)
    s1_centres={'2':A.Vector(120.2,33,85),'5':A.Vector(132.2,33,85),
                '3':A.Vector(120.2,33,73),'6':A.Vector(132.2,33,73)}
    s1_directions={'2':Z,'5':Z,'3':-X,'6':X}
    tips={key:centre+s1_directions[key]*22.123 for key,centre in s1_centres.items()}
    def lateral_angle(offset):return math.pi/4+math.asin((offset/R-1)/math.sqrt(2))
    # Rejected co-running inputs crossed W066 and each other. Opposed upper
    # corridors (Y41 and Y-0.3) change the routing cause, not a tiny offset.
    for identifier,port,key,rise_mm,angle in [('W067',3,'2',9,math.radians(25)),
                                           ('W068',4,'5',10.3,math.radians(-50))]:
        source=wg.Placement.multVec(A.Vector(5.5+(port-1)*7.5,22,5.5))
        a=source+Z*rise_mm;n=X*math.cos(angle)+Y*math.sin(angle)
        turn,b=quarter(a,Z,n,R)
        sign=1 if angle>0 else -1
        flatten,c=arc_turn(b,n,(X*math.sin(angle)-Y*math.cos(angle))*sign,abs(angle),R)
        corner=A.Vector(tips[key].x-R,c.y,c.z)
        assert (corner-c).dot(X)>0
        if abs(c.y-tips[key].y)<1e-6:
            descent,end=quarter(corner,X,-Z,R);last=[descent]
        else:
            side=1 if tips[key].y>c.y else -1
            beta=lateral_angle(abs(c.y-tips[key].y))
            downward=Y*(side*math.sin(beta))-Z*math.cos(beta)
            descent,e=quarter(corner,X,downward,R)
            straighten,end=arc_turn(e,downward,-Y*(side*math.cos(beta))-Z*math.sin(beta),beta,R)
            last=[descent,straighten]
        assert abs(end.y-tips[key].y)<1e-6 and abs(end.x-tips[key].x)<1e-6
        assert end.z-tips[key].z>=9
        routed_wire(identifier,f'P_SYS.{port}',f'S1.{key}',
            [Part.makeLine(source,a),turn,flatten,Part.makeLine(c,corner)]+last+[Part.makeLine(end,tips[key])],
            4.2,['P_SYS_CP2','S1_body_CP2'],14+14.452,None,
            'HELU23802 4mm2/OD4.2/staticR25.2;14 WAGO strip+14.452 TE130171 barrel allowance incl crimp strip; physical port/bearing datums conditional',
            entry_strip=(source,-Z,14,math.sqrt(4/math.pi)))
        wires[-1]['metadata'].update(bend_radius_min_mm=R,
            source_insulation_straight_mm=rise_mm,ring_insulation_straight_mm=end.z-tips[key].z,
            ring_wire_entry_mm=list(tips[key]),wago_entry_mm=list(source),actual_cut_length_mm=None,
            supersedes_unqualified_legacy_blank=True)

    # BOTH output routes in the same model as the four terminals and inputs.
    # Front outlet uses the clear Z73/Y33..38.5 corridor above Pi/monitor,
    # beneath central WAGO. Rear outlet turns beside (not through) the tail,
    # then returns below FHAC through Y20; one diagonal transition preserves R.
    front=d.getObject('P_FRONT_CP2').Placement.multVec(A.Vector(5.5,22,5.5))
    rear=d.getObject('P_REAR_CP2').Placement.multVec(A.Vector(5.5,22,5.5))
    a=tips['3']-X*9
    shifted,b=s_shift(a,-X,A.Vector(0,front.y-a.y,0),R)
    lower=A.Vector(front.x+R,front.y,tips['3'].z)
    turn,c=quarter(lower,-X,Z,R)
    assert (lower-b).dot(-X)>0 and front.z-c.z>=9
    routed_wire('W064','S1.3','P_FRONT.1',
        [Part.makeLine(tips['3'],a)]+shifted+[Part.makeLine(b,lower),turn,Part.makeLine(c,front)],
        4.2,['S1_body_CP2','P_FRONT_CP2'],14.452+14,None,
        'HELU23802/OD4.2/staticR25.2; existing TE130171 barrel14.452 incl crimp strip+14 WAGO; provisional endpoints; replaces legacy220 blank',
        entry_strip=(front,Z,14,math.sqrt(4/math.pi)))
    wires[-1]['metadata'].update(bend_radius_min_mm=R,ring_insulation_straight_mm=9,
        wago_insulation_straight_mm=front.z-c.z,ring_wire_entry_mm=list(tips['3']),
        wago_entry_mm=list(front),actual_cut_length_mm=None,supersedes_unqualified_legacy_blank=True)
    a=tips['6']+X*9;outbend,b=quarter(a,X,Z,R)
    backbend,c=quarter(b,Z,-X,R)
    inside,e=s_shift(c,-X,A.Vector(0,-13,0),R)
    aligned,f=s_shift(e,-X,A.Vector(0,rear.y-e.y,rear.z-e.z),R)
    assert (rear-f).dot(-X)>=9 and (rear-f).cross(X).Length<1e-6
    routed_wire('W065','S1.6','P_REAR.1',
        [Part.makeLine(tips['6'],a),outbend,backbend]+inside+aligned+[Part.makeLine(f,rear)],
        4.2,['S1_body_CP2','P_REAR_CP2'],14.452+14,None,
        'HELU23802/OD4.2/staticR25.2; same two factory screw/ring exits retained;14.452 TE barrel incl crimp strip+14 WAGO; replaces legacy180 blank',
        entry_strip=(rear,-X,14,math.sqrt(4/math.pi)))
    wires[-1]['metadata'].update(bend_radius_min_mm=R,ring_insulation_straight_mm=9,
        wago_insulation_straight_mm=(rear-f).Length,ring_wire_entry_mm=list(tips['6']),
        wago_entry_mm=list(rear),actual_cut_length_mm=None,supersedes_unqualified_legacy_blank=True)

    # Eight factory ends planned TOGETHER before any mount. Inward ends use
    # opposing offsets below populated boards; outward ends turn upward
    # outside leg WAGO. 100mm/side remains ASSUMED, not catalogue L140.
    mta_plan=[]
    for leg,x,y in mta_sites:
        side=1 if y>0 else -1
        inward=-Y*side;outward=Y*side
        in_id,out_id=dict(FL=('W041','W026'),FR=('W042','W037'),
                          RL=('W044','W045'),RR=('W052','W053'))[leg]
        source=A.Vector(x,y-side*17.5,50)
        a=source+inward*9
        bend,b=s_shift(a,inward,A.Vector(-20*side,0,8),R)
        entry=b+inward*9
        joint=in_id+'_Joint_CP2'
        rotation=None if side==1 else A.Rotation(Z,180)
        base=[entry.x-5.5,entry.y-19,entry.z-4.5] if side==1 else [entry.x+5.5,entry.y+19,entry.z-4.5]
        box(joint,base,[14,19,9],'splices',
            'Candidate221-412 source extension;14x19x9 family envelope/port provisional; '
            'not selected purchase; source extension/quantity reconciliation OPEN',rotation=rotation)
        assert (d.getObject(joint).Placement.multVec(A.Vector(5.5,19,4.5))-entry).Length<1e-6
        routed_wire(in_id+'_FACTORY','F_'+leg+'.in',joint+'.1',
            [Part.makeLine(source,a)]+bend+[Part.makeLine(b,entry)],4.2,
            ['MTA_'+leg+'_CP2',joint],11,100,
            'Factory MTA4mm2; OD4.2/R25.2 reserve and100mm/side PROVISIONAL. '
            'CatalogueL140 ambiguous, NOT guaranteed length;11mm joint strip included; extension OPEN',
            entry_strip=(entry,inward,11,math.sqrt(4/math.pi)))
        wires[-1]['metadata'].update(bend_radius_min_mm=R,holder_straight_mm=9,
            joint_straight_mm=9,catalogue_length_interpretation_unverified=True,
            factory_allowance_mm=100,factory_allowance_is_assumption=True,
            actual_cut_length_mm=None,selected=False)
        input_blank=wires[-1]['metadata']['nominal_blank_mm']
        source=A.Vector(x,y+side*17.5,50)
        a=source+outward*9;arc,b=quarter(a,outward,Z,R);entry=b+Z*9
        output_joint=out_id+'_Joint_CP2'
        box(output_joint,[entry.x-5.5,entry.y-4.5,entry.z+19],[14,19,9],'splices',
            'Candidate221-412 output extension; replaces old output joint at selection, '
            'not extra purchased qty yet; DOWN entry, provisional port/grip/lever',
            rotation=A.Rotation(X,-90))
        assert (d.getObject(output_joint).Placement.multVec(A.Vector(5.5,19,4.5))-entry).Length<1e-6
        routed_wire(out_id+'_FACTORY','F_'+leg+'.out',output_joint+'.1',
            [Part.makeLine(source,a),arc,Part.makeLine(b,entry)],4.2,
            ['MTA_'+leg+'_CP2',output_joint],11,100,
            'Factory MTA4mm2; OD4.2/R25.2 reserve and100mm/side PROVISIONAL. '
            'CatalogueL140 NOT two100mm leads;11mm joint strip included; output extension OPEN',
            entry_strip=(entry,Z,11,math.sqrt(4/math.pi)))
        wires[-1]['metadata'].update(bend_radius_min_mm=R,holder_straight_mm=9,
            joint_straight_mm=9,catalogue_length_interpretation_unverified=True,
            factory_allowance_mm=100,factory_allowance_is_assumption=True,
            actual_cut_length_mm=None,selected=False)
        mta_plan.append(dict(leg=leg,centre_mm=[x,y,50],both_exit_axes='opposite Y',
            source_wire=in_id,output_wire=out_id,source_joint=joint,output_joint=output_joint,
            source_factory_blank_mm=input_blank,
            output_factory_blank_mm=wires[-1]['metadata']['nominal_blank_mm'],
            source_extension_to=dict(FL='P_FRONT.2',FR='P_FRONT.3',RL='P_REAR.2',RR='P_REAR.3')[leg],
            output_extension_to=leg+'_P.1',full_extensions_open=True,
            lengths_not_guaranteed_by_L140=True,native_mounts_open=True,stock_reconciliation_open=True))

    s1_group=d.addObject('App::DocumentObjectGroup','S1TerminalCandidates')
    s1_parts={};s1_port={};drivers=[]
    for key,centre in s1_centres.items():
        direction=s1_directions[key];cross=Y.cross(direction)
        vertices=[centre+direction*u+cross*v-Y*1.042 for u,v in
                  [(-5.563,-4.7625),(22.123,-4.7625),(22.123,4.7625),(-5.563,4.7625)]]
        tongue=Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(Y*1.042)
        tongue=tongue.cut(Part.makeCylinder(2.667,1.242,centre-Y*1.142,Y))
        barrel=Part.makeCylinder(3.175,14.452,centre+direction*7.671,direction)
        ring=tongue.fuse(barrel)
        screw=Part.makeCylinder(2.25,6,centre-Y*1.042,Y).fuse(
              Part.makeCylinder(4,3,centre-Y*4.042,Y))
        # Four millimetre terminal-bearing stand-off is conditional, not a
        # claimed exact NKK casing shape or a manufactured extra component.
        seat=Part.makeCylinder(5,4,centre,Y)
        for kind,shape in [('ring',ring),('screw',screw),('seat_budget',seat)]:
            name=f'S1_{kind}_{key}';assert shape.isValid() and len(shape.Solids)==1
            ob=d.addObject('Part::Feature',name);ob.Shape=shape;s1_group.addObject(ob)
            s1_parts[name]=shape;s1_port[name]=key
        name='S1_driver_'+key
        ob=d.addObject('Part::Cylinder',name);ob.Radius=4;ob.Height=30
        ob.Placement=A.Placement(centre-Y*34.042,A.Rotation(X,-90));s1_group.addObject(ob);d.recompute()
        drivers.append(dict(name=name,shape=ob.Shape.copy(),port=key,
                            basis='Generic assumed30mm straight driver/OD8, NOT a selected tool or measured screw actuation'))
    s1_plan=dict(body_axis=[0,1,0],body_origin_mm=[114.2,37,64],body_budget_mm=[24,37,42],
        axis_centre_mm=[126.2,74,85],terminal_centres_mm={k:list(v) for k,v in s1_centres.items()},
        barrel_directions={k:list(v) for k,v in s1_directions.items()},
        ring_wire_entries_mm={k:list(v) for k,v in tips.items()},
        body_axial_supplier_mm=34,body_extra_axial_budget_mm=3,terminal_pitch_supplier_mm=12,
        bearing_offset_budget_mm=4,bearing_datum_and_terminal_indexing_verified=False,
        rings='Four existing TE130171 allocations; no extra ring quantity',
        screws='Four original M4.5x6; headOD8/h3 ASSUMED, not M4 replacements',
        mounting='M12P1 bushing12/lever22; panel max4.5, opening12.5/antirot key; native panel/support OPEN',
        input_routes=['W067','W068'],output_routes_nominal=['W064','W065'],
        output_routes_open=[],physical_entry_datums_and_stock_unqualified=True,
        shared_output_receivers=dict(P_FRONT='DOWN entry108.2',P_REAR='+X entry72.5,33,115.5',D_RL='centre94,0',G2='centre129,0'),
        strain_reliefs_mounts_full_service_open=True,
        service='Four assumed straight driver budgets after removable side-cover access, not full assembly/removal qualification',
        selected=False,physical_pass=False)

    def broad(a,b):
        return a.BoundBox.intersect(b.BoundBox)

    proof=prior
    if prior and prior.get('native_candidate_replaced') is False:
        # Failed hypotheses leave native/layout untouched; retrieve the pinned
        # last committed clean proof rather than repeat all unchanged geometry.
        proof=json.loads(subprocess.check_output(['git','show','HEAD:'+ (OUT/'checks.json').relative_to(ROOT).as_posix()],cwd=ROOT))
    reuse = bool(proof and proof['status']=='COARSE_SHARED_RESERVATIONS_CLEAR'
                 and all(proof['source_sha256'].get(p)==pins[p] for p in
                         [BASE.joinpath('WholeCatLayout.FCStd').relative_to(ROOT).as_posix(),
                          BASE.joinpath('layout.json').relative_to(ROOT).as_posix()]))
    old_rows={r['name']:r for r in old_layout['components']}
    def same_geometry(r):
        old=old_rows.get(r['name'])
        return bool(old and all(len(old.get(k,[]))==len(r.get(k,[])) and
                    all(abs(a-b)<1e-7 for a,b in zip(old.get(k,[]),r.get(k,[])))
                    for k in ['origin_mm','size_mm','rotation_quaternion']))
    unchanged={r['name'] for r in rows if reuse and same_geometry(r)}
    old_access={r['name']:r for r in proof.get('service_reservations',[])} if reuse else {}
    errors, outside, contacts, chassis_hits = [], [], [], []
    wall = 2.4
    for row in rows:
        name=row['name'];s=shapes[name]
        if row['require_internal_shell'] and name not in unchanged:
            p=row['origin_mm'];v=row['size_mm']
            reserve=Part.makeBox(*(a+2*wall for a in v), A.Vector(*(a-wall for a in p)))
            try:
                c=reserve.cut(torso)
                if not c.isValid(): raise RuntimeError('Invalid enclosure boolean')
                if c.Volume>1e-5:outside.append(dict(name=name,outside_mm3=c.Volume))
            except Exception as e:errors.append(dict(pair=[name,'Torso'],error=str(e)))
    checked=0
    for na,nb in itertools.combinations(shapes,2):
        if na in unchanged and nb in unchanged:continue
        if na.startswith('S0_') and nb.startswith('S0_'):continue
        if na.startswith('S1_') and nb.startswith('S1_'):continue
        a,b=shapes[na],shapes[nb]
        if not broad(a,b):continue
        try:
            checked+=1;c=a.common(b)
            if not c.isValid():raise RuntimeError('Invalid intersection')
            if c.Volume>1e-5:contacts.append(dict(pair=[na,nb],volume_mm3=c.Volume))
        except Exception as e:errors.append(dict(pair=[na,nb],error=str(e)))
    # Check genuine retained shapes, not their bounding boxes. No inherited cassette in this test.
    for name,s in shapes.items():
        if name in unchanged:continue
        for rn,rs,cat in refs:
            if not broad(s,rs):continue
            try:
                checked+=1;c=s.common(rs)
                if not c.isValid():raise RuntimeError('Invalid retained-part intersection')
                if c.Volume>1e-5:chassis_hits.append(dict(pair=[name,rn],volume_mm3=c.Volume,category=cat))
            except Exception as e:errors.append(dict(pair=[name,rn],error=str(e)))
    access_hits=[]
    for r in access:
        s=d.getObject(r['name']).Shape
        reused_access=old_access.get(r['name'])==r
        for name,other in list(shapes.items())+[(n,s) for n,s,cat in refs]:
            if reused_access and (name in unchanged or name not in shapes):continue
            if name==r['target'] or not broad(s,other):continue
            try:
                checked+=1;c=s.common(other)
                if not c.isValid():raise RuntimeError('Invalid service intersection')
                if c.Volume>1e-5:access_hits.append(dict(pair=[r['name'],name],volume_mm3=c.Volume))
            except Exception as e:errors.append(dict(pair=[r['name'],name],error=str(e)))
    wire_hits=[]
    for wire in wires:
        wn=wire['metadata']['id'];ws=wire['shape']
        for name,other in list(shapes.items())+[(n,s) for n,s,cat in refs]+[(r['name'],d.getObject(r['name']).Shape) for r in access]:
            if name in wire['targets'] or not broad(ws,other):continue
            try:
                checked+=1;c0=ws.common(other)
                if not c0.isValid():raise RuntimeError('Invalid cable intersection')
                if c0.Volume>1e-5:wire_hits.append(dict(pair=[wn,name],volume_mm3=c0.Volume))
            except Exception as ex:errors.append(dict(pair=[wn,name],error=str(ex)))
        try:
            # A loop's axis-aligned box encloses empty space and cannot prove
            # that the actual wire exits a rounded belly. Test the enlarged
            # swept pipe itself. End-face margin remains a stated open detail.
            clearance=wire['enclosure_reserve'].cut(torso)
            if not clearance.isValid():raise RuntimeError('Invalid cable enclosure check')
            if clearance.Volume>1e-5:outside.append(dict(name=wn,outside_mm3=clearance.Volume))
        except Exception as ex:errors.append(dict(pair=[wn,'Torso'],error=str(ex)))
    for wa,wb in itertools.combinations(wires,2):
        if not broad(wa['shape'],wb['shape']):continue
        checked+=1;c0=wa['shape'].common(wb['shape'])
        if not c0.isValid():errors.append(dict(pair=[wa['metadata']['id'],wb['metadata']['id']],error='Invalid wire-wire Boolean'))
        elif c0.Volume>1e-5:wire_hits.append(dict(pair=[wa['metadata']['id'],wb['metadata']['id']],volume_mm3=c0.Volume))
    terminal_hits=[]
    for name,shape in terminal_parts.items():
        for other_name,other in list(shapes.items())+[(n,s) for n,s,cat in refs]+[(r['name'],d.getObject(r['name']).Shape) for r in access]:
            # Family cylinder explicitly includes its OWN studs/rings, not an
            # exact case. This is not an exclusion for unrelated components.
            if other_name.startswith('S0_') or not broad(shape,other):continue
            checked+=1;c0=shape.common(other)
            if not c0.isValid():errors.append(dict(pair=[name,other_name],error='Invalid terminal Boolean'))
            elif c0.Volume>1e-5:terminal_hits.append(dict(pair=[name,other_name],volume_mm3=c0.Volume))
        for wire in wires:
            own=(name.endswith('IN') and wire['metadata']['id']=='W076_EXTENSION') or (name.endswith('OUT') and wire['metadata']['id']=='W066')
            if own or not broad(shape,wire['shape']):continue
            checked+=1;c0=shape.common(wire['shape'])
            if not c0.isValid():errors.append(dict(pair=[name,wire['metadata']['id']],error='Invalid terminal-wire Boolean'))
            elif c0.Volume>1e-5:terminal_hits.append(dict(pair=[name,wire['metadata']['id']],volume_mm3=c0.Volume))
    for one,two in itertools.combinations(terminal_parts,2):
        if one.endswith('IN')==two.endswith('IN') or not broad(terminal_parts[one],terminal_parts[two]):continue
        checked+=1;c0=terminal_parts[one].common(terminal_parts[two])
        if not c0.isValid():errors.append(dict(pair=[one,two],error='Invalid IN/OUT terminal Boolean'))
        elif c0.Volume>1e-5:terminal_hits.append(dict(pair=[one,two],volume_mm3=c0.Volume))
    # Only intended seating/head/ring contacts of ONE port are excluded.
    # S1 may not exclude unrelated S0, retained parts or other-port geometry.
    for name,shape in s1_parts.items():
        for other_name,other in list(shapes.items())+[(n,s) for n,s,cat in refs]+[(r['name'],d.getObject(r['name']).Shape) for r in access]+list(terminal_parts.items()):
            if other_name in ['S1_body_CP2','S1_control_CP2'] or not broad(shape,other):continue
            checked+=1;c0=shape.common(other)
            if not c0.isValid():errors.append(dict(pair=[name,other_name],error='Invalid S1 terminal Boolean'))
            elif c0.Volume>1e-5:terminal_hits.append(dict(pair=[name,other_name],volume_mm3=c0.Volume))
        for wire in wires:
            own={'2':'W067','5':'W068','3':'W064','6':'W065'}.get(s1_port[name])==wire['metadata']['id']
            if own or not broad(shape,wire['shape']):continue
            checked+=1;c0=shape.common(wire['shape'])
            if not c0.isValid():errors.append(dict(pair=[name,wire['metadata']['id']],error='Invalid S1 wire Boolean'))
            elif c0.Volume>1e-5:terminal_hits.append(dict(pair=[name,wire['metadata']['id']],volume_mm3=c0.Volume))
    for one,two in itertools.combinations(s1_parts,2):
        if s1_port[one]==s1_port[two] or not broad(s1_parts[one],s1_parts[two]):continue
        checked+=1;c0=s1_parts[one].common(s1_parts[two])
        if not c0.isValid():errors.append(dict(pair=[one,two],error='Invalid S1 port pair Boolean'))
        elif c0.Volume>1e-5:terminal_hits.append(dict(pair=[one,two],volume_mm3=c0.Volume))
    for driver in drivers:
        for name,other in list(shapes.items())+[(n,s) for n,s,cat in refs]+list(terminal_parts.items())+list(s1_parts.items())+[(w['metadata']['id'],w['shape']) for w in wires]+[(r['name'],d.getObject(r['name']).Shape) for r in access]:
            if name.startswith('S1_') and (name in shapes or s1_port.get(name)==driver['port']):continue
            if not broad(driver['shape'],other):continue
            checked+=1;c0=driver['shape'].common(other)
            if not c0.isValid():errors.append(dict(pair=[driver['name'],name],error='Invalid driver Boolean'))
            elif c0.Volume>1e-5:access_hits.append(dict(pair=[driver['name'],name],volume_mm3=c0.Volume))
    clean=not (errors or outside or contacts or chassis_hits or access_hits or wire_hits or terminal_hits)
    checks=dict(status='COARSE_SHARED_RESERVATIONS_CLEAR' if clean else 'LAYOUT_PREFLIGHT_REQUIRES_CHANGE',
                selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
                count=len(rows),bus_roles_sorted=sorted(wanted),source_sha256=pins,
                wall_clearance_reserve_mm=wall,exact_brep_intersections_after_bbox_filter=checked,
                outside=outside,contacts=contacts,retained_contacts=chassis_hits,errors=errors,
                service_reservations=access,service_contacts=access_hits,
                service_motion_supplier_verified=False,W043_nominal_route=fpi_wire,
                nominal_source_wires=[w['metadata'] for w in wires],
                S0_terminal_contacts=terminal_hits,terminal_contacts=terminal_hits,
                S0_joint_plan=source_switch_plan,S1_joint_plan=s1_plan,MTA_joint_plan=mta_plan,
                wire_enclosure_test='Actual swept pipe OD+2x2.4mm cut from torso, NOT its enclosing bbox; cap axial margin not qualified',
                wire_contacts=wire_hits,wire_termination_target_bodies_excluded={w['metadata']['id']:w['targets'] for w in wires},
                reused_unchanged_component_names=sorted(unchanged),
                reused_reference_basis='Prior clear proof + unchanged CP1 reference hashes and exact box coordinates/rotation; changed interfaces and new wire checked')
    checks['BUS_vendor_compound_valid'] = bus_reference_valid
    checks['BUS_contact_test_basis'] = 'full vendor bounding reservation, NOT invalid compound'
    if prior and prior.get('rejected_preflights'):
        checks['rejected_preflights'] = prior['rejected_preflights']
    if prior and prior['status']=='LAYOUT_PREFLIGHT_REQUIRES_CHANGE':
        checks.setdefault('rejected_preflights', []).append(
            {k:prior.get(k,[]) for k in ['outside','contacts','retained_contacts','service_contacts','wire_contacts','S0_terminal_contacts','errors']})
    save('checks.json',checks)
    print('Preflight:',checks['status'],'outside',outside,'contacts',contacts,'retained',chassis_hits,'service',access_hits,'wire',wire_hits,'terminals',terminal_hits,'errors',errors,flush=True)
    colors={'logic':(.18,.53,.69),'fuses':(.72,.37,.22),'wago':(.96,.65,.14),
            'splices':(.65,.51,.15),'inline':(.52,.37,.64),'switch':(.35,.55,.40)}
    for row in rows:
        ob=d.getObject(row['name'])
        if ob.ViewObject:ob.ViewObject.ShapeColor=colors[row['group']]
    if d.getObject('TorsoEnvelope').ViewObject:d.getObject('TorsoEnvelope').ViewObject.Transparency=85
    d.getObject('Layout').Status='CP2: REZERWACJE PRZESTRZENI, NIE WYBRANY MONTAŻ'
    # Do not replace the last clean native candidate with a rejected layout.
    if not clean:
        checks['native_candidate_replaced'] = False
        save('checks.json',checks)
        raise RuntimeError('Shared preflight rejected; previous native candidate retained, see checks.json')
    target=OUT/'WholeCatInterior.FCStd'
    d.recompute();d.saveAs(str(target));A.closeDocument(d.Name)
    d=A.openDocument(str(target));d.recompute()
    assert len(d.getObject('InteriorReservations').Group)==len(rows)
    assert all(d.getObject(r['name']).Shape.isValid() for r in rows)
    assert len(d.getObject('ServiceReservations').Group)==17
    assert all(d.getObject(r['name']).Shape.isValid() for r in access)
    assert len(d.getObject('HarnessCandidate').Group)==len(wires)+sum(1 for o in d.getObject('HarnessCandidate').Group if '_strip_' in o.Name)
    assert all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in d.getObject('HarnessCandidate').Group)
    assert len(d.getObject('S0TerminalCandidates').Group)==8
    assert all(o.Shape.isValid() for o in d.getObject('S0TerminalCandidates').Group)
    assert len(d.getObject('S1TerminalCandidates').Group)==16
    assert all(o.Shape.isValid() for o in d.getObject('S1TerminalCandidates').Group)
    ob=d.getObject('P_REAR_CP2');h=ob.Width.Value;w=ob.Shape.BoundBox.XLength
    ob.Width=h+1;d.recompute()
    assert abs(ob.Shape.BoundBox.XLength-w-1)<1e-6
    ob.Width=h;d.recompute();A.closeDocument(d.Name)
    checks.update(native_reopen=True,box_parameter_roundtrip=True,
                  parameter_test='P_REAR Width+1 -> world X footprint+1; restored; cables/rings are builder-owned snapshots')
    checks['previous_preflight_history_git']='9d04972:hardware/cad/studies/whole-cat-packaging/cp2/checks.json'
    checks['shared_revision']='All four nominal S1 wires/terminals/driver budgets; common DOWN P_FRONT/+X P_REAR/D_RL/G2 receiver plan. Existing source/input routes retained. MTA/mounts/restraints/full assembly OPEN.'
    assert all(digest(ROOT/p)==h for p,h in pins.items()),'Reference source was modified'
    save('checks.json',checks)
    plan=dict(status=checks['status'],selected=False,source_sha256=pins,components=rows,
              phase1_result_count=14,phase1_denominator=20,
              removal_strategy=['Disconnect every source, open dorsal cover before operating clamps.',
                               'ATO access: dorsal cover off,12 straight assumed extraction reserves clear; WAGO stay connected. Actual gripper/holder extraction must still be qualified.',
                               'Five horizontal FHAC branches have top access budgets; exact lid hinge, fingers and leads still open.',
                               'Lower outer WAGO need side-cover access; no whole-tray74-disconnection procedure for routine fuse service.',
                               'Complete module removal and lower PCB/Pi access still OPEN; supports must follow one shared wiring/assembly plan.',
                               'P0 legs/frame and battery cradle stay; new removable shell/wall apertures not fabricated yet.'],
              wire_space_plan=['Proposed signal plane Z66..76: above Pi reserve64 and below PCB78; route actual endpoints before allocating supports.',
                               'Outer WAGO wire entries DOWN atZ56; straight9mm plus R12.4 loop needs a lower turn bay, not a zero-radius vertical route.',
                               ('REJECTED MTA repack experiment: all eight paths/joints still collide; see mta-preflight-rejected.json.' if MTA_REPACK else
                                'Four main MTA original reservations atY+/-84,Z80..96; full both-exit routes/stock/mounts OPEN. Two lower plans rejected, do not reuse.'),
                               'Crossings only through assigned between-level risers; full wire radii/straight ends/straps must be modeled together.',
                               'Rotated XT60/F0 in front-side source bay: W075 and W001 full nominal paths modeled with changed MAIN/front splice/G1. Mate/release/actual marked polarity and W076 switch lead still OPEN.',
                               'Central WAGO include DOWN P_FRONT108.2..130.2, +X P_REAR110..121, P_SYS UP95..117 and G1 DOWN103.5..125.5; five FHAC125..147. Ten source-wire pieces incl all four S1 wires modeled;4MTA/restraints OPEN.'],
              not_qualified=['Factory exit datums except vendor BUS USB; FHAC thickness22 prototype assumption, P309 pins/clips, XT60 mating half',
                             'S0 stud/lug/tool access and exact delivered SKU',
                             'S1 nominal four ring/screw approaches and four routes modeled; physical pockets, bushing support, aperture, restraints/stock and actual tool still OPEN',
                             'All full wire solids, 24 ends, bend radii, usable lengths and stock',
                             'Structural supports/fasteners, shell walls and motion sweeps',
                             'Assembly/removal swept volumes and actual connector release'],
              old_supports_superseded=['Deck','Carrier','Cover','BankLeft','BankRight','PiTray','4 fixed loom frames'],
              started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
              worker_wall_seconds=round(time.monotonic()-tick,3))
    save('layout.json',plan)
    save('interfaces.json',dict(
        status='SHARED_DIMENSIONS_RECONCILED_PARTIAL_PORT_PLAN_NOT_WIRING',selected=False,physical_pass=False,
        source_sha256=pins,
        BUS=dict(sku='Waveshare25514',actual_vendor_solids=117,vendor_compound_valid=bus_reference_valid,
                 contact_test='Conservative full bounds; vendor compound not repaired or used for exact qualification',
                 usb_mouth_mm=[143.81628928 if MTA_REPACK else 103.81628928,11.1220508043,45.7695251897],usb_direction=[1,0,0],
                 usb_plug_and_service_open=True, mount_pitch_mm=[37,28],fourth_hole_x_deviation_mm=0.012,
                 supplier='https://www.waveshare.com/bus-servo-adapter-a.htm'),
        U1=dict(sku='575070',owner='PWM1608_CP2',footprint_mm=[30.48,17.78],
                world_xy_mm=[76.35,3.81,106.83,21.59],extra_separate_board=False,
                pcb_thickness_pad_coordinates_open=True),
        P309=dict(supplier_dimensions_mm=[41,25,12],balance_roles=['BAT.B0','BAT.B1','BAT.B2','BAT.B3'],
                  permanently_live_when_S0_off=True,alarm_only=True,physical_pin_exit_datums_open=True,
                  supplier='https://botland.com.pl/wskazniki-rozladowania/5015-wskaznik-napiecia-li-pol-1-8s-z-buzzerem-p309-5904422333270.html'),
        FHAC=dict(source='https://www.littelfuse.com/assetdocs/fhac0001zxj-2d-print?assetguid=3959eb51-0df1-4ffd-a2a6-c64b8e165c85',
                  drawing='OL-FHAC0001ZXJ revL2019',length_max_mm=51,width_max_mm=20.25,
                  thickness_budget_mm=22,thickness_supplier_verified=False,
                  factory_lead_mm=[84.5,94.5],strip_mm=[4.35,8.35],lead_length_includes_strip=True,
                  lead_OD_budget_mm=3.4,bend_radius_budget_mm=6,OD_radius_supplier_verified=False,
                  branches=[dict(role=n,origin_mm=[x,y,125],input_exit_direction=[1,0,0] if n=='F_PI' else [-1,0,0],
                                 output_exit_direction=[-1,0,0] if n=='F_PI' else [1,0,0],exit_datum_provisional=True) for n,x,y in fhac_sites],
                  supply_roles={'F_PI':'P_SYS.2','F_AUX':'P_REAR.5','F_HY':'P_AUX.2','F_HP':'P_AUX.3','F_TY':'P_AUX.4'},
                  complete_lead_routes_open=True,F_PI_input_nominal=fpi_wire),
        F_PWM=dict(sku='0242.100UAT1',assembly='axial sleeved/restraint, no separate holder',
                   supply='P_REAR.4',output='JPWM_IN.1',assembly_bounds_assumed=True),
        F0=dict(sku='FHAC0002ZXJ',housing_axis=[1,0,0],both_factory_exits_retained=True,
                housing_origin_mm=[-48,-68.925,39],prefuse_nominal_route_modeled=True,
                exit_OD_radius_datums_provisional=True,output_to_S0_open=True),
        XT60=dict(own_half='XT60H-M',own_housing_mm=[23.9,16.4,9.2],
                  mate_housing_mm=[25,16.4,9.2],mated_length_not_sum=True,
                  mated_envelope_and_withdrawal_open=True,prefuse_limit_mm=50,prefuse_full_route_open=True),
        WAGO=dict(role_count=20,sku_map_retained=True,leg_power_ground='221-415 NOT221-615',
                  port_face_and_lever_motion_open=True),
        service_boundary=dict(strategy='Direct nominal ATO access after dorsal cover removal; WAGO stay connected.',
                              candidate_boundary='No routine tray removal; complete module boundaries still open.',
                              connector_SKUs_and_swept_release_open=True,
                              invalid='Do not claim removal with connected rigid leads or cut49ties.'),
        progress=dict(completed=14,total=20,W1_complete=False,W5_complete=False)))
    interface=json.loads((OUT/'interfaces.json').read_text(encoding='utf-8'))
    interface['S0_joint_plan']=source_switch_plan
    interface['S1_joint_plan']=s1_plan
    interface['splice_inventory']=splice_roles
    interface['MTA_joint_plan']=dict(holders=mta_plan,selected=False,physical_pass=False,
        complete_factory_source_output_pairs=False,full_extensions_complete=False,
        status='REJECTED_EXPERIMENT_NOT_CURRENT_NATIVE',rejected_report='mta-preflight-rejected.json',
        catalogue='MTA page75 MINI0100335 4mm2 L140, length interpretation unresolved',
        factory_OD_radius_length_and_exit_datums_supplier_verified=False,
        factory_pair_needs_not_qualified_by_ambiguous_L140=True,
        joint_roles_and_old_six_splice_identity_reconciliation_open=False,
        joint_candidates=8,new_purchase_quantity_not_selected=True,
        native_mounts_and_restraints_open=True,W1_complete=False,W5_complete=False)
    interface['F0']['output_to_S0_open']=True
    interface['F0']['output_nominal_candidate_routed']=True
    interface['post_F0_splice']=json.loads((OUT/'post-f0-splice-source.json').read_text(encoding='utf-8'))
    interface['nominal_source_wires']=[w['metadata'] for w in wires];save('interfaces.json',interface)
    complete_service_plan()
    render(rows,checks,colors)
    print('Saved native candidate/reopen; worker',plan['worker_wall_seconds'],'seconds',flush=True)


def mta_shared_plan():
    """One diagonal four-holder/eight-factory-end plan; selected CP2 preserved."""
    raise RuntimeError('Retired rejected diagonal recipe: wrong FL/FR circuit IDs and two failed layouts. Use a newly reconciled shared plan, not this experiment.')
    import FreeCAD as A
    import Part
    started=datetime.now(timezone.utc);tick=time.monotonic()
    native=OUT/'WholeCatInterior.FCStd';pins={native.relative_to(ROOT).as_posix():digest(native)}
    old_report=json.loads((OUT/'mta-shared-plan.json').read_text(encoding='utf-8')) if (OUT/'mta-shared-plan.json').exists() else None
    if old_report and old_report.get('builder_sha256')==digest(Path(__file__)) and old_report['status']=='SHARED_DIAGONAL_PLAN_REQUIRES_CHANGE':
        raise RuntimeError('Unchanged rejected shared plan: change joint source-bay/lane architecture before another CAD run')
    inventory=splice_inventory();pins.update(inventory['source_sha256'])
    d=A.openDocument(str(native));d.recompute();torso=d.getObject('TorsoEnvelope').Shape
    group=d.addObject('App::DocumentObjectGroup','MTAFactoryCandidate')
    X,Y,Z=A.Vector(1,0,0),A.Vector(0,1,0),A.Vector(0,0,1)
    axis=A.Vector(1,0,1)/math.sqrt(2);R=25.2
    changed={};bounds={};excluded={};routes=[];joints=[]
    def add_box(name,base,size,rotation,role):
        ob=d.getObject(name) or d.addObject('Part::Box',name)
        ob.Length,ob.Width,ob.Height=size;ob.Placement=A.Placement(base,rotation)
        ob.Label=role+' candidate';group.addObject(ob);d.recompute()
        changed[name]=ob.Shape.copy()
        local=Part.makeBox(*(v+4.8 for v in size),A.Vector(-2.4,-2.4,-2.4))
        local.Placement=ob.Placement;bounds[name]=local
        return ob
    # Move all ten outer WAGO together, not isolated receivers. Their complete
    # leg routes/mounts become OPEN; existing ten source wire pieces stay.
    for row in json.loads((OUT/'layout.json').read_text(encoding='utf-8'))['components']:
        if row['name'].split('_CP2')[0] not in ['FL_P','FL_G','D_FL','RL_P','RL_G','FR_P','FR_G','D_FR','RR_P','RR_G']:continue
        ob=d.getObject(row['name']);s=1 if ob.Placement.Base.y>0 else -1
        base=ob.Placement.Base;base.y=s*66-4.5;base.z=70
        # Two front negative receivers belong beside the source core, not
        # inside its F0 housing. Allocate the pair together, mounts still OPEN.
        if ob.Name in ['FR_P_CP2','FR_G_CP2']:
            base.x=-90 if ob.Name=='FR_P_CP2' else -55;base.y=-24
        add_box(ob.Name,base,[30,19,9],ob.Placement.Rotation,ob.Name)
    # Inherited four output roles are relocated, never duplicated.
    slots={r['electrical_role']:r['native_slot'] for r in inventory['baseline']}
    for leg,cx,side,in_id,out_id in [('FL',-35,1,'W025','W026'),('RL',65,1,'W044','W045'),
                                   ('FR',-35,-1,'W036','W037'),('RR',65,-1,'W052','W053')]:
        centre=A.Vector(cx,side*82,81)
        rear=leg in ['RL','RR']
        holder_axis=A.Vector(1,0,-1)/math.sqrt(2) if rear else axis
        rot=A.Rotation(Y,45 if rear else -45)
        # Rotation maps local +X to +X/+Z. Width remains transverse Y.
        base=centre-rot.multVec(A.Vector(17.5,11,8))
        holder=add_box('MTA_'+leg+'_CP2',base,[35,22,16],rot,'MTA_'+leg)
        for kind,wire_id,sign in [('source',in_id,-1),('output',out_id,1)]:
            u=holder_axis*sign
            lower=(u.z<0)
            if not rear and lower:
                # New common front-source clocking stays FORWARD of P0 mounts
                # and lifts connector bodies, rather than parking over a mount.
                v=A.Vector(-.5,-side/math.sqrt(2),.5)
            elif lower:v=Y*(-side)
            else:v=A.Vector(-1 if rear else 1,0,-1)/math.sqrt(2)
            begin=centre+u*17.5;a=begin+u*9
            finish=a+(u+v)*R
            arc=Part.Arc(a,a+u*(R/math.sqrt(2))+v*(R*(1-1/math.sqrt(2))),finish).toShape()
            entry=finish+v*9
            edges=[Part.makeLine(begin,a),arc,Part.makeLine(finish,entry)]
            name=wire_id+'_FACTORY_candidate'
            path=Part.Wire(edges)
            shape=path.makePipeShell([Part.Wire([Part.makeCircle(2.1,begin,u)])],True,False)
            assert shape.isValid() and len(shape.Solids)==1
            ob=d.addObject('Part::Feature',name);ob.Shape=shape;group.addObject(ob)
            changed[name]=shape
            bounds[name]=path.makePipeShell([Part.Wire([Part.makeCircle(4.5,begin,u)])],True,False)
            joint_name=('MTA_'+leg+'_SOURCE_joint' if kind=='source' else slots[wire_id+'_output'])
            if not rear and lower:
                ex=axis;ey=-v;ez=ex.cross(ey);factory_port=2
            elif lower:
                ex=X;ey=Y*side;ez=Z*side
                # RR factory occupies port1 to keep its body beyond F0 X=3.
                factory_port=1 if leg=='RR' else 2
            else:
                ex=A.Vector(-1 if rear else 1,0,1)/math.sqrt(2);ey=-v;ez=ex.cross(ey)
                factory_port=2
            jrot=A.Rotation(ex,ey,ez,'ZXY')
            local_port=A.Vector(5.5 if factory_port==1 else 12.25,19,4.5)
            jb=entry-jrot.multVec(local_port)
            add_box(joint_name,jb,[14,19,9],jrot,wire_id+'_joint')
            strip_name=wire_id+'_strip_candidate'
            strip=Part.makeCylinder(math.sqrt(4/math.pi),11,entry,v)
            ob=d.addObject('Part::Feature',strip_name);ob.Shape=strip;group.addObject(ob)
            changed[strip_name]=strip;bounds[strip_name]=strip
            excluded[name]={holder.Name,joint_name,strip_name}
            excluded[strip_name]={joint_name,name}
            # Both ports are assigned. Full extensions beyond this second port
            # MUST be designed before mounts/stock/selection, not assumed clear.
            other=A.Vector(12.25 if factory_port==1 else 5.5,19,4.5)
            joints.append(dict(name=joint_name,leg=leg,kind=kind,factory_port=factory_port,
                factory_entry_mm=list(entry),extension_entry_mm=list(jrot.multVec(other)+jb),
                extension_exit_direction=list(-v),extension_full_route_open=True))
            routes.append(dict(id=wire_id,leg=leg,kind=kind,start_mm=list(begin),entry_mm=list(entry),
                centreline_mm=path.Length,nominal_factory_requirement_mm=path.Length+11,
                first_and_last_straight_mm=9,bend_radius_mm=R,OD_mm=4.2,
                factory_DATUM_OD_radius_length_supplier_verified=False))
    d.recompute()
    fixed={o.Name:o.Shape.copy() for o in d.getObject('InteriorReservations').Group if o.Name not in changed}
    for name in ['HarnessCandidate','S0TerminalCandidates','S1TerminalCandidates','ServiceReservations']:
        fixed.update({o.Name:o.Shape.copy() for o in d.getObject(name).Group if 'Shape' in o.PropertiesList})
    fixed.update({o.Name:o.Shape.copy() for o in d.Objects if 'Category' in o.PropertiesList
                  and o.Category!='electronics' and o.Name!='BatteryNominal'})
    contacts=[];outside=[];errors=[];tested=0
    def intersect(na,a,nb,b):
        nonlocal tested
        if not a.BoundBox.intersect(b.BoundBox):return
        tested+=1
        try:
            c=a.common(b)
            if not c.isValid():raise RuntimeError('Invalid common')
            if c.Volume>1e-5:contacts.append(dict(pair=[na,nb],volume_mm3=c.Volume))
        except Exception as e:errors.append(dict(pair=[na,nb],error=str(e)))
    for name,shape in changed.items():
        for other,static in fixed.items():
            if other not in excluded.get(name,set()):intersect(name,shape,other,static)
        try:
            cut=bounds[name].cut(torso)
            if not cut.isValid():raise RuntimeError('Invalid enclosure cut')
            if cut.Volume>1e-5:outside.append(dict(name=name,outside_mm3=cut.Volume))
        except Exception as e:errors.append(dict(pair=[name,'Torso'],error=str(e)))
    for na,nb in itertools.combinations(changed,2):
        if nb in excluded.get(na,set()) or na in excluded.get(nb,set()):continue
        intersect(na,changed[na],nb,changed[nb])
    clean=not(contacts or outside or errors)
    report=dict(status='EIGHT_FACTORY_END_PLAN_CLEAR_NOT_FULL_WIRING' if clean else 'SHARED_DIAGONAL_PLAN_REQUIRES_CHANGE',
        builder_sha256=digest(Path(__file__)),
        selected=False,physical_pass=False,source_sha256=pins,retained_source_wire_pieces=10,
        changed_components=sorted(changed),routes=routes,joints=joints,contacts=contacts,outside=outside,errors=errors,
        exact_BRep_pairs_tested=tested,ATO_service_reservations_included=True,
        inventory=inventory,side_WAGO_entry_faces_changed_to_Z51=True,full_leg_routes_and_native_mounts_open=True,
        axes='Front+X/+Z45, rear+X/-Z45; both exits retained. Front source bends forward/inward; rear output bends inward below bank. Upper exits fold longitudinally outside ATO banks.',
        chosen_full_extension_routes=False,full_assembly_and_stock_complete=False,W1_complete=False,W5_complete=False,
        started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=round(time.monotonic()-tick,3),current_CP2_native_replaced=False)
    assert all(digest(ROOT/p)==h for p,h in pins.items())
    if old_report and old_report['status']=='SHARED_DIAGONAL_PLAN_REQUIRES_CHANGE':
        report['prior_rejected_plan']={k:old_report[k] for k in ['axes','contacts','outside','errors','worker_wall_seconds']}
    save('mta-shared-plan.json',report)
    print('MTA shared plan:',report['status'],'pairs',tested,'contacts',len(contacts),'outside',len(outside),'errors',len(errors),flush=True)
    if clean:
        d.saveAs(str(OUT/'MTAFactoryPlan.FCStd'))
        report['candidate_native']='MTAFactoryPlan.FCStd';save('mta-shared-plan.json',report)
    A.closeDocument(d.Name)


def reconcile_splice_native():
    """Focused subset correction; unchanged wire/contact proofs are not rerun."""
    import FreeCAD as A
    started=datetime.now(timezone.utc);tick=time.monotonic()
    inventory=splice_inventory()
    checks=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
    plan=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
    interface=json.loads((OUT/'interfaces.json').read_text(encoding='utf-8'))
    assert checks['status']=='COARSE_SHARED_RESERVATIONS_CLEAR'
    assert all(digest(ROOT/p)==h for p,h in checks['source_sha256'].items())
    target=OUT/'WholeCatInterior.FCStd'
    baseline_arg=next((x.split('=',1)[1] for x in sys.argv if x.startswith('--splice-baseline=')),None)
    baseline=Path(baseline_arg) if baseline_arg else target
    before_digest=digest(baseline)
    d=A.openDocument(str(baseline));d.recompute()
    changed={r['native_slot'] for r in inventory['baseline']}
    removed=inventory['removed_unbound_slot']
    assert len(d.getObject('InteriorReservations').Group)==63
    old={o.Name:o.Shape.copy() for o in d.Objects if 'Shape' in o.PropertiesList}
    original_breps={o.Name:o.Shape.exportBrepToString() for o in d.Objects if 'Shape' in o.PropertiesList}
    if baseline!=target:
        A.closeDocument(d.Name);d=A.openDocument(str(target));d.recompute()
    victim=d.getObject(removed)
    assert victim is None or victim.TypeId=='Part::Box' and {o.Name for o in victim.InList}=={'InteriorReservations'}
    # It was an unbound planning reservation, not a referenced purchased part.
    if victim:d.removeObject(removed)
    subset=[]
    for role in inventory['baseline']:
        o=d.getObject(role['native_slot'])
        assert o.TypeId=='Part::Box' and o.Length.Value in [14,30] and [o.Width.Value,o.Height.Value]==[19,9]
        if o.Length.Value==30:o.Length=14;o.Placement.Base.x+=8
        o.Label=role['electrical_role']+' CP2'
        o.DimensionBasis='221-412 catalogue13x18.3x8.15; reserve14x19x9; '+role['electrical_role']+'; mount/ports OPEN'
        if 'ElectricalRole' not in o.PropertiesList:o.addProperty('App::PropertyString','ElectricalRole')
        o.ElectricalRole=role['electrical_role'];d.recompute()
        cut=o.Shape.cut(old[o.Name]);assert cut.isValid() and cut.Volume<1e-5
        assert o.Shape.isValid() and len(o.Shape.Solids)==1
        subset.append(dict(name=o.Name,new_minus_old_volume_mm3=cut.Volume,valid_cut=True))
        row=next(r for r in plan['components'] if r['name']==o.Name)
        b=o.Shape.BoundBox
        row.update(origin_mm=[b.XMin,b.YMin,b.ZMin],size_mm=[b.XLength,b.YLength,b.ZLength],
                   local_size_mm=[14,19,9],placement_base_mm=list(o.Placement.Base),
                   dimension_basis=o.DimensionBasis,electrical_role=o.ElectricalRole)
    retained={n:s for n,s in old.items() if n not in changed|{removed}}
    serialization_fallbacks={}
    def unchanged_geometry(doc):
        for name,shape in retained.items():
            # Shape.copy() has a different topology handle; isSame tests that
            # handle, not geometric equality. Compare the serialized geometry.
            o=doc.getObject(name)
            assert o,(name,'missing geometry')
            if o.Shape.exportBrepToString()!=original_breps[name]:
                # OCC renormalizes direction floats on reload (~1e-16).
                # Compare the complete BRep token structure/curve parameters,
                # NOT bbox or an invalid coincident-shape Boolean difference.
                a=original_breps[name].split();b=o.Shape.exportBrepToString().split()
                assert len(a)==len(b),(name,'BRep structure changed')
                max_delta=0.;numeric_changes=0
                for p,q in zip(a,b):
                    if p==q:continue
                    delta=abs(float(p)-float(q)) # nonnumeric changes fail
                    assert math.isfinite(delta) and delta<=1e-10,(name,p,q)
                    max_delta=max(max_delta,delta);numeric_changes+=1
                serialization_fallbacks[name]=dict(numeric_tokens_changed=numeric_changes,max_numeric_delta=max_delta)
    unchanged_geometry(d)
    # A meaningful test of a changed native box, not another P_REAR audit.
    o=d.getObject('Splice_L1_CP2');width=o.Shape.BoundBox.XLength
    o.Length=15;d.recompute();assert abs(o.Shape.BoundBox.XLength-width-1)<1e-6
    o.Length=14;d.recompute();unchanged_geometry(d)
    d.saveAs(str(target));A.closeDocument(d.Name)
    d=A.openDocument(str(target));d.recompute()
    assert d.getObject(removed) is None
    assert len(d.getObject('InteriorReservations').Group)==62
    assert len(d.getObject('HarnessCandidate').Group)==18
    # Reopened topology has new handles: compare deterministic shape exports.
    unchanged_geometry(d)
    for role in inventory['baseline']:
        o=d.getObject(role['native_slot'])
        assert [o.Length.Value,o.Width.Value,o.Height.Value]==[14,19,9]
        assert o.ElectricalRole==role['electrical_role'] and o.Shape.isValid()
    A.closeDocument(d.Name)
    plan['components']=[r for r in plan['components'] if r['name']!=removed]
    proof=dict(status='FIVE_INSTALLED_ONE_OFF_ROBOT_SPARE_RECONCILED_NOT_SELECTED',
        started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=round(time.monotonic()-tick,3),prior_native_sha256=before_digest,
        native_sha256=digest(target),changed_reservations=sorted(changed),removed_unbound_reservation=removed,
        new_shapes_subset_of_old=subset,unchanged_native_shapes=len(retained),
        serialization_normalization_full_BRep_tokens=serialization_fallbacks,
        serialization_numeric_absolute_tolerance=1e-10,
        unchanged_geometry_after_reopen=True,parameter_test='Splice_L1 Length14->15: X+1; restored14',
        no_new_contact_possible_for_subset_geometry=True,
        proof_scope='Inherited clear geometric reservations only; NEW circuit identities do NOT qualify missing routes/mounts/stock',
        physical_pass=False,W1_complete=False,W5_complete=False)
    for data in [checks,plan,interface]:
        data['source_sha256'].update(inventory['source_sha256'])
        data['splice_inventory']=inventory
        data['splice_native_reconciliation']=proof
    # Persist validated gates before optional legacy metadata normalization.
    save('checks.json',checks)
    checks['count']=62
    checks['reused_unchanged_component_names']=[n for n in checks['reused_unchanged_component_names'] if n not in changed|{removed}]
    checks['shared_revision']='Five221-412 installed roles + one OFF_ROBOT spare; PostF0 additional candidate. All10 source wire pieces/8strips unchanged. Full4MTA paths/mounts/W1/W5 OPEN.'
    interface.setdefault('MTA_joint_plan',dict(selected=False,physical_pass=False,
        complete_factory_source_output_pairs=False,full_extensions_complete=False,
        native_mounts_and_restraints_open=True,W1_complete=False,W5_complete=False))
    interface['MTA_joint_plan']['joint_roles_and_old_six_splice_identity_reconciliation_open']=False
    interface['MTA_joint_plan']['rejected_inventory_scope']='Old six anonymous boxes plus eight extra joints double-counted four output roles and reserved a spare. Negative geometry is not rejection of the reconciled inventory.'
    assert all(digest(ROOT/p)==h for p,h in checks['source_sha256'].items())
    save('checks.json',checks);save('layout.json',plan);save('interfaces.json',interface)
    render(plan['components'],checks,{'logic':(.18,.53,.69),'fuses':(.72,.37,.22),
        'wago':(.96,.65,.14),'splices':(.65,.51,.15),'inline':(.52,.37,.64),'switch':(.35,.55,.40)})
    print('Splice reconciliation:',len(subset),'subsets; unchanged shapes',len(retained),
          'reopen/parameter OK; worker',proof['worker_wall_seconds'],'seconds',flush=True)


def complete_service_plan():
    """Small graph calculation, no geometry rerun. Graph aliases are not wires."""
    data=json.loads((OUT/'interfaces.json').read_text(encoding='utf-8'))
    net=json.loads(NET.read_text(encoding='utf-8'))
    assert digest(NET)==data['source_sha256'][NET.relative_to(ROOT).as_posix()]
    ports={e['a']:e['b'] for e in net['edges'] if e['kind']=='internal_bus'}
    wires={}
    for e in net['edges']:
        if e['kind']!='wire' or not (e['a'] in ports or e['b'] in ports):continue
        key=tuple(sorted([e['a'],e['b']]))
        wires.setdefault(key,[]).append(e['id'])
    external=[];internal=[]
    for (a,b),aliases in sorted(wires.items()):
        item=dict(ends=[a,b],graph_edge_aliases=aliases)
        if a in ports and b in ports:internal.append(item)
        else:
            item['tray_port']=a if a in ports else b
            external.append(item)
    assert len({e['tray_port'] for e in external})==len(external), 'Two physical wires assigned one port'
    used={p for ends in wires for p in ends if p in ports}
    assert len(used)==sum(1 for ends in wires for p in ends if p in ports)
    data['service_boundary']=dict(
        graph_scope='Existing netlist only, not newly routed wires or certified physical pin positions',
        distribution_owners=sorted(set(ports.values())),
        unique_attached_wire_pairs=len(wires),populated_ports=len(used),NC_ports=len(ports)-len(used),
        lower_boundary_wires=external,internal_tray_wires=internal,
        unclamping_only_option=dict(disconnections=len(external),extra_connector_SKUs=0,
                                  status='REJECTED_AS_ROUTINE_ATO_ACCESS; excessive disconnect/reconnect burden'),
        next_shared_plan='Direct ATO access with WAGO retained:12 extraction and5 lid/tool budgets in native model. Next actual full wires, four MTA both exits, lever access and supports together. No full service qualification from empty-space checks.',
        release_sweeps_strain_relief_and_parked_ends_open=True,
        connector_SKUs_not_invented=True,removal_qualified=False)
    # Replacement contribution only: never add old nominal cuts to CP2 cuts.
    legacy_path=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'
    assert digest(legacy_path)==data['source_sha256'][legacy_path.relative_to(ROOT).as_posix()]
    legacy={c['id']:c for c in json.loads(legacy_path.read_text(encoding='utf-8'))['conductors']}
    cuts=[]
    for w in data['nominal_source_wires']:
        if w['id'] not in ['W064','W065','W067','W068']:continue
        old=legacy[w['id']]
        assert {old['a'],old['b']}=={w['a'],w['b']},'Conductor identity changed'
        cuts.append(dict(id=w['id'],legacy_nominal_mm=old['legacy_nominal_mm'],
                         replacement_nominal_mm=w['nominal_blank_mm'],actual_cut_mm=None,
                         selected_in_R53=False,material='HELU23802 red4mm2'))
    assert len(cuts)==4
    subtotal=sum(c['replacement_nominal_mm'] for c in cuts)
    oldsum=sum(c['legacy_nominal_mm'] for c in cuts)
    red_ids=['W076_EXTENSION','W066','W064','W065','W067','W068']
    redsum=sum(w['nominal_blank_mm'] for w in data['nominal_source_wires'] if w['id'] in red_ids)
    data['source_stock_contribution']=dict(status='CANDIDATE_REPLACEMENTS_NOT_FULL_STOCK_SELECTION',
        selected=False,physical_pass=False,units='mm',S1_replacements=cuts,
        S1_legacy_subtotal_mm=oldsum,S1_replacement_subtotal_mm=subtotal,S1_delta_mm=subtotal-oldsum,
        modeled_HELU_subset_ids=red_ids,modeled_HELU_subset_subtotal_mm=redsum,
        bought_HELU_metre_quantity_not_selected=True,other_red_wires_and_trim_stock_open=True,
        factory_F0_W075_and_W076_FACTORY_not_extra_bought_HELU=True,
        TE130171_qty=4,TE130207_qty=2,ring_quantities_existing_allocations_not_extra=True,
        W1_complete=False,W5_complete=False,K3_complete=False)
    save('interfaces.json',data)
    print('WAGO service:',len(external),'external disconnects,',len(internal),'internal wires; routine unclamping rejected',flush=True)


def verify_changed_native():
    """Fresh reopen of new S1 pair/terminals, no collision rerun."""
    import FreeCAD as A
    started=time.monotonic();d=A.openDocument(str(OUT/'WholeCatInterior.FCStd'))
    wires=d.getObject('HarnessCandidate').Group
    assert len(wires)==(34 if MTA_REPACK else 18) and all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in wires)
    terminals=d.getObject('S0TerminalCandidates').Group
    assert len(terminals)==8 and all(o.Shape.isValid() for o in terminals)
    s1=d.getObject('S1TerminalCandidates').Group
    assert len(s1)==16 and all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in s1)
    g=d.getObject('MTA_RL_CP2' if MTA_REPACK else 'P_REAR_CP2');h=g.Width.Value;width=g.Shape.BoundBox.XLength
    g.Width=h+1;d.recompute();assert abs(g.Shape.BoundBox.XLength-width-1)<1e-6
    g.Width=h;d.recompute();assert abs(g.Shape.BoundBox.XLength-width)<1e-6
    checks=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
    for row in checks['nominal_source_wires']:
        name='W043_FPI_CP2' if row['id']=='W043' else row['id']+'_CP2'
        expected_volume=row['centerline_length_mm']*math.pi*(row['OD_mm']/2)**2
        assert abs(d.getObject(name).Shape.Volume-expected_volume)<1e-3,(name,'native cable volume/path')
    torso=d.getObject('TorsoEnvelope').Shape
    assert all(o.Shape.cut(torso).Volume<1e-5 for o in terminals+s1)
    A.closeDocument(d.Name)
    checks['changed_source_native_check']=dict(wires_and_strips=len(wires),S0_terminal_parts=8,S1_terminal_and_tool_parts=16,valid_single_wire_solids=True,
        cable_volume_matches_paths=True,terminals_inside_torso_without_extra_margin=True,
        parameter=g.Name+' Width+1 -> world X+1; restored without saving; wire snapshots do NOT auto-update',
        wall_seconds=round(time.monotonic()-started,3))
    save('checks.json',checks);print('Changed saved source wires/terminals:',checks['changed_source_native_check'],flush=True)


def render(rows,checks,colors):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    body=json.loads((BASE/'layout.json').read_text(encoding='utf-8'))['sections_mm']
    fig,axes=plt.subplots(3,1,figsize=(15,13),constrained_layout=True)
    for level,(ax,title) in enumerate(zip(axes,[
            'Dół: akumulator, Pi, źródło i złącza (Z15–65mm; BUS: obwiednia producenta)',
            'Środek: sterowniki,12 oprawek Z70–134,10 bocznych WAGO oraz P_SYS wejściami w górę',
            'Góra:8 poziomych WAGO, G1 wejściami w dół /5 FHAC Z125–147 / dostęp od grzbietu'])):
        xs=[s[0] for s in body];ys=[s[1] for s in body]
        ax.plot(xs,ys,color='#555555');ax.plot(xs,[-y for y in ys],color='#555555')
        for row in rows:
            x,y,z=row['origin_mm'];dx,dy,dz=row['size_mm']
            if level==0 and not (row['group']=='splices' or row['group'] in ['logic','inline'] and z<75):continue
            if level==1 and not (row['group']=='fuses' or row['group']=='wago' and z<100 or row['group'] in ['logic','inline'] and 75<=z<120 or row['name'] in ['S0_body_CP2','S1_body_CP2']):continue
            if level==2 and not (row['group']=='wago' and z>=100 or row['group']=='inline' and z>=120 or row['name'] in ['S0_key_CP2','S1_control_CP2']):continue
            name=row.get('electrical_role',row['name'].replace('_CP2',''))
            bad=any(q.get('name')==row['name'] for q in checks['outside']) or any(row['name'] in q['pair'] for q in checks['contacts']+checks['retained_contacts'])
            ax.add_patch(Rectangle((x,y),dx,dy,facecolor=colors[row['group']],alpha=.40,
                                   edgecolor='red' if bad else '#444444',linewidth=1.3))
            ax.text(x+dx/2,y+dy/2,name,ha='center',va='center',fontsize=7)
        if level==0:
            ax.add_patch(Rectangle((-23.25,-17.5),106.5,35,fill=False,edgecolor='#ab732d',linestyle='--'))
            ax.text(30,0,'Akumulator pod Pi/BUS',ha='center',fontsize=8)
        ax.set(title=title,xlabel='X mm, głowa po lewej',ylabel='Y mm',xlim=(-125,210),ylim=(-108,108))
        ax.set_aspect('equal');ax.grid(alpha=.15)
    fig.suptitle('CP2: wspólny plan przestrzeni w tułowiu325×200×160mm\nBryły rezerwacji, NIE gotowe części ani pełna wiązka',fontsize=14)
    fig.savefig(OUT/'interior-plan.png',dpi=130);plt.close(fig)


if __name__=='__main__':
    import sys
    if '--mta-shared-plan' in sys.argv:
        mta_shared_plan()
    elif '--reconcile-splice-native' in sys.argv:
        reconcile_splice_native()
    elif '--verify-changed-native' in sys.argv:
        verify_changed_native()
    elif '--service-plan-only' in sys.argv:
        complete_service_plan()
    elif '--render-only' in sys.argv:
        plan=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
        checks=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
        render(plan['components'],checks,{'logic':(.18,.53,.69),'fuses':(.72,.37,.22),
               'wago':(.96,.65,.14),'splices':(.65,.51,.15),'inline':(.52,.37,.64),'switch':(.35,.55,.40)})
    else:main()

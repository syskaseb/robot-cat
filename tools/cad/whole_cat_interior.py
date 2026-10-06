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

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging'
OUT = BASE / 'cp2'
NET = ROOT / 'hardware/electronics/full-cat/connection-map-e4-r1/netlist.json'
BUS = ROOT / 'hardware/electronics/full-cat/pi-bus-primary-r1/PCB.brep'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


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
             ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json']}
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

    box('Pi4_CP2', [-19,-28,42], [85,56,22], 'logic', '85x56 PCB; populated height22 prototype reserve')
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
    box('BUS_CP2',bus_origin,bus_size, 'logic',
        'Waveshare25514 full vendor envelope rotated90Z; cached117-solid compound invalid, envelope only NOT exact fit')
    box('Monitor_CP2', [-44,30,50], [41,25,12], 'logic', 'P309 supplier41x25x12; pin exits/clip/lead still provisional')
    box('PWM9685_CP2', [-39,-12.7,78], [62.5,25.4,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    box('AUX4092_CP2', [35,-12.7,78], [18.8,25.4,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    box('PWM1608_CP2', [70,-25.4,78], [43.18,50.8,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    # Panel flange + TE assemblies + bend space are ONE envelope, not fictitious catalog depth.
    for side, y in [('L',58), ('R',-58)]:
        for i, x in enumerate([-53,-21,11,43,75,107], 1):
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
            box(name+'_CP2',[x-15,y-4.5,75],[30,19,9],'wago',
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
            else:
                by=-16 if name=='D_RR' else y
                box(name+'_CP2',[x-size[0]/2,by-size[1]/2,110],size,'wago',
                    'SKU-specific221-615/415 planning bounds; G1 moved to front for battery minus; not an old qualified route')
    for y, prefix in [(55,'L'),(-55,'R')]:
        for i, x in enumerate([-43,0,43],1):
            origin=([-94,-25,40] if i==1 else [-55,-12,40]) if prefix=='R' and i in [1,2] else [x-15,y-9.5,40]
            box(f'Splice_{prefix}{i}_CP2', origin, [30,19,9], 'splices',
                '221-412 role, intentionally oversized415 planning reserve; not catalog412 dimension')
    for name,x,y in [('FL',-35,84),('RL',55,84),('FR',-35,-84),('RR',55,-84)]:
        box('MTA_'+name+'_CP2', [x-17.5,y-11,80], [35,22,16], 'inline',
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
    for name,z,r,h,shell in [('S0_body_CP2',57,28.5,40,True),
                              ('S0_neck_CP2',97,11,3,True),
                              ('S0_key_CP2',100,15,63.5,False)]:
        o=d.addObject('Part::Cylinder', name);o.Radius=r;o.Height=h
        o.Placement.Base=A.Vector(-77,0,z);g.addObject(o);d.recompute()
        shapes[name]=o.Shape.copy()
        rows.append(dict(name=name,origin_mm=[-77-r,-r,z],size_mm=[2*r,2*r,h],group='switch',
                         dimension_basis='Existing HELLA family reserve rotated vertical; studs/lugs/opening conditional',
                         require_internal_shell=shell))
    box('S1_body_CP2', [137,26,75], [42,24,37], 'switch',
        'NKK S821 body24x42x34 +3 axial budget; rotated90deg; terminals not qualified')
    o=d.addObject('Part::Cylinder','S1_control_CP2');o.Radius=14;o.Height=32
    o.Placement.Base=A.Vector(158,38,112);g.addObject(o);d.recompute()
    shapes[o.Name]=o.Shape.copy()
    rows.append(dict(name=o.Name,origin_mm=[144,24,112],size_mm=[28,28,32],group='switch',
                     dimension_basis='22mm lever + +/-28deg conservative cylinder; shell aperture/tool still required',
                     require_internal_shell=False))
    print('Shared layout:',len(rows),'modules;20 buses,12 holders/24 ends,6 splices,4 MTA,5 branch FHAC+F0+axial F_PWM',flush=True)

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

    wires=[dict(metadata=fpi_wire,shape=lead,targets=['F_PI_CP2','P_SYS_CP2'])]
    def routed_wire(identifier,role_a,role_b,edges,diameter,targets,extra,limit,basis,entry_strip=None):
        p=Part.Wire(edges);point=edges[0].Vertexes[0].Point
        profile=Part.Wire([Part.makeCircle(diameter/2,point,A.Vector(1,0,0))])
        shape=p.makePipeShell([profile],True,False)
        assert shape.isValid() and len(shape.Solids)==1
        length=p.Length+extra;assert length<=limit
        ob=d.addObject('Part::Feature',identifier+'_CP2');ob.Shape=shape;hg.addObject(ob)
        ob.addProperty('App::PropertyString','Status');ob.Status=basis
        if entry_strip:
            location,direction,mm=entry_strip
            ob=d.addObject('Part::Feature',identifier+'_strip_CP2')
            ob.Shape=Part.makeCylinder(1.02,mm,location,direction);hg.addObject(ob)
        meta=dict(id=identifier,a=role_a,b=role_b,centerline_length_mm=p.Length,
                  termination_allowance_in_blank_mm=extra,nominal_blank_mm=length,limit_mm=limit,
                  OD_mm=diameter,dimension_basis=basis,physical_pass=False,
                  geometry='builder-owned snapshot',factory_polarity_from_markings_not_left_right=True)
        wires.append(dict(metadata=meta,shape=shape,targets=targets))
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
            wbb=ws.BoundBox
            clearance=Part.makeBox(wbb.XLength+2*wall,wbb.YLength+2*wall,wbb.ZLength+2*wall,
                                  A.Vector(wbb.XMin-wall,wbb.YMin-wall,wbb.ZMin-wall)).cut(torso)
            if not clearance.isValid():raise RuntimeError('Invalid cable enclosure check')
            if clearance.Volume>1e-5:outside.append(dict(name=wn,outside_mm3=clearance.Volume))
        except Exception as ex:errors.append(dict(pair=[wn,'Torso'],error=str(ex)))
    for wa,wb in itertools.combinations(wires,2):
        if not broad(wa['shape'],wb['shape']):continue
        checked+=1;c0=wa['shape'].common(wb['shape'])
        if not c0.isValid():errors.append(dict(pair=[wa['metadata']['id'],wb['metadata']['id']],error='Invalid wire-wire Boolean'))
        elif c0.Volume>1e-5:wire_hits.append(dict(pair=[wa['metadata']['id'],wb['metadata']['id']],volume_mm3=c0.Volume))
    clean=not (errors or outside or contacts or chassis_hits or access_hits or wire_hits)
    checks=dict(status='COARSE_SHARED_RESERVATIONS_CLEAR' if clean else 'LAYOUT_PREFLIGHT_REQUIRES_CHANGE',
                selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
                count=len(rows),bus_roles_sorted=sorted(wanted),source_sha256=pins,
                wall_clearance_reserve_mm=wall,exact_brep_intersections_after_bbox_filter=checked,
                outside=outside,contacts=contacts,retained_contacts=chassis_hits,errors=errors,
                service_reservations=access,service_contacts=access_hits,
                service_motion_supplier_verified=False,W043_nominal_route=fpi_wire,
                nominal_source_wires=[w['metadata'] for w in wires],
                wire_contacts=wire_hits,wire_termination_target_bodies_excluded={w['metadata']['id']:w['targets'] for w in wires},
                reused_unchanged_component_names=sorted(unchanged),
                reused_reference_basis='Prior clear proof + unchanged CP1 reference hashes and exact box coordinates/rotation; changed interfaces and new wire checked')
    checks['BUS_vendor_compound_valid'] = bus_reference_valid
    checks['BUS_contact_test_basis'] = 'full vendor bounding reservation, NOT invalid compound'
    if prior and prior.get('rejected_preflights'):
        checks['rejected_preflights'] = prior['rejected_preflights']
    if prior and prior['status']=='LAYOUT_PREFLIGHT_REQUIRES_CHANGE':
        checks.setdefault('rejected_preflights', []).append(
            {k:prior[k] for k in ['outside','contacts','retained_contacts','errors']})
    save('checks.json',checks)
    print('Preflight:',checks['status'],'outside',outside,'contacts',contacts,'retained',chassis_hits,'service',access_hits,'wire',wire_hits,'errors',errors,flush=True)
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
    assert len(d.getObject('HarnessCandidate').Group)==5
    assert all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in d.getObject('HarnessCandidate').Group)
    # Changed up-entry box parameter, not an unrelated unchanged Pi retest.
    ob=d.getObject('P_SYS_CP2');h=ob.Height.Value;w=ob.Shape.BoundBox.YLength
    ob.Height=h+1;d.recompute()
    assert abs(ob.Shape.BoundBox.YLength-w-1)<1e-6
    ob.Height=h;d.recompute();A.closeDocument(d.Name)
    checks.update(native_reopen=True,box_parameter_roundtrip=True,
                  parameter_test='P_SYS local Height+1 -> world Y footprint+1; restored; cable is explicitly builder-owned snapshot')
    checks['previous_preflight_history_git']='9d04972:hardware/cad/studies/whole-cat-packaging/cp2/checks.json'
    checks['shared_revision']='Joint XT60/F0/negative return/F_PI/MAIN/front splice and central source layout; W001/W075/W043 modeled;17 access reserves retained. Source-switch and remaining full wiring OPEN.'
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
                               'Four main MTA atY+/-84,Z80..96 retain BOTH factory exits; trunk radius25.2 needs explicit X/Z turns.',
                               'Crossings only through assigned between-level risers; full wire radii/straight ends/straps must be modeled together.',
                               'Rotated XT60/F0 in front-side source bay: W075 and W001 full nominal paths modeled with changed MAIN/front splice/G1. Mate/release/actual marked polarity and W076 switch lead still OPEN.',
                               'Nine central WAGO Z110..121 plus up-entry P_SYS Z95..117; five FHAC Z125..147. F_PI nominal input modeled; remaining sources/grounds/4MTA/outputs OPEN.'],
              not_qualified=['Factory exit datums except vendor BUS USB; FHAC thickness22 prototype assumption, P309 pins/clips, XT60 mating half',
                             'S0 stud/lug/tool access and exact delivered SKU',
                             'S1 four terminals, bushing, panel aperture and hand access',
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
                 usb_mouth_mm=[103.81628928,11.1220508043,45.7695251897],usb_direction=[1,0,0],
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
    interface['nominal_source_wires']=[w['metadata'] for w in wires];save('interfaces.json',interface)
    complete_service_plan()
    render(rows,checks,colors)
    print('Saved native candidate/reopen; worker',plan['worker_wall_seconds'],'seconds',flush=True)


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
    save('interfaces.json',data)
    print('WAGO service:',len(external),'external disconnects,',len(internal),'internal wires; routine unclamping rejected',flush=True)


def verify_changed_native():
    """Only newly introduced saved source wires/G1, no layout collision rerun."""
    import FreeCAD as A
    started=time.monotonic();d=A.openDocument(str(OUT/'WholeCatInterior.FCStd'))
    wires=d.getObject('HarnessCandidate').Group
    assert len(wires)==5 and all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in wires)
    g=d.getObject('G1_CP2');h=g.Height.Value;width=g.Shape.BoundBox.YLength
    g.Height=h+1;d.recompute();assert abs(g.Shape.BoundBox.YLength-width-1)<1e-6
    g.Height=h;d.recompute();assert abs(g.Shape.BoundBox.YLength-width)<1e-6
    A.closeDocument(d.Name)
    checks=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
    checks['changed_source_native_check']=dict(wires_and_strips=5,valid_single_solids=True,
        parameter='G1 Height+1 -> world Y+1; restored without saving; wire snapshots do NOT auto-update',
        wall_seconds=round(time.monotonic()-started,3))
    save('checks.json',checks);print('Changed saved source wires/G1:',checks['changed_source_native_check'],flush=True)


def render(rows,checks,colors):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    body=json.loads((BASE/'layout.json').read_text(encoding='utf-8'))['sections_mm']
    fig,axes=plt.subplots(3,1,figsize=(15,13),constrained_layout=True)
    for level,(ax,title) in enumerate(zip(axes,[
            'Dół: akumulator, Pi, źródło i złącza (Z15–65mm; BUS: obwiednia producenta)',
            'Środek: sterowniki,12 oprawek Z70–134,10 bocznych WAGO Z56–75',
            'Góra:10 centralnych WAGO Z110–121 /5 FHAC Z125–147 / dostęp od grzbietu'])):
        xs=[s[0] for s in body];ys=[s[1] for s in body]
        ax.plot(xs,ys,color='#555555');ax.plot(xs,[-y for y in ys],color='#555555')
        for row in rows:
            x,y,z=row['origin_mm'];dx,dy,dz=row['size_mm']
            if level==0 and not (row['group']=='splices' or row['group'] in ['logic','inline'] and z<75):continue
            if level==1 and not (row['group']=='fuses' or row['group']=='wago' and z<100 or row['group'] in ['logic','inline'] and 75<=z<120 or row['name'] in ['S0_body_CP2','S1_body_CP2']):continue
            if level==2 and not (row['group']=='wago' and z>=100 or row['group']=='inline' and z>=120 or row['name'] in ['S0_key_CP2','S1_control_CP2']):continue
            name=row['name'].replace('_CP2','')
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
    if '--verify-changed-native' in sys.argv:
        verify_changed_native()
    elif '--service-plan-only' in sys.argv:
        complete_service_plan()
    elif '--render-only' in sys.argv:
        plan=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
        checks=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
        render(plan['components'],checks,{'logic':(.18,.53,.69),'fuses':(.72,.37,.22),
               'wago':(.96,.65,.14),'splices':(.65,.51,.15),'inline':(.52,.37,.64),'switch':(.35,.55,.40)})
    else:main()

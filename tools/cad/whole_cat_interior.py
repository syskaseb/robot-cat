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

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging'
OUT = BASE / 'cp2'
NET = ROOT / 'hardware/electronics/full-cat/connection-map-e4-r1/netlist.json'


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
             ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json']}
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

    def box(name, origin, size, group, basis, shell=True):
        o = d.addObject('Part::Box', name)
        o.Length, o.Width, o.Height = size
        o.Placement.Base = A.Vector(*origin)
        g.addObject(o)
        o.addProperty('App::PropertyString', 'DimensionBasis'); o.DimensionBasis = basis
        o.addProperty('App::PropertyString', 'Role'); o.Role = name
        d.recompute()
        shapes[name] = o.Shape.copy()
        rows.append(dict(name=name, origin_mm=origin, size_mm=size, group=group,
                         dimension_basis=basis, require_internal_shell=shell))

    box('Pi4_CP2', [-19,-28,42], [85,56,22], 'logic', '85x56 PCB; populated height22 prototype reserve')
    box('MAIN4853_CP2', [-61,-12,42], [30.5,24,12], 'logic', '22.9x30.5x7.7 supplier board + solder reserve')
    box('BUS_CP2', [70,-11,41], [30,22,24], 'logic', 'SPACE BUDGET ONLY: R53 575070 adapter/carrier must be reconciled')
    box('Monitor_CP2', [-55,17,43], [35,25,11], 'logic', 'SPACE BUDGET ONLY: exact P309 populated bounds still required')
    box('PWM9685_CP2', [-39,-12.7,78], [62.5,25.4,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    box('AUX4092_CP2', [35,-12.7,78], [18.8,25.4,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    box('PWM1608_CP2', [70,-25.4,78], [43.18,50.8,30], 'logic', 'CP1 PCB footprint; height30 replaceable assembly reserve')
    # Panel flange + TE assemblies + bend space are ONE envelope, not fictitious catalog depth.
    for side, y in [('L',50), ('R',-50)]:
        for i, x in enumerate([-53,-21,11,43,75,107], 1):
            box(f'F_{side}{i}_CP2', [x-14,y-13,63], [28,26,64], 'fuses',
                'MTA0300330 flange28x15, below panel24.5; TE-IN23.749/OUT21.717; '
                'engagement e=0 provisional; remaining height is ATO/bend budget, NOT measured fit')
    names = [['FL_P','FL_G','D_FL','RL_P','RL_G'],
             ['FR_P','FR_G','D_FR','RR_P','RR_G'],
             ['P_SYS','P_FRONT','P_REAR','G1','G2'],
             ['D_RL','D_RR','P_AUX','G_AUX','G_TAIL']]
    wanted = {e['b'] for e in json.loads(NET.read_text(encoding='utf-8'))['edges'] if e['kind']=='internal_bus'}
    assert wanted == {n for r in names for n in r}, 'Every logical bus must have exactly one place'
    for y, ns in zip([49,-49,17,-17], names):
        for x, name in zip([-40,1,42,83,124], ns):
            box(name+'_CP2', [x-18.5,y-11,130], [37,22,11], 'wago',
                '37x22x11 planning max of221-615/415; role SKU/port map retained, not changed to615')
    for y, prefix in [(55,'L'),(-55,'R')]:
        for i, x in enumerate([-43,0,43],1):
            box(f'Splice_{prefix}{i}_CP2', [x-15,y-9.5,40], [30,19,9], 'splices',
                '221-412 role, intentionally oversized415 planning reserve; not catalog412 dimension')
    for name,x,y in [('FL',-35,84),('RL',55,84),('FR',-35,-84),('RR',55,-84)]:
        box('MTA_'+name+'_CP2', [x-17.5,y-11,80], [35,22,16], 'inline',
            '0100335 rolled family budget35x22x16; BOTH exit faces retained; exact L140 length unknown')
    for i,(x,y) in enumerate([(-43,79),(0,79),(43,79),(-43,-79),(0,-79)],1):
        box(f'FHAC_branch{i}_CP2', [x-17.5,y-8,47], [35,16,16], 'inline',
            'FHAC0001ZXJ SPACE BUDGET ONLY; factory housing/lead bounds require reconciliation')
    box('F0_CP2', [-55,-38,42], [35,18,16], 'inline',
        'FHAC0002ZXJ SPACE BUDGET ONLY; <=50mm battery-to-fuse lead NOT yet routed')
    box('XT60_CP2', [-95,-15,38], [30,18,18], 'inline',
        'SPACE BUDGET ONLY: housing+exit; colocated with front F0; source pin and <=50mm prefuse path still require routing')
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
    print('Shared layout:',len(rows),'reservations;20 buses,12 holders/24 ends,6 splices,4 MTA,5 branch FHAC+F0',flush=True)

    def broad(a,b):
        return a.BoundBox.intersect(b.BoundBox)

    errors, outside, contacts, chassis_hits = [], [], [], []
    wall = 2.4
    for row in rows:
        name=row['name'];s=shapes[name]
        if row['require_internal_shell']:
            p=row['origin_mm'];v=row['size_mm']
            reserve=Part.makeBox(*(a+2*wall for a in v), A.Vector(*(a-wall for a in p)))
            try:
                c=reserve.cut(torso)
                if not c.isValid(): raise RuntimeError('Invalid enclosure boolean')
                if c.Volume>1e-5:outside.append(dict(name=name,outside_mm3=c.Volume))
            except Exception as e:errors.append(dict(pair=[name,'Torso'],error=str(e)))
    checked=0
    for na,nb in itertools.combinations(shapes,2):
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
        for rn,rs,cat in refs:
            if not broad(s,rs):continue
            try:
                checked+=1;c=s.common(rs)
                if not c.isValid():raise RuntimeError('Invalid retained-part intersection')
                if c.Volume>1e-5:chassis_hits.append(dict(pair=[name,rn],volume_mm3=c.Volume,category=cat))
            except Exception as e:errors.append(dict(pair=[name,rn],error=str(e)))
    clean=not (errors or outside or contacts or chassis_hits)
    checks=dict(status='COARSE_SHARED_RESERVATIONS_CLEAR' if clean else 'LAYOUT_PREFLIGHT_REQUIRES_CHANGE',
                selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
                count=len(rows),bus_roles_sorted=sorted(wanted),source_sha256=pins,
                wall_clearance_reserve_mm=wall,exact_brep_intersections_after_bbox_filter=checked,
                outside=outside,contacts=contacts,retained_contacts=chassis_hits,errors=errors)
    save('checks.json',checks)
    print('Preflight:',checks['status'],'outside',outside,'contacts',contacts,'retained',chassis_hits,'errors',errors,flush=True)
    colors={'logic':(.18,.53,.69),'fuses':(.72,.37,.22),'wago':(.96,.65,.14),
            'splices':(.65,.51,.15),'inline':(.52,.37,.64),'switch':(.35,.55,.40)}
    for row in rows:
        ob=d.getObject(row['name'])
        if ob.ViewObject:ob.ViewObject.ShapeColor=colors[row['group']]
    if d.getObject('TorsoEnvelope').ViewObject:d.getObject('TorsoEnvelope').ViewObject.Transparency=85
    d.getObject('Layout').Status='CP2: REZERWACJE PRZESTRZENI, NIE WYBRANY MONTAŻ'
    target=OUT/'WholeCatInterior.FCStd'
    d.recompute();d.saveAs(str(target));A.closeDocument(d.Name)
    d=A.openDocument(str(target));d.recompute()
    assert len(d.getObject('InteriorReservations').Group)==len(rows)
    assert all(d.getObject(r['name']).Shape.isValid() for r in rows)
    # Native box parameter roundtrip, without modifying the saved candidate.
    ob=d.getObject('Pi4_CP2');h=ob.Height.Value;ob.Height=h+1;d.recompute()
    assert abs(ob.Shape.BoundBox.ZLength-h-1)<1e-6
    ob.Height=h;d.recompute();A.closeDocument(d.Name)
    checks.update(native_reopen=True,box_parameter_roundtrip=True)
    if prior and prior['status']=='LAYOUT_PREFLIGHT_REQUIRES_CHANGE':
        history=prior.get('rejected_preflights',[])
        if 'rejected_first_preflight' in prior:history.append(prior['rejected_first_preflight'])
        history.append({k:prior[k] for k in ['outside','contacts','retained_contacts','errors']})
        checks['rejected_preflights']=history
        checks['shared_revision']='Two preflights exposed missing common chassis-height constraint. '
        checks['shared_revision']+='Raise ALL fuse assemblies above61mm P0 hips and ALL upper WAGO correspondingly; '
        checks['shared_revision']+='narrow upper outer rows for curved roof; front source connector colocated with F0, not rear. No cassette cutouts.'
    assert all(digest(ROOT/p)==h for p,h in pins.items()),'Reference source was modified'
    save('checks.json',checks)
    plan=dict(status=checks['status'],selected=False,source_sha256=pins,components=rows,
              phase1_result_count=14,phase1_denominator=20,
              removal_strategy=['Disconnect every source, open dorsal cover before operating clamps.',
                               'Upper distribution plate Z128..130 and two fuse panels assembled on the bench; four mount axes X=-65/131,Y=+/-75.',
                               'Outer WAGO rows are above ATOs: upper distribution plate must be removable BEFORE replacing fuses. Do not claim direct fuse access.',
                               'Do NOT reuse49-cut-tie removal. Design labeled detachable boundary first; actual joints/ports pending.',
                               'Lift only after boundary disconnection; lower PCBs/Pi reached after upper module removal.',
                               'P0 legs/frame and battery cradle stay; new removable shell/wall apertures not fabricated yet.'],
              wire_space_plan=['Central low-voltage lanes between PCB edgeY25.4 and fuse-panel bands innerY37 (11.6mm).',
                               'Power lanes between fuse bands outerY63 and inline bands innerY73 (10mm); radius25.2 turns require separate X/Z bays.',
                               'Crossings only through assigned between-level risers; full wire radii/straight ends/straps must be modeled together.',
                               'XT60 and F0 in front source bay: no long unfused route to rear. Exact pins/factory leads and <=50mm route NOT yet qualified.',
                               '20 upper WAGO blocks have4mm X gaps; lever access requires open dorsal cover, not a guessed closed-cover sector.'],
              not_qualified=['SKU-specific BUS/P309/FHAC/XT60 dimensions and port exits',
                             'S0 stud/lug/tool access and exact delivered SKU',
                             'S1 four terminals, bushing, panel aperture and hand access',
                             'All full wire solids, 24 ends, bend radii, usable lengths and stock',
                             'Structural supports/fasteners, shell walls and motion sweeps',
                             'Assembly/removal swept volumes and actual connector release'],
              old_supports_superseded=['Deck','Carrier','Cover','BankLeft','BankRight','PiTray','4 fixed loom frames'],
              started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
              worker_wall_seconds=round(time.monotonic()-tick,3))
    save('layout.json',plan)
    render(rows,checks,colors)
    print('Saved native candidate/reopen; worker',plan['worker_wall_seconds'],'seconds',flush=True)


def render(rows,checks,colors):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    body=json.loads((BASE/'layout.json').read_text(encoding='utf-8'))['sections_mm']
    fig,axes=plt.subplots(3,1,figsize=(15,13),constrained_layout=True)
    for level,(ax,title) in enumerate(zip(axes,[
            'Dół: akumulator, Pi, źródło i złącza (rezerwacje Z~32–65mm)',
            'Środek: sterowniki / dwie listwy po6 bezpieczników (listwy Z63–127mm)',
            'Góra:20 bloków WAGO (Z130–141mm) / dostęp po zdjęciu grzbietu'])):
        xs=[s[0] for s in body];ys=[s[1] for s in body]
        ax.plot(xs,ys,color='#555555');ax.plot(xs,[-y for y in ys],color='#555555')
        for row in rows:
            x,y,z=row['origin_mm'];dx,dy,dz=row['size_mm']
            if level==0 and not (row['group']=='splices' or row['group'] in ['logic','inline'] and z<75):continue
            if level==1 and not (row['group']=='fuses' or row['group'] in ['logic','inline'] and z>=75 or row['name'] in ['S0_body_CP2','S1_body_CP2']):continue
            if level==2 and not (row['group']=='wago' or row['name'] in ['S0_key_CP2','S1_control_CP2']):continue
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
    if '--render-only' in sys.argv:
        plan=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
        checks=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
        render(plan['components'],checks,{'logic':(.18,.53,.69),'fuses':(.72,.37,.22),
               'wago':(.96,.65,.14),'splices':(.65,.51,.15),'inline':(.52,.37,.64),'switch':(.35,.55,.40)})
    else:main()

"""Whole-cat packaging checkpoint. Saved sources stay read-only.

The new envelope and module placements are a layout proposal, not printable
parts, a solver assembly, or qualification of inherited mounts/wiring.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/cad'))
OUT = ROOT / 'hardware/cad/studies/whole-cat-packaging'

PROPOSAL = dict(HeadForward=42., HeadRaise=25., TailRearward=0., TailRaise=15.,
                BodyHalfWidth=100., BodyFloor=-2., BodyRoof=158., WallReservation=2.4)
SECTIONS = [(-120,38,60,126,28),(-99,76,16,147,55),(-65,100,-2,158,65),
            (70,100,-2,158,65),(142,86,8,158,60),(185,54,30,147,48),(205,20,75,133,18)]
NECK_SECTIONS = [(-142,85,28),(-175,151,28)]


def profile_geometry(A, Part, half, bottom, roof, radius):
    import math
    a,b,c,d=-half,half,bottom,roof
    points=[(a+radius,c),(b-radius,c),(b,c+radius),(b,d-radius),
            (b-radius,d),(a+radius,d),(a,d-radius),(a,c+radius)]
    V=lambda p:A.Vector(p[0],p[1],0)
    edges=[]
    for i in [0,2,4,6]:
        edges.append(Part.LineSegment(V(points[i]),V(points[i+1])))
        j=(i+2)%8
        corner=[(b,c),(b,d),(a,d),(a,c)][i//2]
        cx=corner[0]+(-radius if corner[0]==b else radius)
        cy=corner[1]+(radius if corner[1]==c else -radius)
        v1=V(points[i+1]);v2=V(points[j])
        mid=A.Vector(cx+(v1.x+v2.x-2*cx)/math.sqrt(2),cy+(v1.y+v2.y-2*cy)/math.sqrt(2),0)
        edges.append(Part.Arc(v1,mid,v2))
    return edges


def refine_proportions():
    """Refine ONLY this owned, unselected layout after human visual rejection."""
    import FreeCAD as A
    import Part
    import Sketcher
    from check_main_p0_placement import sha
    info=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
    assert info['selected'] is False and info['status']=='CP1_LAYOUT_PROPOSAL_SAVED'
    assert all(sha(ROOT/p)==h for p,h in info['source_sha256'].items())
    d=A.openDocument(str(OUT/'WholeCatLayout.FCStd'))
    params=d.getObject('Layout')
    if params.getTypeIdOfProperty('BodyFloor')=='App::PropertyLength':
        params.removeProperty('BodyFloor')
        params.addProperty('App::PropertyDistance','BodyFloor','Layout')
    for name,value in PROPOSAL.items():setattr(d.getObject('Layout'),name,value)
    for i,(x,half,bottom,roof,radius) in enumerate(SECTIONS):
        sk=d.getObject('TorsoSection'+str(i))
        for j in reversed(range(sk.GeometryCount)):sk.delGeometry(j)
        sk.Placement.Base=A.Vector(x,0,0)
        for j in sk.addGeometry(profile_geometry(A,Part,half,bottom,roof,radius),False):
            sk.addConstraint(Sketcher.Constraint('Block',j))
        sk.Label='Przekrój tułowia X='+str(x)+' mm'
    for i,(x,z,r) in enumerate(NECK_SECTIONS):
        sk=d.getObject('NeckSection'+str(i));sk.Placement.Base=A.Vector(x,0,z)
        sk.setDatum(0,A.Units.Quantity(str(2*r)+' mm'))
    d.recompute()
    torso=d.getObject('TorsoEnvelope').Shape
    assert torso.isValid() and len(torso.Solids)==1
    assert d.getObject('NeckMountReservation').Shape.isValid()
    b=torso.BoundBox
    info['params_mm']=PROPOSAL;info['sections_mm']=SECTIONS
    info['torso_bbox_mm']=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    info['human_review']='Previous 356x304x234 box rejected as sheep-like; feline proportions take priority over inherited cassette packaging.'
    info['candidate_parts_needing_relayout']=['Deck','Cover','Carrier','Platform','BankLeft','BankRight',
                                             'FLFixedFrame','FRFixedFrame','RLFixedFrame','RRFixedFrame','Head_Fork']
    for row in info['parts']:
        shift=(-PROPOSAL['HeadForward'],0,PROPOSAL['HeadRaise']) if row['category']=='head' else (0,0,PROPOSAL['TailRaise']) if row['category']=='tail' else (0,0,0)
        old=row['shift_mm'];row['bounds_mm']=[row['bounds_mm'][i]+shift[i%3]-old[i%3] for i in range(6)]
        row['shift_mm']=list(shift)
    limitation='Feline envelope intentionally does not enclose the inherited cassette; cassette layout must be redesigned at CP2, not wrapped by a larger shell.'
    if limitation not in info['limitations']:info['limitations'].append(limitation)
    d.saveAs(str(OUT/'WholeCatLayout.FCStd'));A.closeDocument(d.Name)
    d=A.openDocument(str(OUT/'WholeCatLayout.FCStd'));d.recompute()
    assert d.getObject('TorsoEnvelope').Shape.isValid()
    assert d.getObject('Layout').HeadRaise.Value==25
    A.closeDocument(d.Name)
    info['proportions_refined_utc']=datetime.now(timezone.utc).isoformat()
    save('layout.json',info)
    print('Feline envelope',b.XLength,b.YLength,b.ZLength,flush=True)


def save(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def verify():
    """Focused CP1 source, placement and editable-proposal checks, not a fit audit."""
    import FreeCAD as A
    import Part
    import zipfile
    from check_main_p0_placement import SavedShapes, sha
    info=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
    inventory=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT/p)==h for p,h in info['source_sha256'].items())
    reader=SavedShapes()
    earchecks=[]
    main=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
    with zipfile.ZipFile(OUT/'reference-shapes.zip') as archive:
        assert set(archive.namelist())=={r['brep'] for r in inventory['parts']}
        for name in ['EarL','EarR']:
            original=reader.shape(main,name)
            wrapper=reader.doc(main).get('Rigid_'+name)
            if wrapper is not None:original.Placement=reader.placement(wrapper)*original.Placement
            ref=Part.Shape();ref.importBrepFromString(archive.read('Head_'+name+'.brep').decode('utf-8'))
            # Invariant geometry plus real set difference, not bounding-box equality.
            difference=original.cut(ref).Volume+ref.cut(original).Volume
            assert original.isValid() and ref.isValid() and difference<1e-5
            earchecks.append(dict(name=name,symmetric_difference_mm3=difference,
                                  volume_mm3=ref.Volume,equals_saved_E6=True))
    d=A.openDocument(str(OUT/'WholeCatLayout.FCStd'));d.recompute()
    p=d.getObject('Layout');params={n:getattr(p,n).Value for n in PROPOSAL}
    assert all(abs(params[n]-v)<1e-7 for n,v in PROPOSAL.items()), params
    body=d.getObject('TorsoEnvelope').Shape
    assert body.isValid() and len(body.Solids)==1
    assert d.getObject('NeckMountReservation').Shape.isValid()
    refs=d.getObject('SavedReferences').Group
    assert len(refs)==len(inventory['parts'])
    for r in info['parts']:
        o=d.getObject(r['name']);shift=o.Placement.Base-o.SourcePlacement.Base
        assert (shift-A.Vector(*r['shift_mm'])).Length<1e-7
    for parameter,name,axis,sign in [('HeadForward','Head_Nose','x',-1),
                                  ('HeadRaise','Head_EarL','z',1),
                                  ('TailRearward','TailBridge','x',1),
                                  ('TailRaise','TailBridge','z',1)]:
        obj=d.getObject(name);before=getattr(obj.Placement.Base,axis)
        nominal=getattr(p,parameter).Value
        setattr(p,parameter,nominal+1);d.recompute()
        assert abs(getattr(obj.Placement.Base,axis)-before-sign)<1e-7
        setattr(p,parameter,nominal);d.recompute()
        assert abs(getattr(obj.Placement.Base,axis)-before)<1e-7
    A.closeDocument(d.Name)  # Parameter probes are deliberately not saved.
    assert all(sha(ROOT/f)==h for f,h in info['source_sha256'].items())
    save('checks.json',dict(scope='CP1 layout only; no shell, wiring, motion or assembly qualification',
        checked_utc=datetime.now(timezone.utc).isoformat(),sources_unchanged=True,
        fresh_reopen=True,torso_valid_single_solid=True,neck_valid=True,
        snapshots=len(refs),all_reference_shifts_checked=True,parameter_roundtrip=True,
        E6_ears=earchecks,physical_pass=False))
    print('CP1 checked: source pins, E6 ears, 191 placements, reopen, four parameter roundtrips',flush=True)


def inputs():
    import FreeCAD as A
    import Part
    from check_main_p0_placement import SavedShapes, prop, sha
    reader = SavedShapes()
    entry = ROOT / 'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
    old = reader.doc(entry)
    result = []

    def add(name, shape, category, source, kind='saved native reference'):
        # OCCT spline boxes can be conservative. Vertex extents of the display
        # tessellation are labelled sampled extents, never collision evidence.
        vertices, _ = shape.tessellate(1.0)
        xyz = [list(p) for p in vertices]
        bounds = [min(p[i] for p in xyz) for i in range(3)] + [max(p[i] for p in xyz) for i in range(3)]
        filename = name + '.brep'
        shape.exportBrep(str(OUT / filename))
        result.append(dict(name=name, category=category, source=source, kind=kind,
                           display_bounds_mm=bounds, volume_mm3=shape.Volume,
                           valid=shape.isValid(), brep=filename))
        save('inventory-progress.json', dict(parts=result, source_sha256=reader.hashes))

    OUT.mkdir(parents=True, exist_ok=True)
    # Leg geometry and load-bearing chassis remain at their exact saved poses.
    for wrapper, obj in old.items():
        if not wrapper.startswith('Rigid_'):
            continue
        name = prop(obj, 'Group')[0][0].get('value')
        label = prop(obj, 'Label')[0].get('value')
        take = (name.startswith('Part__Feature') and name not in ['Part__Feature005', 'Part__Feature038'])
        take |= name in ['FrameFront20', 'FrameRear20', 'SideLeft22', 'SideRight22']
        take |= name.startswith(('MountFront', 'MountRear', 'NutShoe'))
        take |= name.startswith(('TailModule29_', 'TailRoot29', 'MG92B', 'UpperHousing34', 'BearingCap34',
                                 'BearingLower34', 'BearingUpper34', 'OuterSpacer34', 'InnerSpacer34', 'SpindleCap34'))
        if not take:
            continue
        s = reader.shape(entry, name)
        s.Placement = reader.placement(obj) * s.Placement
        category = 'tail' if name.startswith(('Tail', 'MG92B', 'UpperHousing', 'Bearing', 'OuterSpacer', 'InnerSpacer', 'Spindle')) else 'chassis'
        add('P0_' + name, s, category, dict(file=entry.relative_to(ROOT).as_posix(), object=name, wrapper=wrapper, label=label),
            'retained P0 snapshot; tail internals require selected-adapter reconciliation' if category == 'tail' else 'retained P0 snapshot')
    print('P0 references', len(result), flush=True)

    def native(name, rel, obj, category, parent=None, offset=None):
        p = ROOT / rel
        s = reader.shape(p, obj)
        if parent:
            s.Placement = reader.placement(reader.doc(p)[parent]) * s.Placement
        if offset:
            s.translate(A.Vector(*offset))
        add(name, s, category, dict(file=rel, object=obj, parent=parent, offset_mm=offset))

    # Selected lower parts, not the old example battery and old Pi tray.
    native('BatteryPlate', 'hardware/cad/studies/battery-p0/r4/chassis/BottomPlateP0.FCStd', 'Plate', 'battery')
    native('BatteryTray', 'hardware/cad/studies/battery-p0/r4/electronics/BatteryCarrierP0.FCStd', 'Carrier', 'battery')
    native('TailBridge', 'hardware/cad/studies/tail-p0-bridge-flange-r1/TailBridgeP0Flange.FCStd', 'TailBridge', 'tail')
    battery = Part.makeBox(106.5, 35, 21.5, A.Vector(-23.25, -17.5, 5))
    add('BatteryReservation', battery, 'battery', dict(dimensions_basis='selected nominal Gens Ace 106.5 x 35 x 21.5; placement on tray to qualify'), 'nominal purchased reservation')

    world = dict(
        Deck='hardware/cad/studies/w5-remote-end-native-r1/CompleteDeck_CANDIDATE_WORLD.brep',
        Cover='hardware/electronics/full-cat/w5-carrier-first-service-ports-plan-r1/Cover_PORTS_CANDIDATE.brep',
        Carrier='hardware/cad/studies/w5-side-retention-native-r1/SourceCarrier_CANDIDATE_WORLD.brep',
        Platform='hardware/cad/studies/w5-source-platform-native-r4/Platform_WORLD.brep',
        BankLeft='hardware/cad/studies/w5-source-bank-passage-native-r1/BankLeft_WORLD.brep',
        BankRight='hardware/cad/studies/servo-fuse-bank-inner-feed-service-r1/BankRight_WORLD.brep',
        PiTray='hardware/cad/studies/pi-complete-native-r2/PiTray_WORLD.brep',
    )
    for leg in ['FL', 'FR', 'RL', 'RR']:
        world[leg + 'FixedFrame'] = 'hardware/cad/studies/w5-loom-fixed-native-r1/' + leg + 'FixedFrame_CANDIDATE_WORLD.brep'
    pins = {}
    for name, rel in world.items():
        pins[rel] = sha(ROOT / rel)
        add(name, Part.read(str(ROOT / rel)), 'electronics', dict(file=rel), 'latest saved W1/W5 candidate; not selected R53')
    sidefile = 'hardware/electronics/full-cat/w5-side-retention-plan-r2/plan.json'
    pins[sidefile] = sha(ROOT / sidefile)
    for row in json.loads((ROOT / sidefile).read_text(encoding='utf-8'))['blocks']:
        b = row['bounds_mm']
        add('WAGO_' + row['name'], Part.makeBox(*(b[i+3]-b[i] for i in range(3)), A.Vector(*b[:3])),
            'electronics', dict(file=sidefile, record=row['name']), 'saved purchased block reservation')
    for name, b in dict(PCA9685=[-59,-12.7,154,3.5,12.7,184], AUX4092=[16,-12.7,154,34.8,12.7,184],
                        Adafruit1608=[67.41,-25.4,154,110.59,25.4,184], Pi4=[-19,-28,52,66,28,74]).items():
        add(name, Part.makeBox(*(b[i+3]-b[i] for i in range(3)), A.Vector(*b[:3])), 'electronics',
            dict(basis='existing layout reservation; populated heights assumed, Pi placement requires exact tray datum'), 'nominal purchased reservation')
    print('Electronics references', len(result), flush=True)

    # Current split face and shaped E6 ears, with all transformations carried
    # by the saved conditional assembly, composed once by SavedShapes.
    head = 'hardware/cad/studies/head-p8/head-yaw-fit-jaws-r2/HeadFitR2.FCStd'
    for name in ['FrontLeft','Rear','Nose','EarL','EarR','PassiveJournal','CageBase','CageRetainerLeft','CageRetainerRight']:
        native('Head_' + name, head, name, 'head')
    native('Head_FrontRight', 'hardware/cad/studies/head-external-wire-support-r1/FrontRightWirePassage.FCStd',
           'WireInterface0', 'head')
    # World BReps of the latest fork and carriers avoid duplicate parent poses.
    for name, rel in dict(Fork='hardware/cad/studies/head-yaw-end-restraints-r2/ForkYawEndSeatSplices.brep',
                          YawCarrier='hardware/cad/studies/head-fixed-yaw-feed-r3/YawCarrierJRSeat.brep',
                          PitchCarrier='hardware/cad/studies/head-jr-support-r5/PitchCarrierThroughLeadExit.brep').items():
        pins[rel] = sha(ROOT / rel)
        add('Head_' + name, Part.read(str(ROOT / rel)), 'head', dict(file=rel), 'latest saved head candidate')
    native('Head_Foundation', 'hardware/cad/studies/head-p7/yaw-support-r1/NeckFoundationR2.FCStd', 'Foundation', 'head')
    native('Head_Bridge', 'hardware/cad/studies/head-p8/head-yaw-open-key-r1/bridge-passage-r5/YawBridgeHornPassageR5.FCStd', 'Bridge', 'head')
    hipfile = 'hardware/simulation/p0/e6-leg-compatibility.json'
    pins[hipfile] = sha(ROOT / hipfile)
    hips = [q for q in json.loads((ROOT / hipfile).read_text(encoding='utf-8'))['axes'] if q['stage'] == 'Hip']
    pins['hardware/manufacturing/one-batch-prototype-r53/selection.json'] = sha(ROOT / 'hardware/manufacturing/one-batch-prototype-r53/selection.json')
    assert all(sha(ROOT / rel) == h for rel, h in {**reader.hashes, **pins}.items())
    save('inventory.json', dict(parts=result, hips=hips, source_sha256={**reader.hashes, **pins},
                               scope='packaging reference inventory, not complete physical part accounting',
                               omissions=['wiring geometry and fastener inventory; exact PCB populated heights',
                                          'head/tail small purchased parts and selected printed horns; phase2 calibration'],
                               current_selection='R53', completed=14, total=20))
    for category in ['head', 'electronics', 'tail', 'chassis', 'battery']:
        rows = [q for q in result if q['category'] == category]
        bounds = [min(q['display_bounds_mm'][i] for q in rows) for i in range(3)] + [max(q['display_bounds_mm'][i] for q in rows) for i in range(3,6)]
        print(category, [round(a,2) for a in bounds], flush=True)


def render():
    import FreeCAD as A
    import Part
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.colors import to_rgb
    import zipfile
    import math
    import numpy as np
    inventory=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
    layout=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
    moved={r['name']:r for r in layout['parts']}
    doc=A.openDocument(str(OUT/'WholeCatLayout.FCStd'))
    torso=doc.getObject('TorsoEnvelope').Shape
    shapes=[]
    with zipfile.ZipFile(OUT/'reference-shapes.zip') as z:
        for row in inventory['parts']:
            s=Part.Shape();s.importBrepFromString(z.read(row['brep']).decode('utf-8'))
            shift=moved[row['name']]['shift_mm'];s.translate(A.Vector(*shift))
            vertices,faces=s.tessellate(1.2)
            shapes.append((row['name'],row['category'],[list(p) for p in vertices],faces))
    vertices,faces=torso.tessellate(1)
    shapes.append(('TorsoEnvelope','torso',[list(p) for p in vertices],faces))
    vertices,faces=doc.getObject('NeckMountReservation').Shape.tessellate(1)
    shapes.append(('NeckMountReservation','torso',[list(p) for p in vertices],faces))
    colors=dict(chassis='#48525b',head='#71818c',tail='#657783',torso='#a8bcc5',electronics='#4e9abb',battery='#dbb16e')
    external_head={'Head_FrontLeft','Head_FrontRight','Head_Rear','Head_Nose','Head_EarL','Head_EarR'}
    flagged=set(layout['candidate_parts_needing_relayout'])
    limits=dict(side=((-285,330),(-190,320)),front=((-180,180),(-190,320)),top=((-285,330),(-180,180)))
    # Vectorize view projections rather than repeat Python loops per triangle.
    meshes=[]
    for name,category,vertices,faces in shapes:
        triangles=np.asarray(vertices,dtype=float)[np.asarray(faces,dtype=int)]
        normals=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
        lengths=np.linalg.norm(normals,axis=1);lengths[lengths==0]=1
        meshes.append((name,category,triangles,normals,lengths))

    def draw(ax,view,inside=False):
        projected=[];depths=[];facecolors=[]
        depth_axis={'side':1,'front':0,'top':2}[view]
        axes={'side':(0,2),'front':(1,2),'top':(0,1)}[view]
        for name,category,triangles,normals,lengths in meshes:
            if not inside:
                if category in ('electronics','battery'):continue
                if category=='head' and name not in external_head:continue
            if inside and category=='torso':continue
            mask=normals[:,depth_axis]>0 if view=='top' else normals[:,depth_axis]<0
            pts=triangles[mask]
            shade=.62+.38*np.abs(normals[mask,depth_axis]/lengths[mask])
            base=(.78,.32,.25) if inside and name in flagged else (.59,.38,.40) if name=='Head_Nose' else to_rgb(colors[category])
            projected.append(pts[:,:,axes]);depths.append(pts[:,:,depth_axis].mean(axis=1))
            facecolors.append(shade[:,None]*np.asarray(base)[None,:])
        positions=np.concatenate(projected);depth=np.concatenate(depths);color=np.concatenate(facecolors)
        order=np.argsort(depth)
        if view!='top':order=order[::-1]
        ax.add_collection(PolyCollection(positions[order],facecolors=color[order],edgecolors='none',antialiaseds=False,rasterized=True))
        (xlim,ylim)=limits[view];ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.set_aspect('equal')
        ax.grid(alpha=.14);ax.tick_params(labelsize=8)
        ax.set_xlabel('Y [mm]' if view=='front' else 'X [mm]')
        ax.set_ylabel('Y [mm]' if view=='top' else 'Z [mm]')
        if view!='top':ax.axhline(layout['sampled_ground_z_mm'],color='#c4cad0',lw=1)
        if view=='side':
            for x,color,label in [(-88.81,'#987652','przednie biodra P0'),(130.81,'#987652','tylne biodra P0')]:
                ax.axvline(x,color=color,ls=':',lw=.8)
                if not inside:ax.text(x,-183,label,rotation=0,ha='center',fontsize=7,color=color)
            if inside:
                xs=[q[0] for q in layout['sections_mm']]
                ax.plot(xs,[q[3] for q in layout['sections_mm']],color='#8b99a0',lw=2,ls='--')
                ax.plot(xs,[q[2] for q in layout['sections_mm']],color='#8b99a0',lw=2,ls='--')
        if view=='front':
            half=layout['params_mm']['BodyHalfWidth'];roof=layout['params_mm']['BodyRoof']
            ax.annotate('',xy=(-half,roof+10),xytext=(half,roof+10),arrowprops=dict(arrowstyle='<->',color='#596d78'))
            ax.text(0,roof+17,f'tułów: {2*half:g} mm',ha='center',fontsize=9,color='#596d78')

    fig,axes=plt.subplots(2,2,figsize=(15,13),dpi=130)
    for ax,view,inside,title in [(axes[0,0],'side',False,'Bok: proporcje całego kota'),(axes[0,1],'front',False,'Przód: pełniejszy tułów i zachowane uszy E6'),
                               (axes[1,0],'top',False,'Góra: obrys i rozstaw nóg P0'),(axes[1,1],'side',True,'Wnętrze: czerwone podpory wymagają nowego układu')]:
        draw(ax,view,inside);ax.set_title(title,fontsize=11)
    fig.suptitle('Checkpoint 1 • propozycja układu całego kota',fontsize=17,fontweight='bold')
    fig.text(.5,.015,'Propozycja, nie gotowy wydruk. Widok wnętrza bez objętości tułowia; podpory i chwyty przewodów do CP2. R53 pozostaje wybrany.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.035,1,.96));fig.savefig(OUT/'feline-overview.png');plt.close(fig)
    for view in (['side','front','top'] if '--individual' in sys.argv else []):
        fig,ax=plt.subplots(figsize=(11,7),dpi=145);draw(ax,view)
        ax.set_title('Robot-cat • checkpoint 1 • '+{'side':'bok','front':'przód','top':'góra'}[view],fontsize=14)
        fig.tight_layout();fig.savefig(OUT/(view+'.png'));plt.close(fig)
    A.closeDocument(doc.Name)
    print('Rendered actual CAD projections: overview'+(' + side/front/top' if '--individual' in sys.argv else ''),flush=True)


def build():
    import FreeCAD as A
    import Part
    import Sketcher
    import zipfile
    from check_main_p0_placement import sha
    import math
    start = datetime.now(timezone.utc)
    inventory = json.loads((OUT / 'inventory.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT / rel) == h for rel, h in inventory['source_sha256'].items())
    pi_basis='tools/cad/pi4_mount_complete_r1.py'
    inventory['source_sha256'][pi_basis]=sha(ROOT/pi_basis)
    assert not (OUT / 'WholeCatLayout.FCStd').exists(), 'Preserve previous checkpoint'
    doc = A.newDocument('WholeCatLayout')
    refs = doc.addObject('App::DocumentObjectGroup', 'SavedReferences')
    refs.Label = 'Zapisane części / P0 + R53 + kandydaci W1 W5'
    params = doc.addObject('App::VarSet', 'Layout')
    values = PROPOSAL
    for name, value in values.items():
        kind='App::PropertyDistance' if name=='BodyFloor' else 'App::PropertyLength'
        params.addProperty(kind, name, 'Layout');setattr(params,name,value)
    params.addProperty('App::PropertyString', 'Status', 'Layout')
    params.Status = 'PROPOZYCJA UKŁADU: mocowania, wiązka i ruch do kwalifikacji'
    rows = []
    colors = dict(chassis=(.24,.28,.32), head=(.40,.46,.50), tail=(.32,.38,.42),
                  electronics=(.30,.57,.67), battery=(.80,.55,.23))
    # Correct the earlier coarse Pi reservation without reimporting the assembly.
    # Footprint/origin come from the existing Pi mounting study, PCB Z45 + R1 raise7.
    # Populated height22 is a design reservation, NOT catalog qualification.
    for row in inventory['parts']:
        if row['name']=='Pi4':
            bounds=[-19,-28,52,66,28,74]
            s=Part.makeBox(85,56,22,A.Vector(*bounds[:3]))
            s.exportBrep(str(OUT/row['brep']))
            row.update(display_bounds_mm=bounds,volume_mm3=s.Volume,valid=s.isValid(),
                       source=dict(file='tools/cad/pi4_mount_complete_r1.py',
                                   basis='85x56 PCB origin -19,-28; PCB Z45 plus existing Pi raise7; height22 assumed'))
    save('inventory.json',inventory)
    for row in inventory['parts']:
        s = Part.read(str(OUT / row['brep']))
        obj = doc.addObject('PartDesign::Feature', row['name'])
        obj.Label = row['name'];obj.Shape = s
        obj.addProperty('App::PropertyPlacement', 'SourcePlacement');obj.SourcePlacement=obj.Placement
        obj.addProperty('App::PropertyString', 'SourceReference');obj.SourceReference = json.dumps(row['source'],ensure_ascii=False)
        obj.addProperty('App::PropertyString', 'ReferenceKind');obj.ReferenceKind = row['kind']
        obj.addProperty('App::PropertyString', 'Category');obj.Category = row['category']
        refs.addObject(obj)
        if row['category'] == 'head':
            obj.setExpression('Placement.Base.x', f'({obj.SourcePlacement.Base.x:.15g} mm)-Layout.HeadForward')
            obj.setExpression('Placement.Base.z', f'({obj.SourcePlacement.Base.z:.15g} mm)+Layout.HeadRaise')
        elif row['category'] == 'tail':
            obj.setExpression('Placement.Base.x', f'({obj.SourcePlacement.Base.x:.15g} mm)+Layout.TailRearward')
            obj.setExpression('Placement.Base.z', f'({obj.SourcePlacement.Base.z:.15g} mm)+Layout.TailRaise')
        if obj.ViewObject:
            obj.ViewObject.ShapeColor = colors[row['category']]
            obj.ViewObject.LineColor = (.12,.15,.18)
        rows.append((row, obj))

    # Lofted rounded cross-sections expose the new envelope as a native,
    # editable design. It is a filled volume reservation, not a shell wall.
    profiles = []
    # x, halfwidth, bottom, roof, corner radius. Wider roof accommodates the
    # current PCB-height reservations without forcing wiring against a curve.
    sections = SECTIONS
    rot = A.Rotation(A.Vector(0,0,1), A.Vector(1,0,0))
    for index, (x, half, bottom, roof, radius) in enumerate(sections):
        sketch = doc.addObject('Sketcher::SketchObject','TorsoSection'+str(index))
        sketch.Label = 'Przekrój tułowia X='+str(x)+' mm'
        # local x -> world -Z, local y -> world Y. Rect then translated about Z.
        # Use local horizontal Y, vertical Z via an explicit orthonormal basis.
        sketch.Placement = A.Placement(A.Vector(x,0,0), A.Rotation(A.Vector(0,1,0),A.Vector(0,0,1),A.Vector(1,0,0),'ZXY'))
        edges=profile_geometry(A,Part,half,bottom,roof,radius)
        ids=sketch.addGeometry(edges,False)
        # Fixed profile coordinates document the first proposed envelope;
        # module offsets remain live parameters. Refine wall design in CP3.
        for edge in ids:sketch.addConstraint(Sketcher.Constraint('Block',edge))
        profiles.append(sketch)
        sketch.Visibility=False
    doc.recompute()
    torso = doc.addObject('Part::Loft','TorsoEnvelope')
    torso.Sections=profiles;torso.Solid=True;torso.Ruled=True
    torso.Label='Tułów: przestrzeń projektu, nie gotowa osłona PETG'
    torso.addProperty('App::PropertyString','Purpose');torso.Purpose='Overall shape and space reservation; wall, access panels, leg reliefs and mounting pending'
    if torso.ViewObject:
        torso.ViewObject.ShapeColor=(.50,.57,.60);torso.ViewObject.Transparency=75
    doc.recompute()
    assert torso.Shape.isValid() and len(torso.Shape.Solids)==1
    # A neck transition volume makes the proposed load path visible. It is
    # deliberately not accepted as a finished mount or a replacement servo.
    neck_profiles=[]
    for index,(x,z,radius) in enumerate(NECK_SECTIONS):
        sk=doc.addObject('Sketcher::SketchObject','NeckSection'+str(index))
        sk.Placement=A.Placement(A.Vector(x,0,z),A.Rotation())
        circle=sk.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),radius),False)
        sk.addConstraint(Sketcher.Constraint('Diameter',circle,2*radius))
        sk.addConstraint(Sketcher.Constraint('Coincident',circle,3,-1,1))
        sk.Visibility=False;neck_profiles.append(sk)
    doc.recompute()
    neck=doc.addObject('Part::Loft','NeckMountReservation')
    neck.Sections=neck_profiles;neck.Solid=True;neck.Ruled=False
    neck.Label='Szyja: obrys przejścia / wspornik i kanał OPEN'
    if neck.ViewObject:
        neck.ViewObject.ShapeColor=(.50,.57,.60);neck.ViewObject.Transparency=60
    doc.recompute()
    probe=next(o for r,o in rows if r['name']=='Head_Nose')
    nominal=list(probe.Placement.Base)
    params.HeadForward=43;doc.recompute();assert abs(probe.Placement.Base.x-nominal[0]+1)<1e-7
    params.HeadForward=42;doc.recompute();assert (probe.Placement.Base-A.Vector(*nominal)).Length<1e-7
    params.TailRaise=values['TailRaise']+1;doc.recompute()
    tailobj=next(o for r,o in rows if r['name']=='TailBridge')
    assert abs(tailobj.Placement.Base.z-tailobj.SourcePlacement.Base.z-values['TailRaise']-1)<1e-7
    params.TailRaise=values['TailRaise'];doc.recompute()
    doc.saveAs(str(OUT/'WholeCatLayout.FCStd'))
    planned=[]
    for row,obj in rows:
        shift=list(obj.Placement.Base-obj.SourcePlacement.Base)
        planned.append(dict(name=row['name'],category=row['category'],shift_mm=shift,
                           bounds_mm=[row['display_bounds_mm'][i]+shift[i%3] for i in range(6)],
                           kind=row['kind']))
    b=torso.Shape.BoundBox
    report=dict(status='CP1_LAYOUT_PROPOSAL_SAVED',sources_unchanged=True,source_sha256=inventory['source_sha256'],
        params_mm=values,sections_mm=sections,parts=planned,retained_P0_axes=True,retained_E6_ears=True,
        torso_bbox_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
        editable=['TorsoSection0..6 fixed profile geometry + native Loft; edit sketches for body changes',
                  'Layout HeadForward/HeadRaise/TailRearward/TailRaise + expressions'],
        informational_params=['BodyHalfWidth','BodyFloor','BodyRoof','WallReservation'],
        candidate_parts_needing_relayout=['Deck','Cover','Carrier','Platform','BankLeft','BankRight',
                                          'FLFixedFrame','FRFixedFrame','RLFixedFrame','RRFixedFrame','Head_Fork'],
        sampled_ground_z_mm=min(q['bounds_mm'][2] for q in planned if q['category']=='chassis'),
        snapshots=len(rows), parameter_roundtrip=True,phase1_completed=14,phase1_total=20,
        selected=False,physical_pass=False,printable_shell=False,whole_wiring_qualified=False,
        head_mount_qualified=False,tail_mount_qualified=False,motion_qualified=False,
        next='CP1 visual review; then joint space allocation and mounts/service at CP2. Do not resume microcuts.',
        limitations=inventory['omissions']+['Tail/head moved as whole reference groups: new structural load paths needed',
            'Torso is filled spatial reservation; intersections of interior references are intentional',
            'Neck loft is a planning reservation; wall, physical hardware and new harness not designed'],
        started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat())
    save('layout.json',report)
    archive=OUT/'reference-shapes.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for row in inventory['parts']:z.write(OUT/row['brep'],row['brep'])
    A.closeDocument(doc.Name)
    # Fresh open confirms the snapshot layout is self-contained.
    reopened=A.openDocument(str(OUT/'WholeCatLayout.FCStd'))
    reopened.recompute()
    assert reopened.getObject('TorsoEnvelope').Shape.isValid()
    assert len(reopened.getObject('SavedReferences').Group)==len(rows)
    reopened_nose=reopened.getObject('Head_Nose')
    assert abs(reopened_nose.Placement.Base.x-reopened_nose.SourcePlacement.Base.x+42)<1e-7
    A.closeDocument(reopened.Name)
    report['fresh_reopen']=True
    report['finished_utc']=datetime.now(timezone.utc).isoformat()
    report['worker_wall_seconds']=(datetime.now(timezone.utc)-start).total_seconds()
    save('layout.json',report)
    print('Layout',len(rows),'references; body', [round(b.XLength,1),round(b.YLength,1),round(b.ZLength,1)],flush=True)


if __name__ == '__main__':
    if '--verify' in sys.argv:verify()
    elif '--refine-proportions' in sys.argv:refine_proportions()
    elif '--render' in sys.argv:render()
    elif '--build' in sys.argv:build()
    else:inputs()

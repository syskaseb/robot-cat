"""One raised source-star platform with body retention and a shared inlet grip.

R4 places both bolts west of the full W066 cable envelope, not just its
inlet. R3 retains one cable/bolt-tip interference. The integral access C-frame replaces the closed bolt roof with a C-frame access corridor; narrows the
bearing footprint away from the installed FL strap, relocates both bolt axes
away from its head/W066, and moves the inlet strap head clear of XB22.
Two M3x12 fasteners on the actual left Deck rail, a native bearing pad,
two T18I145 straps, full W043/W066 routes, and staged tool access. No changes
to P0 or electrical nets. Only this source inlet module is qualified here;
the four S1 routes and the complete source family remain open.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,sys,math,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-source-platform-native-r4'
CAD=ROOT/'hardware/cad/studies/w5-source-platform-native-r4'
INLET=ROOT/'hardware/electronics/full-cat/w5-source-inlet-joint-r2/checks.json'
PARENT=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r3'
TIE=ROOT/'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json'
DECK=ROOT/'hardware/cad/studies/w5-bus-native-grips-r4/BusStrapSlots.FCStd'

def specification():
    return dict(foot=[-100.4,23,109,-86.4,45,112],deck_bearing_pad=[-100.4,23,105,-86.4,45,109],
        bolt_centres=[[-94.4,27.5],[-94.4,40.5]],body_bounds=[-87.5,7,131,-50.5,29,142],
        insulation_centres=[[-84,2,135.5],[-76.5,2,135.5]],groove_allowance_mm=.2,
        strap_SKU='111-02370',strap_length_mm=145,strap_band_mm=[2.5,1.2],
        separate_platform_prints=1,replacement_deck=True,new_M3x12=2,new_M3_nuts=2,new_M3_washers=4,
        body_ties=1,shared_inlet_ties=1,selected=False,physical_pass=False)

def main():
    import FreeCAD as A
    import Part,MeshPart
    from w5_r53_owners import installed
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    inlet=json.loads(INLET.read_text(encoding='utf-8'))
    assert inlet['status']=='SOURCE_INLET_PAIR_STATIC_CLEAR_SUPPORTS_OPEN' and not inlet['hits'] and not inlet['errors']
    assert all(sha(ROOT/k)==v for k,v in {**inlet['source_sha256'],**inlet['files']}.items())
    spec=specification();tie=json.loads(TIE.read_text(encoding='utf-8'))
    assert tie['length_mm']==145 and tie['band_thickness_mm']==1.2
    owners,pins,_=installed(A,Part);original_deck=owners.pop('CandidateDeck')
    owners.pop('P_SYS_design')
    for key in list(owners):
        if key.startswith(('source-switch-layout-r6/W066_','R49/W043_')):owners.pop(key)
    owners['P_SYS_candidate']=Part.read(str(PARENT/'CHANGED_BODIES_WORLD.brep')).childShapes()[0]
    owners['W066_candidate']=Part.read(str(PARENT/'SOURCE_ROUTES_WORLD.brep')).childShapes()[4]
    owners['W043_candidate']=Part.read(str(INLET.parent/'W043_WORLD.brep'))
    d=A.newDocument('SourceStarInletPlatform');target=CAD/'SourceInletPlatform.FCStd';d.saveAs(str(target))
    p=d.addObject('App::VarSet','InletParameters');p.addProperty('App::PropertyLength','GrooveAllowance');p.GrooveAllowance=.2
    primitives=[]
    def box(name,b):
        q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2]
        q.Placement.Base=A.Vector(*b[:3]);primitives.append(q);return q
    def cylinder(name,point,r,h,axis=(0,0,1),expression=None):
        q=d.addObject('Part::Cylinder',name);q.Radius=r;q.Height=h
        q.Placement=A.Placement(A.Vector(*point),A.Rotation(A.Vector(0,0,1),A.Vector(*axis)))
        if expression:q.setExpression('Radius',expression)
        primitives.append(q);return q
    def compound(name,objects):
        q=d.addObject('Part::Compound',name);q.Links=objects;return q
    raw=d.addObject('Part::MultiFuse','PlatformRaw');raw.Refine=False
    raw.Shapes=[box('Foot',spec['foot']),
        box('FrontUpright',[-100.4,23,111.8,-86.4,24,131]),
        box('RearUpright',[-100.4,44,111.8,-86.4,45,131]),
        box('WestBackbone',[-100.4,23,111.8,-98.8,45,131]),
        box('BodyShelf',[-100.4,7,126,-50.5,29,131]),
        box('BodyBackStop',[-87.8,29.3,129,-50.2,31.3,134]),
        box('BackStopRoot',[-87.8,28.7,126,-50.2,31.3,130.8]),
        box('BodyEastStop',[-50.2,7,129,-48.2,31.3,134]),
        box('EastStopRoot',[-51,7,126,-48.2,31.3,130.8]),
        box('InletBridge',[-100.4,0,126,-71.8,9,131]),
        box('W066Seat',[-87.3,0,130.8,-80.7,5.5,135.3]),
        box('W043Seat',[-79.8,0,130.8,-73.2,5.5,135.3])]
    tools=[cylinder('FootHole'+str(i),[x,y,108.8],1.7,3.4) for i,(x,y) in enumerate(spec['bolt_centres'])]
    tools += [box('OpenDriverCorridor',[-98,23.9,115.3,-90.8,44.1,135]),cylinder('W066Groove',[-84,-.1,135.5],2.3,5.7,(0,1,0),'2.1 mm + InletParameters.GrooveAllowance'),
        cylinder('W043Groove',[-76.5,-.1,135.5],1.9,5.7,(0,1,0),'1.7 mm + InletParameters.GrooveAllowance'),
        box('InletTieWestSlot',[-88.15,.4,125.8,-86.25,3.6,139.2]),
        box('InletTieEastSlot',[-73.65,.4,125.8,-71.75,3.6,139.2]),
        box('BodyTieSouthSlot',[-58.6,5.3,125.8,-55.4,7,143.7]),
        box('BodyTieNorthSlot',[-58.6,28.8,125.8,-55.4,31.7,143.7])]
    platform=d.addObject('Part::Cut','PlatformFinished');platform.Base=raw;platform.Tool=compound('PlatformPassages',tools);platform.Refine=False
    pad=box('DeckBearingPad',spec['deck_bearing_pad'])
    d.recompute();d.save();assert platform.Shape.isValid() and len(platform.Shape.Solids)==1
    assert all(q.Shape.isValid() and not q.Shape.check(True) for q in primitives)
    nominal=platform.Shape.Volume;p.GrooveAllowance=.3;d.recompute();probe=platform.Shape.Volume
    assert probe<nominal;p.GrooveAllowance=.2;d.recompute();assert abs(platform.Shape.Volume-nominal)<1e-5;d.save()
    def solidbox(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def xz_band(points,y,width):
        vs=[A.Vector(x,y,z) for x,z in points]
        return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,width,0))
    pieces={
        'InletTieWest':solidbox([-87.8,.75,124.6,-86.6,3.25,139]),
        'InletTieEast':solidbox([-73.3,.75,124.6,-72.1,3.25,138.6]),
        'InletTieBottom':solidbox([-87.8,.75,124.6,-72.1,3.25,125.8]),
        'InletTieTop':xz_band([(-87.8,137.8),(-81,137.8),(-78,137.4),(-72.1,137.4),(-72.1,138.6),(-78,138.6),(-81,139),(-87.8,139)],.75,2.5),
        'InletTieHead':solidbox([-72.7,-1.25,121.1,-67.9,3.25,124.6]),
        'BodyTieSouth':solidbox([-58.25,5.6,124.6,-55.75,6.8,143.5]),
        'BodyTieNorth':solidbox([-58.25,29.2,124.6,-55.75,30.4,143.5]),
        'BodyTieBottom':solidbox([-58.25,5.6,124.6,-55.75,30.4,125.8]),
        'BodyTieTop':solidbox([-58.25,5.6,142.3,-55.75,30.4,143.5]),
        'BodyTieHead':solidbox([-59.25,29.2,121.1,-54.75,34,124.6])}
    hardware={}
    def cylinder_solid(r,h,point):return Part.makeCylinder(r,h,A.Vector(*point))
    for i,(x,y) in enumerate(spec['bolt_centres']):
        hardware['Bolt'+str(i)]=Part.makeCompound([cylinder_solid(1.5,12,[x,y,100.5]),cylinder_solid(2.85,3,[x,y,112.5])])
        hardware['Washers'+str(i)]=Part.makeCompound([cylinder_solid(3.5,.5,[x,y,z]).cut(cylinder_solid(1.6,.5,[x,y,z])) for z in (104.5,112)])
        vertices=[A.Vector(x+3.175*math.cos(a*math.pi/3),y+3.175*math.sin(a*math.pi/3),102.1) for a in range(6)]
        hardware['Nut'+str(i)]=Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(A.Vector(0,0,2.4)).cut(cylinder_solid(1.5,2.4,[x,y,102.1]))
    shapes={'Platform':platform.Shape.copy(),'DeckBearingPad':pad.Shape.copy(),**pieces,**hardware}
    for name,s in shapes.items():s.exportBrep(str(OUT/(name+'_WORLD.brep')))
    hits=[];errors=[];pairs=0
    def check(label,s,key,t):
        nonlocal pairs
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    common=a.common(b)
                    if common.Volume>1e-5:
                        bb=common.BoundBox;hits.append(dict(part=label,owner=key,mm3=common.Volume,bounds_mm=[getattr(bb,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc:errors.append(dict(part=label,owner=key,error=str(exc)))
    # Native pad deliberately joins existing rail; this is a load-path contact,
    # not an omitted foreign obstacle. Bore modification is checked below.
    bearing_join=pad.Shape.common(original_deck).Volume
    assert bearing_join>1e-5
    for label,s in shapes.items():
        for key,t in owners.items():check(label,s,key,t)
        if label not in ('DeckBearingPad',) and not label.startswith(('Bolt','Washers','Nut')):check(label,s,'OriginalDeck',original_deck)
    for label,s in {**pieces,**hardware}.items():check(label,s,'Platform',platform.Shape)
    for label,s in pieces.items():check(label,s,'DeckBearingPad',pad.Shape)
    labels=list(hardware)
    for i,label in enumerate(labels):
        for other in labels[i+1:]:check(label,hardware[label],other,hardware[other])
    # Before body/Carrier/Cover fitting, both heads are reachable from above.
    for i,(x,y) in enumerate(spec['bolt_centres']):
        allowance=cylinder_solid(3.5,35,[x,y,115.5]);allowance.exportBrep(str(OUT/('Bolt'+str(i)+'_DRIVER_ALLOWANCE.brep')))
        for key,t in {**owners,'Platform':platform.Shape}.items():
            if key in ('P_SYS_candidate','Cover','hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep'):continue
            check('Driver'+str(i),allowance,key,t)
    base=dict(status='SOURCE_PLATFORM_REJECTED' if hits or errors else 'SOURCE_PLATFORM_LOCAL_NATIVE_CLEAR_DECK_PENDING',
        hits=hits,errors=errors,pairs=pairs,specification=spec,bearing_pad_to_existing_rail_join_mm3=bearing_join,
        parameter_allowance_mm=[.2,.3,.2],parameter_volumes=[nominal,probe,platform.Shape.Volume],
        strict_new_primitive_BOP_errors=0,full_final_strict_BOP_verified=False,
        reused_routes=['W043 inlet-r2','W066 source-r3'],four_S1_routes_qualified=False,
        T18I_supplier=TIE.relative_to(ROOT).as_posix(),strap_loop_allowance_mm={'body':85,'inlet':61},
        minimum_pull_tail_allowance_mm=20,nominal_strap_geometry_not_physical_test=True,
        native_retention=True,native_deck_complete=False,closed_STLs=False,relocated_reopen=False,
        selected=False,W5_complete=False,physical_pass=False,started_utc=begin.isoformat())
    assert all(length+tie['head_length_mm']+20<tie['length_mm'] for length in base['strap_loop_allowance_mm'].values())
    pins += [ROOT/'tools/electronics/w5_source_platform_native_r3.py',ROOT/'hardware/electronics/full-cat/w5-source-platform-native-r3/checks.json',ROOT/'tools/electronics/w5_source_platform_native_r2.py',ROOT/'hardware/electronics/full-cat/w5-source-platform-native-r2/checks.json',Path(__file__),INLET,PARENT/'checks.json',TIE,DECK]
    def receipt():
        end=datetime.now(timezone.utc);base.update(finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds(),
            source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in list(dict.fromkeys(pins))},
            files={q.relative_to(ROOT).as_posix():sha(q) for q in [*OUT.glob('*.brep'),*CAD.glob('*.FCStd'),*CAD.glob('*.brep'),*CAD.glob('*.stl')]})
        save(OUT/'checks.json',base)
    print('SOURCE_PLATFORM_CONTACTS',pairs,len(hits),len(errors),flush=True)
    if hits or errors:receipt();return
    # One-way native Deck modification: bearing pad and two actual through bores.
    parent=A.openDocument(str(DECK));link=d.addObject('App::Link','SelectedDeck');link.setLink(parent.BusStrapSlotsFinished)
    link.LinkPlacement=parent.BusStrapSlotsFinished.Placement
    fused=d.addObject('Part::MultiFuse','DeckWithBearingPad');fused.Shapes=[link,pad];fused.Refine=False
    holes=[cylinder('DeckThroughHole'+str(i),[x,y,104.8],1.7,7.4) for i,(x,y) in enumerate(spec['bolt_centres'])]
    deck=d.addObject('Part::Cut','SourcePlatformDeckFinished');deck.Base=fused;deck.Tool=compound('DeckMountingBores',holes);deck.Refine=False
    d.save();print('SOURCE_PLATFORM_DECK_RECOMPUTE',flush=True);d.recompute();d.save()
    assert deck.Shape.isValid() and len(deck.Shape.Solids)==1
    for label,s in hardware.items():check(label,s,'FinishedDeck',deck.Shape)
    base.update(pairs=pairs,hits=hits,errors=errors,native_deck_complete=True)
    if hits or errors:base['status']='SOURCE_PLATFORM_DECK_REJECTED';receipt();return
    dependencies=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    assert all(q.is_relative_to(ROOT) for q in dependencies);pins+=dependencies
    nominal=[platform.Shape.Volume,deck.Shape.Volume];dimensions={}
    for name,s in [('Platform',platform.Shape),('Deck',deck.Shape)]:
        s.exportBrep(str(CAD/(name+'_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        bb=mesh.BoundBox;dimensions[name]=[bb.XLength,bb.YLength,bb.ZLength]
        assert bb.XLength+6<=256 and bb.YLength+6<=256 and bb.ZLength<=256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(name+'_UNSELECTED_x1.stl')))
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-inlets-') as td:
        tmp=Path(td)
        for q in [target,*dependencies]:
            dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
        restored=A.openDocument(str(tmp/target.relative_to(ROOT)));restored.recompute()
        for name,volume in zip(('PlatformFinished','SourcePlatformDeckFinished'),nominal):
            s=restored.getObject(name).Shape;assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-volume)<max(1e-5,volume*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    base.update(status='SOURCE_INLET_PLATFORM_LOCAL_COMPLETE_UNSELECTED',closed_STLs=True,relocated_reopen=True,dimensions_mm=dimensions,
        PETG_print_orientation='Platform foot on bed; support cantilever underside; printer/nozzle/layers unset until phase2.',
        physical_tests=['PETG cantilever/bolt clamp creep and stiffness, supplier body/strap dimensions and grip pull-out before power.',
            'Exact F_PI end-face/OD/radius and both inlet mouths, before trimming the delivered factory lead.'],
        assembly=['On bare Deck fit two lower washers/nuts; bolt platform using2M3x12 and2upper washers before P_SYS/Carrier/Cover.',
            'Thread both145mmT18I loosely through native passages; body and shared inlet straps are independent.',
            'Operate P_SYS lever cages before final dressing; fit body against stops, connect W066.1/W043.2, route/grip both insulations.',
            'Tighten body and inlet straps by hand only; keep lever region free. Cut straps before later lever access/removal.',
            'FourS1 routes, whole source-module removal and stock selection remain open; do not select this module alone.'])
    receipt();print('SOURCE_PLATFORM_COMPLETE',dimensions,flush=True)

if __name__=='__main__':main()

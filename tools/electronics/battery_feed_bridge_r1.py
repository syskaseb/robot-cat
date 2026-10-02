"""Editable F0/XT60 bridge and correct reserved G1.1 return, not a whole inlet.

Preserve the rejected S0 arrangement and all selected R47 sources. Dimensions
not supplied by the exact manufacturer remain explicit prototype assumptions.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, math, tempfile, shutil
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/cad'), str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import rounded, save, sha
OUT = ROOT/'hardware/electronics/full-cat/battery-feed-bridge-r1'
CAD = ROOT/'hardware/cad/studies/battery-feed-bridge-r1'


def main():
    import FreeCAD as A
    import Part, MeshPart
    from open_deck_p0_plate import rect
    from check_main_p0_placement import SavedShapes
    import main_positive_input_r1 as C
    start = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True); CAD.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Do not overwrite a completed experiment'
    d = A.newDocument('BatteryFeedBridge')
    p = d.addObject('App::VarSet', 'BridgeParameters')
    p.addProperty('App::PropertyLength', 'FloorThickness'); p.FloorThickness = 2
    sketches = []
    def block(n, b):
        sk = d.addObject('Sketcher::SketchObject', n+'Profile')
        sk.Placement.Base.z = b[2]; rect(sk, b[0], b[1], b[3]-b[0], b[4]-b[1])
        sketches.append(sk)
        f = d.addObject('Part::Extrusion', n); f.Base = sk
        f.Dir = A.Vector(0, 0, b[5]-b[2]); f.Solid = True
        return f
    def cy(n, xyz, r, h, direction=(0,0,1)):
        f = d.addObject('Part::Cylinder', n); f.Radius = r; f.Height = h
        f.Placement = A.Placement(A.Vector(*xyz), A.Rotation(A.Vector(0,0,1), A.Vector(*direction)))
        return f
    def fusion(n, objects):
        f = d.addObject('Part::MultiFuse', n); f.Shapes = objects; f.Refine = True; return f
    def subtract(n, base, tool):
        f = d.addObject('Part::Cut', n); f.Base = base; f.Tool = tool; f.Refine = True; return f
    def box(b):
        return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))
    def cylinder(xyz,r,h,axis=(0,0,1)):
        return Part.makeCylinder(r,h,A.Vector(*xyz),A.Vector(*axis))
    floor = block('Floor', [-32,50,57,65,99,59])
    floor.setExpression('Dir.z','BridgeParameters.FloorThickness')
    additions = [floor]; tools = []
    for i,x in enumerate((-10,61)):
        additions.extend([block('Stem'+str(i),[x-4,50,57,x+4,56,101]),
                          block('DeckFoot'+str(i),[x-6,47,101,x+6,59,105])])
        tools.append(cy('MountBore'+str(i),[x,53,100.9],1.2,4.2))
    additions.append(block('XT60Shelf',[37.5,79,59,57.5,102,64.4]))
    # Actual tie lanes through the floor, not a shallow decorative groove.
    for i,x in enumerate((-12,29)):
        for j,y in enumerate((54.85,73.65)):
            tools.append(block('HolderTieSlot%d_%d'%(i,j),[x-1.6,y,56.9,x+1.6,y+1.4,59.1]))
    for j,x in enumerate((37.8,56)):
        tools.append(block('PlugTieSlot'+str(j),[x,86.4,56.9,x+1.4,89.6,64.5]))
    # Separate insulated-wire seats: source output, source return and free F0
    # switch lead. The latter is NOT a qualified S0 route or selected cut.
    seats = [('Plus',44,77.5,69,'Y'),('Return',51,77.5,69,'Y'),('FreeSwitchLead',-26,65,69,'X')]
    ties = {}; seat_names = []
    for n,x,y,z,axis in seats:
        if axis=='Y':
            additions.append(block(n+'Seat',[x-3.4,y-1.8,59,x+3.4,y+1.8,71.7]))
            tools.append(cy(n+'Groove',[x,y-1.9,z],2.45 if n=='Plus' else 1.75,3.8,(0,1,0)))
            band=[]
            for sx in (x-3.4,x+2.2):
                tools.append(block(n+'StrapSlot'+str(len(tools)),[sx-.1,y-1.35,56.9,sx+1.3,y+1.35,71.8]))
                band.append(box([sx,y-1.25,55.8,sx+1.2,y+1.25,z+3.7]))
            band.extend([box([x-3.4,y-1.25,z+2.5,x+3.4,y+1.25,z+3.7]),
                         box([x-3.4,y-1.25,55.8,x+3.4,y+1.25,57])])
        else:
            additions.append(block(n+'Seat',[x-1.8,y-3.9,59,x+1.8,y+3.9,71.7]))
            tools.append(cy(n+'Groove',[x-1.9,y,z],2.45,3.8,(1,0,0)))
            band=[]
            for sy in (y-3.9,y+2.7):
                tools.append(block(n+'StrapSlot'+str(len(tools)),[x-1.35,sy-.1,56.9,x+1.35,sy+1.3,71.8]))
                band.append(box([x-1.25,sy,55.8,x+1.25,sy+1.2,z+3.7]))
            band.extend([box([x-1.25,y-3.9,z+2.5,x+1.25,y+3.9,z+3.7]),
                         box([x-1.25,y-3.9,55.8,x+1.25,y+3.9,57])])
        band.append(box([x-2,y-2,52,x+2,y+2,56]))
        ties[n+'WireTie'] = Part.makeCompound(band); seat_names.append(n)
    raw = fusion('BridgeStock',additions)
    final = subtract('FinishedBatteryFeedBridge',raw,fusion('BoresAndTieLanes',tools))
    d.recompute()
    shape = final.Shape.copy()
    assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
    assert all(sk.FullyConstrained and sk.solve()==0 for sk in sketches)
    v = shape.Volume; p.FloorThickness=2.2; d.recompute(); probe=final.Shape.Volume
    assert abs(probe-v)>1e-4
    p.FloorThickness=2; d.recompute(); assert abs(final.Shape.Volume-v)<1e-5
    native=CAD/'BatteryFeedBridge.FCStd'; d.saveAs(str(native)); A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-feed-reopen-') as td:
        dest=Path(td)/native.name; shutil.copy2(native,dest); re=A.openDocument(str(dest)); re.recompute()
        assert re.FinishedBatteryFeedBridge.Shape.isValid()
        assert len(re.FinishedBatteryFeedBridge.Shape.Solids)==1
        assert abs(re.FinishedBatteryFeedBridge.Shape.Volume-v)<1e-5
        A.closeDocument(re.Name)
    shape.exportBrep(str(CAD/'Bridge_WORLD.brep'))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
    assert max(dims)+10<256
    b=mesh.BoundBox; mesh.translate(-b.XMin,-b.YMin,-b.ZMin); mesh.write(str(CAD/'Bridge_x1.stl'))
    owners,hashes=C.current_owners()
    def load(rel):
        pp=ROOT/rel; hashes[rel]=sha(pp); s=Part.Shape(); s.read(str(pp)); return s
    owners.pop('Deck_R41'); owners.pop('MAIN_R40')
    deck=load('hardware/cad/studies/main-positive-native-r2/Deck_WORLD.brep')
    owners['MAIN_R44']=load('hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    for folder,pattern in [('hardware/electronics/full-cat/main-positive-complete-r8','*_DESIGN.brep'),
                           ('hardware/cad/studies/main-positive-native-r2','*_WORLD.brep')]:
        for pp in (ROOT/folder).glob(pattern):
            if pp.stem not in ('Deck_WORLD','MAIN_WORLD'):
                owners['R44/'+pp.stem]=load(pp.relative_to(ROOT).as_posix())
    for n in list(owners):
        if n.startswith(('BatteryCarrier','BatteryLiner','BatteryStrap','BatteryScrew','BatteryNut')): del owners[n]
    reader=SavedShapes(); carrier=ROOT/'hardware/cad/studies/battery-p0/r4/electronics/BatteryCarrierP0.FCStd'
    for n in ('Carrier','SelectedPack','SoftLinerEnvelope'): owners['R4/'+n]=reader.shape(carrier,n)
    hashes.update(reader.hashes)
    w075=Part.Wire([Part.Arc(A.Vector(34,65,69),A.Vector(34+10/math.sqrt(2),75-10/math.sqrt(2),69),
                            A.Vector(44,75,69)).toShape(),Part.makeLine(A.Vector(44,75,69),A.Vector(44,80,69))])
    w001=rounded([A.Vector(51,80,69),A.Vector(51,26,69),A.Vector(51,26,113.5),A.Vector(51,11,113.5)],12.4)
    partial=Part.Wire([Part.makeLine(A.Vector(-31,65,69),A.Vector(-17,65,69))])
    parts={'Bridge':shape,'F0_project_body':box([-17,56.15,59,34,73.85,81]),
           'XT60_robot_body':box([39.3,80,64.4,55.7,103.9,73.6]), **ties}
    for i,x in enumerate((-12,29)):
        parts['F0BodyTie'+str(i)]=Part.makeCompound([
            box([x-1.25,54.95,55.8,x+1.25,56.15,82.2]),
            box([x-1.25,73.85,55.8,x+1.25,75.05,82.2]),
            box([x-1.25,54.95,81,x+1.25,75.05,82.2]),
            box([x-1.25,54.95,55.8,x+1.25,75.05,57]),
            box([x-2,52,52,x+2,56,56])])
    parts['XT60BodyTie']=Part.makeCompound([
        box([37.9,86.75,55.8,39.1,89.25,74.8]),box([56.1,86.75,55.8,57.3,89.25,74.8]),
        box([37.9,86.75,73.6,57.3,89.25,74.8]),box([37.9,86.75,55.8,57.3,89.25,57]),
        box([37.5,86,52,41.5,90,56])])
    lengths={}; wires={}
    for n,w,od,strip,limit in [('W075',w075,4.5,5,50),('W001',w001,3.1,19,150),('W076_FREE_STUB',partial,4.5,0,None)]:
        for a,bb in zip(w.Edges,w.Edges[1:]):
            assert (a.valueAt(a.LastParameter)-bb.valueAt(bb.FirstParameter)).Length<1e-6
            assert (a.tangentAt(a.LastParameter)-bb.tangentAt(bb.FirstParameter)).Length<1e-6
        blank=math.ceil((w.Length+strip+10)/10)*10
        lengths[n]=dict(path_mm=w.Length,blank_mm=None if n.endswith('STUB') else blank,
                       within_limit=limit is None or blank<=limit,limit_mm=limit,actual_cut_mm=None,
                       complete_route=not n.endswith('STUB'))
        for i,e in enumerate(w.Edges):
            s=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(od/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
            assert s.isValid(); wires[n+'_'+str(i)]=s
            e.exportBrep(str(OUT/(n+'_'+str(i)+'_CENTERLINE.brep')))
    # A complete through-Deck return portal and two correctly stacked fasteners.
    for n,s in wires.items():
        if n.startswith('W001') and s.BoundBox.intersect(deck.BoundBox):
            e=w001.Edges[int(n.rsplit('_',1)[1])]
            tool=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(1.95,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
            deck=deck.cut(tool)
    for i,x in enumerate((-10,61)):
        deck=deck.cut(cylinder([x,53,104.9],1.2,4.2))
        parts['M2x12_'+str(i)]=cylinder([x,53,97.3],1,12).fuse(cylinder([x,53,109.3],1.9,2))
        washers=[cylinder([x,53,z],2.5,.3).cut(cylinder([x,53,z-.1],1.1,.5)) for z in (100.7,109)]
        parts['M2Washers_'+str(i)]=Part.makeCompound(washers)
        parts['M2Nut_'+str(i)]=cylinder([x,53,99.1],2.31,1.6).cut(cylinder([x,53,99],1,1.8))
    assert deck.isValid()
    owners['Deck_candidate']=deck; deck.exportBrep(str(OUT/'Deck_UNSELECTED.brep'))
    hits=[]; errors=[]; count=0
    def check(n,s,m,t):
        nonlocal count
        if not s.BoundBox.intersect(t.BoundBox): return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox): continue
                count+=1
                try:
                    vol=a.common(b).Volume
                    if vol>1e-5: hits.append(dict(part=n,owner=m,hit_mm3=vol))
                except Exception as exc: errors.append(dict(part=n,owner=m,error=str(exc)))
    for n,s in {**parts,**wires}.items():
        s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
        for m,t in owners.items(): check(n,s,m,t)
        check(n,s,'R4_drop40',box([-87,-27,-44,129,27,28.7]))
    for n,s in wires.items():
        check(n,s,'Bridge',shape)
        for m,t in wires.items():
            if n.split('_')[0]!=m.split('_')[0] and n<m: check(n,s,m,t)
    end=datetime.now(timezone.utc)
    report=dict(status='REVIEW_HITS' if hits or errors else 'LOCAL_RIGID_CLEAR_INCOMPLETE_SOURCE',
        hits=hits,errors=errors,pairs=count,lengths=lengths,
        native=dict(fully_constrained_sketches=len(sketches),single_solid=True,strict_BOP_errors=0,
                    parameter_volumes=[v,probe,v],relocated_reopen=True,closed_STL=True,dimensions_mm=dims),
        fasteners=dict(M2x12=2,DIN125_M2=4,DIN934_M2=2,underhead_z=109.3,tip_z=97.3,
                       deck_z=[105,109],foot_z=[101,105],nut_z=[99.1,100.7],projection_mm=1.8),
        assumptions=['F0 body51x17.7x22, lead axis10 and OD4.5/R10 are prototype, not vendor dimensions.',
            'XT60 cup pitch7 and box are nominal; mating shell and battery lead reach still need a whole-source route.',
            'Six T18I source ties modeled; tie head is conservative project4x4x4, not exact supplier CAD.'],
        remaining=['G1.1 W001 end restraint/native Deck integration and hardware access.',
                   'S0 has no accepted location; W076 free stub is NOT a selected length or completed route.',
                   'Whole connector mate/hand reserve and factory battery lead reach.',
                   'F0 factory minimum lead length, OD/crimp and delivered plastic fit phase2.'],
        selected=False,W5_complete=False,physical_pass=False,source_sha256=hashes,
        script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds())
    save(OUT/'checks.json',report)
    print(json.dumps(dict(status=report['status'],hits=hits,errors=errors,lengths=lengths,native=report['native'],
                         seconds=report['worker_wall_seconds'])),flush=True)


if __name__=='__main__': main()

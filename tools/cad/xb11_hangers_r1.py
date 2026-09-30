"""Two identical bolted under-deck cable hangers and one replacement Deck.

One fixed XB11 route only; no source rewriting or old route reruns.
"""
import json, sys, shutil, tempfile
from pathlib import Path
import FreeCAD as A
import Part, Mesh, MeshPart
from fuse_aux_cradle_r1 import sketch, rect, pad, pocket, sha
from check_main_p0_placement import SavedShapes, prop
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
import xb11_upstream_route as wire
OUT=ROOT/'hardware/cad/studies/xb11-hangers-r1'
MOUNT_X=(5,15)
INHERIT=None
if '--r2' in sys.argv:
    INHERIT=OUT
    OUT=ROOT/'hardware/cad/studies/xb11-hangers-r2'
    MOUNT_X=(5,13)
DECK=ROOT/'hardware/cad/studies/deck-aux-wago-r5/DeckAuxWagoR5.FCStd'
ROUTE=ROOT/'hardware/electronics/full-cat/xb11-upstream-route-r3'

def dump(n,v): (OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def mesh(s,name):
    p=s.copy();b=p.BoundBox;p.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
    target=OUT/name
    MeshPart.meshFromShape(Shape=p,LinearDeflection=.05,AngularDeflection=.15,Relative=False).write(str(target))
    m=Mesh.Mesh(str(target));assert m.isSolid() and m.countComponents()==1
    dims=[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength]
    assert max(dims)+10<256
    return dict(stl=name,sha256=sha(target),bbox_mm=dims,closed=True,components=1)

def main():
    assert not (OUT/'geometry.json').exists(),'Preserve completed stage'
    OUT.mkdir(exist_ok=True)
    route=json.loads((ROUTE/'checks.json').read_text(encoding='utf-8'))
    assert route['geometry_nominal_clear']
    plan=dict(status='SOURCE_BEFORE_CONSTRUCTION',source_deck_sha256=sha(DECK),
        route_sha256=sha(ROUTE/'XB11_DESIGN.brep'),hangers_quantity=2,
        sites_y_mm=[50.5,-50.5],mount_holes_x_mm=list(MOUNT_X),mount_hole_diameter_mm=2.4,
        top_plate_bbox_local_mm=[2,-3,102,19,3,105],
        vertical_web_bbox_local_mm=[16,-3,74.75,19,3,105],
        bottom_rail_bbox_local_mm=[-29,-3,74.75,19,3,77.75],
        tie_slot_centers_local_xy_mm=[[-26.5,0],[-19.5,0]],tie_slot_size_xy_mm=[2,4],
        wire_center_xz_mm=[-23,79],fasteners='4 M2x10 DIN912 + 4 M2 DIN934 AF4 + 4 washers OD5/ID2.2/t0.3',
        fastener_stack_mm=8.9,fastener_nominal_protrusion_mm=1.1,
        additional_ties='2 T18I, one per hanger, from existing bag100',
        material='PETG',physical_pass=False,phase1_complete=False,
        print_orientation='hanger top plate on bed (invert world Z), web vertical; rail cantilever needs slicer supports in phase2',
        wiring='P_AUX.2 red HELU23502 1mm2 AUX6 -> XB11 cageA; unchanged factory F_HY lead to cageB. R15 full path supported at Y+/-50.5. Source and connector restraints remain R17; no moving duty.',
        assembly=['bare replacement Deck: insert four M2 nuts beneath hanger top plates; use washers beneath screw heads above Deck',
                  'bolt both hangers under Deck before WAGO, fuse holders, PCB or side covers',
                  'remove burrs and round cable-contact edges before fitting; place XB11 route onto bottom rails and tie around insulated cable through paired slots',
                  'leave source and XB11 restraints loose until full route shaped; cut after fitting with service allowance, then tighten without crushing silicone',
                  'battery disconnected: continuity/polarity/tug inspection, ensure no trapped insulation; fit upper cover last'])
    dump('plan.json',plan)
    doc=A.newDocument('XB11Hanger')
    try:
        body=doc.addObject('PartDesign::Body','Hanger')
        sk=sketch(body,'BottomRail',74.75);rect(sk,-29,-3,19,3);pad(body,'Rail3mm',sk,3,doc)
        sk=sketch(body,'VerticalWeb',77.75);rect(sk,16,-3,19,3);pad(body,'WebToDeck',sk,27.25,doc)
        sk=sketch(body,'MountPlate',102);rect(sk,2,-3,19,3);pad(body,'TopPlate3mm',sk,3,doc)
        sk=sketch(body,'BoltAxes',105)
        import Sketcher
        for x in MOUNT_X:
            i=sk.addGeometry(Part.Circle(A.Vector(x,0,0),A.Vector(0,0,1),1.2),False)
            sk.addConstraint(Sketcher.Constraint('DistanceX',i,3,x))
            sk.addConstraint(Sketcher.Constraint('DistanceY',i,3,0.0))
            sk.addConstraint(Sketcher.Constraint('Radius',i,1.2))
        pocket(body,'BoltThroughTop',sk,3,doc)
        sk=sketch(body,'CableTieSlots',77.75)
        for x in (-26.5,-19.5):rect(sk,x-1,-2,x+1,2)
        pocket(body,'TieThroughRail',sk,3,doc)
        doc.recompute();doc.saveAs(str(OUT/'XB11Hanger.FCStd'))
        hanger=body.Shape.copy();assert hanger.isValid() and len(hanger.Solids)==1 and not hanger.check(True)
        printable=hanger.copy();printable.rotate(A.Vector(),A.Vector(1,0,0),180)
        hanger_mesh=mesh(printable,'XB11_hanger_candidate_x2.stl')
        sketches=[o for o in doc.Objects if o.TypeId=='Sketcher::SketchObject']
        assert len(sketches)==5 and all(o.FullyConstrained for o in sketches)
    finally:A.closeDocument(doc.Name)
    doc=A.openDocument(str(DECK))
    try:
        body=doc.getObject('Deck');original=body.Shape.copy()
        sk=sketch(body,'XB11HangerMountAxes',4)
        for y in plan['sites_y_mm']:
            for x in MOUNT_X:
                i=sk.addGeometry(Part.Circle(A.Vector(x-21,y,0),A.Vector(0,0,1),1.2),False)
                sk.addConstraint(Sketcher.Constraint('DistanceX',i,3,x-21))
                sk.addConstraint(Sketcher.Constraint('DistanceY',i,3,y))
                sk.addConstraint(Sketcher.Constraint('Radius',i,1.2))
        pocket(body,'XB11FourBoltHoles',sk,4,doc)
        doc.recompute();doc.saveAs(str(OUT/'DeckXB11Hangers.FCStd'))
        deck=body.Shape.copy();assert deck.isValid() and len(deck.Solids)==1 and not deck.check(True)
        removed=original.cut(deck).Volume;expected=4*3.141592653589793*1.2**2*4
        assert abs(removed-expected)<1e-5,(removed,expected)
        deck_mesh=mesh(deck,'Deck_XB11_hangers_candidate_x1.stl')
    finally:A.closeDocument(doc.Name)
    placed={}
    for y in plan['sites_y_mm']:
        h=hanger.copy();h.translate(A.Vector(0,y,0));placed['hanger_'+str(y)]=h
    tube=Part.Shape();tube.read(str(ROUTE/'XB11_DESIGN.brep'))
    rows=[]
    for name,h in placed.items():
        rows.append(dict(target=name,obstacle='replacementDeck',volume_mm3=wire.volume(h.common(deck)),distance_mm=h.distToShape(deck)[0]))
        rows.append(dict(target=name,obstacle='XB11_DESIGN',volume_mm3=wire.volume(h.common(tube)),distance_mm=h.distToShape(tube)[0]))
    # Newly changed mounts only. Physical wrappers exclude aggregate duplicates.
    reader=SavedShapes();entry=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';objects=reader.doc(entry)
    targets=placed
    inherited=[]
    if INHERIT:
        old=json.loads((INHERIT/'geometry.json').read_text(encoding='utf-8'))
        previous=reader.shape(INHERIT/'XB11Hanger.FCStd','Hanger')
        # Changing a hole relocates removed volume: added material must be
        # checked against affected obstacles, not claimed as a subset.
        added=hanger.cut(previous)
        assert added.Volume<15 and added.BoundBox.ZMin>=102-1e-5
        inherited=[r for r in old['exact_pairs'] if r['obstacle'] not in ('replacementDeck','XB11_DESIGN') and not r['obstacle'].endswith('_design')]
    for link in prop(objects['RobotCatAssembly24'],'Group').findall('.//Link'):
        wrapper=link.get('value')
        if not wrapper.startswith('Rigid_'):continue
        name=prop(objects[wrapper],'Group').findall('.//Link')[0].get('value')
        if name in ('ShellMounted20','Part__Feature038'):continue
        s=reader.shape(entry,name);s.Placement=reader.placement(objects[wrapper])*s.Placement
        for target,full in targets.items():
            h=full
            if INHERIT:
                h=added.copy();h.translate(A.Vector(0,50.5 if target.endswith('50.5') and not target.endswith('-50.5') else -50.5,0))
            if not wire.overlap(s.BoundBox,h.BoundBox):continue
            for i,solid in enumerate(s.Solids):
                if not wire.overlap(solid.BoundBox,h.BoundBox):continue
                assert solid.isValid()
                rows.append(dict(target=target,obstacle=name,solid=i,volume_mm3=wire.volume(solid.common(h))))
    for name,b in {'F_HY_design':[0,-85.6,90,20,-64.4,102],
        'P_AUX_design':[.5,57,109,19.5,87,118],'F_TY_design':[0,64.4,93,20,85.6,105],
        'G_TAIL_design':[.5,-87,109,19.5,-57,118]}.items():
        for target,h in placed.items():
            rows.append(dict(target=target,obstacle=name,volume_mm3=wire.volume(wire.box(b).common(h))))
    hardware=[]
    import math
    for y in plan['sites_y_mm']:
        for x in MOUNT_X:
            vertices=[A.Vector(x+4/math.sqrt(3)*math.cos(i*math.pi/3),y+4/math.sqrt(3)*math.sin(i*math.pi/3),100.4) for i in range(6)]
            nut=Part.Face(Part.Wire(Part.makePolygon(vertices+[vertices[0]]).Edges)).extrude(A.Vector(0,0,1.6))
            nut=nut.cut(Part.makeCylinder(1,1.6,A.Vector(x,y,100.4)))
            parts={'nut_AF4':nut,'shaft_M2x10':Part.makeCylinder(1,10,A.Vector(x,y,99.3)),
                   'head_DIN912_design':Part.makeCylinder(1.9,2,A.Vector(x,y,109.3)),
                   'washer_OD5':Part.makeCylinder(2.5,.3,A.Vector(x,y,109)).cut(Part.makeCylinder(1.1,.3,A.Vector(x,y,109)))}
            for part,s in parts.items():
                for target,obstacle in {'Deck':deck,**placed}.items():
                    hardware.append(dict(x=x,y=y,part=part,obstacle=target,volume_mm3=wire.volume(s.common(obstacle))))
    hits=[r for r in rows+hardware+inherited if r['volume_mm3']>1e-5]
    result=dict(status='NEW_MOUNTS_REJECTED' if hits else 'NOMINAL_MOUNTED_XB11_CANDIDATE',
        plan_sha256=sha(OUT/'plan.json'),source_sha256=reader.hashes,
        deck_source_unchanged=sha(DECK)==plan['source_deck_sha256'],hanger_mesh=hanger_mesh,deck_mesh=deck_mesh,
        removed_deck_mm3=removed,exact_pairs=rows,hardware_pairs=hardware,inherited_unchanged_pairs=inherited,
        hits=hits,new_stls=2,new_installed_petg_parts=2,
        replacement_deck_not_additional=True,physical_pass=False,phase1_complete=False)
    dump('geometry.json',result)
    for filename,bodyname in [('XB11Hanger.FCStd','Hanger'),('DeckXB11Hangers.FCStd','Deck')]:
        with tempfile.TemporaryDirectory(prefix='xb11-hanger-reopen-') as tmp:
            p=Path(tmp)/filename;shutil.copy2(OUT/filename,p);d=A.openDocument(str(p))
            try:
                before=d.getObject(bodyname).Shape.Volume;d.recompute()
                after=d.getObject(bodyname).Shape
                assert after.isValid() and len(after.Solids)==1 and abs(after.Volume-before)<1e-5
            finally:A.closeDocument(d.Name)
    result['relocated_recompute_ok']=True
    dump('geometry.json',result)
    print(json.dumps(dict(status=result['status'],hits=hits,new_stls=2)),flush=True)

if __name__=='__main__':main()

"""Complete fixed converter wire support on the selected removable Carrier."""
import json,sys,math,shutil,tempfile
from pathlib import Path
import FreeCAD as A,Part,Mesh,MeshPart,Sketcher
from fuse_aux_cradle_r1 import sketch,rect,pad,pocket,sha
from check_main_p0_placement import SavedShapes
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
import xb11_upstream_route as R
OUT=ROOT/'hardware/cad/studies/aux-carrier-wire-ports-r1'
SRC=ROOT/'hardware/cad/studies/full-cat-board-carrier/service-access-r1/CarrierServicePorts.FCStd'
ROUTES=ROOT/'hardware/electronics/full-cat/aux-converter-routes-r5'
P=ROOT/'hardware/electronics/full-cat/aux-converter-routes-r2'
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    assert not (OUT/'geometry.json').exists()
    OUT.mkdir(exist_ok=True);assert not read(ROUTES/'checks.json')['hits']
    ports=[[-20,48],[-35,-44],[-25,66]]
    plan=dict(source_sha256=sha(SRC),frame='Carrier local XY -> world+21,0,144',
      wire_ports_world_xy_mm=ports,port_diameter_mm=5,tie_slots='Two2x4mm slots per port at world Xcenter+/-5, sameY',
      added_north_wing_world_bbox_mm=[-35,56.5,144,-15,72,148],
      purpose='Fixed XA02/XA04 through no sharp shared tool opening; XA03 north-edge wing supports insulated vertical lead.',
      material='PETG',quantity=1,print='Carrier bottom localZ0 on bed; all holes vertical. Deburr/round contact edges0.5mm manually; no slicer in phase1.',
      assembly=['Fit new bare Carrier on unchanged spacers; no new screws or PCB spacers.',
        'Fit three T18I through paired slots before populated PCBs; leave loose.',
        'Route XA02/XA03/XA04 through dedicated5mm holes, shape R15 and restrain insulated vertical legs without crushing.',
        'Three further releasable board-end ties interlinked to existing Carrier X11 pair restrain rising pad legs; no ties on bare solder or components.',
        'Solder marked pads with battery disconnected, sleeves up to joints, inspect bridges. Fit converter only after continuity/polarity inspection.',
        'Cassette and terminal-end restraints stay in place; remove board-end ties before lifting Carrier, do not pull pads. Cut after full dry-fit.'],
      new_stls=1,replacement='CarrierServicePorts_candidate_x1; do not print both',new_fasteners=0,additional_ties=6,
      cables='XA02 F_AUX->VIN red1mm2 BAT_SW, XA03 VOUT->P_AUX red1mm2 AUX6, XA04 GND->G_AUX black1mm2 return. HELU23502/23501 OD2.5 fixedR15.',
      physical_pass=False,phase1_complete=False)
    dump('plan.json',plan)
    d=A.openDocument(str(SRC))
    try:
        b=d.getObject('Carrier');old=b.Shape.copy();print('source_bbox',old.BoundBox,flush=True)
        sk=sketch(b,'NorthWireSupport',0);rect(sk,-56,56.5,-36,72);pad(b,'NorthWing4mm',sk,4,d)
        sk=sketch(b,'ThreeWirePassages',4)
        for x,y in ports:
            i=sk.addGeometry(Part.Circle(A.Vector(x-21,y,0),A.Vector(0,0,1),2.5),False)
            sk.addConstraint(Sketcher.Constraint('DistanceX',i,3,x-21))
            sk.addConstraint(Sketcher.Constraint('DistanceY',i,3,y))
            sk.addConstraint(Sketcher.Constraint('Radius',i,2.5))
        pocket(b,'WireHoles5mm',sk,4,d)
        sk=sketch(b,'WireTiePairs',4)
        for x,y in ports:
            for dx in (-5,5):rect(sk,x-21+dx-1,y-2,x-21+dx+1,y+2)
        pocket(b,'SixTieSlots',sk,4,d);d.recompute();d.saveAs(str(OUT/'CarrierAuxWirePorts.FCStd'))
        s=b.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        added=s.cut(old);removed=old.cut(s)
        perturb=d.getObject('ThreeWirePassages');c=perturb.Constraints
        # Native parameter probe: change the first radius only and restore.
        v=s.Volume;perturb.setDatum(2,A.Units.Quantity('2.6 mm'));d.recompute();vp=b.Shape.Volume
        assert abs(vp-v)>1e-5;perturb.setDatum(2,A.Units.Quantity('2.5 mm'));d.recompute();assert abs(b.Shape.Volume-v)<1e-5
        d.save();s=b.Shape.copy()
        m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
        m.transform(A.Matrix());bb=m.BoundBox;m.translate(-bb.XMin,-bb.YMin,-bb.ZMin);m.write(str(OUT/'Carrier_aux_wire_ports_candidate_x1.stl'))
        assert m.isSolid() and m.countComponents()==1
        dims=[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength];assert max(dims)+10<256
    finally:A.closeDocument(d.Name)
    world=s.copy();world.translate(A.Vector(21,0,144));add=added.copy();add.translate(A.Vector(21,0,144))
    rows=[];oldchecks=read(P/'checks.json')
    for o in oldchecks['obstacle_cache']:
        if o['owner']=='Carrier_world21_0_144':continue
        target=Part.Shape();target.read(str(P/o['file']))
        if R.overlap(add.BoundBox,target.BoundBox):rows.append(dict(target='new_wing_only',owner=o['owner'],positive_mm3=R.volume(add.common(target))))
    for n in ('XA02','XA03','XA04'):
        t=Part.Shape();t.read(str((P if n=='XA03' else ROUTES)/(n+'_DESIGN.brep')))
        rows.append(dict(target=n,owner='complete_new_Carrier',positive_mm3=R.volume(world.common(t))))
    with tempfile.TemporaryDirectory(prefix='robot-cat-aux-carrier-') as td:
        p=Path(td)/'CarrierAuxWirePorts.FCStd';shutil.copy2(OUT/'CarrierAuxWirePorts.FCStd',p);doc=A.openDocument(str(p))
        try:doc.recompute();assert doc.getObject('Carrier').Shape.isValid() and abs(doc.getObject('Carrier').Shape.Volume-s.Volume)<1e-5
        finally:A.closeDocument(doc.Name)
    hits=[r for r in rows if r['positive_mm3']>1e-5]
    dump('geometry.json',dict(status='ASSEMBLY_REJECTED' if hits else 'FIXED_CONVERTER_SUPPORT_CANDIDATE',exact_pairs=rows,hits=hits,
      source_sha256=sha(SRC),script_sha256=sha(Path(__file__)),fcstd_sha256=sha(OUT/'CarrierAuxWirePorts.FCStd'),
      added_mm3=added.Volume,removed_mm3=removed.Volume,valid=True,single_solid=True,strict_bop_errors=0,
      radius_probe_volumes=[v,vp,s.Volume],relocated_recompute_ok=True,stl_dimensions_mm=dims,stl_closed=True,stl_components=1,
      new_stls=1,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,dims=dims)),flush=True)
if __name__=='__main__':main()

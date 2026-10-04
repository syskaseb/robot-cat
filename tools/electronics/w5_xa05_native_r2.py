"""One XA05 outrigger with two unobstructed fasteners; preserve proven Deck.

R1's four hardware contacts require a joint stem/bridge/foot correction,
not new screw positions or a rerun of the unchanged large Deck model.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, sys, shutil, tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save, sha
OUT=ROOT/'hardware/electronics/full-cat/w5-xa05-native-r2'
CAD=ROOT/'hardware/cad/studies/w5-xa05-native-r2'
OLD=ROOT/'hardware/electronics/full-cat/w5-xa05-native-r1/checks.json'
RAW=ROOT/'hardware/electronics/full-cat/w5-xa05-outer-support-r5'

def main():
    import FreeCAD as A
    import Part, MeshPart
    from w5_r53_owners import installed
    start=datetime.now(timezone.utc)
    old=json.loads(OLD.read_text(encoding='utf-8'))
    assert old['status']=='XA05_NATIVE_REJECTED' and not old['errors']
    assert {h['part'] for h in old['hits']}=={'Bolt0','Washers0','Bolt1','Washers1'}
    assert all(h['owner']=='NativeOutrigger' for h in old['hits'])
    assert all(sha(ROOT/k)==v for k,v in {**old['source_sha256'],**old['files']}.items())
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    parent=A.openDocument(str(ROOT/'hardware/cad/studies/w5-xa05-native-r1/XA05JointSupports.FCStd'))
    d=A.newDocument('XA05AccessibleOutrigger');target=CAD/'XA05JointSupports.FCStd';d.saveAs(str(target))
    deck=d.addObject('App::Link','XA05DeckFinished');deck.setLink(parent.XA05DeckFinished)
    deck.LinkPlacement=parent.XA05DeckFinished.Placement
    p=d.addObject('App::VarSet','XA05Parameters');p.addProperty('App::PropertyLength','GrooveRadius');p.GrooveRadius=1.5
    primitives=[]
    def box(name,b):
        q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2]
        q.Placement.Base=A.Vector(*b[:3]);primitives.append(q);return q
    def cyl(name,point,r,h,axis=(0,0,1),groove=False):
        q=d.addObject('Part::Cylinder',name);q.Radius=r;q.Height=h
        q.Placement=A.Placement(A.Vector(*point),A.Rotation(A.Vector(0,0,1),A.Vector(*axis)))
        if groove:q.setExpression('Radius','XA05Parameters.GrooveRadius')
        primitives.append(q);return q
    def compound(name,parts):
        q=d.addObject('Part::Compound',name);q.Links=parts;return q
    raw=d.addObject('Part::MultiFuse','OutriggerRaw');raw.Refine=False
    raw.Shapes=[box('Foot',[126.5,32,109,138.5,48,112]),
        box('Stem',[135.1,35.6,111.8,137.7,42.6,119]),
        box('Bridge',[135.1,35.6,116,156.3,42.6,119.8]),
        box('Rail',[149.7,-17.5,116,156.3,42.6,119.5]),
        box('Seat',[149.7,-17.3,119.3,156.3,-10.7,121.7])]
    tools=[cyl('FootHole'+str(i),[131,y,108.9],1.7,3.2) for i,y in enumerate((44,36))]
    tools += [cyl('InsulationGroove',[153,-17.4,121],1.5,6.8,(0,1,0),True),
        box('UnderTieTunnel',[147.9,-15.6,115.9,158.1,-12.4,117.7]),
        box('RisePassage',[151.4,-6,112,154.6,7,125.3])]
    tools += [box('TieSlot'+str(i),[x-.8,-15.6,115.9,x+.8,-12.4,123.6]) for i,x in enumerate((148.9,157.1))]
    bracket=d.addObject('Part::Cut','OutriggerFinished');bracket.Base=raw;bracket.Tool=compound('Passages',tools);bracket.Refine=False
    d.recompute();d.save();print('XA05_R2_NATIVE_SAVED',flush=True)
    assert all(q.Shape.isValid() and not q.Shape.check(True) for q in primitives)
    assert deck.Shape.isValid() and len(deck.Shape.Solids)==1
    assert bracket.Shape.isValid() and len(bracket.Shape.Solids)==1
    v=bracket.Shape.Volume;p.GrooveRadius=1.6;d.recompute();probe=bracket.Shape.Volume;assert probe<v
    p.GrooveRadius=1.5;d.recompute();assert abs(bracket.Shape.Volume-v)<1e-5;d.save()
    shapes={'NativeDeck':deck.Shape.copy(),'NativeOutrigger':bracket.Shape.copy()}
    for label,s in shapes.items():s.exportBrep(str(CAD/(label.removeprefix('Native')+'_WORLD.brep')))
    owners,pins,omitted=installed(A,Part)
    owners.pop('CandidateDeck');owners.pop('hardware/electronics/full-cat/xa05-main-aux-return-r2/XA05_DESIGN.brep')
    children=Part.read(str(RAW/'ADDITIONS_WORLD.brep')).childShapes();assert len(children)==10
    changed={'XA05':Part.read(str(RAW/'XA05_WORLD.brep'))}
    changed.update(dict(zip(('InnerTie','OuterTie','Bolt0','Washers0','Nut0','Bolt1','Washers1','Nut1'),children[2:])))
    hits=[];errors=[];pairs=0
    def check(label,s,others):
        nonlocal pairs
        for key,t in others.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                c=s.common(t)
                if c.Volume>1e-5:
                    b=c.BoundBox;hits.append(dict(part=label,owner=key,mm3=c.Volume,bounds_mm=[getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
            except Exception as exc:errors.append(dict(part=label,owner=key,error=str(exc)))
    # Deck/wire/straps versus unchanged owners inherited from R5 and R1;
    # the enlarged/shifted bracket is checked against the actual census.
    check('NativeOutrigger',shapes['NativeOutrigger'],{**owners,'NativeDeck':shapes['NativeDeck'],**changed})
    for label,s in changed.items():check(label,s,{'NativeDeck':shapes['NativeDeck']})
    phases={k:s for k,s in owners.items() if k not in ('Cover','hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep')}
    phases.update(shapes);phases.update(changed)
    # Explicit cylindrical driver allowance, not a measured tool or hinge.
    driver_files=[]
    for i,y in enumerate((44,36)):
        driver=Part.makeCylinder(3.5,35,A.Vector(131,y,115.5))
        check('Bolt'+str(i)+'_driver_allowance',driver,{k:s for k,s in phases.items() if k!='Bolt'+str(i)})
        q=OUT/('Bolt'+str(i)+'_DRIVER_ALLOWANCE.brep');driver.exportBrep(str(q));driver_files.append(q)
    dependencies=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    assert all(q.is_relative_to(ROOT) for q in dependencies)
    pins += [Path(__file__),OLD,RAW/'checks.json',*dependencies]
    base=dict(status='XA05_NATIVE_REJECTED' if hits or errors else 'XA05_NATIVE_EXPORT_PENDING',hits=hits,errors=errors,changed_pairs=pairs,
        reused_receipt=OLD.relative_to(ROOT).as_posix(),reused_scope='Unchanged native Deck parameter roundtrip/equivalence and unchanged R5 route versus owners; NOT inherited bracket qualification.',
        parameter_radius_mm=[1.5,1.6,1.5],parameter_volumes=[v,probe,bracket.Shape.Volume],
        strict_local_primitive_BOP_errors=0,full_final_strict_BOP_verified=False,
        slot_bounds_mm=[151.4,-6,112,154.6,7,125.3],minimum_continuous_rail_cheek_mm=1.7,
        foot_bounds_mm=[126.5,32,109,138.5,48,112],stem_x_mm=[135.1,137.7],
        washer_to_stem_clearance_mm=.6,washer_nominal_full_bearing=True,
        driver_allowance=dict(radius_mm=3.5,start_z_mm=115.5,top_z_mm=150.5,assembly_phase='Cover/upperCarrier not installed',actual_tool_verified=False),
        native_supports_constructed=True,single_solids=[1,1],new_ties=2,tie_SKU='111-02370 T18I-PA66-BK',
        new_M3x12=2,new_M3_nuts=2,new_M3_washers=4,new_separate_prints=1,one_replacement_Deck=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},started_utc=start.isoformat())
    def receipt():
        finish=datetime.now(timezone.utc);base.update(finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
            files={q.relative_to(ROOT).as_posix():sha(q) for q in [*CAD.glob('*.FCStd'),*CAD.glob('*.brep'),*CAD.glob('*.stl'),*driver_files]})
        save(OUT/'checks.json',base)
    print('XA05_R2_CONTACTS',pairs,len(hits),len(errors),flush=True)
    if hits or errors:receipt();return
    dims={}
    for label,s in shapes.items():
        name=label.removeprefix('Native');mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        b=mesh.BoundBox;dims[name]=[b.XLength,b.YLength,b.ZLength]
        assert b.XLength+6<=256 and b.YLength+6<=256 and b.ZLength<=256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(name+'_UNSELECTED_x1.stl')))
    nominal=[deck.Shape.Volume,bracket.Shape.Volume]
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-xa05-r2-') as td:
        tmp=Path(td)
        for q in [target,*dependencies]:
            dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
        restored=A.openDocument(str(tmp/target.relative_to(ROOT)))
        # Cached unchanged parent is deliberately not rebuilt. Recompute only
        # the new local document, checking resolved relocated dependencies.
        restored.recompute()
        for name,v in zip(('XA05DeckFinished','OutriggerFinished'),nominal):
            q=restored.getObject(name);assert q.Shape.isValid() and len(q.Shape.Solids)==1 and abs(q.Shape.Volume-v)<max(1e-5,v*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    base.update(status='XA05_NATIVE_STATIC_COMPLETE_UNSELECTED',closed_STLs=True,relocated_reopen=True,dimensions_mm=dims)
    receipt();print('XA05_R2_COMPLETE',dims,flush=True)

if __name__=='__main__':main()

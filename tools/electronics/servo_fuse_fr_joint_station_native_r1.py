"""Native two-sided W042 insulation seats and open-bottom cover relief.

Retain the R10 factory/lap datums, which meet the100mm PROJECT assumption
with the original10mm reserve. Add two integral seats to the actual R6 bank
panel; prove their entire24mm2 foot, route/grip/strap/shared static fit and
editable single-solid exports. R11 source routing's XA02 conflict remains
OPEN; a native joint station does not select the bank or close W5.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-joint-station-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-fr-joint-station-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve completed result'
    pins={};V=A.Vector
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]))
    def nativebox(d,n,b):
        o=d.addObject('Part::Box',n);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);return o
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r11'
    q=folder/'checks.json';pin(q);route=json.loads(q.read_text(encoding='utf-8'))
    assert not route['errors'] and not route['factory_failures']
    j=next(r for r in route['joints'] if r['id']=='W042');y=j['centre_mm'][1];z=j['centre_mm'][2]
    assert abs(y+92)<1e-6 and abs(z-160.64101615137753)<1e-6
    assert j['intact_insulation_overlap_each_mm']==9
    owners=retained_owners(pin,load,Part)
    owners['CandidateDeck']=load(ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/Deck_WORLD.brep')
    owners.pop('Bank/RightClipAccessFinished_WORLD')
    oldcover=load(ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/Cover_WORLD.brep')
    owners.pop('RetainedCover')
    for f in (ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r7').glob('*Tie*_DESIGN.brep'):owners['BodyStrap/'+f.stem]=load(f)
    for f in (ROOT/'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r3').glob('*_MTA_BODY.brep'):owners[f.stem]=load(f)
    feeds={f.stem.replace('_DESIGN',''):load(f) for f in folder.glob('*_DESIGN.brep')}
    owners.update(feeds)
    bankpath=ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r6/BankRightFeedReliefs.FCStd';pin(bankpath)
    coverpath=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/CoverCantileverClearance.FCStd';pin(coverpath)
    d=A.openDocument(str(bankpath));bankname=d.Name;changed={};ties={};seats=[]
    try:
        parent=d.getObject('FeedReliefsRaw');base=parent.Shape.copy()
        assert abs(base.Volume-load(ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r6/BankRight_WORLD.brep').Volume)<1e-5
        p=d.addObject('App::VarSet','FRGripParameters');p.addProperty('App::PropertyLength','GrooveRadius');p.GrooveRadius=3
        stocks=[parent];tools=[]
        for tag,x in (('Factory',-48),('Extension',-81.5)):
            # Four by six foot fully overlaps the real1.8mm bank panel. Its
            # 2mm inner cantilever carries the insulation groove, not a fake
            # full foot extending outside the material.
            foot=box([x-2,-97,146.4,x+2,-91,146.5]);bearing=base.common(foot).Volume/.1
            assert abs(bearing-24)<1e-5,(tag,bearing)
            stock=nativebox(d,'FR'+tag+'Seat',[x-2,-97,144.4,x+2,-89,z]);stocks.append(stock)
            groove=d.addObject('Part::Cylinder','FR'+tag+'WireGroove');groove.Height=6
            groove.setExpression('Radius','FRGripParameters.GrooveRadius')
            groove.Placement=A.Placement(V(x-3,y,z),A.Rotation(V(0,0,1),V(1,0,0)));tools.append(groove)
            slot=nativebox(d,'FR'+tag+'TiePass',[x-1.4,-98,154,x+1.4,-88,155.8]);tools.append(slot)
            #2.5mm tie width inX,1.2mm thickness, underpass1.8x2.8mm.
            bands=[[x-1.25,-98.2,154.3,x+1.25,-87.8,155.5],
                   [x-1.25,-98.2,154.3,x+1.25,-97,z+4.2],
                   [x-1.25,-89,154.3,x+1.25,-87.8,z+4.2],
                   [x-1.25,-98.2,z+3,x+1.25,-87.8,z+4.2]]
            head=[x-2.25,-87.8,z-.5,x+2.25,-83,z+3]
            for i,b in enumerate(bands):ties[f'FR{tag}_TieBand{i}']=box(b)
            ties[f'FR{tag}_TieHead']=box(head)
            seats.append(dict(side=tag,x_mm=x,y_mm=y,z_mm=z,foot_area_mm2=24,bearing_area_mm2=bearing,
                              straight_insulation_grip_mm=4,tie='T18I111-02370',wire_OD_mm=5 if tag=='Factory' else 4.2,
                              foot_overlap_z_mm=[146.4,146.5],slot_mm=[2.8,10,1.8],head_bounds_mm=head))
        union=d.addObject('Part::MultiFuse','FRGripStock');union.Shapes=stocks;union.Refine=False
        holes=d.addObject('Part::MultiFuse','FRGripTools');holes.Shapes=tools;holes.Refine=False
        final=d.addObject('Part::Cut','FRJointStationFinished');final.Base=union;final.Tool=holes;final.Refine=False
        print('FR_BANK_RECOMPUTE',flush=True);d.recompute();s=final.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        # Only newly added material is checked against retained owners; base
        # geometry itself is identical, its previous qualification is retained.
        changed['AddedBankSeats']=s.cut(base);assert changed['AddedBankSeats'].Volume>0
        v=s.Volume;p.GrooveRadius=3.1;d.recompute();probe=final.Shape.Volume;assert probe<v
        p.GrooveRadius=3;d.recompute();assert abs(final.Shape.Volume-v)<1e-5
        for o in d.Objects:
            if hasattr(o,'Visibility'):o.Visibility=False
        final.Visibility=True;bankdest=CAD/'BankRightFRJointStation.FCStd';d.saveAs(str(bankdest));bankshape=s
    finally:A.closeDocument(bankname)
    for n,s in ties.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    changed.update(ties)
    hits=[];errors=[];pairs=0
    for n,s in changed.items():
        s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
        for m,t in owners.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                h=s.common(t)
                if h.Volume>1e-5:hits.append(dict(part=n,owner=m,volume_mm3=h.Volume))
            except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,t in ties.items():
        h=t.common(bankshape)
        if h.Volume>1e-5:hits.append(dict(part=n,owner='NativeBank',volume_mm3=h.Volume))
    # All intentional strap-corner overlaps are within the SAME physical tie,
    # not a collision between different purchased items.
    assert not errors
    if hits:
        save(OUT/'fault.json',dict(hits=hits,errors=errors,selected=False,physical_pass=False,seats=seats,source_sha256=pins))
    assert not hits,hits
    d=A.openDocument(str(coverpath));covername=d.Name;openings=[]
    try:
        parent=d.getObject('CantileverCoverFinished');base=parent.Shape.copy();assert abs(base.Volume-oldcover.Volume)<1e-5
        p=d.addObject('App::VarSet','FRPassageParameters');p.addProperty('App::PropertyLength','Allowance');p.Allowance=1
        cutters=[];cover_parts=dict(changed,W042_factory=feeds['W042_factory'],W042_Sleeve=feeds['W042_Sleeve'])
        for i,(n,t) in enumerate(cover_parts.items()):
            h=base.common(t)
            if h.Volume<1e-5:continue
            b=bounds(h);bottom=base.BoundBox.ZMin-1
            o=d.addObject('Part::Box','FRPassage'+str(i))
            for prop,expr in [('Length',f'{b[3]-b[0]} mm + 2*FRPassageParameters.Allowance'),
                              ('Width',f'{b[4]-b[1]} mm + 2*FRPassageParameters.Allowance'),
                              ('Height',f'{b[5]-bottom} mm + FRPassageParameters.Allowance'),
                              ('Placement.Base.x',f'{b[0]} mm - FRPassageParameters.Allowance'),
                              ('Placement.Base.y',f'{b[1]} mm - FRPassageParameters.Allowance')]:o.setExpression(prop,expr)
            o.Placement.Base.z=bottom;cutters.append(o);openings.append(dict(part=n,contact_volume_mm3=h.Volume,bounds_mm=b))
        assert cutters
        if len(cutters)==1:tool=cutters[0]
        else:tool=d.addObject('Part::MultiFuse','FRPassageTools');tool.Shapes=cutters;tool.Refine=False
        final=d.addObject('Part::Cut','FRJointCoverFinished');final.Base=parent;final.Tool=tool;final.Refine=False
        print('FR_COVER_RECOMPUTE',len(cutters),flush=True);d.recompute();s=final.Shape.copy();vcover=s.Volume
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        for n,t in cover_parts.items():assert s.common(t).Volume<1e-5,n
        p.Allowance=1.2;d.recompute();coverprobe=final.Shape.Volume;assert coverprobe<vcover
        p.Allowance=1;d.recompute();assert abs(final.Shape.Volume-vcover)<1e-5
        for o in d.Objects:
            if hasattr(o,'Visibility'):o.Visibility=False
        final.Visibility=True;coverdest=CAD/'CoverFRJointStation.FCStd';d.saveAs(str(coverdest));covershape=s
    finally:A.closeDocument(covername)
    exports=[]
    for tag,dest,finalname,s,vol in [('BankRight',bankdest,'FRJointStationFinished',bankshape,v),('Cover',coverdest,'FRJointCoverFinished',covershape,vcover)]:
        s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        if tag=='BankRight':mesh.rotate(math.pi,0,0)
        b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];assert b.XLength+10<256 and b.YLength+10<256 and b.ZLength<256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
        with tempfile.TemporaryDirectory(prefix='robot-cat-fr-station-') as td:
            moved=Path(td)/dest.name;shutil.copy2(dest,moved);re=A.openDocument(str(moved))
            try:re.recompute();assert abs(re.getObject(finalname).Shape.Volume-vol)<1e-5
            finally:A.closeDocument(re.Name)
        exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=finalname,single_solid=True,
                            strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,dimensions_mm=dims))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_FR_STATION_STATIC_FIT_SOURCE_SERVICE_OPEN',selected=False,physical_pass=False,W5_complete=False,
        seats=seats,additional_T18I_ties=2,additional_prints=0,exports=exports,openings=openings,
        parameter_volumes_mm3=dict(bank=[v,probe,v],cover=[vcover,coverprobe,vcover]),pairs=pairs,hits=hits,errors=errors,
        recipe=['Bare unpowered bank before other modules: pre-thread both145mm T18I ties through1.8x2.8mm underpasses; heads face inward.',
                'Slide26mm sleeve before soldering8mm opposing lap; shrink9mm intact insulation each side. No solder/tinning at WAGO.',
                'Seat straight insulation on both4mm grip lengths outside sleeve ends, cinch ties; inspect actual groove/gap and pull retention.',
                'Keep these factory/source datums with bank; cover is removed with bank, not lifted independently over routed leads.'],
        open=['FR source routing not accepted; R11 intersects XA02. Exterior west-loop protection and full casing shared fit remain OPEN.',
              'Tie insertion tool/finger access, actual2mm seat cantilever/PETG stiffness/pull retention and shared removal remain OPEN.',
              'Other feeds/WAGO grips/stock/E3/one selected export are not closed by this station.'],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(native_exports=len(exports),pairs=pairs,hits=len(hits),additional_ties=2)),flush=True)
if __name__=='__main__':main()

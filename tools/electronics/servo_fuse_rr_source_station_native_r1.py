"""One complete RR source station: native Deck grips, four ends and casing.

Use the full R6 RR route, retain front and the four MTA mounts. Added PETG
is checked against exact retained owners/current other feeds. RL remains
rejected, not selected or credited. Two T18I ties are additional roles.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-station-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rr-source-station-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve completed proof'
    pins={};V=A.Vector
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]))
    def nativebox(d,n,b):
        o=d.addObject('Part::Box',n);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);return o
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-complete-r8'
    p=folder/'checks.json';pin(p);r=json.loads(p.read_text(encoding='utf-8'))
    rr_hits=[h for h in r['hits'] if h['part'].startswith('W052') or h['owner'].startswith('W052')]
    assert not r['errors'] and not r['factory_failures']
    assert all(h['owner']=='RetainedCover' for h in rr_hits),rr_hits
    j=next(x for x in r['joints'] if x['id']=='W052');cx=j['centre_mm'][0];z=j['centre_mm'][2]
    assert j['intact_insulation_overlap_each_mm']==9 and j['grip_length_mm']==4
    owners=retained_owners(pin,load,Part)
    olddeck=load(ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/Deck_WORLD.brep')
    owners.pop('CandidateDeck',None);owners.pop('RetainedCover')
    owners['Bank/RightClipAccessFinished_WORLD']=load(ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r3/BankRight_WORLD.brep')
    owners['FRReturnGuard']=load(ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r3/Guard_WORLD.brep')
    for foldername,pattern,prefix in [
        ('servo-fuse-main-joint-layout-r3','*_MTA_BODY.brep','MTA'),
        ('servo-fuse-rolled-cradles-native-r7','*Tie*_DESIGN.brep','BodyTie'),
        ('servo-fuse-fr-joint-station-native-r1','*Tie*_DESIGN.brep','FRTie'),
        ('servo-fuse-fr-return-guard-native-r3','*_DESIGN.brep','FRHardware')]:
        for p in (ROOT/'hardware/electronics/full-cat'/foldername).glob(pattern):owners[prefix+'/'+p.stem]=load(p)
    source=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2'
    for p in source.glob('*_DESIGN.brep'):
        if not p.stem.startswith(('W044','W052')):owners['OtherFeed/'+p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r3').glob('W044*_DESIGN.brep'):
        owners['RL_R3_CANDIDATE/'+p.stem]=load(p)
    feeds={p.stem.replace('_DESIGN',''):load(p) for p in folder.glob('*_DESIGN.brep')}
    owners.update(feeds)
    deckpath=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/DeckRolledCradles.FCStd';pin(deckpath)
    coverpath=ROOT/'hardware/cad/studies/servo-fuse-fr-joint-station-native-r1/CoverFRJointStation.FCStd';pin(coverpath)
    ties={};seats=[];d=A.openDocument(str(deckpath));deckdest=CAD/'DeckRRSourceStation.FCStd'
    try:
        parent=d.getObject('RolledCantileversFinished');assert abs(parent.Shape.Volume-olddeck.Volume)<1e-5
        par=d.addObject('App::VarSet','RRSourceGripParameters');par.addProperty('App::PropertyLength','GrooveAllowance');par.GrooveAllowance=.2
        foot=[cx+.5,-59.5,108.8,cx+4.5,-55.5,109]
        area=olddeck.common(box(foot)).Volume/.2;assert abs(area-16)<1e-5,dict(foot=foot,bearing_mm2=area)
        stocks=[parent,nativebox(d,'RRSourceFoot',[cx+.5,-59.5,108.8,cx+4.5,-55.5,z])]
        stocks.append(nativebox(d,'RRSourceCantilever',[cx-.7,-67,z-8,cx+4.5,-31,z]))
        tools=[]
        for role,key,od in [('Factory','factory_grip_centre_mm',5),('Extension','extension_grip_centre_mm',4.2)]:
            x,y,zz=j[key];assert abs(x-cx)<1e-6 and abs(zz-z)<1e-6
            groove=d.addObject('Part::Cylinder','RR'+role+'InsulationGroove');groove.Height=6
            groove.setExpression('Radius',f'{od/2} mm + RRSourceGripParameters.GrooveAllowance')
            groove.Placement=A.Placement(V(x,y-3,z),A.Rotation(V(0,0,1),V(0,1,0)));tools.append(groove)
            # Band inserted through a real1.8x2.8 underpass. Head is on the
            # east side, away from XA06/MAIN; four mm of straight insulation.
            tools.append(nativebox(d,'RR'+role+'TiePass',[cx-2,y-1.4,z-6.3,cx+6,y+1.4,z-4.5]))
            xa=cx-1.9;xb=cx+5.7
            bands=[[xa,y-1.25,z-6,xb,y+1.25,z-4.8],
                   [xa,y-1.25,z-6,cx-.7,y+1.25,z+4.2],
                   [cx+4.5,y-1.25,z-6,xb,y+1.25,z+4.2],
                   [xa,y-1.25,z+3,xb,y+1.25,z+4.2]]
            head=[xb,y-2.25,z-.5,xb+4.8,y+2.25,z+3]
            for k,b in enumerate(bands):ties[f'RR{role}_TieBand{k}']=box(b)
            ties[f'RR{role}_TieHead']=box(head)
            seats.append(dict(role=role,grip_centre_mm=[x,y,z],grip_mm=4,groove_allowance_mm=.2,
                foot_shared_bearing_mm2=area,T18I='111-02370',head_bounds_mm=head,
                open_side='Asymmetric open groove, insulation retained by separate T18I; prototype pull/creep qualification in phase2.'))
        union=d.addObject('Part::MultiFuse','RRSourceGripStock');union.Shapes=stocks;union.Refine=False
        tool=d.addObject('Part::MultiFuse','RRSourceGripTools');tool.Shapes=tools;tool.Refine=False
        final=d.addObject('Part::Cut','RRSourceStationFinished');final.Base=union;final.Tool=tool;final.Refine=False
        print('RR_NATIVE_DECK_RECOMPUTE',flush=True);d.recompute();deck=final.Shape.copy()
        assert deck.isValid() and len(deck.Solids)==1 and not deck.check(True)
        added=deck.cut(olddeck);assert added.Volume>0
        vol=deck.Volume;par.GrooveAllowance=.3;d.recompute();probe=final.Shape.Volume;assert probe<vol
        par.GrooveAllowance=.2;d.recompute();assert abs(final.Shape.Volume-vol)<1e-5
        for o in d.Objects:
            if hasattr(o,'Visibility'):o.Visibility=False
        final.Visibility=True;d.saveAs(str(deckdest))
    finally:A.closeDocument(d.Name)
    changed={'AddedRRSourceGrips':added,**ties}
    for n,s in changed.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            h=s.common(t)
            if h.Volume>1e-5:hits.append(dict(part=n,owner=m,volume_mm3=h.Volume,bounds_mm=bounds(h)))
        except Exception as exc:errors.append(dict(part=n,owner=m,error=str(exc)))
    for n,s in changed.items():
        for m,t in owners.items():check(n,s,m,t)
    for n,s in ties.items():check(n,s,'NativeDeck',deck)
    save(OUT/'grips-fit.json',dict(pairs=pairs,hits=hits,errors=errors,seats=seats,selected=False,physical_pass=False,source_sha256=pins))
    assert not hits and not errors,hits
    d=A.openDocument(str(coverpath));coverdest=CAD/'CoverRRSourceStation.FCStd';openings=[]
    try:
        parent=d.getObject('FRJointCoverFinished');base=parent.Shape.copy()
        par=d.addObject('App::VarSet','RRSourcePassageParameters');par.addProperty('App::PropertyLength','Allowance');par.Allowance=1
        cutters=[];cover_parts={**changed,**{n:s for n,s in feeds.items() if n.startswith('W052')}}
        for i,(n,s) in enumerate(cover_parts.items()):
            h=base.common(s)
            if h.Volume<1e-5:continue
            b=bounds(h);low=base.BoundBox.ZMin-1
            o=d.addObject('Part::Box','RRSourcePassage'+str(i))
            for prop,expr in [('Length',f'{b[3]-b[0]} mm + 2*RRSourcePassageParameters.Allowance'),
                ('Width',f'{b[4]-b[1]} mm + 2*RRSourcePassageParameters.Allowance'),
                ('Height',f'{b[5]-low} mm + RRSourcePassageParameters.Allowance'),
                ('Placement.Base.x',f'{b[0]} mm - RRSourcePassageParameters.Allowance'),
                ('Placement.Base.y',f'{b[1]} mm - RRSourcePassageParameters.Allowance')]:o.setExpression(prop,expr)
            o.Placement.Base.z=low;cutters.append(o);openings.append(dict(part=n,bounds_mm=b,removed_contact_mm3=h.Volume))
        assert cutters
        if len(cutters)==1:tool=cutters[0]
        else:tool=d.addObject('Part::MultiFuse','RRSourcePassageTools');tool.Shapes=cutters;tool.Refine=False
        final=d.addObject('Part::Cut','RRSourceCoverFinished');final.Base=parent;final.Tool=tool;final.Refine=False
        print('RR_NATIVE_COVER_RECOMPUTE',len(cutters),flush=True);d.recompute();cover=final.Shape.copy();cv=cover.Volume
        assert cover.isValid() and len(cover.Solids)==1 and not cover.check(True)
        for n,s in cover_parts.items():check(n,s,'NewCover',cover)
        assert not hits and not errors,hits
        par.Allowance=1.2;d.recompute();cprobe=final.Shape.Volume;assert cprobe<cv
        par.Allowance=1;d.recompute();assert abs(final.Shape.Volume-cv)<1e-5
        for o in d.Objects:
            if hasattr(o,'Visibility'):o.Visibility=False
        final.Visibility=True;d.saveAs(str(coverdest))
    finally:A.closeDocument(d.Name)
    exports=[]
    for tag,dest,name,s,volume in [('Deck',deckdest,'RRSourceStationFinished',deck,vol),('Cover',coverdest,'RRSourceCoverFinished',cover,cv)]:
        s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1;b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
        assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
        with tempfile.TemporaryDirectory(prefix='robot-cat-rr-source-') as td:
            moved=Path(td)/dest.name;shutil.copy2(dest,moved);re=A.openDocument(str(moved))
            try:re.recompute();assert abs(re.getObject(name).Shape.Volume-volume)<1e-5
            finally:A.closeDocument(re.Name)
        exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=name,single_solid=True,strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,dimensions_mm=dims))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='RR_SOURCE_NATIVE_STATION_STATIC_CLEAR',selected=False,physical_pass=False,W5_complete=False,
        pairs=pairs,hits=hits,errors=errors,seats=seats,exports=exports,additional_T18I=2,additional_prints=0,
        replaced_old_cover_contacts=rr_hits,openings=openings,parameter_volumes_mm3=dict(deck=[vol,probe,vol],cover=[cv,cprobe,cv]),
        recipe=['Removed unpowered Deck: pre-thread both145mm T18I bands; east-facing heads,1.8x2.8mm underpasses.',
            'Slide26mm RNF100 sleeve before8mm opposing lap, inspect solder, shrink9mm intact overlap each end. Never tin WAGO ends.',
            'Lay straight insulation in both4mm native grooves, tighten bands; preserve full source/factory route and radius.',
            'Use updated Cover with Deck/Bank assembly; no independent cover removal is qualified.'],
        open=['RL source remains rejected, unrelated output/WAGO grips/RR body clips/whole assembly-removal and final selection/stock/E3 open.',
            'Tie insertion/tool access, cantilever/pull/PETG creep and actualMTA lead lengths remain prototype trials, not physical PASS.'],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(exports=len(exports),pairs=pairs,hits=len(hits),additional_ties=2)),flush=True)
if __name__=='__main__':main()

"""One coherent support correction: outer-strip cantilevers, transverse straps.

Keep all four holder bodies and R4 feeds, replace rejected full-height inner
feet/longitudinal straps. Only changed supports/straps are rechecked. Nominal
PETG bridge, creep and actual ties still need phase2 trials; no selection.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, tempfile, shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
from servo_fuse_rolled_cradles_native_r1 import retained_owners
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r2'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r2'


def main():
    import FreeCAD as A
    import Part, MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve completed result'
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    body_report=ROOT/'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r3/checks.json';pin(body_report)
    holders=json.loads(body_report.read_text(encoding='utf-8'))['holders']
    source=ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/DeckParentFeedGrips.FCStd';pin(source)
    base=load(source.with_name('Deck_WORLD.brep'))
    tie_stock=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json';pin(tie_stock)
    tie=next(r for r in json.loads(tie_stock.read_text(encoding='utf-8'))['lines'] if r['id']=='tie:111-02370')
    assert tie['dimensions_mm']==dict(length=145,width=2.5,thickness=1.2,head_length=4.8,head_width=4.5,height_H=3.5)
    owners=retained_owners(pin,load,Part)
    owners['RetainedCover']=load(ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r6/Cover_WORLD.brep')
    owners['Bank/RightClipAccessFinished_WORLD']=load(ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r6/BankRight_WORLD.brep')
    feed=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r4';pin(feed/'checks.json')
    for q in feed.glob('*_DESIGN.brep'):owners['R4Feed/'+q.stem]=load(q)
    for h in holders:owners[h['leg']+'_MTA_BODY']=load(body_report.parent/(h['leg']+'_MTA_BODY.brep'))
    parts={};integral=[];rows=[];straps=[];mount=[]
    strap_y=dict(FL=(69,73),FR=(-66,-79),RL=(66,79),RR=(-82,-77))
    for h in holders:
        leg=h['leg'];b=h['bounds_mm'];thick=1.5 if leg=='RR' else 2
        fy0,fy1=(-95,-92) if leg=='RR' else ((91,95) if leg.endswith('L') else (-95,-91))
        roof=[b[0]+2,min(b[1],fy0),b[2]-thick,b[3]-2,max(b[4],fy1),b[2]]
        integral.append((leg+'Roof',roof,True,thick));parts[leg+'_Roof']=box(roof)
        for j,x in enumerate((b[0]+4,b[3]-8)):
            foot=[x,fy0,108.8,x+4,fy1,b[2]-thick]
            integral.append((leg+'Foot'+str(j),foot,False,thick));parts[leg+'_Foot_'+str(j)]=box(foot)
            # Check the load-bearing bottom slice, not the whole foot volume.
            slice_b=foot.copy();slice_b[5]=109
            support=box(slice_b).common(base).Volume;expected=4*(fy1-fy0)*.2
            mount.append(dict(leg=leg,foot=j,bottom_slice_mm=[108.8,109],expected_mm3=expected,actual_mm3=support,full_bearing=abs(expected-support)<1e-4))
        # Two low stop lips resist Y sliding; straps hold X/Z on this prototype.
        for j,y in enumerate((b[1]-1.5,b[4]+.5)):
            lip=[roof[0],y,b[2]-.2,roof[3],y+1,b[2]+2]
            integral.append((leg+'Stop'+str(j),lip,None,thick));parts[leg+'_Stop_'+str(j)]=box(lip)
        z0=b[2]-thick-1.2;z1=b[5]+1.2
        for j,y in enumerate(strap_y[leg]):
            bands=[(b[0]-1.2,y-1.25,z0,b[0],y+1.25,z1),
                   (b[3],y-1.25,z0,b[3]+1.2,y+1.25,z1),
                   (b[0],y-1.25,z0,b[3],y+1.25,b[2]-thick),
                   (b[0],y-1.25,b[5],b[3],y+1.25,z1)]
            for k,q in enumerate(bands):parts[f'{leg}_Tie_{j}_Band_{k}']=box(q)
            head=[b[3]-4.8,y-2.25,z1,b[3],y+2.25,z1+3.5]
            parts[f'{leg}_Tie_{j}_Head']=box(head)
            length=2*((b[3]-b[0])+1.2+(z1-z0)-1.2)
            assert length+15<=145
            straps.append(dict(leg=leg,index=j,axis='X',y_mm=y,sku='111-02370',centreline_mm=length,reserve_mm=15,head_bounds_mm=head))
        rows.append(dict(leg=leg,roof_bounds_mm=roof,roof_thickness_mm=thick,foot_y_mm=[fy0,fy1],body=h,
            phase2='Two outer-strip feet support a PETG cantilever. Body seated on roof, two transverse T18I ties and0.5mm stop-lip nominal clearance. Thin RR1.5mm roof/bridge/creep/tie insertion require actual prototype trials, no strength claim.'))
    save(OUT/'intent.json',dict(selected=False,holders=rows,straps=straps,mounts=mount,
        inherited_open='Unchanged R4 feed collisions remain failures, not cleared by support change.'))
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            h=s.common(t)
            if h.Volume>1e-5:
                hits.append(dict(part=n,owner=m,volume_mm3=h.Volume,bounds_mm=bounds(h)))
                h.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as e:errors.append(dict(part=n,owner=m,error=str(e)))
    for n,s in parts.items():
        s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
        for m,t in owners.items():check(n,s,m,t)
        print('CANTILEVER_FIT',n,len(hits),len(errors),flush=True)
    for i,(n,s) in enumerate(list(parts.items())):
        for m,t in list(parts.items())[i+1:]:
            if n[:2]==m[:2] and '_Tie_' not in n and '_Tie_' not in m:continue # integral native union
            check(n,s,m,t)
    # Persist actual editable native construction even if shared fit is rejected.
    d=A.openDocument(str(source));dest=CAD/'DeckRolledCradles.FCStd'
    try:
        p=d.addObject('App::VarSet','RolledCantileverParameters');p.addProperty('App::PropertyLength','Thickness');p.Thickness=2
        additions=[]
        for name,b,kind,thick in integral:
            o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=A.Vector(*b[:3])
            floor=next(h['bounds_mm'][2] for h in holders if h['leg']==name[:2]);offset=2-thick
            if kind is True:
                o.setExpression('Height',f'RolledCantileverParameters.Thickness - {offset} mm')
                o.setExpression('Placement.Base.z',f'{floor+offset} mm - RolledCantileverParameters.Thickness')
            elif kind is False:o.setExpression('Height',f'{floor+offset-108.8} mm - RolledCantileverParameters.Thickness')
            additions.append(o)
        f=d.addObject('Part::MultiFuse','RolledCantileversFinished');f.Shapes=[d.ParentFeedGripFinished]+additions;f.Refine=False
        d.recompute();s=f.Shape.copy();strict=s.check(True)
        assert s.isValid() and len(s.Solids)==1 and not strict,str(strict)
        volume=s.Volume;p.Thickness=2.2;d.recompute();probe=f.Shape.Volume;assert abs(volume-probe)>1
        p.Thickness=2;d.recompute();assert abs(f.Shape.Volume-volume)<1e-5
        s=f.Shape.copy();d.saveAs(str(dest));s.exportBrep(str(CAD/'Deck_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert max(dims[0]+10,dims[1]+10)<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'DeckRolledCradles_UNSELECTED.stl'))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-cantilever-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);d=A.openDocument(str(q))
        try:d.recompute();assert abs(d.RolledCantileversFinished.Shape.Volume-volume)<1e-5
        finally:A.closeDocument(d.Name)
    for n,s in parts.items():
        if '_Tie_' in n:check(n,s,'NewNativeDeck',load(CAD/'Deck_WORLD.brep'))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='CANTILEVER_CONTACTS' if hits or errors or not all(r['full_bearing'] for r in mount) else 'CANTILEVERS_STATIC_CLEAR_FULL_FEEDS_GRIPS_SERVICE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,holders=rows,straps=straps,mounts=mount,hits=hits,errors=errors,pairs=pairs,
        native=dict(file=dest.relative_to(ROOT).as_posix(),final='RolledCantileversFinished',single_solid=True,strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,parameter_mm=[2,2.2,2],volumes_mm3=[volume,probe,volume],dimensions_mm=dims),
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds(),
        open=['R4 feed source/fixed-owner conflicts and native joint grips remain OPEN.','Full bank/cover/shared removal and stock selection remain OPEN.']))
    print(json.dumps(dict(hits=len(hits),errors=len(errors),mount_failures=sum(not r['full_bearing'] for r in mount),pairs=pairs)),flush=True)


if __name__=='__main__':main()

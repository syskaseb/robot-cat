"""Coupled rear cage trays and independent insulation seats on actual R19 Deck.

Retain accepted complete routes. Preflight the whole added construction against
all current owners BEFORE an expensive native union. No guessed fastener holes,
no waiver for wires or purchased bodies. Any casing contact needs matched CAD.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys, tempfile, shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha, save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rear-output-stations-native-r1'

def main():
    import FreeCAD as A
    import Part, MeshPart
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'preflight.json').exists(),'Preserve previous evidence'
    pins={};V=A.Vector
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    # Reuse exactly the R8 owner recipe, but replace ALL four modified parts.
    definition=ROOT/'tools/electronics/servo_fuse_output_returns_complete_r8.py';pin(definition)
    wrapper=definition.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
    assert wrapper.rstrip().endswith(tail)
    ns=dict(__file__=str(definition),__name__='definition_only')
    exec(compile(wrapper.rstrip()[:-len(tail)],str(definition),'exec'),ns)
    text=ns['code'];recipe=text[text.index('    native=ROOT/'):text.index('    changed={};routes=')]
    fr=text[text.index('    fr_folder=ROOT/'):text.index('    for leg,ident,left,cy,cz,drop,tx,target_y')]
    ctx=dict(ROOT=ROOT,A=A,Part=Part,json=json,pin=pin,load=load,V=V,math=math,retained_owners=retained_owners)
    exec(compile('def receive():\n'+recipe+fr+'\n    return owners\n','rear_station_owners','exec'),ctx)
    owners=ctx['receive']()
    native=ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1'
    owners['CandidateDeck']=load(native/'Deck_WORLD.brep')
    owners['ModifiableCover']=load(native/'Cover_WORLD.brep')
    owners['Bank/RightClipAccessFinished_WORLD']=load(native/'BankRight_WORLD.brep')
    shelf='hardware/cad/studies/pwm-branch-restraints-r4/ShelfPWMGroundTerminal.brep'
    assert shelf in owners;owners[shelf]=load(native/'Shelf_WORLD.brep')
    routefolder=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r8'
    pin(routefolder/'checks.json');r=json.loads((routefolder/'checks.json').read_text(encoding='utf-8'))
    assert not r['errors'] and not r['factory_failures']
    for ident in ('W045','W053'):
        for role in ('221412','factory','extension'):
            owners[ident+'/'+role]=load(routefolder/(ident+'_'+role+'_DESIGN.brep'))
    stocks=[];grooves=[];slots=[];ties=[];changed={};feet=[];mount_failures=[];rows=[]
    def stock(name,b):stocks.append((name,b));return box(b)
    def tie(name,x,ya,yb,za,zt):
        # Tight nominal band surfaces touch housing/insulation envelopes.
        bs=[[x-1.25,ya,za,x+1.25,yb,za+1.2],
            [x-1.25,ya,za,x+1.25,ya+1.2,zt+1.2],
            [x-1.25,yb-1.2,za,x+1.25,yb,zt+1.2],
            [x-1.25,ya,zt,x+1.25,yb,zt+1.2]]
        hb=[x-2.25,ya-4.8,zt-3.5,x+2.25,ya,zt]
        for k,b in enumerate(bs):changed[name+'Band'+str(k)]=box(b)
        changed[name+'Head']=box(hb)
        length=2*((yb-ya)+(zt-za))+15;assert length<=145
        ties.append(dict(role=name,sku='111-02370',installed=1,PROJECT_length_with_insertion_mm=length,head_bounds_mm=hb))
    for row in r['joints']:
        leg=row['leg'];ident=row['id'];b=row['body_bounds_mm'];tx,y,fz=row['ports_mm'][0];ez=row['ports_mm'][1][2];z0=b[2]
        assert leg in ('RL','RR') and row['same_face_and_tangents_asserted']
        # Housing tray and its two staggered grips form ONE supported Deck part.
        ya=y-6.8;yb=y+6.8;end=-27 if leg=='RL' else -26
        stock(leg+'Tray',[b[0]-2.4,ya,z0-2.4,end,yb,z0])
        stock(leg+'RailSouth',[b[0]-2.4,ya,z0,b[3]+.3,b[1]-.2,z0+3])
        stock(leg+'RailNorth',[b[0]-2.4,b[4]+.2,z0,b[3]+.3,yb,z0+3])
        stock(leg+'WestStop',[b[0]-2.4,ya,z0,b[0]-.2,yb,z0+3])
        # Two complete footprints; don't infer support from a bbox or point.
        fy0,fy1=(ya,ya+2.4) if leg=='RL' else (yb-2.4,yb)
        for k,x in enumerate((b[0]-1,end-4)):
            fb=[x,fy0,108.8,x+4,fy1,z0-2.1];fs=stock(leg+'Foot'+str(k),fb)
            footprint=box([x,fy0,108.8,x+4,fy1,109])
            actual=footprint.common(owners['CandidateDeck']).Volume;expected=footprint.Volume
            feet.append(dict(leg=leg,index=k,bounds_mm=fb,expected_embed_mm3=expected,actual_embed_mm3=actual))
            if abs(actual-expected)>1e-4:mount_failures.append(feet[-1])
        fx0,fx1=(-34,-28) if leg=='RL' else (-33,-27)
        ex0,ex1=(-49,-44.5) if leg=='RL' else (-44,-39)
        stock(leg+'FactorySeat',[fx0,y-5.5,z0,fx1,y+5.5,fz+2.5])
        stock(leg+'ExtensionSeat',[ex0,y-5.5,z0,ex1,y+5.5,ez+2.1])
        for role,z,od in [('Factory',fz,5),('Extension',ez,4.2)]:
            grooves.append((leg+role,z,od,[tx-.1,y,z],end-tx+.2))
        hx=(b[0]+b[3])/2
        tie(leg+'HousingTie',hx,ya-1.2,yb+1.2,z0-3.9,b[5])
        tie(leg+'FactoryTie',(fx0+fx1)/2,y-6.7,y+6.7,ez+2.6,fz+2.5)
        tie(leg+'ExtensionTie',(ex0+ex1)/2,y-6.7,y+6.7,z0-1.5,ez+2.1)
        for name,x,za in [(leg+'HousingPass',hx,z0-3.9),
            (leg+'FactoryPass',(fx0+fx1)/2,ez+2.6),
            (leg+'ExtensionPass',(ex0+ex1)/2,z0-1.5)]:
            slots.append((name,[x-1.4,ya-2,za-.15,x+1.4,yb+2,za+1.35]))
        rows.append(dict(leg=leg,id=ident,body_bounds_mm=b,port_coordinates_mm=row['ports_mm'],
            factory_seat_x_mm=[fx0,fx1],extension_seat_x_mm=[ex0,ex1],
            end_straight_mm=row['grip_straight_extension_mm'],additional_T18I=3,
            physical_pass=False,selected=False,recipe='Lay prewired housing in open tray, independently restrain each intact insulation. Feet integral with Deck. Release three straps and both cages before shared bank removal. Lever path remains OPEN.'))
    toolshapes=[Part.makeCylinder(od/2+.2,length,V(*p),V(1,0,0)) for _,z,od,p,length in grooves]+[box(b) for _,b in slots]
    union=box(stocks[0][1]).multiFuse([box(b) for _,b in stocks[1:]])
    fixture=union.cut(toolshapes[0].multiFuse(toolshapes[1:]))
    changed['CoupledRearFixture']=fixture
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:
                hits.append(dict(part=n,owner=m,volume_mm3=c.Volume,bounds_mm=bounds(c)))
                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as exc:errors.append(dict(part=n,owner=m,error=str(exc)))
    for name,s in changed.items():
        s.exportBrep(str(OUT/(name+'_DESIGN.brep')))
        for owner,t in owners.items():
            if name=='CoupledRearFixture' and owner=='CandidateDeck':continue
            check(name,s,owner,t)
    # Every strap must also fit its new fixtures, not only retained owners.
    for name,s in changed.items():
        if name!='CoupledRearFixture':check(name,s,'CoupledRearFixture',fixture)
    strict=fixture.check(True) or []
    pre=dict(status='REAR_OUTPUT_STATIONS_PREFLIGHT',selected=False,physical_pass=False,W5_complete=False,
        pairs=pairs,hits=hits,errors=errors,mount_failures=mount_failures,feet=feet,stations=rows,ties=ties,
        stocks=stocks,grooves=grooves,slots=slots,strict_BOP=[str(x) for x in strict],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds())
    save(OUT/'preflight.json',pre)
    print('REAR_OUTPUT_STATION_PREFLIGHT',json.dumps(dict(pairs=pairs,hits=len(hits),errors=len(errors),mount_failures=len(mount_failures))),flush=True)
    if hits or errors or mount_failures or strict:return
    gp=native/'DeckRearOutputPassages.FCStd';pin(gp)
    d=A.openDocument(str(gp));dest=CAD/'DeckRearOutputStations.FCStd'
    try:
        p=d.addObject('App::VarSet','RearGripParameters');p.addProperty('App::PropertyLength','Clearance');p.Clearance=.2
        objs=[];ntools=[]
        for name,b in stocks:
            o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);objs.append(o)
        for name,z,od,pt,length in grooves:
            o=d.addObject('Part::Cylinder',name+'Groove');o.Height=length
            o.Placement=A.Placement(V(*pt),A.Rotation(V(0,0,1),V(1,0,0)))
            o.setExpression('Radius',f'{od/2} mm + RearGripParameters.Clearance');ntools.append(o)
        for name,b in slots:
            o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);ntools.append(o)
        u=d.addObject('Part::MultiFuse','RearGripStock');u.Shapes=objs;u.Refine=False
        t=d.addObject('Part::MultiFuse','RearGripTools');t.Shapes=ntools;t.Refine=False
        c=d.addObject('Part::Cut','RearGripFixture');c.Base=u;c.Tool=t;c.Refine=False
        f=d.addObject('Part::MultiFuse','RearOutputStationsFinished');f.Shapes=[d.RearOutputPassagesFinished,c];f.Refine=False
        d.saveAs(str(dest));print('REAR_OUTPUT_STATIONS_RECOMPUTE',flush=True);d.recompute()
        s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        volume=s.Volume;p.Clearance=.3;d.recompute();probe=f.Shape.Volume;assert abs(probe-volume)>1e-4
        p.Clearance=.2;d.recompute();assert abs(f.Shape.Volume-volume)<1e-5
        s=f.Shape.copy();d.saveAs(str(dest));s.exportBrep(str(CAD/'Deck_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'Deck_UNSELECTED.stl'))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-rear-output-stations-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:re.recompute();assert abs(re.RearOutputStationsFinished.Shape.Volume-volume)<1e-5
        finally:A.closeDocument(re.Name)
    save(OUT/'checks.json',dict(pre,status='REAR_OUTPUT_NATIVE_STATIONS_STATIC_COMPLETE_SERVICE_OPEN',
        native=dict(file=dest.relative_to(ROOT).as_posix(),final='RearOutputStationsFinished',single_solid=True,strict_BOP_errors=0,
            closed_STL=True,relocated_reopen=True,parameter_mm=[.2,.3,.2],volumes_mm3=[volume,probe,volume],dimensions_mm=dims),
        stock_delta=dict(additional_T18I=6,additional_prints=0,new_fasteners=0,replacement='Deck'),
        open=['Genuine lever action and full shared assembly/removal remain OPEN.','Phase2 housing/lead fit, PETG bending/creep and strap insertion/pull; no physical PASS.'],
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('REAR_OUTPUT_STATIONS_NATIVE_SAVED',flush=True)
if __name__=='__main__':main()

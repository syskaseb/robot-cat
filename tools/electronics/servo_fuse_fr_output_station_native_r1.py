"""Complete FR output restraint on the existing removable passive wire guard.

Do not add guessed fastener holes through the populated Deck. Extend the
guard's rear wall down to a housing tray and two insulation grips; its two
already dimensioned M3 fixings remain unchanged. Three T18I are added roles.
Preflight all added solids/straps before computing native editable export.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-output-station-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-fr-output-station-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'preflight.json').exists(),'Preserve construction evidence'
    pins={};V=A.Vector
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    ref=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r3/checks.json';pin(ref)
    r=json.loads(ref.read_text(encoding='utf-8'));assert not r['hits'] and not r['errors'] and not r['factory_failures']
    j=r['joints'][0];assert j['same_face_and_tangents_asserted']
    tx=j['ports_mm'][0][0];fz=j['ports_mm'][0][2];ez=j['ports_mm'][1][2]
    z0=j['body_bounds_mm'][2]
    # Reuse the exact R3 owner construction, not a new copy of the robot.
    definition=ROOT/'tools/electronics/servo_fuse_output_returns_complete_r3.py';pin(definition)
    ns=dict(__file__=str(definition),__name__='definition_only')
    exec(compile(definition.read_text(encoding='utf-8'),str(definition),'exec'),ns)
    code=ns['code'];recipe=code[code.index('    native=ROOT/'):code.index('    changed={};routes=')]
    tail=code[code.index('    prior_outputs=ROOT/'):code.index("    leg='FR'")]
    ctx=dict(ROOT=ROOT,A=A,Part=Part,json=json,pin=pin,load=load,V=V,math=math)
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    ctx['retained_owners']=retained_owners
    exec(compile('def receive():\n'+recipe+tail+'\n    return owners\n','fr_owner_recipe','exec'),ctx)
    owners=ctx['receive']();parent=owners.pop('FRReturnGuard')
    for role in ('221412','factory','extension'):
        owners['FR_output/'+role]=load(ref.parent/('W037_'+role+'_DESIGN.brep'))
    gp=ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r3/FRReturnGuard.FCStd';pin(gp)
    stocks=[('OutputSpine',[-109.5,-130,z0-2.4,-107,-95,134.5]),
        ('OutputTray',[-109.5,-130,z0-2.4,-93,-95,z0]),
        ('HousingWestRail',[-105.9,-129,z0,-103.7,-108.8,z0+3]),
        ('HousingEastRail',[-95.15,-129,z0,-93,-108.8,z0+3]),
        ('HousingEndStop',[-105.9,-129.7,z0,-93,-127.5,z0+3]),
        ('LowerInsulationSeat',[-107.5,-107,z0,-96,-101,ez+1.7]),
        ('UpperInsulationSeat',[-107.5,-103,z0,-96,-97,fz+2.1])]
    stockshapes=[box(b) for _,b in stocks]
    grooves=[]
    for role,z,od in [('Factory',fz,5),('Extension',ez,4.2)]:
        grooves.append((role,z,od,Part.makeCylinder(od/2+.2,13,V(tx,-109,z),V(0,1,0))))
    slots=[('LowerTiePass',[-110,-105.4,z0-3,-93,-102.6,z0-1.5]),
        ('UpperTiePass',[-110,-101.4,ez+2.3-.3,-93,-98.6,ez+3.5+.3])]
    tools=[s for _,_,_,s in grooves]+[box(b) for _,b in slots]
    fixture=stockshapes[0].multiFuse(stockshapes[1:]).cut(tools[0].multiFuse(tools[1:]))
    changed={'FR_OutputFixture':fixture};ties=[]
    def tie(name,y,xa,xb,za,zt,head_x):
        bands=[[xa,y-1.25,za,xb,y+1.25,za+1.2],
            [xa,y-1.25,za,xa+1.2,y+1.25,zt+1.2],
            [xb-1.2,y-1.25,za,xb,y+1.25,zt+1.2],
            [xa,y-1.25,zt,xb,y+1.25,zt+1.2]]
        hb=[head_x,y-2.25,zt-3.5,head_x+4.8,y+2.25,zt]
        for k,b in enumerate(bands):changed[name+'Band'+str(k)]=box(b)
        changed[name+'Head']=box(hb)
        length=2*((xb-xa)+(zt-za))+15;assert length<145,length
        ties.append(dict(role=name,sku='111-02370',centreline_plus_PROJECT_insertion_mm=length,
            head_bounds_mm=hb,installed=1,phase2='PETG bending/creep, tie insertion/pull and delivered housing fit.'))
    tie('HousingTie',-120,-107.1,-91.75,z0-4,z0+13,-111.9)
    tie('ExtensionTie',-104,-108.7,-93.8,z0-2.7,ez+2.1,-113.5)
    tie('FactoryTie',-100,-108.7,-93.8,ez+2.3,fz+2.5,-113.5)
    # Check actual nominal housing/insulation restraint and the whole
    # retained source group. Parent guard union is intentional only.
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
    for n,s in changed.items():
        s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
        for m,t in owners.items():check(n,s,m,t)
    items=list(changed.items())
    for i,(n,s) in enumerate(items):
        for m,t in items[i+1:]:
            if n[:n.find('Band')] == m[:m.find('Band')] and 'Band' in n and 'Band' in m:continue
            check(n,s,m,t)
    strict=fixture.check(True) or []
    pre=dict(selected=False,physical_pass=False,pairs=pairs,hits=hits,errors=errors,
        fixture_single_solid=len(fixture.Solids)==1,fixture_strict_BOP=[str(x) for x in strict],
        union_with_guard_mm3=fixture.common(parent).Volume,ties=ties,
        stocks=stocks,grooves=[dict(role=role,z_mm=z,OD_mm=od,allowance_mm=.2) for role,z,od,_ in grooves],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),
        finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds(),
        open='Native export/combined removal/lever access/stock not qualified by preflight alone.')
    save(OUT/'preflight.json',pre)
    print('FR_OUTPUT_PREFLIGHT',json.dumps(dict(pairs=pairs,hits=len(hits),errors=len(errors))),flush=True)
    if hits or errors or strict or len(fixture.Solids)!=1 or pre['union_with_guard_mm3']<=0:return
    d=A.openDocument(str(gp));dest=CAD/'FRGuardOutputStation.FCStd'
    try:
        p=d.addObject('App::VarSet','OutputGripParameters');p.addProperty('App::PropertyLength','Clearance');p.Clearance=.2
        native=[];ntools=[]
        for name,b in stocks:
            o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);native.append(o)
        for role,z,od,_ in grooves:
            o=d.addObject('Part::Cylinder',role+'OutputGroove');o.Height=13
            o.Placement=A.Placement(V(tx,-109,z),A.Rotation(V(0,0,1),V(0,1,0)))
            o.setExpression('Radius',f'{od/2} mm + OutputGripParameters.Clearance');ntools.append(o)
        for name,b in slots:
            o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);ntools.append(o)
        union=d.addObject('Part::MultiFuse','OutputGripStock');union.Shapes=native;union.Refine=False
        tool=d.addObject('Part::MultiFuse','OutputGripTools');tool.Shapes=ntools;tool.Refine=False
        cut=d.addObject('Part::Cut','OutputFixture');cut.Base=union;cut.Tool=tool;cut.Refine=False
        final=d.addObject('Part::MultiFuse','FRGuardOutputFinished');final.Shapes=[d.FRReturnGuardFinished,cut];final.Refine=False
        d.recompute();s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        vol=s.Volume;p.Clearance=.3;d.recompute();probe=final.Shape.Volume;assert abs(vol-probe)>1e-4
        p.Clearance=.2;d.recompute();assert abs(final.Shape.Volume-vol)<1e-5
        s=final.Shape.copy();d.saveAs(str(dest));s.exportBrep(str(CAD/'Guard_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        mesh.rotate(0,math.pi/2,0);bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
        assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'Guard_UNSELECTED.stl'))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fr-output-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:re.recompute();assert abs(re.FRGuardOutputFinished.Shape.Volume-vol)<1e-5
        finally:A.closeDocument(re.Name)
    save(OUT/'checks.json',dict(pre,status='FR_OUTPUT_NATIVE_STATIC_COMPLETE_SERVICE_OPEN',
        native=dict(file=dest.relative_to(ROOT).as_posix(),final='FRGuardOutputFinished',single_solid=True,strict_BOP_errors=0,
            closed_STL=True,relocated_reopen=True,parameter_mm=[.2,.3,.2],volumes_mm3=[vol,probe,vol],dimensions_mm=dims),
        stock_delta=dict(replacement_print='FRGuard',additional_prints=0,additional_T18I=3,new_fasteners=0),
        recipe=['Attach guard to unpowered removed bank using the SAME two M3x8/nuts before routing.',
            'Prewire two bare untinned cage ends,11mm nominal strip; clip housing into tray and close one housing tie.',
            'Lay each insulation end into its open groove and close its own tie; no shared tie substitutes for either end.',
            'Guard moves with bank; whole module disconnect/removal and lever access remain OPEN.'],
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('FR_OUTPUT_NATIVE_COMPLETE',flush=True)
if __name__=='__main__':main()

"""Editable two-panel bank and nominal Deck fasteners, not a selected release.

Reusable construction for the single side-bank design. Routes stay separate
owned evidence; this module owns PETG panels/posts/feet, not a private Deck.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, shutil, sys, tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/cad'), str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save, sha
CAD = ROOT/'hardware/cad/studies/servo-fuse-bank-native-r1'
OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-bank-native-r1'

def main():
    import FreeCAD as A
    import Part, MeshPart
    from open_deck_p0_plate import rect, circle
    import servo_fuse_side_bank_r7 as layout
    begin = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists(), 'Preserve completed evidence'
    CAD.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    route_checks = layout.OUT/'checks.json'
    report = json.loads(route_checks.read_text(encoding='utf-8'))
    assert not report['errors']
    assert sha(ROOT/'tools/electronics/servo_fuse_side_bank_r7.py') == report['script_sha256']
    cart_path=ROOT/'hardware/manufacturing/fixed-fastener-skus-r1/cart.json'
    cart=json.loads(cart_path.read_text(encoding='utf-8'))['rows']
    bolt=next(r for r in cart if r['supplier_sku']=='0912A2-M020X012VISK')
    nut=next(r for r in cart if r['supplier_sku']=='SKL000381')
    washer=next(r for r in cart if r['supplier_sku']=='00125202')
    bd=bolt['dimensions_mm'];nd=nut['dimensions_mm'];wd=washer['dimensions_mm']
    assert bd['L']==12 and bd['d']==2
    sources={route_checks.relative_to(ROOT).as_posix():sha(route_checks),
        cart_path.relative_to(ROOT).as_posix():sha(cart_path)}
    d=A.newDocument('ServoFuseBank'); sketches=[]; parts={}; axes=[]
    parameters=d.addObject('App::VarSet','BankParameters')
    parameters.addProperty('App::PropertyLength','PanelThickness');parameters.PanelThickness=2
    def block(name,b,thickness=False):
        sk=d.addObject('Sketcher::SketchObject',name+'Profile');sk.Placement.Base.z=b[2]
        rect(sk,b[0],b[1],b[3]-b[0],b[4]-b[1]);sketches.append(sk)
        f=d.addObject('Part::Extrusion',name);f.Base=sk;f.Dir=A.Vector(0,0,b[5]-b[2]);f.Solid=True
        if thickness:f.setExpression('Dir.z','BankParameters.PanelThickness')
        return f
    finals=[]
    for side in (-1,1):
        lo,hi=sorted((side*90,side*130)); tag='Right' if side<0 else 'Left'
        panel=block(tag+'Panel',[-97,lo,144.5,107,hi,146.5],True);stock=[panel]
        holes=[]
        for x in (-95,105):
            a,b=sorted((side*91,side*97))
            stock.extend([block(tag+'Post'+str(abs(x)),[x-2,a,109,x+2,b,144.7]),
                          block(tag+'Foot'+str(abs(x)),[x-9,a,109,x+9,b,113])])
            hx=x+(-6 if x<0 else 6);hy=side*93;axes.append((hx,hy))
            sk=d.addObject('Sketcher::SketchObject',tag+'Bolt'+str(abs(x))+'Profile')
            sk.Placement.Base.z=108.9;circle(sk,hx,hy,2.4);sketches.append(sk)
            hole=d.addObject('Part::Extrusion',tag+'Bolt'+str(abs(x)))
            hole.Base=sk;hole.Dir=A.Vector(0,0,4.2);hole.Solid=True;holes.append(hole)
        for base in (-69,39):
            for i in range(3):
                cx=base+26*i;cy=side*110
                cut=block(tag+'MTA'+str(cx).replace('-','N'),[cx-5.65,cy-11.1,144.4,cx+5.65,cy+11.1,146.6])
                cut.setExpression('Dir.z','BankParameters.PanelThickness + 0.2 mm');holes.append(cut)
        raw=d.addObject('Part::MultiFuse',tag+'Stock');raw.Shapes=stock;raw.Refine=True
        cutters=d.addObject('Part::MultiFuse',tag+'Cutters');cutters.Shapes=holes
        finished=d.addObject('Part::Cut',tag+'Finished');finished.Base=raw;finished.Tool=cutters;finished.Refine=True
        finals.append(finished)
    d.recompute()
    for f in finals:
        assert f.Shape.isValid() and len(f.Shape.Solids)==1 and not f.Shape.check(True),f.Name
        parts[f.Name]=f.Shape.copy()
    assert all(s.solve()==0 and s.FullyConstrained for s in sketches)
    before=[f.Shape.Volume for f in finals]
    parameters.PanelThickness=2.1;d.recompute();probe=[f.Shape.Volume for f in finals]
    assert all(p>b for p,b in zip(probe,before))
    parameters.PanelThickness=2;d.recompute()
    assert all(abs(f.Shape.Volume-v)<1e-6 for f,v in zip(finals,before))
    native=CAD/'ServoFuseBank.FCStd';d.saveAs(str(native));A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fuse-bank-') as td:
        relocated=Path(td)/native.name;shutil.copy2(native,relocated);re=A.openDocument(str(relocated))
        try:
            re.recompute()
            for name,v in zip(parts,before):
                assert re.getObject(name).Shape.isValid()
                assert abs(re.getObject(name).Shape.Volume-v)<1e-6
        finally:A.closeDocument(re.Name)
    dimensions={}
    for name,s in parts.items():
        s.exportBrep(str(CAD/(name+'_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        mesh.rotate(math.pi,0,0);b=mesh.BoundBox
        dimensions[name]=[b.XLength,b.YLength,b.ZLength]
        assert b.XLength+10<256 and b.YLength+10<256 and b.ZLength<256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(name+'_x1.stl')))
    owners,hashes,_=layout.current_owners();deck=Part.read(str(layout.OUT/'Deck_candidate_UNSELECTED.brep'))
    def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,A.Vector(x,y,z))
    def ring(x,y,z):
        return cyl(x,y,z,wd['OD']/2,wd['t']).cut(cyl(x,y,z-.1,wd['ID']/2,wd['t']+.2))
    hardware={};tool_reserves={}
    for i,(x,y) in enumerate(axes):
        deck=deck.cut(cyl(x,y,104.9,1.2,4.2))
        underhead=113+wd['t'];tip=underhead-bd['L'];nut_top=105-wd['t'];nut_z=nut_top-nd['H']
        assert nut_z-tip >= bd['pitch']
        hardware[f'Bolt{i}']=cyl(x,y,tip,1,bd['L']).fuse(cyl(x,y,underhead,bd['head_d']/2,bd['head_h']))
        hardware[f'Washers{i}']=Part.makeCompound([ring(x,y,113),ring(x,y,105-wd['t'])])
        radius=nd['AF']/math.sqrt(3)
        pts=[A.Vector(x+radius*math.cos(k*math.pi/3),y+radius*math.sin(k*math.pi/3),nut_z) for k in range(6)]
        hardware[f'Nut{i}']=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,0,nd['H'])).cut(cyl(x,y,nut_z-.1,1,nd['H']+.2))
        tool_reserves[f'Allen{i}']=cyl(x,y,underhead+bd['head_h'],2,28)
        tool_reserves[f'NutTool{i}']=cyl(x,y,nut_z-20,3.5,20).cut(cyl(x,y,nut_z-20.1,1.1,20.2))
    assert deck.isValid() and len(deck.Solids)==1
    owners['R49Deck']=deck;deck.exportBrep(str(OUT/'Deck_candidate_UNSELECTED.brep'))
    for p in layout.OUT.glob('*_DESIGN.brep'):
        if p.stem.startswith(('Post_','Panel_')):continue
        sources[p.relative_to(ROOT).as_posix()]=sha(p);owners['Routes/'+p.stem]=Part.read(str(p))
    hits=[];cover_hits=[];access=[];errors=[];pairs=0
    def check(n,s,m,t,tools=False):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    v=a.common(b).Volume
                    if v>1e-5:
                        h=dict(part=n,owner=m,hit_mm3=v)
                        if tools:access.append(h)
                        elif m.endswith('/CoverYawEndSeat.brep'):cover_hits.append(h)
                        elif n.endswith('Finished') and m.startswith('Routes/F_') and '_ATO_' not in m and not m.endswith(('_IN_DESIGN','_OUT_DESIGN')):
                            pass # Conservative holder box includes its own nominal flange/latch; explicit delivery condition below.
                        else:hits.append(h)
                except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in {**parts,**hardware}.items():
        for m,t in owners.items():check(n,s,m,t)
    for n,s in hardware.items():
        for m,t in parts.items():check(n,s,m,t)
    for n,s in tool_reserves.items():
        for m,t in {**owners,**parts}.items():check(n,s,m,t,True)
    for n,s in {**hardware,**tool_reserves}.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_CANDIDATE_NOT_SELECTED',selected=False,W5_complete=False,physical_pass=False,
        hits=hits,errors=errors,cover_hits_not_waived=cover_hits,tool_access_contacts=access,pairs=pairs,
        native=dict(path=native.relative_to(ROOT).as_posix(),sketches=len(sketches),strict_BOP_errors=0,
            single_solid_per_panel=True,parameter_volumes=[before,probe,before],relocated_reopen=True,closed_STLs=True,print_dimensions_mm=dimensions),
        deck_bolt_xy=axes,nominal_added_hardware=dict(M2x12=4,M2_DIN934=4,M2_DIN125=8),
        fastener_sources=[bolt,nut,washer],MTA_condition='Nominal2mm panel/22.2x11.3cutout; conservative housing box includes own flange/latch. e and terminal axes provisional; delivery coupon required.',
        remaining=['Resolve every physical hit and tool access by actual geometry/order.','Complete output wires/strain relief and cover.','Native Deck modification, package/quantities and mounting order before selection.'],
        source_sha256={**hashes,**sources},script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=len(hits),errors=len(errors),cover_hits=len(cover_hits),tool_contacts=len(access),dimensions=dimensions)),flush=True)

if __name__=='__main__':main()

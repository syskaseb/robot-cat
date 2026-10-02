"""Four independent Deck-mounted MTA carriers, not banks pulling short leads.

One editable PETG master, mirrored for the opposite side. Both factory exits
are reserved; outgoing leads terminate at the actual four P-WAGO datums.
The other four leads have exit reserves only, NOT complete source routes.
Body/OD/usable lengths remain explicit delivery assumptions. Rejected R1
shelves are not retried. Changed cover windows remain candidate geometry.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys, shutil, tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-carriers-r2'
CAD=ROOT/'hardware/cad/studies/servo-fuse-parent-carriers-r2'


def local_blocks():
    # Body centre is local X0, world |Y|115.5, Z131.5.
    # Carrier sits at world Y=68 (or its mirror), Z109.
    return [(-12,29.5,9.5,12,67.5,11.5),       # pad
            (11,0,0,17,10,2.5),               # two M2 foot axes
            (16.5,4,2.3,18.5,8,13.5),         # tower, outside axial tool approach
            (16.5,7,11.5,18.5,29.6,13.5),     # arm above selected brackets
            (10,29.5,11.5,18.5,32,13.5),      # bridge
            (10,29.5,9.5,12,32,13.5)]         # pad/bridge connection


def outgoing_path(A,Part,x,cx,side):
    start=A.Vector(x,side*49.5,113.5);end=A.Vector(cx,side*98,131.5)
    out=A.Vector(0,side,0);shift=end-start;shift.y=0
    h=shift.Length;t=shift/h;R=20;angle=math.acos(1-h/(2*R))
    p=start+out*9;edges=[Part.makeLine(start,p)];begin=A.Vector(p)
    def q(a):return begin+out*(R*math.sin(a))+t*(R*(1-math.cos(a)))
    edges.append(Part.Arc(q(0),q(angle/2),q(angle)).toShape());p=q(angle);begin=A.Vector(p)
    tangent=out*math.cos(angle)+t*math.sin(angle);inward=out*math.sin(angle)-t*math.cos(angle)
    def q2(a):return begin+tangent*(R*math.sin(a))+inward*(R*(1-math.cos(a)))
    edges.append(Part.Arc(q2(0),q2(angle/2),q2(angle)).toShape());p=q2(angle)
    assert (end-p).dot(out)>0 and abs(end.x-p.x)<1e-7 and abs(end.z-p.z)<1e-7
    edges.append(Part.makeLine(p,end));path=Part.Wire(edges)
    assert all(abs(e.Curve.Radius-R)<1e-6 for e in edges if hasattr(e.Curve,'Radius'))
    return path,path.makePipeShell([Part.Wire([Part.makeCircle(2.5,start,out)])],True,False)


def main():
    import FreeCAD as A
    import Part,MeshPart
    import servo_fuse_side_bank_r10 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();hashes={}
    def pin(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,A.Vector(x,y,z))
    def mirror(s):
        m=A.Matrix();m.A22=-1;return s.transformGeometry(m)
    p=ROOT/'hardware/manufacturing/fixed-fastener-skus-r1/cart.json';pin(p)
    cart=json.loads(p.read_text(encoding='utf-8'))['rows']
    bd=next(r for r in cart if r['supplier_sku']=='0912A2-M020X012VISK')['dimensions_mm']
    nd=next(r for r in cart if r['supplier_sku']=='SKL000381')['dimensions_mm']
    wd=next(r for r in cart if r['supplier_sku']=='00125202')['dimensions_mm']
    assert bd['d']==2 and bd['L']==12 and wd['OD']==5
    d=A.newDocument('ParentFuseCarrier')
    try:
        par=d.addObject('App::VarSet','CarrierParameters');par.addProperty('App::PropertyLength','TieSlotWidth');par.TieSlotWidth=1.6
        blocks=[]
        for i,b in enumerate(local_blocks()):
            obj=d.addObject('Part::Box','Support'+str(i));obj.Length=b[3]-b[0];obj.Width=b[4]-b[1];obj.Height=b[5]-b[2]
            obj.Placement.Base=A.Vector(*b[:3]);blocks.append(obj)
        fused=d.addObject('Part::MultiFuse','CarrierSolid');fused.Shapes=blocks;fused.Refine=True;previous=fused
        for i,y in enumerate((43.5,60.5)):
            for j,sgn in enumerate((-1,1)):
                tool=d.addObject('Part::Box','TieSlot'+str(i)+str(j));tool.Length=1.6;tool.Width=2.9;tool.Height=6
                tool.Placement.Base=A.Vector(sgn*8.6-.8,y-1.45,7);tool.setExpression('Length','CarrierParameters.TieSlotWidth')
                f=d.addObject('Part::Cut','TiePass'+str(i)+str(j));f.Base=previous;f.Tool=tool;f.Refine=True;previous=f
        for i,y in enumerate((2,8)):
            tool=d.addObject('Part::Cylinder','MountHole'+str(i));tool.Radius=1.2;tool.Height=3
            tool.Placement.Base=A.Vector(14,y,-.1)
            f=d.addObject('Part::Cut','MountPass'+str(i));f.Base=previous;f.Tool=tool;f.Refine=True;previous=f
        previous.Label='Carrier positive-Y master'
        opposite=d.addObject('Part::Mirroring','CarrierOpposite');opposite.Source=previous;opposite.Normal=A.Vector(0,1,0);opposite.Base=A.Vector(0,0,0)
        d.recompute();master=previous.Shape.copy();assert master.isValid() and len(master.Solids)==1 and not master.check(True)
        rows=[];links={}
        for leg,wire,upstream in [('FL','W026','W041'),('FR','W037','W042'),('RL','W045','W044'),('RR','W053','W052')]:
            side=1 if leg.endswith('L') else -1;base=-69 if leg.startswith('F') else 39;x=base-13.5;cx=x-10.5
            obj=d.addObject('App::Link',leg+'Carrier');obj.setLink(previous if side==1 else opposite)
            obj.Placement.Base=A.Vector(cx,side*68,109);links[leg]=obj
            path,tube=outgoing_path(A,Part,x,cx,side);assert tube.isValid() and len(tube.Solids)==1
            path.exportBrep(str(OUT/(wire+'_CENTERLINE.brep')));tube.exportBrep(str(OUT/(wire+'_DESIGN.brep')))
            blank=math.ceil((path.Length+11+10)/10)*10;assert blank<=100
            rows.append(dict(leg=leg,wire=wire,upstream_wire=upstream,cx=cx,side=side,
                WAGO_mm=[x,side*49.5,113.5],holder_out_mm=[cx,side*98,131.5],holder_in_mm=[cx,side*133,131.5],
                path_mm=path.Length,provisional_factory_out_required_mm=blank,assumed_available_each_lead_mm=100,
                actual_cut_mm=None,actual_available_mm=None,upstream_route_complete=False))
        d.recompute();volumes={leg:obj.Shape.Volume for leg,obj in links.items()}
        par.TieSlotWidth=1.8;d.recompute();probe={leg:obj.Shape.Volume for leg,obj in links.items()}
        assert all(probe[n]<volumes[n] for n in links)
        par.TieSlotWidth=1.6;d.recompute();assert all(abs(obj.Shape.Volume-volumes[n])<1e-5 for n,obj in links.items())
        dest=CAD/'ParentFuseCarrier.FCStd';d.saveAs(str(dest))
        carriers={n:obj.Shape.copy() for n,obj in links.items()}
        for n,s in carriers.items():s.exportBrep(str(CAD/(n+'_WORLD.brep')))
        for suffix,s in [('L',master),('R',opposite.Shape.copy())]:
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1;b=mesh.BoundBox
            assert b.XLength+10<256 and b.YLength+10<256 and b.ZLength<256
            mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/('Carrier_'+suffix+'_x2.stl')))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-parent-carrier-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert all(re.getObject(n+'Carrier').Shape.isValid() and abs(re.getObject(n+'Carrier').Shape.Volume-volumes[n])<1e-5 for n in links)
        finally:A.closeDocument(re.Name)
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,started_utc=begin.isoformat(),routes=rows,
        assumptions=dict(MTA_body_mm=[16,35,22],lead_OD_mm=5,R_mm=20,each_free_factory_lead_mm=100,all_project_not_supplier=True),
        part_ownership='Two mirrored carrier prints x2 each, eight M2x12 Deck fasteners; bank/cover removal leaves carriers stationary.',
        manufacturing='PETG; proposed pad-down with sacrificial support under cantilever/tower, +10mm brim allowance; actual nozzle/profile/strength/creep unverified.',
        assembly='Power absent. Fasten carriers to removed Deck, prewire loose P-WAGOs then close levers. Mount holders with two ties each, heads below pads. Source-side factory lead exits reserved only; exact routes/lengths remain open.',
        open=['Source-side four leads must reach their actual P_FRONT/P_REAR ports, not merely free exit reserves.',
              'Native Deck bores and cover reliefs required only after shared fit accepted.',
              'Eight M2 tool approaches and bank/cover removal must be qualified.']))
    print('LOAD_SHARED_CURRENT',flush=True)
    owners,more,_=layout.current_owners();hashes.update(more)
    coverkey='hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep'
    oldcover=owners.pop(coverkey)
    for n in list(owners):
        if '/servo-fuse-bank-restraints-r2/' in n or '/servo-fuse-bank-restraints-fit-r2/' in n:del owners[n]
    deck=load(ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/Deck_WORLD.brep')
    owners.pop('R49Deck')
    for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep'):owners['Bank/'+p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11').glob('F_*_DESIGN.brep'):owners['R11/'+p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4').glob('release_0.0_W*_DESIGN.brep'):owners['NewInputs/'+p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r2').glob('*_DESIGN.brep'):owners['FeedTies/'+p.stem]=load(p)
    installed={};hardware={};toolreserves={};cuts=[];axes=[];bearing=[]
    cover=oldcover
    def ring(x,y,z):return cyl(x,y,z,wd['OD']/2,wd['t']).cut(cyl(x,y,z-.1,wd['ID']/2,wd['t']+.2))
    for r in rows:
        leg=r['leg'];cx=r['cx'];side=r['side']
        def span(x0,y0,z0,x1,y1,z1):
            lo,hi=sorted((side*y0,side*y1));return [x0,lo,z0,x1,hi,z1]
        installed[leg+'_Carrier']=carriers[leg]
        installed[leg+'_Body']=box(span(cx-8,98,120.5,cx+8,133,142.5))
        installed[r['wire']+'_Wire']=load(OUT/(r['wire']+'_DESIGN.brep'))
        # Necessary straight access at BOTH factory exits, not an upstream connection claim.
        installed[r['upstream_wire']+'_EXIT_ONLY']=cyl(cx,side*133,131.5,2.5,10)
        installed[r['upstream_wire']+'_EXIT_ONLY']=Part.makeCylinder(2.5,10,A.Vector(cx,side*133,131.5),A.Vector(0,side,0))
        for index,y in enumerate((111.5,128.5)):
            for j,b in enumerate([span(cx-9.2,y-1.25,117.3,cx-8,y+1.25,143.7),
                                 span(cx+8,y-1.25,117.3,cx+9.2,y+1.25,143.7),
                                 span(cx-8,y-1.25,142.5,cx+8,y+1.25,143.7),
                                 span(cx-8,y-1.25,117.3,cx+8,y+1.25,118.5),
                                 span(cx-3,y-2,112.3,cx+3,y+2,117.3)]):installed[leg+'_BodyTie'+str(index)+'_'+str(j)]=box(b)
        b=span(cx-12.5,97.4,116,cx+19,100.6,144.2);cuts.append(b);cover=cover.cut(box(b))
        for index,y in enumerate((side*70,side*76)):
            x=cx+14;axes.append([x,y]);cut=cyl(x,y,104.9,1.2,4.2);deck=deck.cut(cut)
            footprint=cyl(x,y,105.1,wd['OD']/2,3.8).cut(cyl(x,y,105,1.2,4.1))
            bearing.append(dict(leg=leg,xy=[x,y],missing_mm3=footprint.cut(deck).Volume))
            top=111.5;underhead=top+wd['t'];tip=underhead-bd['L'];nuttop=105-wd['t'];nz=nuttop-nd['H']
            assert nz-tip>=bd['pitch']
            hardware[leg+'_Bolt'+str(index)]=cyl(x,y,tip,1,bd['L']).fuse(cyl(x,y,underhead,bd['head_d']/2,bd['head_h']))
            hardware[leg+'_Washers'+str(index)]=Part.makeCompound([ring(x,y,top),ring(x,y,105-wd['t'])])
            rad=nd['AF']/math.sqrt(3);pts=[A.Vector(x+rad*math.cos(k*math.pi/3),y+rad*math.sin(k*math.pi/3),nz) for k in range(6)]
            hardware[leg+'_Nut'+str(index)]=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,0,nd['H'])).cut(cyl(x,y,nz-.1,1,nd['H']+.2))
            toolreserves[leg+'_Allen'+str(index)]=cyl(x,y,underhead+bd['head_h'],2,28)
            toolreserves[leg+'_NutTool'+str(index)]=cyl(x,y,nz-20,3.5,20).cut(cyl(x,y,nz-20.1,1.1,20.2))
    assert deck.isValid() and len(deck.Solids)==1
    assert cover.isValid() and len(cover.Solids)==1
    owners['CandidateDeck']=deck;owners['CandidateCover']=cover
    deck.exportBrep(str(OUT/'Deck_candidate_UNSELECTED.brep'));cover.exportBrep(str(OUT/'Cover_candidate_UNSELECTED.brep'))
    hits=[];errors=[];access=[];pairs=0
    def check(n,s,m,t,is_tool=False):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:
                row=dict(part=n,owner=m,hit_mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')])
                target=access if is_tool else hits;target.append(row)
                c.exportBrep(str(OUT/(('ACCESS_' if is_tool else 'HIT_')+str(len(target))+'.brep')))
        except Exception as exc:errors.append(dict(part=n,owner=m,error=str(exc)))
    for n,s in {**installed,**hardware}.items():
        print('FIT '+n,flush=True);s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
        for m,t in owners.items():check(n,s,m,t)
    items=list({**installed,**hardware}.items())
    for i,(n,s) in enumerate(items):
        for m,t in items[i+1:]:check(n,s,m,t)
    for n,s in toolreserves.items():
        s.exportBrep(str(OUT/(n+'_RESERVE.brep')))
        for m,t in {**owners,**installed}.items():
            # Own foot hole/tool approach tested by actual clearance; no own body waiver.
            check(n,s,m,t,True)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='PARENT_CARRIER_CONFLICTS' if hits or errors or access or any(r['missing_mm3']>1e-5 for r in bearing) else 'NATIVE_PARENT_CARRIERS_STATIC_CLEAR_SOURCE_SERVICE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,native=dest.relative_to(ROOT).as_posix(),native_links=4,
        single_solid=True,strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,parameter_volumes=dict(before=volumes,probe=probe,restored=volumes),
        routes=rows,cover_cuts_mm=cuts,deck_axes_mm=axes,bearing_checks=bearing,
        nominal_added_hardware=dict(M2x12=8,M2_DIN934=8,M2_DIN125=16),body_ties=8,
        hits=hits,access_hits=access,errors=errors,pairs=pairs,
        open=['Source-side exact routes/lengths and both-exit full feed completion remain OPEN.',
              'Native Deck/cover export and complete bank/cover removal after static fit.',
              'MTA dimensions/lead stock and PETG load/creep are delivery/prototype assumptions, no physical PASS.'],
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=len(hits),access_hits=len(access),errors=len(errors),pairs=pairs)),flush=True)


if __name__=='__main__':main()

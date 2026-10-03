"""One shared four-holder design, BOTH exits and complete source/output wires.

R2/3/4 mount-only layouts are rejected. Here holders turn 90 degrees and
sit on integral Deck saddles. Front extensions use the already catalogued
221-412; rear extensions use supported insulated lap joints and existing
4mm2/solder/shrink stock. Dimensions of MTA, joints and port labels remain
explicit prototype assumptions. Nothing is selected or physically passed.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys, shutil, tempfile
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/electronics'), str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT/'hardware/electronics/full-cat/servo-fuse-parent-complete-layout-r5'
CAD = ROOT/'hardware/cad/studies/servo-fuse-parent-complete-layout-r5'


def main():
    import FreeCAD as A
    import Part, MeshPart
    import servo_fuse_side_bank_r10 as layout
    started = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True); CAD.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve completed evidence'
    pins = {}
    def pin(p): pins[p.relative_to(ROOT).as_posix()] = sha(p)
    def load(p):
        pin(p); return Part.read(str(p))
    def box(b): return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))
    def bounds(s): return [getattr(s.BoundBox, k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    V = A.Vector

    class Route:
        def __init__(self, p): self.p=V(*p); self.edges=[]; self.radii=[]
        def line(self, q):
            q=V(*q) if not isinstance(q, V) else q
            if (q-self.p).Length > 1e-8: self.edges.append(Part.makeLine(self.p,q)); self.p=q
        def arc(self, tangent, normal, radius, angle=math.pi/2):
            p=V(self.p)
            def q(t): return p+tangent*(radius*math.sin(t))+normal*(radius*(1-math.cos(t)))
            self.edges.append(Part.Arc(q(0),q(angle/2),q(angle)).toShape())
            self.p=q(angle); self.radii.append(radius)
        def shift(self, tangent, delta, radius):
            h=delta.Length
            assert 0<h<2*radius
            normal=delta/h; a=math.acos(1-h/(2*radius))
            self.arc(tangent,normal,radius,a)
            self.arc(tangent*math.cos(a)+normal*math.sin(a), tangent*math.sin(a)-normal*math.cos(a),radius,a)
        def shape(self, od, tangent):
            path=Part.Wire(self.edges)
            for a,b in zip(self.edges,self.edges[1:]):
                assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6
                assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-6
            tube=path.makePipeShell([Part.Wire([Part.makeCircle(od/2,self.edges[0].valueAt(self.edges[0].FirstParameter),tangent)])],True,False)
            assert tube.isValid() and len(tube.Solids)==1
            return path,tube

    X=V(1,0,0); Z=V(0,0,1)
    rows=[]; changed={}; routes={}; seats=[]; collar_rows=[]
    ledger=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'; pin(ledger)
    catalogue=ROOT/'hardware/manufacturing/one-batch-prototype-r51/nonfastener-catalog.json'; pin(catalogue)
    stock=json.loads(catalogue.read_text(encoding='utf-8'))['rows']
    assert any(r['manufacturer_part']=='23802' for r in stock)
    assert any(r['manufacturer_part']=='T0051402499' for r in stock)
    assert any('221-412' in str(r) for r in stock)
    def wire(name,r,od,tangent,kind,strip,leg):
        path,tube=r.shape(od,tangent); routes[name]=tube; changed[name]=tube
        path.exportBrep(str(OUT/(name+'_CENTERLINE.brep'))); tube.exportBrep(str(OUT/(name+'_DESIGN.brep')))
        row=dict(id=name,leg=leg,kind=kind,OD_mm=od,path_mm=path.Length,
                 start_mm=list(path.Vertexes[0].Point),end_mm=list(r.p),
                 radii_mm=r.radii,strip_allowance_mm=strip,trim_reserve_mm=10,
                 rough_blank_mm=math.ceil((path.Length+strip+10)/10)*10,
                 actual_cut_mm=None,physical_pass=False)
        if kind.startswith('MTA'):
            row['assumed_usable_factory_lead_mm']=100
            row['within_assumed_factory_length']=row['rough_blank_mm']<=100
        rows.append(row); return tube
    for leg,out_id,in_id in [('FL','W026','W041'),('FR','W037','W042'),('RL','W045','W044'),('RR','W053','W052')]:
        side=1 if leg.endswith('L') else -1; Y=V(0,side,0)
        mouth_x=-82.5 if leg.startswith('F') else 25.5
        cx=-18.5 if leg.startswith('F') else 90.5
        cy=side*87.5; cz=122.5; left=cx-17.5; right=cx+17.5
        changed[leg+'_MTA_body']=box([left,cy-8,cz-11,right,cy+8,cz+11])
        # Full output lead: retained straight at P-leg grip, turn then S-rise.
        r=Route([mouth_x,side*49.5,113.5]); r.line([mouth_x,side*67.5,113.5]); r.arc(Y,X,20)
        r.shift(X,Z*9,20); r.line([left,cy,cz])
        wire(out_id,r,5,Y,'MTA0100335_factory_4mm2',11,leg)
        # Integral saddle touches the solid outer Deck strip Y90..95.
        seat=[left-1,cy-10,108.8,right+1,cy+8,111.5]
        seats.append((leg,seat))
        # Two tie passages are on opposite sides of the actual body.
        for j,x in enumerate((cx-9,cx+9)):
            def span(y0,y1,z0,z1,x0=x-1.25,x1=x+1.25):
                ya,yb=sorted((side*y0,side*y1)); return [x0,ya,z0,x1,yb,z1]
            for k,b in enumerate([span(78.3,79.5,107.6,134.7),span(95.5,96.7,107.6,134.7),
                                   span(79.5,95.5,133.5,134.7),span(79.5,95.5,107.6,108.8),
                                   span(80,84,102.6,107.6,x-3,x+3)]):
                changed[leg+'_body_tie_'+str(j)+'_'+str(k)]=box(b)
        r=Route([right,cy,cz])
        if leg=='FL':
            r.line([50,cy,cz])
            wire(in_id+'_factory',r,5,X,'MTA0100335_factory_4mm2',11,leg)
            # Two mouths on SAME connector face are intentional, not a splice
            # through its back. Physical cage numbers are project labels.
            changed[leg+'_221412']=box([50,84.25,118.5,68.3,97.25,126.65])
            e=Route([-31.5,11,113.5]); e.line([-31.5,17,113.5]); e.shift(V(0,1,0),Z*22.5,25.2)
            e.line([-31.5,68.8,136]); e.arc(V(0,1,0),X,25.2)
            run=2*25.2*math.sin(math.acos(1-13.5/(2*25.2)))
            e.line([50-run,94,136]); e.shift(X,-Z*13.5,25.2)
            assert (e.p-V(50,94,122.5)).Length<1e-6
            wire(in_id+'_extension',e,4.2,V(0,1,0),'HELU23802_SIF4.00-R',14+11,leg)
            collar_rows.append(dict(leg=leg,kind='WAGO221-412',existing_quantity_id='splice:WAGO221-412',added_installed=1,
                end_recipe='4mm2 factory and HELU bare ends each in separate cage,11mm strip,no tin,no doubled cage',
                mouth_datums_mm=[[50,87.5,122.5],[50,94,122.5]],dimensions_source='selected commercial221412 envelope18.3x13x8.15; mouth centres project datums'))
        elif leg=='FR':
            r.line([right+6,cy,cz]); r.arc(X,-Y,20); r.line([25,-60,cz])
            wire(in_id+'_factory',r,5,X,'MTA0100335_factory_4mm2',11,leg)
            changed[leg+'_221412']=box([21.75,-60,118.5,34.75,-41.7,126.65])
            e=Route([-24,11,113.5]); e.line([-24,17,113.5]); e.shift(V(0,1,0),Z*9,25.2)
            e.line([-24,46.8,cz]); e.arc(V(0,1,0),X,25.2)
            e.line([100,72,cz]); e.arc(X,V(0,-1,0),25.2)
            e.line([125.2,-74.8,cz]); e.arc(V(0,-1,0),-X,25.2)
            e.line([56.7,-100,cz]); e.arc(-X,V(0,1,0),25.2); e.line([31.5,-60,cz])
            wire(in_id+'_extension',e,4.2,V(0,1,0),'HELU23802_SIF4.00-R',14+11,leg)
            collar_rows.append(dict(leg=leg,kind='WAGO221-412',existing_quantity_id='splice:WAGO221-412',added_installed=1,
                end_recipe='4mm2 factory and HELU bare ends each in separate cage,11mm strip,no tin,no doubled cage',
                mouth_datums_mm=[[25,-60,122.5],[31.5,-60,122.5]],dimensions_source='same selected221412 envelope rotated90deg; cage datums provisional'))
        else:
            # Rear supported lap joint, opposite incoming tangents. The 26mm
            # insulation envelope is on straight stock, NOT around a bend.
            r.line([right+6,cy,cz]); r.arc(X,-Y,21.2); r.line([135.2,side*33,cz])
            wire(in_id+'_factory',r,5,X,'MTA0100335_factory_4mm2',8,leg)
            source_y=-6.8 if leg=='RL' else 6.8
            e=Route([32,source_y,129]); e.line([38,source_y,129]); e.shift(X,-Z*6.5,25.2)
            e.line([110,source_y,cz]); e.arc(X,Y,25.2); e.line([135.2,side*47,cz])
            wire(in_id+'_extension',e,4.2,X,'HELU23802_SIF4.00-R',14+8,leg)
            sleeve=Part.makeCylinder(4.5,26,V(135.2,side*27,cz),Y)
            changed[leg+'_splice_insulation']=sleeve
            collar_rows.append(dict(leg=leg,kind='Supported_solder_lap',existing_solder='T0051402499',existing_shrink='Botland5375 assortment13mm',
                joint_centre_mm=[135.2,side*40,cz],strip_each_mm=8,outer_blank_mm=26,outer_overlap_each_mm=9,
                conservative_envelope_OD_mm=9,recipe='Dry-fit on unpowered removed Deck. Slide13mm sleeve first;8mm opposing bare copper lap, solder with existing Weller wire, inspect, shrink with9mm intact overlap both sides. Independent insulation grips both sides; no solder at WAGO ends.',
                assumptions='Lap/envelope/strip/thermal process are prototype design assumptions, not manufacturer joint qualification; delivery current/pull/temperature trial phase2'))
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,W5_complete=False,
        old_layouts='R2/R3/R4 rejected; do not repeat',holders=dict(axis='X',front_cx=-18.5,rear_cx=90.5,y_abs=87.5,z=122.5),
        assumptions=dict(MTA_mm=[35,16,22],MTA_OD_mm=5,MTA_radius_mm=20,MTA_usable_each_lead_mm=100,
            HELU23802_OD_mm=4.2,HELU_design_radius_mm=25.2,front_mouths=[[-31.5,11,113.5],[-24,11,113.5]],front_mouths_are_project_labels_not_manufacturer=True),
        routes=rows,joints=collar_rows,
        stock_contribution=dict(HELU23802_additional_blank_mm=sum(r['rough_blank_mm'] for r in rows if r['kind'].startswith('HELU')),
                               WAGO221412_extra_installed=2,solder_joints=2,shrink13mm_blank_mm=52,body_ties=8),
        assembly='Before power: Deck removed, fit four holders and two WAGO/joint mounts, prewire source WAGOs, then P-leg ends; each end one cage. Main holders fixed to Deck during bank+cover removal. Source/WAGO/splice grips, native cover and full disconnect still require fit below.',
        started_utc=started.isoformat()))
    print('COMPLETE_EIGHT_ROUTES_SAVED',flush=True)
    owners,extra,_=layout.current_owners(); pins.update(extra)
    owners.pop('R49Deck')
    owners.pop('hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep')
    for n in list(owners):
        if '/servo-fuse-bank-restraints-r2/' in n or '/servo-fuse-bank-restraints-fit-r2/' in n: del owners[n]
    for folder,pattern,prefix in [('hardware/cad/studies/servo-fuse-bank-clip-access-r1','*_WORLD.brep','Bank'),
        ('hardware/electronics/full-cat/servo-fuse-side-bank-r11','F_*_DESIGN.brep','R11'),
        ('hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4','release_0.0_W*_DESIGN.brep','InputR4'),
        ('hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r2','*_DESIGN.brep','RetainedGrip')]:
        for p in (ROOT/folder).glob(pattern): owners[prefix+'/'+p.stem]=load(p)
    basepath=ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/DeckParentFeedGrips.FCStd';pin(basepath)
    d=A.openDocument(str(basepath)); dest=CAD/'DeckMainHolders.FCStd'
    try:
        par=d.addObject('App::VarSet','MainHolderParameters');par.addProperty('App::PropertyLength','PadHeight');par.PadHeight=2.7
        previous=d.getObject('ParentFeedGripFinished'); before=previous.Shape.Volume
        for leg,b in seats:
            pad=d.addObject('Part::Box',leg+'MainPad');pad.Length=b[3]-b[0];pad.Width=b[4]-b[1];pad.Height=b[5]-b[2];pad.Placement.Base=V(*b[:3])
            pad.setExpression('Height','MainHolderParameters.PadHeight')
            f=d.addObject('Part::Fuse',leg+'MainSeat');f.Base=previous;f.Tool=pad;f.Refine=True;previous=f
            # Full tie travel through integral seat, not a strap intersecting Deck.
            for j,x in enumerate(((-18.5 if leg.startswith('F') else 90.5)-9,(-18.5 if leg.startswith('F') else 90.5)+9)):
                sgn=1 if leg.endswith('L') else -1
                for k,ya in enumerate((78.3,95.5)):
                    low,high=sorted((sgn*ya,sgn*(ya+1.2)))
                    tool=d.addObject('Part::Box',leg+'TieSlot'+str(j)+str(k));tool.Length=2.9;tool.Width=1.6;tool.Height=8
                    tool.Placement.Base=V(x-1.45,low-.2,104)
                    f=d.addObject('Part::Cut',leg+'TiePass'+str(j)+str(k));f.Base=previous;f.Tool=tool;f.Refine=True;previous=f
                low,high=sorted((sgn*79.5,sgn*95.5))
                tool=d.addObject('Part::Box',leg+'UnderTie'+str(j));tool.Length=2.9;tool.Width=high-low;tool.Height=1.7
                tool.Placement.Base=V(x-1.45,low,107.4)
                f=d.addObject('Part::Cut',leg+'UnderTiePass'+str(j));f.Base=previous;f.Tool=tool;f.Refine=True;previous=f
        previous.Label='Four integral main fuse saddles (UNSELECTED)';d.recompute()
        deck=previous.Shape.copy();assert deck.isValid() and len(deck.Solids)==1
        volume=deck.Volume;par.PadHeight=2.9;d.recompute();probe=previous.Shape.Volume;assert probe>volume
        par.PadHeight=2.7;d.recompute();assert abs(previous.Shape.Volume-volume)<1e-5
        d.saveAs(str(dest));deck.exportBrep(str(CAD/'Deck_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=deck,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        bb=mesh.BoundBox;assert max(bb.XLength+10,bb.YLength+10)<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'DeckMainHolders_UNSELECTED.stl'))
        final=previous.Name
    finally: A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-main-holder-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try: re.recompute();assert abs(re.getObject(final).Shape.Volume-volume)<1e-5
        finally: A.closeDocument(re.Name)
    owners['CandidateDeck']=deck
    owners['RetainedCoverR4']=load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r4/Cover_WORLD.brep')
    hits=[]; errors=[]; pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox): return
        pairs+=1
        try:
            common=s.common(t)
            if common.Volume>1e-5:
                row=dict(part=n,owner=m,hit_mm3=common.Volume,bounds_mm=bounds(common));hits.append(row)
                common.exportBrep(str(OUT/('HIT_'+str(len(hits))+'.brep')))
        except Exception as exc: errors.append(dict(part=n,owner=m,error=str(exc)))
    for n,s in changed.items():
        print('SHARED_FIT '+n,flush=True);s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
        for m,t in owners.items():check(n,s,m,t)
    # Expected splice/WAGO mating only. No waiver for body collisions.
    intended=set()
    for leg in ('FL','FR'):
        intended.add(frozenset((leg+'_221412',('W041' if leg=='FL' else 'W042')+'_factory')))
        intended.add(frozenset((leg+'_221412',('W041' if leg=='FL' else 'W042')+'_extension')))
    for leg,w in [('RL','W044'),('RR','W052')]:
        for n in (w+'_factory',w+'_extension'):intended.add(frozenset((leg+'_splice_insulation',n)))
        intended.add(frozenset((w+'_factory',w+'_extension')))
    items=list(changed.items())
    for i,(n,s) in enumerate(items):
        for m,t in items[i+1:]:
            if frozenset((n,m)) not in intended: check(n,s,m,t)
    ended=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='COMPLETE_ROUTE_LAYOUT_CONFLICTS' if hits or errors else 'COMPLETE_ROUTE_LAYOUT_STATIC_CLEAR_MORE_MOUNTS_SERVICE_REQUIRED',
        selected=False,physical_pass=False,W5_complete=False,routes=rows,joints=collar_rows,
        native=dict(file=dest.relative_to(ROOT).as_posix(),final=final,single_solid=True,closed_STL=True,relocated_reopen=True,
                    pad_height_probe_mm=[2.7,2.9,2.7],volumes_mm3=[volume,probe,volume],strict_BOP_report=deck.check(True)),
        hits=hits,errors=errors,pairs=pairs,source_sha256=pins,script_sha256=sha(Path(__file__)),
        open=['Source joints/WAGO native mounts and insulation-grip support not yet qualified.',
              'Cover alteration only after inspecting these complete route witnesses.',
              'Full bank disconnect/removal, stock selection and E3 still open.'],
        started_utc=started.isoformat(),finished_utc=ended.isoformat(),worker_wall_seconds=(ended-started).total_seconds()))
    print(json.dumps(dict(hits=len(hits),errors=len(errors),pairs=pairs)),flush=True)


if __name__=='__main__': main()

"""Two curved source hoods and four integral mounts in the received Cover.

Received R2 had two Cover/skirt contacts. Raise only skirt lower edges
from181 to185.5, preserving mounts, source paths and analytic roof. Covers above
the old185mm roof only; lower S1 terminals remain their separate interface.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-source-roof-native-r1'
PARENT=ROOT/'hardware/cad/studies/w5-source-grips-native-r2/SourceCarrierInsulationGrips.FCStd'
MOUNTS=[(-72,5),(-72,-42),(44.5,5),(44.5,-42)]


def main(revision='r3'):
    global OUT,CAD
    assert revision == 'r3'
    OUT=ROOT/f'hardware/electronics/full-cat/w5-source-roof-native-{revision}'
    CAD=ROOT/f'hardware/cad/studies/w5-source-roof-native-{revision}'
    import FreeCAD as A,Part,MeshPart
    from w5_source_grips_native_r1 import current_owners
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    received=ROOT/'hardware/electronics/full-cat/w5-source-grips-native-r2/checks.json'
    r=json.loads(received.read_text(encoding='utf-8'))
    assert not r['hits'] and not r['errors'] and r['closed_STL'] and r['relocated_reopen']
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    cart=ROOT/'hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json'
    c=json.loads(cart.read_text(encoding='utf-8'))
    rows=c if isinstance(c,list) else next(v for v in c.values() if isinstance(v,list) and any(isinstance(x,dict) and x.get('supplier_sku')=='SKL000625' for x in v))
    bolt_row=next(x for x in rows if x.get('supplier_sku')=='SKL000625')
    assert bolt_row['dimensions_mm']['L']==16 and bolt_row['dimensions_mm']['b']==16
    parent=A.openDocument(str(PARENT));d=A.newDocument('TwoSourceProtectiveHoods')
    target=CAD/'SourceProtectiveHoods.FCStd';d.saveAs(str(target))
    p=d.addObject('App::VarSet','RoofParameters');p.addProperty('App::PropertyFloat','OuterScale');p.OuterScale=1.12
    p.addProperty('App::PropertyLength','RoofWall');p.RoofWall=3
    p.addProperty('App::PropertyLength','SeamGap');p.SeamGap=.6
    def box(name,b):
        q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2]
        q.Placement.Base=A.Vector(*b[:3]);return q
    def cylinder(name,r,h,point):
        q=d.addObject('Part::Cylinder',name);q.Radius=r;q.Height=h;q.Placement.Base=A.Vector(*point);return q
    def compound(name,objects):
        q=d.addObject('Part::Compound',name);q.Links=objects;return q
    def union(name,objects):
        q=d.addObject('Part::MultiFuse',name);q.Shapes=objects;q.Refine=False;return q
    def intersect(name,a,b):
        q=d.addObject('Part::Common',name);q.Base=a;q.Tool=b;q.Refine=False;return q
    def cut(name,a,b):
        q=d.addObject('Part::Cut',name);q.Base=a;q.Tool=b;q.Refine=False;return q
    if revision=='r1':
        outer=d.addObject('Part::Ellipsoid','CurvedOuterRoof')
        inner=d.addObject('Part::Ellipsoid','CurvedInnerRoof')
        for q in (outer,inner):q.Placement.Base=A.Vector(30,58,205)
        inner.Radius1=20;inner.Radius2=250;inner.Radius3=130
        for name,value in [('Radius1',20),('Radius2',250),('Radius3',130)]:outer.setExpression(name,f'{value} mm * RoofParameters.OuterScale')
    else:
        # Analytic cylinder replaces the rejected native ellipsoid C0 surface.
        inner=cylinder('CurvedInnerRoof',500,340,[-140,45,-277])
        outer=cylinder('CurvedOuterRoof',503,340,[-140,45,-277])
        for q in (outer,inner):q.Placement.Rotation=A.Rotation(A.Vector(0,0,1),A.Vector(1,0,0))
        outer.setExpression('Radius','500 mm + RoofParameters.RoofWall')
    shell=cut('CurvedRoofShell',outer,inner)
    top=intersect('UpperCurvedSkin',shell,box('RoofSkinWindow',[-134,-50,207,194,140,240]))
    # The edge skirts are vertical2.4mm bands clipped by the outside curve.
    # Unlike the raised skin alone, they shield upper loops from side knocks.
    skirts=[intersect('CurvedSkirt'+str(i),outer,box('SkirtExtent'+str(i),b)) for i,b in enumerate([
        [-134,-50,185.5,-131.6,140,240],[191.6,-50,185.5,194,140,240],
        [-134,-50,185.5,194,-47.6,240],[-134,137.6,185.5,194,140,240]])]
    guards=union('ContinuousSourceRoof',[top,*skirts])
    left_window=box('WestPrintWindow',[-134,-50,180,25,140,240])
    right_window=box('EastPrintWindow',[25.6,-50,180,194,140,240])
    right_window.setExpression('Placement.Base.x','25 mm + RoofParameters.SeamGap')
    right_window.setExpression('Length','169 mm - RoofParameters.SeamGap')
    raw_halves=[intersect('WestCurvedHood',guards,left_window),intersect('EastCurvedHood',guards,right_window)]
    pads=[[],[]];holes=[[],[]];mount_data=[];posts=[];post_tools=[]
    cover_link=d.addObject('App::Link','ReceivedCover');cover_link.setLink(parent.SourceGripCoverFinished)
    cover_link.LinkPlacement=parent.SourceGripCoverFinished.Placement
    for i,(x,y) in enumerate(MOUNTS):
        if revision=='r1':
            inner_z=205+20*math.sqrt(1-((x-30)/250)**2-((y-58)/130)**2)
            outer_z=205+22.4*math.sqrt(1-((x-30)/280)**2-((y-58)/145.6)**2)
        else:
            inner_z=-277+math.sqrt(500**2-(y-45)**2)
            outer_z=-277+math.sqrt(503**2-(y-45)**2)
        plane=math.floor(inner_z)-1.5;pad_top=math.ceil(outer_z)+1.5
        #16mm bolt covers both washers, roof pad and the full2.4mm nut.
        under_head=pad_top+.5;tip=under_head-16
        assert tip<=plane-3.4 and tip>185
        group=0 if i<2 else 1
        pads[group].append(box('FlatHoodMount'+str(i),[x-5,y-5,plane,x+5,y+5,pad_top]))
        holes[group].append(cylinder('HoodBoltBore'+str(i),1.7,30,[x,y,plane-1]))
        root=184 if revision=='r1' or i>=2 else 174
        posts.append(box('CoverPost'+str(i),[x-5,y-5,root,x+5,y+5,plane]))
        post_tools.append(cylinder('PostScrewBore'+str(i),1.7,plane-185+1,[x,y,185.5]))
        post_tools.append(cylinder('LowerWasherSeat'+str(i),3.6,.7,[x,y,plane-.6]))
        nut=d.addObject('Part::Prism','M3NutPocket'+str(i));nut.Polygon=6;nut.Circumradius=3.4;nut.Height=2.8
        nut.Placement=A.Placement(A.Vector(x,y,plane-3.1),A.Rotation(A.Vector(0,0,1),30));post_tools.append(nut)
        post_tools.append(box('SideNutEntry'+str(i),[x-3,y,plane-3.1,x+3,y+5.2,plane-.3]))
        mount_data.append(dict(x=x,y=y,bearing_z=plane,pad_top_z=pad_top,bolt_tip_z=tip,
            nut_z=[plane-2.9,plane-.5],root_z=root,bolt_sku='SKL000625'))
    new_posts=cut('FourBoredCoverPosts',union('FourPostBlanks',posts),compound('PostHardwareClearances',post_tools))
    cover=union('SourceRoofCoverFinished',[cover_link,new_posts])
    halves=[cut(name,union(name+'WithMounts',[raw,*pad]),compound(name+'Bores',bore))
            for name,raw,pad,bore in zip(('WestHoodFinished','EastHoodFinished'),raw_halves,pads,holes)]
    d.save();print('SOURCE_ROOF_NATIVE_RECOMPUTE',flush=True);d.recompute();d.save()
    assert all(q.Shape.isValid() and len(q.Shape.Solids)==1 and not q.Shape.check(True) for q in [cover,*halves])
    for q in posts:assert q.Shape.common(cover_link.Shape).Volume>1e-5
    assert cover_link.Shape.cut(cover.Shape).Volume<1e-5
    nominal=[q.Shape.Volume for q in [cover,*halves]]
    if revision=='r1':p.OuterScale=1.13
    else:p.RoofWall=3.2
    d.recompute();assert all(q.Shape.Volume>v for q,v in zip(halves,nominal[1:]))
    p.OuterScale=1.12;p.RoofWall=3;d.recompute();assert all(abs(q.Shape.Volume-v)<1e-5 for q,v in zip([cover,*halves],nominal));d.save()
    owners,pins=current_owners(A,Part)
    owners.pop('SourceCover')
    carrier_path=ROOT/'hardware/cad/studies/w5-source-grips-native-r2/Carrier_WORLD.brep'
    owners['SourceCarrier']=Part.read(str(carrier_path));pins.append(carrier_path)
    for wire in ('W064','W065','W067','W068'):
        q=ROOT/f'hardware/electronics/full-cat/w5-source-grips-native-r2/{wire}_T18I_WORLD.brep'
        owners[wire+'_grip_band']=Part.read(str(q));pins.append(q)
    added=cover.Shape.cut(cover_link.Shape);hardware={}
    for i,m in enumerate(mount_data):
        x,y,plane,top,tip=m['x'],m['y'],m['bearing_z'],m['pad_top_z'],m['bolt_tip_z']
        hardware['Bolt'+str(i)]=Part.makeCompound([Part.makeCylinder(1.5,16,A.Vector(x,y,tip)),Part.makeCylinder(2.75,3,A.Vector(x,y,top+.5))])
        hardware['Washers'+str(i)]=Part.makeCompound([Part.makeCylinder(3.5,.5,A.Vector(x,y,z)).cut(Part.makeCylinder(1.6,.5,A.Vector(x,y,z))) for z in (plane-.5,top)])
        vs=[A.Vector(x+3.175*math.cos(math.pi/6+k*math.pi/3),y+3.175*math.sin(math.pi/6+k*math.pi/3),plane-2.9) for k in range(6)]
        hardware['Nut'+str(i)]=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,2.4)).cut(Part.makeCylinder(1.5,2.4,A.Vector(x,y,plane-2.9)))
    hits=[];errors=[];pairs=0
    def check(label,s,key,t):
        nonlocal pairs
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    overlap=a.common(b)
                    if overlap.Volume>1e-5:
                        bb=overlap.BoundBox;hits.append(dict(part=label,owner=key,mm3=overlap.Volume,bounds_mm=[getattr(bb,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc:errors.append(dict(part=label,owner=key,error=str(exc)))
    moving={name:q.Shape.copy() for name,q in zip(('WestHood','EastHood'),halves)}
    for label,s in {'NewCoverPosts':added,**moving,**hardware}.items():
        for key,t in owners.items():check(label,s,key,t)
    for label,s in moving.items():check(label,s,'FinishedCover',cover.Shape)
    for label,s in hardware.items():
        check(label,s,'FinishedCover',cover.Shape)
        for key,t in moving.items():check(label,s,key,t)
    check('WestHood',moving['WestHood'],'EastHood',moving['EastHood'])
    print('SOURCE_ROOF_CONTACTS',pairs,len(hits),len(errors),flush=True)
    for name,s in {'AddedPosts':added,**moving,**hardware}.items():s.exportBrep(str(OUT/(name+'_WORLD.brep')))
    dims={};exports={};reopened=False
    if not hits and not errors:
        for tag,q in zip(('Cover','WestHood','EastHood'),[cover,*halves]):
            shape=q.Shape.copy();shape.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1;mesh.rotate(math.pi,0,0)
            bb=mesh.BoundBox;dims[tag]=[bb.XLength,bb.YLength,bb.ZLength]
            assert bb.XLength+10<=256 and bb.YLength+10<=256 and bb.ZLength<=256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED_x1.stl')))
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    for name in list(A.listDocuments()):A.closeDocument(name)
    if not hits and not errors:
        with tempfile.TemporaryDirectory(prefix='robot-cat-source-roof-') as td:
            tmp=Path(td)
            for q in [target,*deps]:
                dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
            rd=A.openDocument(str(tmp/target.relative_to(ROOT)));rd.recompute()
            for name,v in zip(('SourceRoofCoverFinished','WestHoodFinished','EastHoodFinished'),nominal):
                s=rd.getObject(name).Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-v)<1e-5
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values());reopened=True
    end=datetime.now(timezone.utc);pins += [Path(__file__),received,PARENT,cart,*deps,ROOT/'tools/electronics/w5_source_grips_native_r1.py']
    save(OUT/'checks.json',dict(status='SOURCE_ROOF_REJECTED' if hits or errors else 'SOURCE_ROOF_NATIVE_STATIC_COMPLETE_SERVICE_OPEN',
        pairs=pairs,hits=hits,errors=errors,solids_per_part=1,strict_BOP_errors=0,
        dimensions_mm=dims,closed_STLs=bool(dims),parameter_recompute=True,relocated_reopen=reopened,
        source_routes_unchanged=True,original_Cover_material_preserved=True,
        installed_counts=dict(replacement_Cover=1,new_hoods=2,M3x16=4,M3nuts=4,M3washers=8),
        mounts=mount_data,roof_geometry=('ellipsoid' if revision=='r1' else 'analytic cylinder X-axis, Y45 Z-277, R500/503'),
        nominal_skirt_wall_mm=2.4,radial_roof_wall_mm=(2.4 if revision=='r1' else 3),
        source_lower_terminal_guard_claimed=False,full_robot_or_motion_pass=False,
        style='Curved graphite protective top; unchanged E6 head/ears/P0. Wider source canopy is intentional, split into two256cube prints.',
        PETG_orientation='Open interior upward after180degX; supports under curved exterior and accessible pads/skirt; actual nozzle/layers/profile unset for phase2.',
        physical_tests=['PETG bridge/pad/post bending and clamp creep; support removal; insulation clearance, heat and delivered hardware.'],
        assembly=['Insert four M3nuts/lower washers into side-open native posts before fitting hoods.',
            'Fit the west/east hood separately with two M3x16 and upper washers each; supplier2.5mm key nominal, actual tool access still to qualify.'],
        complete_staged_assembly_and_removal=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in dict.fromkeys(pins)},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in [*OUT.glob('*.brep'),*CAD.glob('*.FCStd'),*CAD.glob('*.brep'),*CAD.glob('*.stl')]},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('SOURCE_ROOF_RESULT',len(hits),dims,flush=True)


if __name__=='__main__':main()



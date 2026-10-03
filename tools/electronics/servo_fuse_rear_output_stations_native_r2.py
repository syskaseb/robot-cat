"""R1 feedback: use actual raised Deck/Bank anchors, not feet into Deck holes.

Couple both trays, open strap channels and wire passages with their native
parents. RL is supported by existing FL roof, RR by the removable right bank.
Retain all wire paths and account for release before lifting the bank.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rear_output_stations_native_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-rear-output-stations-native-r1','servo-fuse-rear-output-stations-native-r2')
code=code.replace("    pins={};V=A.Vector", "    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rear_output_stations_native_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_rear_output_stations_native_r1.py')\n    pins['hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r1/preflight.json']=sha(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r1/preflight.json')")
code=code.replace("        hb=[x-2.25,ya-4.8,zt-3.5,x+2.25,ya,zt]", "        hb=([x-2.25,yb,zt-3.5,x+2.25,yb+4.8,zt] if name.startswith('RL') else [x-2.25,ya-4.8,zt-3.5,x+2.25,ya,zt])")
code=code.replace("        ya=y-6.8;yb=y+6.8;end=-27 if leg=='RL' else -26", "        ya=y-5.7 if leg=='RL' else y-6.8;yb=y+6.8;end=-27 if leg=='RL' else -26")
a=code.index('        # Two complete footprints;');b=code.index('        fx0,fx1=',a)
code=code[:a]+'''        # R1 had four feet completely over holes. The two RL tabs embed
        # into the existing raised FL roof; RR anchors into real bank stock.
        anchor_specs=([[-68,85,117.85,-64,89,118.05],[-53,85,117.85,-49,89,118.05]] if leg=='RL'
            else [[-64,-93,109.35,-60,-90,111.75],[-53,-93,109.35,-49,-90,111.75]])
        owner='CandidateDeck' if leg=='RL' else 'Bank/RightClipAccessFinished_WORLD'
        for k,fb in enumerate(anchor_specs):
            fs=stock(leg+'Anchor'+str(k),fb);actual=fs.common(owners[owner]).Volume
            expected=fs.Volume
            feet.append(dict(leg=leg,index=k,parent=owner,bounds_mm=fb,expected_embed_mm3=expected,actual_embed_mm3=actual))
            if abs(actual-expected)>1e-4:mount_failures.append(feet[-1])
''' +code[b:]
# Real four factory/extension routes protect curved sections under upper seats,
# not just the straight cylinders at the mouths.
a=code.index('    toolshapes=');b=code.index('    hits=[];',a)
code=code[:a]+'''    # Native full-route Sweeps will share this same geometry and radius.
    full_paths=[];wiretools=[]
    for ident in ('W045','W053'):
        for role,od in [('factory',5),('extension',4.2)]:
            raw=load(routefolder/(ident+'_'+role+'_CENTERLINE.brep'));path=Part.Wire(raw.Edges)
            edge=path.Edges[0];normal=edge.tangentAt(edge.FirstParameter)
            profile=Part.Wire([Part.makeCircle(od/2+.2,path.Vertexes[0].Point,normal)])
            wiretools.append(path.makePipeShell([profile],True,False))
            full_paths.append((ident+'_'+role,od,path,normal))
    toolshapes=[Part.makeCylinder(od/2+.2,length,V(*p),V(1,0,0)) for _,z,od,p,length in grooves]+[box(b) for _,b in slots]+wiretools
    strap_slots=[]
    for name,s in changed.items():
        bb=bounds(s)
        # Clearance from complete real strap bounds, not an ignored clash.
        strap_slots.append((name+'Pass',[bb[0]-.15,bb[1]-.15,bb[2]-.15,bb[3]+.15,bb[4]+.15,bb[5]+.15]))
    all_tools=toolshapes+[box(b) for _,b in strap_slots]
    united_tools=all_tools[0].multiFuse(all_tools[1:])
    fixtures={}
    for leg in ('RL','RR'):
        stock_shapes=[box(b) for name,b in stocks if name.startswith(leg)]
        fixtures[leg]=stock_shapes[0].multiFuse(stock_shapes[1:]).cut(united_tools)
        changed[leg+'Fixture']=fixtures[leg]
    candidate={}
    for tag,key,leg in [('Deck','CandidateDeck','RL'),('BankRight','Bank/RightClipAccessFinished_WORLD','RR')]:
        candidate[tag]=owners[key].fuse(fixtures[leg]).cut(united_tools)
    # Cover channels open at its negativeY side, not closed traps for straps.
    cover_tools=[]
    for name,b in strap_slots:
        if name.startswith('RR'):
            q=list(b);q[1]=min(q[1],-111);cover_tools.append((name+'OpenSide',q))
    candidate['Cover']=owners['ModifiableCover'].cut(box(cover_tools[0][1]).multiFuse([box(b) for _,b in cover_tools[1:]]))
    owners['CandidateDeck']=candidate['Deck'];owners['Bank/RightClipAccessFinished_WORLD']=candidate['BankRight'];owners['ModifiableCover']=candidate['Cover']
''' +code[b:]
code=code.replace("            if name=='CoupledRearFixture' and owner=='CandidateDeck':continue", "            if (name=='RLFixture' and owner=='CandidateDeck') or (name=='RRFixture' and owner=='Bank/RightClipAccessFinished_WORLD'):continue")
a=code.index('    # Every strap must');b=code.index('    pre=dict(',a)
code=code[:a]+'''    for name,s in changed.items():
        if not name.endswith('Fixture'):
            for leg,fixture in fixtures.items():check(name,s,leg+'Fixture',fixture)
    strict=[]
    for tag,s in candidate.items():
        strict.extend((tag,str(e)) for e in (s.check(True) or []))
        if not s.isValid() or len(s.Solids)!=1:strict.append((tag,'Not one valid solid'))
''' +code[b:]
code=code.replace("        stocks=stocks,grooves=grooves,slots=slots,strict_BOP=[str(x) for x in strict],", "        stocks=stocks,grooves=grooves,slots=slots,strap_slots=strap_slots,cover_tools=cover_tools,strict_BOP=[str(x) for x in strict],")
a=code.index('    gp=native/');b=code.index("if __name__=='__main__':",a)
code=code[:a]+'''    exports=[]
    for tag,source,leg in [('Deck','DeckRearOutputPassages.FCStd','RL'),('BankRight','BankRightRearOutputPassages.FCStd','RR'),('Cover','CoverRearOutputPassages.FCStd',None)]:
        gp=native/source;pin(gp);d=A.openDocument(str(gp));dest=CAD/(tag+'RearOutputStations.FCStd')
        try:
            p=d.addObject('App::VarSet','RearGripParameters');p.addProperty('App::PropertyLength','Clearance');p.Clearance=.2
            objs=[];ntools=[]
            for name,b in stocks:
                if leg and name.startswith(leg):
                    o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);objs.append(o)
            if leg:
                for name,z,od,pt,length in grooves:
                    o=d.addObject('Part::Cylinder',name+'Groove');o.Height=length
                    o.Placement=A.Placement(V(*pt),A.Rotation(V(0,0,1),V(1,0,0)))
                    o.setExpression('Radius',f'{od/2} mm + RearGripParameters.Clearance');ntools.append(o)
                for name,od,path,normal in full_paths:
                    route=d.addObject('Part::Feature',name+'Path');route.Shape=path
                    profile=d.addObject('Part::Circle',name+'Profile');profile.setExpression('Radius',f'{od/2} mm + RearGripParameters.Clearance')
                    profile.Placement=A.Placement(path.Vertexes[0].Point,A.Rotation(V(0,0,1),normal))
                    sweep=d.addObject('Part::Sweep',name+'WirePassage');sweep.Sections=[profile];sweep.Spine=(route,[]);sweep.Solid=True;sweep.Frenet=False;ntools.append(sweep)
            for name,b in (slots+strap_slots if leg else cover_tools):
                o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);ntools.append(o)
            parent=d.RearOutputPassagesFinished
            if leg:
                u=d.addObject('Part::MultiFuse','RearGripStock');u.Shapes=objs;u.Refine=False
                united=d.addObject('Part::MultiFuse','RearGripsAndParent');united.Shapes=[parent,u];united.Refine=False
            else:united=parent
            t=d.addObject('Part::MultiFuse','RearGripTools');t.Shapes=ntools;t.Refine=False
            f=d.addObject('Part::Cut','RearOutputStationsFinished');f.Base=united;f.Tool=t;f.Refine=False
            d.saveAs(str(dest));print('REAR_OUTPUT_STATIONS_RECOMPUTE',tag,flush=True);d.recompute()
            s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            volume=s.Volume
            if leg:
                p.Clearance=.3;d.recompute();probe=f.Shape.Volume;assert abs(probe-volume)>1e-4
                p.Clearance=.2;d.recompute();assert abs(f.Shape.Volume-volume)<1e-5
            else:probe=volume
            s=f.Shape.copy();d.saveAs(str(dest));s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
        finally:A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-rear-output-stations-') as td:
            q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
            try:re.recompute();assert abs(re.RearOutputStationsFinished.Shape.Volume-volume)<1e-5
            finally:A.closeDocument(re.Name)
        exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final='RearOutputStationsFinished',single_solid=True,strict_BOP_errors=0,
            closed_STL=True,relocated_reopen=True,parameter_mm=[.2,.3,.2] if leg else None,volumes_mm3=[volume,probe,volume],dimensions_mm=dims))
        print('REAR_OUTPUT_STATIONS_NATIVE_SAVED',tag,flush=True)
    save(OUT/'checks.json',dict(pre,status='REAR_OUTPUT_NATIVE_STATIONS_STATIC_COMPLETE_SERVICE_OPEN',exports=exports,
        stock_delta=dict(additional_T18I=6,additional_prints=0,new_fasteners=0,replacements=['Deck','BankRight','Cover']),
        recipe='RL fixed to raised Deck platform; RR integral with removable bank. Release both RR cages/three RR straps before bank lift. Shared removal and lever qualification still OPEN.',
        open=['Genuine lever action and full shared assembly/removal remain OPEN.','Phase2 housing/lead fit, PETG bending/creep and strap insertion/pull; no physical PASS.'],
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
''' +code[b:]
exec(compile(code,str(Path(__file__).resolve()),'exec'))

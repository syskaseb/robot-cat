"""Four editable loom frames, integral Deck pads and one passive hood passage.

Use the received whole mounting blueprint. Do not run before that receipt;
neither fixed geometry nor exports qualify moving looms or whole W1/W5.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, shutil, tempfile
from servo_fuse_inputs_r1 import sha, save
import w5_loom_mount_receive as R

ROOT=R.ROOT; OUT=R.M.BASE/'w5-loom-fixed-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-loom-fixed-native-r1'


def main():
    import FreeCAD as A, Part, MeshPart
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    receipt=R.OUT/'checks.json'; proof=json.loads(receipt.read_text(encoding='utf-8'))
    assert proof['all_static_material_pairs_clear'] and not proof['hits'] and not proof['errors']
    for rel, digest in {**proof['source_sha256'],**proof['files']}.items():assert sha(ROOT/rel)==digest,rel
    bpp=R.OUT/'native-blueprint.json';bp=json.loads(bpp.read_text(encoding='utf-8'))
    oldbp=R.M.PRIOR/'native-blueprint.json';original=json.loads(oldbp.read_text(encoding='utf-8'))
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    state=dict(status='FIXED_LOOM_NATIVE_PENDING',selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
               started_utc=start.isoformat())
    def progress(stage,**kw):
        state.update(stage=stage,updated_utc=datetime.now(timezone.utc).isoformat(),**kw);save(OUT/'progress.json',state)
        print('FIXED_LOOM_NATIVE',stage,flush=True)
    parents={}
    def source(path,name):
        if path not in parents:parents[path]=A.openDocument(str(path))
        obj=parents[path].getObject(name);assert obj is not None,(path,name)
        assert obj.Shape.isValid(),name
        return obj
    source_deck=source(ROOT/'hardware/cad/studies/w5-central-retention-native-r1/WholeHarnessCentralRetention.FCStd','CentralRetentionDeckFinished')
    source_hood=source(ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1/WholeHarnessPassages.FCStd','SourceEastHoodHarnessFinished')
    d=A.newDocument('WholeHarnessFixedLoomFrames');target=CAD/'WholeHarnessFixedLoomFrames.FCStd';d.saveAs(str(target))
    param=d.addObject('App::VarSet','LoomParameters');param.addProperty('App::PropertyLength','HoleClearance');param.HoleClearance=.2
    param.addProperty('App::PropertyString','Readiness');param.Readiness='Fixed geometry candidate; shared removal/moving looms/load/stock open'
    def box(name,b):
        o=d.addObject('Part::Box',name);o.Length,o.Width,o.Height=[b[i+3]-b[i] for i in range(3)];o.Placement.Base=A.Vector(*b[:3]);return o
    def cylinder(name,x,y,z,r,h,expression=None):
        o=d.addObject('Part::Cylinder',name);o.Radius=r;o.Height=h;o.Placement.Base=A.Vector(x,y,z)
        if expression:o.setExpression('Radius',expression)
        return o
    def fuse(name,items):
        o=d.addObject('Part::MultiFuse',name);o.Shapes=items;o.Refine=False;return o
    def compound(name,items):
        o=d.addObject('Part::Compound',name);o.Links=items;return o
    def cut(name,base,tool):
        o=d.addObject('Part::Cut',name);o.Base=base;o.Tool=tool;o.Refine=False;return o
    def half_ring(name,center,ri,ro,z,h,halfbox):
        x,y=center;outer=cylinder(name+'Outer',x,y,z,ro,h)
        inner=cylinder(name+'Inner',x,y,z-.1,ri,h+.2)
        ann=cut(name+'Ring',outer,inner);half=box(name+'HalfPlane',halfbox)
        o=d.addObject('Part::Common',name);o.Base=ann;o.Tool=half;o.Refine=False;return o
    def link(name,obj):
        o=d.addObject('App::Link',name);o.setLink(obj);o.LinkPlacement=obj.Placement;return o
    def pocket(name,x,y):
        o=d.addObject('Part::Prism',name);o.Polygon=6;o.Circumradius=5.9/math.sqrt(3);o.Height=23.2
        o.Placement.Base=A.Vector(x,y,106.3)
        o.setExpression('Circumradius','(5.5 mm + 2 * LoomParameters.HoleClearance) / sqrt(3)');return o
    finals={};pads=[];decktools=[]
    channels={r['loom']:r for r in bp['correction_channels']}
    relief=original['coupled_correction']['relief_specs']
    for leg,g in bp['groups'].items():
        roots=[box(leg+name,b) for name,b in g['raw_boxes'].items()];cuts=[]
        for groove in g['grooves']:
            x,y,z=groove['origin_mm'];n=groove['name']
            roots.append(cylinder(n+'Saddle',x,y,z,groove['outer_radius_mm'],groove['height_mm']))
            cuts.extend([cylinder(n+'CableOpening',x,y,76,groove['inner_radius_mm'],18),box(n+'SideEntry',groove['opening_box_mm'])])
        for row in g['tie_slot_and_belt_recipes']:
            n=row['loom'];x,y,_=row['axis_mm']
            cuts.extend(box(n+'TieCorner'+str(i),b) for i,b in enumerate(row['slot_boxes_mm']))
            c=row['back_channel'];ro=c['outer_radius_mm'];back=1 if leg.startswith('F') else -1
            hb=[x if back>0 else x-ro-.1,y-ro-.1,c['z_mm']-.1,
                x+ro+.1 if back>0 else x,y+ro+.1,c['z_mm']+c['height_mm']+.1]
            cuts.append(half_ring(n+'BackTieChannel',[x,y],c['inner_radius_mm'],ro,c['z_mm'],c['height_mm'],hb))
            q=channels[n];c=q['front_channel']
            cuts.append(half_ring(n+'FrontTieChannel',c['center_xy_mm'],c['inner_radius_mm'],c['outer_radius_mm'],c['z_mm'],c['height_mm'],c['half_box_mm']))
            cuts.append(box(n+'LockingHeadPassage',q['head_slot_mm']))
        cuts.extend(box(leg+'FrameRelief'+str(i),r['bounds_mm']) for i,r in enumerate(relief.get(leg+'FixedFrame',[])))
        for i,(x,y) in enumerate(g['proper_axes_xy_mm']):
            cuts.append(cylinder(leg+'FrameBore'+str(i),x,y,94,1.7,18,'1.5 mm + LoomParameters.HoleClearance'))
            decktools.extend([cylinder(leg+'DeckBore'+str(i),x,y,94,1.7,18,'1.5 mm + LoomParameters.HoleClearance'),pocket(leg+'CaptivePocket'+str(i),x,y)])
        finals[leg+'FixedFrame']=cut(leg+'FixedFrameFinished',fuse(leg+'FrameBlank',roots),compound(leg+'FrameTools',cuts))
        pad=box(leg+'LandingBlank',g['landing_box_mm'])
        local=[box(leg+'LandingRelief'+str(i),r['bounds_mm']) for i,r in enumerate(relief.get(leg+'DeckLanding',[]))]
        if local:pad=cut(leg+'RelievedLanding',pad,compound(leg+'LandingTools',local))
        pads.append(pad)
    deckblank=fuse('DeckAndIntegralLandings',[link('ReceivedCentralDeck',source_deck),*pads])
    finals['CompleteDeck']=cut('FixedLoomDeckFinished',deckblank,compound('WholeDeckMountingTools',decktools))
    finals['SourceEastHood']=cut('FixedLoomEastHoodFinished',link('ReceivedEastHood',source_hood),box('RLFrameHoodPassage',original['coupled_correction']['hood_tool_box_mm']))
    d.save();progress('editable_tree_saved',objects=len(d.Objects),separate_new_frames=4)
    d.recompute()
    expected=dict(zip(bp['current_roles'],Part.read(str(ROOT/bp['geometry'])).childShapes()))
    expected['SourceEastHood']=Part.read(str(R.M.BASE/'w5-loom-common-layout-r3/EastHood_RL_FRAME_PASSAGE_UNSELECTED_WORLD.brep'))
    nominal={};dims={}
    for name,obj in finals.items():
        s=obj.Shape;assert s.isValid() and len(s.Solids)==1,(name,len(s.Solids))
        assert not (s.check(True) or []),name
        difference=s.cut(expected[name]).Volume+expected[name].cut(s).Volume
        assert difference<max(1e-5,s.Volume*1e-8),(name,difference)
        nominal[name]=s.Volume;progress('nominal_received_'+name,volumes_mm3=nominal)
    param.HoleClearance=.3;progress('parameter_probe_started');d.recompute()
    probe={}
    for name,obj in finals.items():
        assert obj.Shape.isValid() and len(obj.Shape.Solids)==1,name
        probe[name]=obj.Shape.Volume
        if name!='SourceEastHood':assert probe[name]<nominal[name],name
    param.HoleClearance=.2;progress('nominal_restore_started');d.recompute()
    for name,obj in finals.items():
        assert abs(obj.Shape.Volume-nominal[name])<max(1e-5,nominal[name]*1e-8),name
        assert not (obj.Shape.check(True) or []),name
    for obj in d.Objects:
        if hasattr(obj,'ViewObject') and obj.ViewObject:obj.ViewObject.Visibility=obj in finals.values()
    d.save()
    for name,obj in finals.items():
        obj.Shape.exportBrep(str(CAD/(name+'_CANDIDATE_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=obj.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1,name
        bb=mesh.BoundBox;dims[name]=[bb.XLength,bb.YLength,bb.ZLength];assert max(dims[name])+6<=256,(name,dims[name])
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(name+'_UNSELECTED_x1.stl')))
        progress('closed_export_'+name,dimensions_mm=dims)
    deps=list(dict.fromkeys(Path(doc.FileName) for doc in A.listDocuments().values() if doc.FileName and Path(doc.FileName)!=target))
    assert all(p.is_relative_to(ROOT) for p in deps)
    names={name:obj.Name for name,obj in finals.items()}
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fixed-loom-') as td:
        tmp=Path(td)
        for p in [target,*deps]:
            dest=tmp/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        relocated=A.openDocument(str(tmp/target.relative_to(ROOT)));relocated.recompute()
        for name,objname in names.items():
            s=relocated.getObject(objname).Shape;assert s.isValid() and len(s.Solids)==1,name
            assert abs(s.Volume-nominal[name])<max(1e-5,nominal[name]*1e-8),name
        assert all(Path(doc.FileName).is_relative_to(tmp) for doc in A.listDocuments().values())
        for name in list(A.listDocuments()):A.closeDocument(name)
    finish=datetime.now(timezone.utc)
    pins=[Path(__file__),receipt,bpp,oldbp,*deps]
    state.update(status='FOUR_FIXED_LOOM_FRAMES_DECK_HOOD_NATIVE_EXPORT_REOPEN_COMPLETE',
        finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        editable_final_objects=names,nominal_mm3=nominal,probe_mm3=probe,parameter_probe_mm=[.2,.3,.2],restored=True,
        solids=6,BOP_errors=0,closed_STLs=6,relocated_reopen=True,dimensions_mm=dims,
        new_prints=4,replacements=['CompleteDeck','SourceEastHood'],installed_M3x16=8,installed_M3nuts=8,installed_T18I=12,
        effective_clamp_to_nut_floor_mm=11.3,overall_foot_and_pad_height_mm=14,
        full_nut_engagement_mm=2.4,bolt_tip_beyond_nut_mm=2.3,
        assembly=bp['assembly'],all_installed_service_access=False,moving_loom_retention_motion_stock_pending=True,
        prototype_PETG_strength_creep_and_fit_tests_pending=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in CAD.iterdir() if p.suffix.lower() in ('.fcstd','.brep','.stl')})
    save(OUT/'checks.json',state);progress('complete')


if __name__=='__main__':main()

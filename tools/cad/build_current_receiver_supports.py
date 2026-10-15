"""Resume source history only AFTER rooted36-wire layout acceptance.

Four replacement Frame prints and seven independent caps, not22 new Frames.
Save each complete owner before parameters; never overwrite source masters.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from plan_body36_receiver_space import P
from current_mixed_receiver_material import material
from current_native_receiver_primitives import Construction
from current_work_guard import check
from plan_axial_source_supports import arm_box
from build_remaining_loom_supports import print_orientation
from short_feed_lacing_saddle import build as feed_material
from current_fl_ground_feed import geometry as fl_feed


def valid(s,name):assert s.isValid() and len(s.Solids)==1 and not s.check(True),name
def equal(s,t,name):assert max(s.cut(t).Volume,t.cut(s).Volume)<1e-4,name

def editable_feed(ops,recipe,name):
    frame=recipe['local_to_world']
    positive=ops.fuse([ops.box(p['bounds_mm'],name+'Pad'+str(i),frame) for i,p in enumerate(recipe['pads'])],name+'Positive')
    ring=recipe['ring_cut'];tool=ops.cut(ops.box(ring['outer'],name+'RingOuter',frame),ops.box(ring['inner'],name+'RingInner',frame),name+'RingTool')
    return ops.cut(positive,tool,name+'Current')


def run():
    check();tick=time.monotonic()
    rootfile=P.OUT/'body36-receiver-support-reservations.json';wirefile=P.OUT/'body36-shared-macro-layout.json'
    choicefile=P.OUT/'receiver-joint-selection.json';sourcefile=P.OUT/'fixed-source-supports/manifest.json'
    roots,wiring,choice,source=[json.loads(p.read_text()) for p in (rootfile,wirefile,choicefile,sourcefile)]
    assert roots['status']=='ALL_GROUPED_RECEIVER_SUPPORT_RESERVATIONS_CLEAR_MIDDLES_OPEN'
    assert not wiring['remaining_wire_ids'],'Receive complete36wire gate before native work'
    basewirefile=P.ROOT/wiring['inherited_receipt'];basewire=json.loads(basewirefile.read_text())
    current_routes={n:basewire['routes'][n] for n in wiring['retained_route_ids']}
    current_routes.update(wiring['qualified_changed_routes'])
    assert len(current_routes)==36 and len(roots['groups'])==22
    assert all(not a['contacts'] and not a['errors'] for a in wiring['attempts'])
    feedfile=P.OUT/'retained-feed-restraints-checks.json';feeds=json.loads(feedfile.read_text())
    assert feeds['status']=='TEN_FEED_COMMON_COMPONENT_GATE_COMPLETE' and feeds['full_body_curves_accepted']
    assert len(feeds['restraints'])==10 and not feeds['errors']
    assert feeds['source_sha256'][wirefile.relative_to(P.ROOT).as_posix()]==P.SHA(wirefile),'Receive current36vsfeed component gate'
    coveragefile=P.OUT/'body36-fixed-restraint-coverage.json';coverage=json.loads(coveragefile.read_text())
    assert coverage['status']=='CURRENT36_AND_TWENTY_RETAINED_ENDS_GEOMETRY_COVERAGE_COMPOSED'
    assert coverage['source_sha256'][wirefile.relative_to(P.ROOT).as_posix()]==P.SHA(wirefile)
    extra_feed=fl_feed()
    assert wiring['source_sha256'][rootfile.relative_to(P.ROOT).as_posix()]==P.SHA(rootfile)
    for receipt in (roots,wiring,choice,source,feeds,coverage):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    domainfile=P.ROOT/choice['domain_receipt'];options=json.loads(domainfile.read_text())['qualified_options']
    if choice['override_receipt']:options.update(json.loads((P.ROOT/choice['override_receipt']).read_text())['replacement_options'])
    groups={n:options[n][i] for n,i in choice['selected_options'].items()}
    hardwarefile=P.OUT/'receiver-hardware-contribution.json';identified=json.loads(hardwarefile.read_text())
    assert identified['quantities']['T18I_receiver_quantity']==21
    for n,h in identified['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    src=P.OUT/'fixed-source-supports/FixedSourceSupports.FCStd'
    out=P.OUT/'receiver-supports';out.mkdir(exist_ok=True)
    final=out/'ReceiverSupportsCurrent.FCStd';partial=out/'ReceiverSupports.partial.FCStd'
    assert not final.exists() and not partial.exists(),'Receive existing native result; do not overwrite/rebuild'
    files=[rootfile,wirefile,basewirefile,feedfile,coveragefile,choicefile,sourcefile,hardwarefile,src,Path(__file__),Path(__file__).with_name('current_fl_ground_feed.py'),Path(__file__).with_name('short_feed_lacing_saddle.py'),Path(__file__).with_name('current_native_receiver_primitives.py'),
        Path(__file__).with_name('current_work_guard.py'),Path(__file__).with_name('native_support_primitives.py')]
    records=[];exports=[];expected={};ops=None;hardware=[];feed_records=[]
    def save(status):
        result=dict(status=status,parts=records,exports=exports,hardware=hardware,feed_restraints=feed_records,
            source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
            fully_constrained_new_sketches=ops.sketches if ops else 0,
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            replaces_source_fixed_prints=[r['name'] for r in source['parts']],
            physical_Frame_prints=4,physical_CAP_prints=7,T18I_receiver_quantity=21,M2x14_receiver_quantity=1,M2_nut_receiver_quantity=1,
            lacing_feed_blanks=11,lacing_feed_project_total_mm=1650,lacing_stock_selected=False,
            scope='Editable4Frames+7caps incl9Framefeeds/1D_FLcapfeed/independentFL_GW025. Complete36/current10feed/composedG1G2FLcoverage required. Whole source/stock/package still OPEN.')
        p=out/'manifest.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(p)
    with tempfile.TemporaryDirectory(prefix='robot-cat-receiver-native-') as td:
        work=Path(td)/'ReceiverSupports.FCStd';shutil.copy2(src,work);doc=A.openDocument(str(work));ops=Construction(doc)
        par=doc.getObject('ReceiverParameters');assert par and abs(par.ArmThickness.Value-4)<1e-8
        par.addProperty('App::PropertyLength','CoreBoreRadius');par.CoreBoreRadius=1.3
        try:
            for owner in sorted({q['owner'] for q in groups.values()}):
                check();base=doc.getObject(owner+'SourceRooted');assert base
                children=[base];planned=[base.Shape.copy()]
                for name,g in groups.items():
                    if g['owner']!=owner:continue
                    check();profile,_=material(g)
                    body=(ops.triple(g,owner+name+'Seat')[0] if g['kind']=='triple' else ops.seat(profile['recipe'],owner+name+'Seat'))
                    equal(body.Shape,profile['body'],name+'seat');children.append(body);planned.append(profile['body'])
                    row=next(r for r in roots['groups'] if r['wire']==name);assert row['paths'] and row['name']==owner
                    for path in row['paths']:
                        for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                            s=arm_box(a,b,row['arm_half_widths_world_mm']);arm=ops.arm(s,owner+name+'Arm'+str(i))
                            equal(arm.Shape,s,name+'arm');children.append(arm);planned.append(s)
                    if g['kind']=='triple':
                        cap,_=ops.triple(g,'ReceiverCap'+name,True);equal(cap.Shape,profile['cap'],name+'cap');valid(cap.Shape,name+'cap')
                        cap_expected=profile['cap'];cap_children=[cap]
                        for fr in (r for r in feeds['restraints'] if r['group']==name):
                            label=name+fr['wire'];support=fr.get('parent_component',fr['recipe'].get('parent_component','body'))
                            physical=next(f for f in g['feeds'] if f['wire']==fr['wire'])
                            planned_feed=feed_material(profile['recipe'],physical,support=support)
                            seat=editable_feed(ops,fr['recipe'],'ReceiverFeed'+label);equal(seat.Shape,planned_feed['body'],label+'feed')
                            if support=='cap':cap_children.append(seat);cap_expected=cap_expected.fuse(planned_feed['body']).removeSplitter()
                            else:children.append(seat);planned.append(planned_feed['body'])
                            reference=doc.addObject('Part::Feature','ReceiverFeedLacing'+label);reference.Shape=planned_feed['band'];reference.Visibility=False
                            feed_records.append(dict(group=name,wire=fr['wire'],parent_component=support,native_seat=seat.Name,
                                lacing_reference=reference.Name,lacing_candidate_part='802534B',project_blank_mm=150,
                                separate_additional_prints=0,separate_additional_screws=0,stock_selected=False))
                        if len(cap_children)>1:cap=ops.fuse(cap_children,'ReceiverCap'+name+'Current')
                        valid(cap.Shape,name+'completecap');equal(cap.Shape,cap_expected,name+'completecap')
                        expected[cap.Name]=cap_expected;records.append(dict(part='ReceiverCap'+name,object=cap.Name,owner=owner,kind='separate_CAP',quantity=1,volume_mm3=cap.Shape.Volume))
                    if g.get('retainer')=='M2_cap':
                        for kind in ('screw','nut'):
                            ref=doc.addObject('Part::Feature','ReceiverRR_'+kind);ref.Shape=profile[kind];ref.Visibility=False
                            offer=next(r for r in identified['hardware'] if r['role']=='RR_G_cap_'+kind)
                            hardware.append(dict(role='RR_G_'+kind,quantity=1,native_object=ref.Name,
                                sku=offer['sku'],url=offer['url'],offer_evidence_date=identified['offer_evidence_date'],
                                nominal_reservation_not_supplier_model=True,physical_fit_gate_open=True,
                                current_availability_not_checked=True))
                if owner=='FrontLeftFixedCarrier':
                    r=extra_feed['recipe']
                    seat_recipe=dict(r,pads=[dict(bounds_mm=r['seat']),dict(bounds_mm=r['foot'])])
                    seat=editable_feed(ops,seat_recipe,'ReceiverFeedFL_GW025')
                    additions=[seat]
                    for i,(a,b) in enumerate(zip(r['root_path_mm'],r['root_path_mm'][1:])):
                        additions.append(ops.arm(arm_box(a,b,[2,2,2]),'ReceiverFeedFL_GW025Arm'+str(i)))
                    whole=ops.fuse(additions,'ReceiverFeedFL_GW025Current')
                    equal(whole.Shape,extra_feed['body'],'FL_GW025completefeed')
                    children.append(whole);planned.append(extra_feed['body'])
                    ref=doc.addObject('Part::Feature','ReceiverFeedLacingFL_GW025');ref.Shape=extra_feed['band'];ref.Visibility=False
                    feed_records.append(dict(group='FL_G',wire='W025',parent_component='body',native_seat=whole.Name,
                        lacing_reference=ref.Name,lacing_candidate_part='802534B',project_blank_mm=150,
                        separate_additional_prints=0,separate_additional_screws=0,stock_selected=False))
                current=ops.fuse(children,owner+'ReceiverCurrent');valid(current.Shape,owner)
                # One expected union per owner, not a rebuild of every source
                # and every prior Boolean after each added receiver feature.
                compare=planned[0].multiFuse(planned[1:]).removeSplitter();valid(compare,owner+'planned');equal(current.Shape,compare,owner)
                expected[current.Name]=compare;records.append(dict(part=owner,object=current.Name,owner=owner,kind='replacement_Frame',quantity=1,volume_mm3=current.Shape.Volume))
                doc.saveAs(str(partial))
                if partial not in files:files.append(partial)
                save('PARTIAL_CURRENT_RECEIVER_NATIVE_OWNERS');print('native receiver owner saved',owner,flush=True)
            assert len(records)==11 and len(feed_records)==11
            par.CoreBoreRadius=1.4;doc.recompute()
            for row in records:
                check();s=doc.getObject(row['object']).Shape;valid(s,row['part']);assert s.Volume<row['volume_mm3']
            par.CoreBoreRadius=1.3;doc.recompute()
            for row in records:equal(doc.getObject(row['object']).Shape,expected[row['object']],row['part'])
            par.ArmThickness=4.2;doc.recompute()
            for row in records:
                check();s=doc.getObject(row['object']).Shape;valid(s,row['part'])
                if row['kind']=='replacement_Frame':assert s.Volume>row['volume_mm3']
                else:assert abs(s.Volume-row['volume_mm3'])<1e-4
            par.ArmThickness=4;doc.recompute()
            for row in records:equal(doc.getObject(row['object']).Shape,expected[row['object']],row['part'])
            for o in doc.Objects:
                if hasattr(o,'Visibility'):o.Visibility=False
            for row in records:doc.getObject(row['object']).Visibility=True
            doc.saveAs(str(final));files.append(final);save('CURRENT_RECEIVER_NATIVE_PARAMETERS_CLEAR_REOPEN_OPEN')
        finally:
            if par.CoreBoreRadius.Value!=1.3:par.CoreBoreRadius=1.3;doc.recompute()
            if par.ArmThickness.Value!=4:par.ArmThickness=4;doc.recompute()
            A.closeDocument(doc.Name)
        relocated=Path(td)/'Relocated.FCStd';shutil.copy2(final,relocated);doc=A.openDocument(str(relocated));doc.recompute()
        try:
            for row in records:
                check();s=doc.getObject(row['object']).Shape;valid(s,row['part']);equal(s,expected[row['object']],row['part'])
                orient=print_orientation(s);assert orient['fits_with_5mm_brim'],row['part']
                q=s.copy();q.Placement=A.Placement(A.Vector(),A.Rotation(*orient['rotation_quaternion']))*q.Placement
                bb=q.BoundBox;q.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
                mesh=MeshPart.meshFromShape(Shape=q,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
                assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
                file=out/(row['part']+'_x1.stl');mesh.write(str(file));files.append(file)
                row.update(core_bore_restore_mm=[1.3,1.4,1.3],arm_restore_mm=[4,4.2,4],relocated_reopen=True)
                exports.append(dict(part=row['part'],path=file.relative_to(P.ROOT).as_posix(),sha256=P.SHA(file),quantity=1,printing=orient))
                save('PARTIAL_CURRENT_RECEIVER_NATIVE_EXPORTS');print('receiver export',row['part'],flush=True)
        finally:A.closeDocument(doc.Name)
    save('FOUR_CURRENT_RECEIVER_FRAMES_SEVEN_CAPS_NATIVE_PREPARED')


if __name__=='__main__':run()

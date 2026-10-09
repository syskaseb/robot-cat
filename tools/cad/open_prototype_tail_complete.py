"""One plate-rooted, editable CP2 tail mechanical package; no wiring credit."""
from pathlib import Path
from datetime import datetime, timezone
import json, math, time
import FreeCAD as A
import Part, Mesh, MeshPart
from check_main_p0_placement import SavedShapes, sha
from open_prototype_tail_mount import ROOT, BASE, OUT
from open_prototype_side_source_routes import load_scene
from open_prototype_tail_clearance import near, wire, profiles
from open_deck_p0_supports import sketch, feature
from open_deck_p0_plate import rect, circle
from open_prototype_shared_distribution_carriers import validate

MODEL=OUT/'TailMechanicalCurrent.FCStd'
AXES=[(x,y) for x in (112,122) for y in (-22.5,22.5)]


def build(mount,tail,bridge_source):
    d=A.newDocument('TailMechanicalCurrent')
    par=d.addObject('App::VarSet','TailParameters')
    par.addProperty('App::PropertyLength','TailRise');par.TailRise=15
    carrier=d.copyObject(mount.LowerCarrier,True);d.recompute()
    # Both side/front alternatives occupied other owners. Keep the monitor in
    # its original rear bay, BETWEEN the four posts, in a1.8mm-floor recess.
    # Remove ONLY its four old seat cylinders, not other board anchor bosses.
    sk=sketch(carrier,'OldMonitorSeatRemovalPlan',47.72)
    for x in (112,145):
        for y in (-22.5,-2.5):circle(sk,x,y,4.5)
    carrier.Tip=feature(carrier,'Pocket','OldMonitorSeatRemoval',sk,5)
    sk=sketch(carrier,'MonitorRecessPlan',42.72);rect(sk,108,-12.5,41,25)
    carrier.Tip=feature(carrier,'Pocket','MonitorRecess',sk,1.2)
    sk=sketch(carrier,'RelocatedMonitorPadsPlan',41.52)
    for x in (112,145):
        for y in (-10,10):circle(sk,x,y,4.5)
    carrier.Tip=feature(carrier,'Pad','RelocatedMonitorPads',sk,1.4)
    # A frame washer blocks under-plate straps. Anchor both bands ABOVE the
    # floor with integral bridge tunnels, not through any component/pad.
    sk=sketch(carrier,'MonitorAnchorBridgesPlan',41.52)
    rect(sk,123.4,-15.5,15,2.5)
    carrier.Tip=feature(carrier,'Pad','MonitorAnchorBridges',sk,3.48)
    sk=sketch(carrier,'MonitorAnchorTunnelsPlan',43)
    for x in (126,133):rect(sk,x-.15,-16,2.8,3.2)
    carrier.Tip=feature(carrier,'Pocket','MonitorAnchorTunnels',sk,1.48)
    sk=sketch(carrier,'TailPostPassagesPlan',53.72)
    for x,y in AXES:circle(sk,x,y,7.6)
    carrier.Tip=feature(carrier,'Pocket','TailPostPassages',sk,15)
    post=d.addObject('PartDesign::Body','TailRiser')
    sk=sketch(post,'TailRiserAnnulus',0);circle(sk,0,0,7);circle(sk,0,0,2.6)
    post.Tip=feature(post,'Pad','TailRiserPad',sk,'TailParameters.TailRise + 4 mm')
    post.Visibility=False
    for i,(x,y) in enumerate(AXES):
        ob=d.addObject('App::Link',f'TailRiser{i+1}');ob.setLink(post)
        ob.LinkPlacement=A.Placement(A.Vector(x,y,38.52),A.Rotation())
    bridge=d.copyObject(bridge_source.TailBridge,True);d.recompute();bridge.Visibility=False
    ob=d.addObject('App::Link','RaisedTailBridge');ob.setLink(bridge)
    ob.setExpression('Placement.Base.z','TailParameters.TailRise')
    # Existing fully editable local support, not a newly frozen mesh.
    support=d.copyObject(tail.CurrentTailSupport.getLinkedObject(),True)
    support.Visibility=False
    ob=d.addObject('App::Link','RaisedTailSupport');ob.setLink(support)
    ob.setExpression('Placement.Base.z','TailParameters.TailRise')
    d.recompute()
    return d,carrier,post,bridge,support


def run():
    assert not MODEL.exists(),'Receive current output; do not overwrite a selected native file'
    tick=time.monotonic();docs=[];d=None
    r=dict(status='PENDING',selected=False,mechanical_M3_complete=False,physical_pass=False,
           wiring_complete=False,contacts=[],errors=[],tested_pairs=0,motion_samples=[],
           reference_reservations_are_not_manufacturer_geometry=True)
    def progress(s):print(json.dumps(dict(phase=s,seconds=round(time.monotonic()-tick,2))),flush=True)
    def hit(n,s,m,t):
        if not near(s,t,0):return
        assert s.isValid() and t.isValid(),(n,m,'invalid BRep')
        r['tested_pairs']+=1;c=s.common(t);assert c.isValid()
        if c.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=c.Volume))
    try:
        progress('load shared unchanged scene')
        p=json.loads((BASE/'wiring-checkpoint/source-group-allocation.json').read_text())['family']
        docs,fixed,rings,torso,paths=load_scene(p)
        bridgepath=ROOT/'hardware/cad/studies/tail-p0-bridge-flange-r1/TailBridgeP0Flange.FCStd'
        bs=A.openDocument(str(bridgepath));docs.append(bs)
        reader=SavedShapes();entry=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
        xml=reader.doc(entry)
        p0={}
        for n in ('Part__Feature038','FrameRear20'):
            s=reader.shape(entry,n);s.Placement=reader.placement(xml['Rigid_'+n])*s.Placement;p0[n]=s
        d,carrier,post,bridge,support=build(docs[1],docs[4],bs)
        bodies=[carrier,post]
        for inherited in (bridge,support):
            assert inherited.Shape.isValid() and len(inherited.Shape.Solids)==1 and not inherited.Shape.check(True)
        base=validate(d,bodies)
        before=docs[1].LowerCarrier.Shape
        delta=carrier.Shape.cut(before)
        # Existing broad module reservations overlap their own board pads.
        # Only newly added material is a changed-interface clearance claim.
        r['inherited_nominal_reservation_overlaps']={}
        for n,s,basis in fixed:
            if n in ('Pi4_CP2','BUS_CP2','F0_CP2'):
                r['inherited_nominal_reservation_overlaps'][n]=before.common(s).Volume
        fixed=[q for q in fixed if q[0] not in ('LowerCarrier','Monitor_CP2')]
        fixed += [('P0_'+n,s,'unchanged native material') for n,s in p0.items()]
        changed=[(f'TailRiser{i+1}',d.getObject(f'TailRiser{i+1}').Shape) for i in range(4)]
        # A purely subtractive receiver change has an EMPTY added-material
        # set, not an invalid solid. Never ask its void bounding box for gaps.
        if not delta.isNull() and delta.Volume>1e-6:changed.append(('CarrierAddedMaterial',delta))
        monitor=Part.makeBox(41,25,12,A.Vector(108,-12.5,42.92))
        changed.append(('MonitorRelocatedCaseReservation',monitor))
        for i,x in enumerate((126,133)):
            outer=Part.makeBox(2.5,33.6,14.52,A.Vector(x,-16.8,41.6))
            inner=Part.makeBox(3,31.2,12.12,A.Vector(x-.25,-15.6,42.8))
            strap=outer.cut(inner)
            head=Part.makeBox(4.8,4.5,3.5,A.Vector(x-1.15,-16.8,54.92))
            for suffix,s in (('StrapAllowance',strap),('HeadAllowance',head)):
                o=d.addObject('Part::Feature',f'MonitorTie{i+1}{suffix}');o.Shape=s
                changed.append((o.Name,s))
        r['monitor_ties']=dict(quantity=2,retained_not_additional=True,sku='111-02370',
             nominal_length_mm=145,loop_perimeter_mm=96.24,reserve_tail_mm=25,
             band_mm=[2.5,1.2],head_mm=[4.8,4.5,3.5],actual_pull_and_case_fit_open=True)
        for n,s in changed:
            for m,t,_ in fixed:hit(n,s,m,t)
            if n!='CarrierAddedMaterial':hit(n,s,'LowerCarrierMatched',carrier.Shape)
        for i,(n,s) in enumerate(changed):
            for m,t in changed[i+1:]:
                if n.startswith('MonitorTie') and m.startswith('MonitorTie') and n[10]==m[10]:
                    # Strap threads its own nominal head allowance. The head
                    # box is a size budget, not a solid with a modelled tunnel.
                    continue
                hit(n,s,m,t)
        for n,(parts,radius,_,_) in profiles(p).items():
            c=wire(parts)
            for m,s in changed:
                if near(c,s,radius):
                    r['tested_pairs']+=1;distance=c.distToShape(s)[0]
                    if distance<radius-1e-6:r['contacts'].append(dict(a=n,b=m,distance_mm=distance,required_mm=radius))
        progress('new material and complete relocated monitor checked')
        # Four existing axes, no second set of chassis bolts. DIN912 supplier
        # drawing: M2x30 full thread, head3.8x2, hex1.5. P0 holes reamed only
        # after delivery, as already required by retained P0 assembly recipe.
        hardware=[]
        from open_prototype_source_shared_layout import prism
        for i,(x,y) in enumerate(AXES):
            screw=Part.makeCylinder(1,30,A.Vector(x,y,35.22)).fuse(Part.makeCylinder(1.9,2,A.Vector(x,y,33.22)))
            washer=lambda z:Part.makeCylinder(2.5,.3,A.Vector(x,y,z)).cut(Part.makeCylinder(1.1,.3,A.Vector(x,y,z)))
            poly=Part.makePolygon([A.Vector(x+2/math.cos(math.pi/6)*math.cos(a*math.pi/3),y+2/math.cos(math.pi/6)*math.sin(a*math.pi/3),60.82) for a in range(7)])
            nut=Part.Face(Part.Wire(poly.Edges)).extrude(A.Vector(0,0,1.6)).cut(Part.makeCylinder(1.1,1.6,A.Vector(x,y,60.82)))
            for suffix,s in [('Bolt',screw),('LowerWasher',washer(35.22)),('UpperWasher',washer(60.52)),('Nut',nut)]:
                o=d.addObject('Part::Feature',f'RearShared{i+1}{suffix}');o.Shape=s;hardware.append(o)
                for n,t,_ in fixed:
                    if n=='P0_FrameRear20':
                        # Reamed2.4 clearance preview, retained frame unchanged.
                        t=t.cut(Part.makeCylinder(1.2,2,A.Vector(x,y,35.32)))
                    hit(o.Name,s,n,t)
                hit(o.Name,s,'LowerCarrierMatched',carrier.Shape)
                hit(o.Name,s,'RaisedTailBridge',d.RaisedTailBridge.Shape)
                hit(o.Name,s,'TailRiser',d.getObject(f'TailRiser{i+1}').Shape)
            # The frame lower shelf blocks bottom insertion. Introduce the
            # complete30mm screw horizontally between the shelves, tip35.22,
            # then raise30mm through the existing axes. X122 before X112.
            from tail_p0_fastener_access import xc
            sweeps=[('SideShaft',xc(x,y,5.22,1,30)),
                    ('SideHead',xc(x,y,3.22,1.9,2)),
                    ('SideLowerWasher',xc(x,y,5.22,2.5,.3)),
                    ('RaiseShaft',Part.makeCylinder(1,60,A.Vector(x,y,5.22))),
                    ('RaiseHead',Part.makeCylinder(1.9,32,A.Vector(x,y,3.22))),
                    ('RaiseLowerWasher',Part.makeCylinder(2.5,30.3,A.Vector(x,y,5.22)))]
            access=Part.makeCylinder(.9,8,A.Vector(x,y,25.22))
            for n,t in p0.items():
                t=t.cut(Part.makeCylinder(1.2,4,A.Vector(x,y,35.32)))
                for tag,s in sweeps:hit('Mount'+tag+str(i),s,n,t)
                hit('Hex1_5Driver'+str(i),access,n,t)
            # Nut goes on before the support/body module or upper electronics.
            holder=Part.makeBox(7,7,4.3,A.Vector(x-3.5,y-3.5,60.82))
            hit('AF4ThinNutHolder'+str(i),holder,'RaisedTailBridge',d.RaisedTailBridge.Shape)
        r['hardware_stack_mm']=dict(underhead=35.22,thread_tip=65.22,nut=[60.82,62.42],engagement=1.6,protrusion=2.8,
             riser=[38.52,57.52],bridge=[57.52,60.52],lower_plate_clearance_diameter=7.6)
        progress('four shared frame fasteners and early assembly access checked')
        # Changed support/master parameter actually moves the complete tail,
        # not merely a cosmetic label or a different STL resolution.
        z=d.RaisedTailBridge.Shape.BoundBox.ZMin
        d.TailParameters.TailRise=16;validate(d,[post])
        assert abs(d.RaisedTailBridge.Shape.BoundBox.ZMin-z-1)<1e-6
        assert abs(post.Shape.BoundBox.ZLength-20)<1e-6
        d.TailParameters.TailRise=15;restored=validate(d,[post])
        assert abs(base[post.Name]-restored[post.Name])<1e-6
        assert abs(carrier.Shape.Volume-base[carrier.Name])<1e-6
        r['parameter_restore']=dict(TailRise_mm=[15,16,15],post_height_mm=[19,20,19],bridge_and_support_coupled=True)
        if r['contacts']:
            r['status']='REJECTED_CHANGED_INTERFACES';return
        o=d.addObject('Part::Feature','MonitorCaseReservation');o.Shape=monitor
        o.addProperty('App::PropertyString','Qualification');o.Qualification='Nominal casing only; delivered connector/pad fit and all wiring remain OPEN'
        d.recompute();d.saveAs(str(MODEL))
        r['native_volumes_mm3']=base;r['native_sha256']=sha(MODEL)
        r['exports']={}
        for body,quantity in ((carrier,1),(post,4)):
            mesh=MeshPart.meshFromShape(Shape=body.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds()
            dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
            assert max(dims)+10<256
            mesh.translate(-mesh.BoundBox.XMin,-mesh.BoundBox.YMin,-mesh.BoundBox.ZMin)
            f=OUT/(body.Name+f'_x{quantity}.stl');mesh.write(str(f));re=Mesh.Mesh(str(f))
            assert re.isSolid() and not re.hasNonManifolds()
            r['exports'][f.name]=dict(sha256=sha(f),quantity=quantity,dimensions_mm=dims,closed=True)
        A.closeDocument(d.Name);d=None
        reopened=A.openDocument(str(MODEL))
        validate(reopened,[reopened.getObject(n) for n in base]);A.closeDocument(reopened.Name)
        r.update(status='NATIVE_PLATE_ROOTED_TAIL_MOUNT_PREPARED',reopen_verified=True,
                 mechanical_M3_complete=False,full_current_tail_selection_and_motion_still_open=True)
    except Exception as e:
        r['errors'].append(str(e));r['status']='ERROR_NO_ACCEPTANCE';raise
    finally:
        if d:A.closeDocument(d.Name)
        for doc in docs:
            if doc.Name in A.listDocuments():A.closeDocument(doc.Name)
        r['source_sha256']={f.relative_to(ROOT).as_posix():sha(f) for f in paths+[bridgepath,Path(__file__)]} if 'paths' in locals() else {}
        if 'reader' in locals():r['source_sha256'].update(reader.hashes)
        r.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        (OUT/'native-mount-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:r.get(k) for k in ('status','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()

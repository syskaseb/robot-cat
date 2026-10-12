"""One rooted, replaceable twelve-station support layout, not whole W5.

All station poses come from the current archive. Four existing boss feet retain
P0 without drilling. Low case shoes never bridge the lever/terminal gallery.
Adhesive compatibility remains a delivered-fit gate, not cable strain relief.
"""
import json, math, time, hashlib, sys
from pathlib import Path
import FreeCAD as A
import Part
import plan_low_power_station_mounts as P
ROOT, BASE, OUT, SHA = P.ROOT, P.BASE, P.OUT, P.SHA


def bearing_area(a,b,z):
    """Intersect coincident planar faces, not a zero-volume solid Common.

    Solid Boolean Common may discard shared faces. Normalize only sub-micron
    plane roundoff; positive-volume interference is still checked separately.
    """
    aa=[f for f in a.Faces if f.BoundBox.ZLength<1e-7 and abs(f.BoundBox.ZMin-z)<1e-7]
    bb=[f for f in b.Faces if f.BoundBox.ZLength<1e-7 and abs(f.BoundBox.ZMin-z)<1e-7]
    total=0
    for f in aa:
        f=f.copy();f.translate(A.Vector(0,0,z-f.BoundBox.ZMin))
        for g in bb:
            g=g.copy();g.translate(A.Vector(0,0,z-g.BoundBox.ZMin))
            hit=f.common(g);assert hit.isValid();total+=hit.Area
    return total


def allocate(targets):
    pads=[]; parts={}; hardware={}; bonds={}; stations=[]; clamps=[];foundation_bearings=[]
    for leg,side,rx in [('FL',1,-35),('FR',-1,-35),('RL',1,80),('RR',-1,80)]:
        owner=leg+'StationFrame';current_owner=owner
        def B(x,y,z,X,Y,Z):
            lo,hi=sorted((side*y,side*Y));return [x,lo,z,X,hi,Z]
        def pad(n,b,o=None):pads.append(dict(owner=o or current_owner,name=n,bounds_mm=b))
        # Actual boss bottom Z-2, existing R1.7 bore and TOP captive nut.
        # A top exit crosses the oblique side wall: take the whole arm below
        # the rail instead. No material removed from P0 or old support reused.
        foot_bounds=B(rx-5,34,-5,rx+5,46,-2)
        pad('ActualBossFoot',foot_bounds)
        for name in ('D_'+leg,leg+'_G',leg+'_P'):
            current_owner='FoundationStationSupports' if leg=='FL' and not name.endswith('_P') else owner
            bb=targets[name].BoundBox
            cx=(bb.XMin+bb.XMax)/2;yy=abs((bb.YMin+bb.YMax)/2);z=bb.ZMin
            assert abs(bb.XLength-30)<1e-6 and abs(bb.YLength-9)<1e-6 and abs(bb.ZLength-19)<1e-6
            # All back spines face OUTWARD, not into fuse/input/head wiring.
            # The front-left common column goes east of the Foundation floor;
            # the front-right one stays west of both differently-height cases.
            # This changes the whole load path, not each collision coordinate.
            tag=name.replace('_',''); px=bb.XMin-4 if name.endswith('_P') else max(bb.XMax,targets[leg+'_P'].BoundBox.XMax)+6 if leg=='FR' and name.startswith('D_') else -40 if leg=='FR' else rx
            xmin=min(px-2,cx-16);xmax=max(px+2,cx+16)
            if leg=='FL' and not name.endswith('_P'):
                # Root locally on actual Foundation top71.52; F_HP occupies
                # the entire common-spine vertical alley69.99..91.99. A long
                # bridge around it is both blocked and mechanically poor.
                fb=B(cx-8,65,71.52,cx+8,74,74.52);pad(tag+'FoundationFoot',fb)
                area=bearing_area(P.box(fb),targets['Foundation'],71.52)
                assert area>30,(name,'No actual Foundation support face',area)
                foundation_bearings.append(dict(station=name,actual_top_z_mm=71.52,contact_area_mm2=area))
                pad(tag+'ShortOutrigger',B(cx-2,70,71.52,cx+2,yy+7,79.52))
                pad(tag+'LocalRiser',B(cx-2,yy+5,71.52,cx+2,yy+7,z-.25))
                pad(tag+'Spine',B(cx-16,yy+5,z-8.25,cx+16,yy+7,z-.25))
            elif leg=='FR' and name=='FR_G':
                # Knee motion crosses the old X-40 under-rail transverse arm.
                # Share the P-station's east root/run, then return OUTBOARD
                # below both cases. Keep the G post/seat and all case datums.
                ex=targets['FR_P'].BoundBox.XMin-4
                pad(tag+'SharedEastRoot',B(rx-2,40,-5,ex+2,43,-2))
                pad(tag+'EastRootArm',B(ex-2,40,-5,ex+2,yy+7,-2))
                pad(tag+'OutboardReturn',B(px-2,yy+5,-5,ex+2,yy+7,-2))
                pad(tag+'Post',B(px-2,yy+5,-5,px+2,yy+7,z-.25))
                pad(tag+'Spine',B(xmin,yy+5,z-8.25,xmax,yy+7,z-.25))
            elif leg=='RR' and name=='D_RR':
                # The complete deep spine must pass OUTSIDE W053, whose
                # descending source curve crosses the inner span. Return to
                # the case only east of its X130 edge, not by shaving a notch.
                tx=bb.XMin+1
                pad(tag+'RootArm',B(rx-2,40,-5,rx+2,100,-2))
                pad(tag+'Post',B(rx-2,98,-5,rx+2,100,z-.25))
                pad(tag+'OuterSpine',B(rx-2,98,z-8.25,tx+2,100,z-.25))
                pad(tag+'ShortReturn',B(tx-2,yy+5,z-8.25,tx+2,100,z-.25))
                pad(tag+'Spine',B(cx-16,yy+5,z-8.25,cx+16,yy+7,z-.25))
            else:
                if px!=rx:pad(tag+'RootRun',B(min(rx,px)-2,40,-5,max(rx,px)+2,43,-2))
                pad(tag+'RootArm',B(px-2,40,-5,px+2,yy+7,-2))
                pad(tag+'Post',B(px-2,yy+5,-5,px+2,yy+7,z-.25))
                pad(tag+'Spine',B(xmin,yy+5,z-8.25,xmax,yy+7,z-.25))
            # Support/bond only the OUTER half of every lower casing. Whole
            # inner half remains available to existing fuse/input approaches.
            # This is a shared seat allocation, not a cut around one witness.
            pad(tag+'Seat',B(cx-16,yy,z-3.25,cx+16,yy+7,z-.25))
            pad(tag+'LowBack',B(cx-16,yy+5,z-3.25,cx+16,yy+7,z+5.5))
            for i,x in enumerate((cx-16,cx+15.5)):
                pad(tag+'EndCurb'+str(i),B(x,yy,z-3.25,x+.5,yy+5,z+3))
            bonds[name+'BottomBond']=P.box(B(cx-13.5,yy+.5,z-.25,cx+13.5,yy+4,z))
            bonds[name+'BackBond']=P.box(B(cx-10,yy+4.5,z,cx+10,yy+5,z+5))
            stations.append(dict(name=name,owner=current_owner,case_bounds_world_mm=[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax],
                adhesive_area_mm2=[94.5,100],support_top_z_mm=z-.25,
                clear_terminal_reservation_mm=[bb.XMin,bb.YMin-3,bb.ZMax,bb.XMax,bb.YMax+3,bb.ZMax+23],
                load_path='Lower case -> provisional removable bond -> low shoe/back -> short integral Foundation outrigger -> existing Foundation supports' if current_owner=='FoundationStationSupports' else 'Lower case -> provisional removable bond -> low shoe/back -> outboard post/under-rail arm/foot -> actual retained P0 boss bottom Z-2',
                wire_strain_relief='OPEN: no cable load assigned to case adhesive; above-case gallery kept free for independent grips/full fans'))
        for o in (owner,):
            s=P.fuse([P.box(r['bounds_mm']) for r in pads if r['owner']==o])
            s=s.cut(Part.makeCylinder(1.7,25,A.Vector(rx,side*40,-12)))
            parts[o]=s.removeSplitter()
            assert parts[o].isValid() and len(parts[o].Solids)==1 and not parts[o].check(True),o
        x,y=rx,side*40;n=leg
        hardware[n+'Bolt']=Part.makeCylinder(1.5,16,A.Vector(x,y,-5.5)).fuse(Part.makeCylinder(2.75,3,A.Vector(x,y,-8.5)))
        hardware[n+'Washer']=Part.makeCylinder(3.5,.5,A.Vector(x,y,-5.5)).cut(Part.makeCylinder(1.6,.5,A.Vector(x,y,-5.5)))
        poly=[A.Vector(x+3.175*math.cos(i*math.pi/3),y+3.175*math.sin(i*math.pi/3),6.3) for i in range(7)]
        hardware[n+'Nut']=Part.Face(Part.makePolygon(poly)).extrude(A.Vector(0,0,2.4)).cut(Part.makeCylinder(1.5,2.4,A.Vector(x,y,6.3)))
        rail='P0_SideLeft22' if side>0 else 'P0_SideRight22'
        # Real face contact is a load-path datum, not bbox intersection.
        foot=P.box(foot_bounds).cut(Part.makeCylinder(1.7,25,A.Vector(rx,side*40,-12)))
        bearing=foot.common(targets[rail]);area=bearing_area(foot,targets[rail],-2)
        assert bearing.Volume<1e-5 and area>1 and foot.distToShape(targets[rail])[0]<1e-6,(leg,'No actual boss bearing',bearing.Volume,area)
        bore=[f for f in targets[rail].Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-1.7)<1e-6 and (f.Surface.Center-A.Vector(rx,side*40,9)).Length<1e-5]
        assert len(bore)==1,(leg,'Missing actual M3 bore')
        clamps.append(dict(leg=leg,owner=owner,rail=rail,bolt_axes_mm=[[rx,side*40]],
            measured_bottom_contact_area_mm2=area,actual_bore_radius_mm=1.7,
            nut_bottom_z_mm=6.3,bolt_tip_z_mm=10.5,tip_past_nut_mm=1.8,
            preload_retention='Single M3 friction foot, provisional PETG bearing/rotation/creep trial; not a load rating'))
    additions=P.fuse([P.box(r['bounds_mm']) for r in pads if r['owner']=='FoundationStationSupports'])
    foundation=targets['Foundation'].fuse(additions).removeSplitter()
    assert foundation.isValid() and len(foundation.Solids)==1 and not foundation.check(True)
    assert targets['Foundation'].cut(foundation).Volume<1e-6,'Retain entire current Foundation, no cuts'
    parts['FoundationStationSupports']=foundation
    return parts,hardware,bonds,dict(pads=pads,stations=stations,clamps=clamps,
        foundation_bearings=foundation_bearings,inherited_base={'FoundationStationSupports':'Foundation'},
        replaces_current_Foundation_only_on_future_complete_selection=True,
        hardware_nominal={'M3x16':4,'M3nut':4,'M3washer':4},new_prints=5,
        replaces_unselected_low_power_mounts=True,
        rejected_root_basis='Earlier upper jaws Y45..61 miss the actual top rail lip Y27..35.474. Old four low-power native mounts are NOT qualified rooted supports. No phase1 points depended on those unselected candidates.',
        rejected_top_exit='A common foot/arm above the Z9 boss crossed the actual oblique P0 wall (FL165.4536495mm3). Under-rail exit changes the load-path topology, not a micro-offset.',
        shared_change='All12outer-half seats/back spines preserve inner input/fuse/wire gallery. FL D/G integral short Foundation outriggers replace blocked and weak long common bridge, actual144mm2 floor feet. FR Dcolumn EAST of BOTH D/Pcases avoids lower five-port galleries; FR G shares the P-station east under-rail root and returns outboard, avoiding the complete moving Knee alley rather than cutting a local notch. RR D entire deep spine goes outside W053 and returns east of caseX130. Horizontal spine depth8mm rather than3mm. Same case poses/nets; no cuts, wire waiver or side widening (outermost Y100).',
        assembly=['Disconnect/remove all power sources. Install four nuts in actual P0 top captive pockets before frames, before E1 lower carrier/wiring. Do not drill or trim P0.',
            'Fit each frame foot below its actual Z-2 boss with one upward M3x16 and washer. Check rotation/friction bearing by phase2 coupon; no load rating assigned.',
            'Dry-fit twelve delivered WAGO cases. Retention is provisional removable bottom/back bonding after compatibility/peel trial; support the case during lever operation.',
            'All low shoes stop below the lever/terminal gallery. Independent wire grips/full fan routing must be fitted before loading a cable.',
            'Deep repair: support case, release five ends with no pulling, remove bond/case. Bottom screw is accessible from below; captive nut must be held/replaced before E1 lower carrier installation. Full carrier/wiring removal sequence remains A2 OPEN, not routine service.'],
        provisional=['Nominal purchased bolt/nut/washer envelopes, exact SKU and PETG clamp preload/creep remain K2/phase2 gates',
            'Bond thickness/area are project allocations, not measured adhesion; delivered WAGO lower casing and lever fit remain phase2 gates'],
        open=['Independent insulation grips and full five-port fan/lever operation', 'Complete leg/head wiring, stock and whole assembly selection'],
        selected=False,W5_complete=False,physical_pass=False)


def run():
    tick=time.monotonic();pf=OUT/'data-ground-mounts-plan.json'
    previous=json.loads(pf.read_text()) if pf.exists() else None
    motion_file=OUT/'station-frames-motion.json'
    prior_motion=json.loads(motion_file.read_text()) if motion_file.exists() else None
    targets,curves,archive=P.scene();parts,hardware,bonds,p=allocate(targets)
    print('Allocated4 rooted frames/12stations. Bearing areas',[round(r['measured_bottom_contact_area_mm2'],3) for r in p['clamps']],flush=True)
    changed_parts={n:s.cut(targets['Foundation']) if n=='FoundationStationSupports' else s for n,s in parts.items()}
    all_new={**changed_parts,**hardware,**bonds};report=dict(pairs=0,contacts=[],errors=[])
    if prior_motion and prior_motion['status']=='REJECTED_CURRENT_STATION_SUPPORT_MOTION':
        assert prior_motion['source_sha256'][pf.relative_to(ROOT).as_posix()]==SHA(pf)
        p['prior_motion_rejected']=dict(receipt_sha256=SHA(motion_file),contacts=prior_motion['contacts'],errors=prior_motion['errors'],
            leg_poses=prior_motion['leg_poses'],worker_seconds=prior_motion['worker_seconds'],
            change='FR_G under-rail transverse X-40 arm replaced by shared FR_P east root and outboard return. Seat/case/post datums unchanged; no leg or wire trim.')
    fingerprints={n:hashlib.sha256(s.exportBrepToString().encode()).hexdigest() for n,s in all_new.items()}
    changed=set(all_new);reused=[]
    if '--reuse-unchanged' in sys.argv:
        assert previous and not previous['errors']
        assert previous['status'] in ('REJECTED_DATA_GROUND_SHARED_MOUNT_LAYOUT','DATA_GROUND_MOUNTS_STATIC_TOOL_CLEAR_MOTION_NATIVE_OPEN')
        assert previous['stations']==p['stations'] and previous['clamps']==p['clamps']
        for f in (archive,Path(P.__file__),OUT/'current-leg-receiver-datums.json'):
            assert previous['source_sha256'][f.relative_to(ROOT).as_posix()]==SHA(f)
        reused=[n for n,h in fingerprints.items() if previous['tested_geometry_sha256'].get(n)==h]
        changed-=set(reused)
        p['reused_static_evidence']=dict(previous_report_sha256=SHA(pf),previous_source_sha256=previous['source_sha256'],
            exact_unchanged_geometry_sha256={n:fingerprints[n] for n in reused},
            previous_contacts=previous['contacts'],previous_worker_seconds=previous['worker_seconds'],
            basis='Identical complete BRep bytes/radii and retained archive. Only changed shapes/changed pairs/tools/gallery rechecked; no negative result waived.')
        assert all(r['a'] in changed or r['b'] in changed for r in previous['contacts']), 'Unchanged prior contact must remain rejected'
        print('Exact static reuse',len(reused),'changed',sorted(changed),flush=True)
    def test(n,s,m,t,rad=0):
        if not P.W.near(s,t,rad+.001):return
        report['pairs']+=1
        try:
            assert s.isValid() and t.isValid(), 'Invalid input'
            if rad:
                q=s.distToShape(t);gap=q[0]
                if gap<rad-1e-4:report['contacts'].append(dict(a=n,b=m,gap_mm=gap,required_mm=rad,witness_mm=[list(v) for v in q[1][0]] if q[1] else None))
            else:
                hit=s.common(t);assert hit.isValid(),'Invalid Boolean'
                if hit.Volume>1e-5:
                    b=hit.BoundBox;report['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]))
        except Exception as exc:report['errors'].append(dict(a=n,b=m,error=str(exc)))
    for n,s in all_new.items():
        if n not in changed:continue
        for m,t in targets.items():
            if t.Solids:test(n,s,m,t)
        for m,(t,r) in curves.items():test(n,s,m,t,r)
        print('checked',n,'contacts',len(report['contacts']),flush=True)
    names=list(all_new)
    for i,n in enumerate(names):
        for m in names[i+1:]:
            if n in changed or m in changed:test(n,all_new[n],m,all_new[m])
    # Project tool envelopes and full top fan space are checked independently:
    # the latter is an allocation only, not real lever motion/finished wires.
    report['tools']=0
    for row in p['clamps']:
        for x,y in row['bolt_axes_mm']:
            for tag,s in [('BottomDriver',Part.makeCylinder(2,25,A.Vector(x,y,-33.5)))]:
                report['tools']+=1
                for m,t in {**targets,**all_new}.items():
                    if reused and m not in changed:continue
                    if t.Solids:test(row['owner']+tag,s,m,t)
    for row in p['stations']:
        s=P.box(row['clear_terminal_reservation_mm'])
        for n,t in changed_parts.items():
            if n in changed:test(row['name']+'TerminalGallery',s,n,t)
    if previous and previous['status']=='REJECTED_DATA_GROUND_SHARED_MOUNT_LAYOUT':
        p['previous_rejected']={k:previous[k] for k in ('pads','contacts','errors','pairs','worker_seconds','source_sha256')}
        p['prior_rejected_summary']=previous.get('prior_rejected_summary',[])+[dict(contacts=len(previous['contacts']),pairs=previous['pairs'],seconds=previous['worker_seconds'],shared_change=previous.get('shared_change'))]
    p.update(report,status='REJECTED_DATA_GROUND_SHARED_MOUNT_LAYOUT' if report['contacts'] or report['errors'] else 'DATA_GROUND_MOUNTS_STATIC_TOOL_CLEAR_MOTION_NATIVE_OPEN',
        tested_geometry_sha256=fingerprints,unchanged_parts_reused=len(reused),changed_geometry_names=sorted(changed),
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (archive,Path(__file__),Path(P.__file__),OUT/'current-leg-receiver-datums.json')},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'data-ground-mounts-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:p[k] for k in ('status','pairs','tools','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()

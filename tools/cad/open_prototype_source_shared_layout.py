"""One support-first source-zone proposal; read-only native inputs.

Reuse the vacant lower RR_P land for D_RL, retain every frame column, and
allocate the moved MTA/P_REAR supports together BEFORE detailed PartDesign.
Nominal service/entry allowances are project reservations, not supplier data.
"""
from datetime import datetime, timezone
import copy, json, math, time
from pathlib import Path
import FreeCAD as A
import Part
from open_prototype_source_retention import OUT, BASE, ROOT, sha
from open_prototype_source_receipt import verified_family
from open_prototype_tail_clearance import box, near, wire, profiles

DEST=OUT/'source-shared-layout.json'


def prism(lo, hi):
    return Part.makeBox(*[b-a for a,b in zip(lo,hi)], A.Vector(*lo))


def proposal():
    p=copy.deepcopy(verified_family())
    row=next(r for r in p['stations'] if r['role']=='D_RL')
    old=copy.deepcopy(row)
    row.update(centre_mm=[149,50,91],rotation='180',
               mount_status='REAR_NORTH_SOURCE_TRELLIS_PROPOSAL')
    for i in range(1,6):
        p['ports'][f'D_RL.{i}'].update(point_mm=[149-(i-3)*4.75,59.5,91],departure=[0,1,0])
    # Coupled data rack: stagger in Y as well as Z so lower levers are not
    # covered by the upper connector. This replaces the tail-support conflict.
    dr=next(r for r in p['stations'] if r['role']=='D_RR')
    dr.update(centre_mm=[155,20,128],rotation='180')
    gt=next(r for r in p['stations'] if r['role']=='G_TAIL')
    gt.update(centre_mm=[-41,-46.5,124],size_mm=[30,9,19],rotation='X-90')
    for i in range(1,6):
        p['ports'][f'D_RR.{i}'].update(point_mm=[155-(i-3)*4.75,29.5,128],departure=[0,1,0])
        p['ports'][f'G_TAIL.{i}'].update(point_mm=[-41+(i-3)*4.75,-46.5,133.5],departure=[0,0,1])
    for e in p['body_ends']:
        if e['current_role'].startswith(('D_RL.','D_RR.','G_TAIL.')):
            e['datum']=copy.deepcopy(p['ports'][e['current_role']])
    # Matched floor pads avoid the whole PCB envelopes (top108) instead of
    # inserting a continuous 3mm raft beneath MTA bottoms109.
    supports={}
    owners={}
    for m in p['mta']:
        x,y,z=m['centre_mm'];front=y>0
        ya,yb=(13.7,40.5) if front else (-40.5,-26.4)
        floor=prism([x-12,ya,106],[x+12,yb,109])
        py=20 if front else -29.5
        arm=prism([x-3,py-3,77.72],[x+3,py+3,109])
        supports[m['role']+'/floor_arm']=floor.fuse(arm).removeSplitter()
        owners[m['role']+'/floor_arm']='UpperCarrier'
        if not front:
            supports[m['role']+'/plate_ear']=prism([x-5,-34.5,74.72],[x+5,-24,77.72])
            owners[m['role']+'/plate_ear']='UpperCarrier'
    # P_REAR sits above the PCB and is reached from the rear right branch.
    # The post and dog-leg are west/north of the retained TY sleeve, not
    # through the ATO bank on the side spine.
    floor=prism([50.3,.5,127.01],[87.3,25.5,130.01])
    cross=prism([68.8,8.5,127.01],[111,14.5,130.01])
    longitudinal=prism([105,11.5,127.01],[111,47,130.01])
    turn=prism([108,41,127.01],[116,47,130.01])
    post=prism([110,41,77.72],[116,47,130.01])
    supports['P_REAR/platform']=floor.fuse(cross).fuse(longitudinal).fuse(turn).fuse(post).removeSplitter()
    owners['P_REAR/platform']='UpperCarrier'
    supports['P_REAR/plate_ear']=prism([107,24,74.72],[120,47,77.72])
    owners['P_REAR/plate_ear']='UpperCarrier'
    # D_RR is not silently left floating. Its removable shelf is a separate
    # interface on the upper plate, with screw/tool design still a gate.
    ear=prism([132.5,30,74.72],[148,53,77.72])
    ear=ear.cut(Part.makeCylinder(3.7,3,A.Vector(138,30,74.72)))
    supports['DATA/plate_ear']=ear;owners['DATA/plate_ear']='UpperCarrier'
    low=prism([134,40.5,81.01],[164,59.5,84.01])
    low=low.fuse(prism([142,35,77.72],[148,53,84.01])).removeSplitter()
    supports['D_RL/shelf']=low;owners['D_RL/shelf']='UpperCarrier'
    high=prism([140,10.5,118.01],[170,29.5,121.01])
    high=high.fuse(prism([142,26.5,118.01],[148,38,121.01]))
    high=high.fuse(prism([142,32,77.72],[148,38,121.01])).removeSplitter()
    supports['D_RR/shelf']=high;owners['D_RR/shelf']='UpperCarrier'
    floor=prism([-56,-51,109.01],[-26,-42,112.01])
    arm=prism([-44,-46.5,109.01],[-38,-21,112.01])
    post=prism([-44,-27,77.72],[-38,-21,112.01])
    supports['G_TAIL/platform']=floor.fuse(arm).fuse(post).removeSplitter()
    owners['G_TAIL/platform']='UpperCarrier'
    return p,old,supports,owners


def run():
    tick=time.monotonic();p,old,supports,owners=proposal()
    inputs=[OUT/'SourceRetentionCurrent.FCStd',BASE/'mounting-checkpoint/RetentionMountsAssembly.FCStd',
            BASE/'OpenPrototypePlan.FCStd',OUT/'LocalStationsAssembly.FCStd',OUT/'TailLocalCurrent.FCStd',
            OUT/'obstacle-map-current.json',OUT/'source-current-receipt.json',OUT/'source-low-gap-plan.json',
            ROOT/'hardware/reference/manual-stop-p0-2026-09-24/S821-A120.png',
            OUT/'ground-upstream-grip-plan.json',Path(__file__)]
    pins={f.relative_to(ROOT).as_posix():sha(f) for f in inputs}
    previous=json.loads(DEST.read_text()) if DEST.exists() else None
    docs=[];contacts=[];errors=[];outside=[];pairs=0
    result=dict(selected=False,stage_completed=False,physical_pass=False,native_files_changed=0,
        scope='Shared source-zone planning, not whole wiring or finished mounts',source_sha256=pins,
        changed_station=dict(before=old,after=next(r for r in p['stations'] if r['role']=='D_RL')),
        invalidated=['D_RL old case/support/ports and W012-W015 endpoints; these routes were not completed',
            'Old4MTA mounting roots and P_REAR platform; current complete conductor profiles retained only if new supports clear',
            'D_RR and G_TAIL old positions and all associated endpoints/routes; these cannot retain their previous qualification',
            'Upper secondary distribution beams/pads retired together, lower10-station rails retained; G1/G2/F_AUX mounts remain explicitly OPEN'],
        retained_frame_columns=['Spacer1','Spacer2','Spacer3','Spacer4'],
        support_owners=owners,contacts=contacts,errors=errors,outside=outside,
        delivery_gates=['WAGO cavity/lever envelopes','MTA usable factory lengths','S1 supplier fit',
                        'U1 unknown pad map','PETG retention and nominal W068 gap'],
        geometry_acceptance=False,assembly_acceptance=False,
        previous_rejected_proposal=previous,
        plan_revision='Internal source trellis, staggered data rack, vertical west-tail ground; no side-bank-crossing MTA arms',
        inherited_unresolved=['S1 ring6/Spacer4','W068/Spacer3',
            'Moved G_TAIL receiving and TY output paths must be regenerated together',
            'S1 broad operator reservation must distinguish M12 bushing from28mm operator sweep'],
        no_third_proposal_without_root_change=True)
    def progress(s):print(json.dumps(dict(phase=s,seconds=round(time.monotonic()-tick,2),pairs=pairs)),flush=True)
    def overlap(n,s,m,t,basis):
        nonlocal pairs
        if not near(s,t,0):return
        if not s.isValid() or not t.isValid():errors.append(dict(a=n,b=m,error='invalid BRep'));return
        pairs+=1;v=s.common(t).Volume
        if v>1e-6:contacts.append(dict(a=n,b=m,volume_mm3=round(v,6),basis=basis))
    def clearance(n,s,m,t,r,basis):
        nonlocal pairs
        if not near(s,t,r):return
        if not s.isValid() or not t.isValid():errors.append(dict(a=n,b=m,error='invalid distance inputs'));return
        pairs+=1;d=s.distToShape(t)[0]
        if d<r-1e-6:contacts.append(dict(a=n,b=m,distance_mm=round(d,6),required_mm=r,basis=basis))
    try:
        progress('Load current native owners, not old roots')
        docs=[A.openDocument(str(f)) for f in inputs[:5]]
        native,mount,ctx,stations,tail=docs
        fixed={o.Name:o.Shape for o in native.Objects if o.TypeId=='PartDesign::Body'}
        # The secondary distribution upper tier carries OLD station poses.
        # Retire that whole tier, not many contact-shaped notches. Frame load
        # columns and all lower rail bolt bosses/pads remain unmodified.
        for n in ('LeftDistributionCarrier','RightDistributionCarrier'):
            fixed[n]=fixed[n].common(prism([-150,-120,0],[200,120,61]))
        for n in ('LowerCarrier','Spacer1','Spacer2','Spacer3','Spacer4'):
            fixed[n]=mount.getObject(n).Shape
        # Explicit owner substitution, rather than excluding every replaceable
        # support. CommonSourcePlatform is retired; new floors above replace it.
        retired={'UpperCarrier','CommonSourcePlatform','LeftDistributionCarrier','RightDistributionCarrier'}
        for r in json.loads((OUT/'obstacle-map-current.json').read_text())['objects']:
            n=r['name']
            if r['kind'] in ('candidate_station','service_budget') or n in retired or n.startswith('S1_'):continue
            if r['kind']=='replaceable_support':raise AssertionError('Unowned replacement '+n)
            if r['kind']=='delivery_reservation':
                v=r['bounds_mm'];s=prism(v[:3],v[3:]);basis='whole-component PROJECT reservation'
            else:
                ob=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or stations.getObject(n) or mount.getObject(n)
                assert ob is not None and hasattr(ob,'Shape'),n
                s=ob.Shape;basis='retained saved material'
            fixed.setdefault(n,s)
        bodies={r['role']:box(r['centre_mm'],r['size_mm']) for r in p['stations']+p['mta']+p['holders']}
        # Actual S1 pieces preserve the verified whole rotation once.
        spec=p['s1_module']
        for o in ctx.Objects:
            if not o.Name.startswith('S1_') or not hasattr(o,'Shape') or o.Shape.isNull() or 'service' in o.Name.lower():continue
            s=o.Shape.copy();s.rotate(A.Vector(*spec['pivot_mm']),A.Vector(1,0,0),spec['whole_rotation_deg']);s.translate(A.Vector(*spec['translation_mm']))
            if o.Name=='S1_control_CP2':
                # A120:12mm M12 bushing THEN22mm operator. The old28mm-wide
                # cylinder over BOTH was a reservation, not material through
                # the12.5mm panel bore. Keep the28mm operator motion budget.
                s=Part.makeCylinder(6,12,A.Vector(126.2,0,109.25)).fuse(
                    Part.makeCylinder(14,22,A.Vector(126.2,0,121.25)))
            if o.Name.startswith('S1_ring_'):
                ring=next(q for q in spec['rings'] if q['terminal']==int(o.Name[-1]))
                s.rotate(A.Vector(*ring['eye_mm']),A.Vector(0,0,1),ring['ring_rotation_z_deg'])
            bodies[o.Name]=s
        rows=profiles(p);rows.update({r['wire']:(r['segments'],r['OD_mm']/2,None,None) for r in p['s1_routes']})
        ground=json.loads((OUT/'ground-upstream-grip-plan.json').read_text())['row']
        rows['W001']=(ground['segments'],ground['OD_mm']/2,None,None)
        curves={n:(wire(parts),r) for n,(parts,r,_,_) in rows.items()}
        progress('All source cases and actual matched skeleton')
        for n,s in bodies.items():
            for m,t in fixed.items():
                if m in ('UpperCarrier','S1Bracket','LeftDistributionCarrier','RightDistributionCarrier','Spacer1','Spacer2','Spacer3','Spacer4'):
                    overlap(n,s,m,t,'current native owner')
            if n in ('D_RL','D_RR','G_TAIL'):
                for m,t in fixed.items():
                    if m not in ('UpperCarrier','S1Bracket','LeftDistributionCarrier','RightDistributionCarrier','Spacer1','Spacer2','Spacer3','Spacer4'):
                        overlap(n,s,m,t,'changed case versus ALL retained material/reservations')
        names=list(bodies)
        for i,n in enumerate(names):
            for m in names[i+1:]:
                if n.startswith('S1_') and m.startswith('S1_'):continue # supplied assembly interfaces
                overlap(n,bodies[n],m,bodies[m],'shared nominal module allocation, NOT measured purchased material')
        progress('Whole new support allocations versus cases/material/wires')
        torso=ctx.TorsoEnvelope.Shape
        for n,s in supports.items():
            assert s.isValid() and len(s.Solids)==1,n
            v=s.cut(torso).Volume
            if v>1e-6:outside.append(dict(name=n,volume_mm3=v))
            for m,t in bodies.items():overlap(n,s,m,t,'nominal case or saved S1 material')
            for m,t in fixed.items():
                if m==owners[n]:continue # only deliberate new root union
                overlap(n,s,m,t,'retained material or whole-component reservation')
            for m,(curve,r) in curves.items():clearance(n,s,m,curve,r,'whole current conductor profile')
        # The relocated case gets ALL changed entry allowances at once.
        # Four occupied BUS_DATA ports:9mm straight +1.05mm nominal radius.
        # Also conservative top service box; not a manufacturer lever sweep.
        entries={}
        for i in range(1,5):
            a=p['ports'][f'D_RL.{i}']['point_mm']
            entries[f'D_RL.{i}/entry']=Part.makeCylinder(1.05,9,A.Vector(*a),A.Vector(0,1,0))
        entries['D_RL/top_service_budget']=prism([134,40.5,95.5],[164,59.5,111.5])
        entries['D_RR/top_service_budget']=prism([140,10.5,132.5],[170,29.5,148.5])
        for n,s in entries.items():
            v=s.cut(torso).Volume
            if v>1e-6:outside.append(dict(name=n,volume_mm3=v,basis='project service/entry reservation'))
            for m,t in fixed.items():overlap(n,s,m,t,'project entry/service reservation')
            for m,t in bodies.items():
                if m!='D_RL':overlap(n,s,m,t,'project entry/service reservation')
            for m,(curve,r) in curves.items():clearance(n,s,m,curve,r,'project entry/service versus current wire')
        for n,(curve,r) in curves.items():
            for m in ('UpperCarrier','S1Bracket','LeftDistributionCarrier','RightDistributionCarrier','Spacer1','Spacer2','Spacer3','Spacer4'):
                clearance(n,curve,m,fixed[m],r,'whole profile versus actual retained structural owner')
        # Both exits of every MTA stay in the scene through the eight full tails.
        result.update(tested_pairs=pairs,current_profiles=len(curves),fixed_shapes=len(fixed),
            full_MTA_tails=[r['wire'] for r in p['tails'] if r['leg'] in ('FL','FR','RL','RR')],
            support_bounds={n:[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax] for n,s in supports.items()},
            changed_bus_ports={n:r for n,r in p['ports'].items() if n.startswith('D_RL.')},
            restraint_stations_considered=14,
            assembly_gates=['D_RR removable shelf must not cover the rear frame bolt tool axis',
                'Install common rail supports before boards, fit MTA bodies from above, retain both factory tails',
                'P_REAR pillar/beam and MTA strap heads require native attachment and tool qualification',
                'Install data WAGO in vacant lower station; W012-W015 route lengths/relief still OPEN',
                '14 source relief seats/tie heads and fully wired ATO access still OPEN'])
        result['status']='REJECTED_SHARED_SUPPORT_LAYOUT' if contacts or errors or outside else 'SHARED_SPATIAL_PROPOSAL_NO_KNOWN_CONTACTS_ASSEMBLY_OPEN'
    except Exception as exc:
        errors.append(str(exc));result['status']='ERROR_NOT_ACCEPTANCE';raise
    finally:
        for d in docs:A.closeDocument(d.Name)
        assert all(sha(ROOT/n)==h for n,h in pins.items()),'Changed inputs during read-only gate'
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:result.get(k) for k in ('status','tested_pairs','contacts','outside','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()

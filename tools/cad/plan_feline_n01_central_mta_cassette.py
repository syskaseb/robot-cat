"""One central two-tier MTA cassette, before detailed native construction.

Keep each whole three-case branch and both complete factory wires rigid.
Include 24 independent9mm wire seats, two trays and four existing foot roots.
No source/purchased part, lead length or robot motion is changed.
"""
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, sha, prop
from plan_feline_layout import OUT, MODEL, STAGES
from check_feline_leg_body import placement

BRANCHES={'FL':(-95,-14,-34,('W026','W041')),
          'FR':(-32,14,-34,('W037','W042')),
          'RL':(65,-14,-10,('W044','W045')),
          'RR':(90,14,-10,('W052','W053'))}


def main():
    tick=time.monotonic();reader=SavedShapes()
    dest=OUT/'n01-central-mta-cassette-plan.json'
    assert not dest.exists(),'Receive existing result; no unchanged replay'
    manifest=OUT/'n01-shared-probe.json';source=json.loads(manifest.read_text())
    priorpath=OUT/'n01-shared-probe-motion-envelope.json';prior=json.loads(priorpath.read_text())
    assert prior['status']=='CHANGED_SHARED_SCOPE_REJECTED' and len(prior['poses'])==36
    assert sha(ROOT/source['shared_probe'])==source['shared_probe_sha256']
    report=dict(status='RUNNING_CENTRAL_TWO_TIER_CASSETTE',selected=False,N01_complete=False,
        physical_pass=False,native_changed=False,contacts=[],reservation_contacts=[],errors=[],
        envelope_outside=[],wall_budget_failures=[],poses=[],pairs=0,parts={},wire_seats=[],
        reused_unchanged_scope='Pi full3routes/8ends/backbone and BUS static/36pose receipts. Only relocated whole4MTAbranches and new tray/seat reservations checked.',
        changed_cause='Lower transverse four-column bay strikes folded legs and true torso. Rotate whole branches into longitudinal central two-tier cassette below battery, not offsets of individual joints.',
        branch_datums={c:dict(old_centre_mm=[x,0,-34],new_centre_mm=[17.5,y,z],relative_rotation_z_degrees=-90,wires=list(ws)) for c,(x,y,z,ws) in BRANCHES.items()},
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (manifest,priorpath,Path(__file__))},
        assembly=['Install lower tier and its4factory/4custom wire seats on bench; no powered work.',
                  'Install upper tier after lower ties; lower-tier ties are not serviced through the5.5mm tier gap.',
                  'Clamp common cassette to four retained hollow belly-foot stems, not cosmetic shell. Split clamps/actual screws and strength remain unqualified.',
                  'Routine12ATO bank access unchanged. Deep MTA repair: power disconnected, label8outer conductors, remove cassette from underneath without74WAGOoperations. Actual tools/parking/access remain open.'],
        material_candidates=dict(wire_ties_T18I=24,holder_ties_T18I=8,trays=2,foot_split_clamps=4,
            new_electrical_parts=0,stock_selected=False),
        root_basis='Four actual OD18hollow belly-foot stems, existing8M2bolts and load path retained. Collar innerR9.2 provisional fit, wall2.8; split/ears/screws/access require native follow-up.',
        print_budget_mm=252,estimated_tray_extents_mm=[218,104,26.3])
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s scope cap; preserve partial')
    def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
    shapes={};kinds={};owners={};fixed={}
    with zipfile.ZipFile(ROOT/source['shared_probe']) as archive:
        for row in source['parts']:
            s=Part.Shape();s.importBrepFromString(archive.read(row['entry']).decode('utf-8'))
            assert s.isValid() and s.Solids,row['name']
            fixed[row['name']]=s
    for code,(oldx,y,z,ws) in BRANCHES.items():
        old=A.Vector(oldx,0,-34);new=A.Vector(17.5,y,z);rot=A.Rotation(A.Vector(0,0,1),-90)
        T=A.Placement(new-rot.multVec(old),rot)
        names=[f'Ref_Material_MTA_{code}_0_0']+[f'Ref_Material_{w}_Joint_0_0' for w in ws]
        names += [f'Factory:{w}' for w in ws]+[f'CustomPrefix:{w}/custom/start' for w in ws]
        for n in names:
            s=fixed.pop(n);s.Placement=T*s.Placement
            assert s.isValid(),n
            shapes[n]=s;kinds[n]='actual_branch';owners[n]=code
        # Factory20.75mm: two intact9mm lands separated2.75; custom9mm: one.
        for w in ws:
            for n in (f'Factory:{w}',f'CustomPrefix:{w}/custom/start'):
                b=shapes[n].BoundBox;cy=(b.YMin+b.YMax)/2;cz=(b.ZMin+b.ZMax)/2
                assert abs(cy-y)<1e-5 and abs(cz-z)<1e-5
                starts=[b.XMin,b.XMax-9] if n.startswith('Factory:') else [b.XMin]
                for i,x in enumerate(starts):
                    name=f'Seat:{w}:{"factory" if n.startswith("Factory:") else "custom"}:{i}'
                    outer=Part.makeCylinder(4.35,9,A.Vector(x,cy,cz),A.Vector(1,0,0))
                    hole=Part.makeCylinder(2.35,11,A.Vector(x-1,cy,cz),A.Vector(1,0,0))
                    top=box([x-1,cy-5,cz],[x+10,cy+5,cz+5])
                    seat=outer.cut(hole).cut(top)
                    base=box([x,cy-3,z-8.2],[x+9,cy+3,z-3.8])
                    seat=seat.fuse(base).cut(hole).removeSplitter()
                    # Crosswise strap tunnel below full jacket, not through a lever.
                    tunnel=box([x+3.1,cy-5,z-6.5],[x+5.9,cy+5,z-5.1])
                    seat=seat.cut(tunnel).removeSplitter()
                    assert seat.isValid() and len(seat.Solids)==1,name
                    shapes[name]=seat;kinds[name]='seat_reservation';owners[name]=code
                    report['wire_seats'].append(dict(name=name,wire=w,owner_pipe=n,
                        land_x_mm=[x,x+9],axis_mm=[cy,cz],cavity_R_mm=2.35,
                        minimum_project_wall_mm=2,nominal_tie_tunnel_mm=[2.8,1.4],
                        delivered_OD_and_strap_fit_gate=True))
    assert len(report['wire_seats'])==24
    feet={f'BellyFoot{i}':reader.shape(OUT/'FelineBellyFeet.FCStd',f'BellyFoot{i}') for i in range(1,5)}
    foot_centres=[(-75.5,-40),(-75.5,40),(117.5,-40),(117.5,40)]
    for tier,z in (('Lower',-34),('Upper',-10)):
        tray=box([-88,-52,z-10.3],[130,52,z-8])
        for x,y in foot_centres:tray=tray.cut(Part.makeCylinder(9.2,4,A.Vector(x,y,z-11)))
        assert tray.isValid() and len(tray.Solids)==1
        name=tier+'TrayReserve';shapes[name]=tray;kinds[name]='tray_reservation'
    for i,(x,y) in enumerate(foot_centres,1):
        collar=Part.makeCylinder(12,26.3,A.Vector(x,y,-44.3)).cut(Part.makeCylinder(9.2,28,A.Vector(x,y,-45)))
        name=f'FootCollarReserve{i}';shapes[name]=collar;kinds[name]='load_root_reservation'
    report['tray_interfaces']='Seat bottoms and MTA bottom surfaces meet own tier top. Joint case risers/contact patches and split collar bolt stacks still open; no load qualification inferred.'
    motionpath=OUT/'motion-layout.json';motion=json.loads(motionpath.read_text())
    moving_names={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    native=OUT/'FelineInteriorMotion.FCStd'
    for row in motion['inventory']:
        n=row['object']
        if row['kind']=='surface' and n not in moving_names and n not in fixed and (n.startswith(('Ref_Material_P0_','Print_P0_','Battery')) or row['label'].startswith('P0_')):
            if not n.startswith('BatteryFrameHardware'):fixed[n]=reader.shape(native,n)
    fixed.update(feet)
    for i in range(8):fixed[f'FootHardware{i}']=reader.shape(OUT/'FelineBellyFeet.FCStd',f'FrameHardwareNew{i}')
    bounds={n:s.BoundBox for n,s in {**fixed,**shapes}.items()}
    def check(n,s,m,t,pose=None):
        gate()
        if not bounds[n].intersect(t.BoundBox if pose is not None else bounds[m]):return
        report['pairs']+=1
        c=s.common(t);assert c.isNull() or c.isValid(),(n,m)
        if c.Volume>1e-5:
            key='contacts' if kinds[n]=='actual_branch' and (m not in kinds or kinds[m]=='actual_branch') else 'reservation_contacts'
            report[key].append(dict(a=n,b=m,pose=pose,volume_mm3=c.Volume))
    try:
        save()
        for n,s in shapes.items():
            for m,t in fixed.items():check(n,s,m,t)
        # Within a branch, retained supplier joins/owned wire seats unchanged.
        for n,s in shapes.items():
            if kinds[n]!='actual_branch':continue
            for m,t in shapes.items():
                if kinds[m]=='actual_branch' and m>n and owners[n]!=owners[m]:check(n,s,m,t)
                elif kinds[m]!='actual_branch':check(m,t,n,s)
        outer=reader.shape(OUT/'FelineLayoutEnvelope.FCStd','TorsoEnvelope');shell=Part.makeCompound(outer.Shells)
        for n,s in shapes.items():
            gate();diff=s.cut(outer);assert diff.isNull() or diff.isValid(),n
            if diff.Volume>1e-5:report['envelope_outside'].append(dict(object=n,outside_mm3=diff.Volume))
            else:
                gap=s.distToShape(shell)[0]
                if gap<3.65-1e-5:report['wall_budget_failures'].append(dict(object=n,gap_mm=gap))
            b=s.BoundBox;report['parts'][n]=dict(kind=kinds[n],bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],valid=s.isValid())
        save()
        # Stop before36poses if the complete static dependency is already bad.
        if any(report[k] for k in ('contacts','reservation_contacts','envelope_outside','wall_budget_failures')):
            report['status']='CENTRAL_CASSETTE_STATIC_REJECTED_MOTION_NOT_REPEATED'
        else:
            axispath=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axispath.read_text())['axes']
            moving={n:reader.shape(MODEL,n) for n in moving_names}
            corners={n:[A.Vector(x,y,z) for x in (s.BoundBox.XMin,s.BoundBox.XMax) for y in (s.BoundBox.YMin,s.BoundBox.YMax) for z in (s.BoundBox.ZMin,s.BoundBox.ZMax)] for n,s in moving.items()}
            for index,sample in enumerate(motion['poses'][:36]):
                for code,group in motion['membership'].items():
                    aa=[next(a for a in axes if a['code']==code and a['stage']==st) for st in STAGES]
                    tf=placement(aa,sample['legs'][code]['angles_delta_degrees'])
                    for st,names in group.items():
                        for n in names:
                            gate();B=A.BoundBox()
                            for v in corners[n]:B.add(tf[st].multVec(v))
                            near=[m for m in shapes if B.intersect(bounds[m])]
                            if not near:continue
                            s=moving[n].copy();s.Placement=tf[st]*s.Placement;assert s.isValid(),n
                            for m in near:check(m,shapes[m],n,s,index)
                floor=motion['ground_rest_z_mm']+sample['body_drop_mm']
                report['poses'].append(dict(index=index,floor_z_mm=floor,below_floor=[n for n in shapes if bounds[n].ZMin<floor]))
                save();print('pose',index,'pairs',report['pairs'],'contacts',len(report['contacts']),len(report['reservation_contacts']),flush=True)
            report['status']='CENTRAL_CASSETTE_MOTION_REJECTED' if report['contacts'] or report['reservation_contacts'] else 'CENTRAL_CASSETTE_SCOPED_CLEAR_ROOT_BOLTS_JOINT_SEATS_TOOLS_FULL_HARNESS_OPEN'
        report['source_sha256'].update(reader.hashes)
    except Exception as exc:
        report['errors'].append(repr(exc));report['status']='CENTRAL_CASSETTE_INCOMPLETE_ERROR'
    save()
    print(json.dumps({k:report[k] for k in ('status','worker_seconds','pairs','errors','contacts','reservation_contacts','envelope_outside','wall_budget_failures')}),flush=True)


if __name__=='__main__':main()

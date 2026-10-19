"""One constructive underhung-Pi/negative-flank USB service layout.

Both real mouths, first entries/full9 lands, R30 turns, a variable-length
planar spiral and final C1 biarc are planned TOGETHER before CAD changes.
Only mathematics here; exact whole-world/retention/root acceptance is OPEN.
"""
import json,math,sys,time,zipfile,hashlib
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.spatial.distance import cdist
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from fit_feline_current_usb_space import biarc_join,bus_prefix


@lru_cache(maxsize=1)
def constant_inputs():
    plan=json.loads((OUT/'n01-whole-pi-rigid-ports-space.json').read_text())
    usb=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb']
    return plan,usb


def construct(turns,spacing=6.5,ratio=1.):
    plan,usb=constant_inputs()
    pose=dict(next(p for p in plan['proposals'] if p['orientation_index']==0))
    pose['USB_mouth_mm']=list(pose['USB_mouth_mm'])
    positive='--positive-service-deck' in sys.argv
    if positive:
        pose['target_PCB_centre_mm']=[86.,2.,106.]
        pose['USB_mouth_mm']=[pose['USB_mouth_mm'][0],pose['USB_mouth_mm'][1],pose['USB_mouth_mm'][2]+2]
    fore_bay='--fore-coil-bay' in sys.argv
    if fore_bay:
        # Roof hardware retains original104 datum; the WHOLE coil gets a bay
        # west of EthernetX40.5, not a local notch in the cable or component.
        pose['target_PCB_centre_mm'][2]=104.
        pose['USB_mouth_mm'][2]-=2
    alternate='--rear-A-port' in sys.argv
    if alternate:
        # Discrete free socket choice, NOT a translation of a soldered port.
        # Underhung orientation0 has canonical sourceY parallel to worldY.
        contract=json.loads((OUT/'n01-pi-full-port-contract.json').read_text())
        bounds={r['role']:np.array(r['source_bounds_mm']) for r in contract['parts']}
        dy=float(bounds['USB_A_rear'][:,1].mean()-bounds['USB_A_front'][:,1].mean())
        assert abs(dy-18.73)<1e-8
        pose['USB_mouth_mm'][1]+=dy
        pose['data_boot_translation_from_old_port_mm']=[0.,dy,0.]
        pose['data_socket']='USB_A_rear_existing_free_socket'
    p=np.array(pose['USB_mouth_mm']);d=np.array(pose['USB_departure_axis']);edges=[]
    def line(L):
        nonlocal p
        q=p+L*d;edges.append(dict(kind='line',start=p.tolist(),end=q.tolist(),length=L,samples_mm=np.linspace(p,q,max(2,int(L/.2)+1)).tolist()));p=q
    def turn(b,R,angle):
        nonlocal p,d
        b=np.array(b,float);assert abs(b@d)<1e-8
        v=np.linspace(0,angle,max(2,int(R*angle/.2)+1))[:,None]
        samples=p+R*np.sin(v)*d+R*(1-np.cos(v))*b
        edges.append(dict(kind='arc',start=p.tolist(),tangent=d.tolist(),normal=b.tolist(),R=R,angle=angle,length=R*angle,samples_mm=samples.tolist()))
        p=samples[-1];d=math.cos(angle)*d+math.sin(angle)*b
    before='--prebend-grip' in sys.argv
    if positive:
        line(3);entry_after3=p.copy();turn([0,1,0],30,math.pi/2)
        grip0=p.copy();line(9);grip1=p.copy();Pi_prefix_length=sum(e['length'] for e in edges)
        shift=10. if fore_bay and not alternate else 2.1
        alpha=math.acos(1-shift/60);turn([-1,0,0],30,alpha)
        turn([math.cos(alpha),math.sin(alpha),0],30,alpha);assert np.allclose(d,[0,1,0])
        line(2. if fore_bay else 45-p[1])
    else:
        line(3);entry_after3=p.copy();grip0=p.copy()
        if before:line(9)
        grip1=p.copy();a=math.radians(16);turn([0,-math.cos(a),-math.sin(a)],30,math.pi/2)
        if not before:grip0=p.copy();line(9);grip1=p.copy()
        Pi_prefix_length=sum(e['length'] for e in edges)
        k=brentq(lambda v:p[2]-30*math.sin(a)+30*math.cos(a)*(v+1-math.sqrt(1-v*v))-88.,0,.6) if before else .2885
        n=np.array([math.sqrt(1-k*k),-math.sin(a)*k,math.cos(a)*k]);turn(n,30,math.pi/2)
        beta=math.acos(d[0]);b=(np.array([1.,0,0])-d*math.cos(beta))/math.sin(beta);turn(b,30,beta)
    spiral_start=p.copy();r0=30.1;b=spacing/(2*math.pi);theta0=math.pi-math.atan(b/r0) if positive else -math.atan(r0/b)
    centre=p-np.array([r0*math.cos(theta0),r0*math.sin(theta0),0])
    angle=2*math.pi*turns;v=np.linspace(0,angle,max(161,int(angle*(r0+spacing)/.2)+1));r=r0+b*v;t=theta0-v if positive else theta0+v
    points=centre+np.column_stack([r*np.cos(t),r*np.sin(t),np.zeros(len(t))])
    derivative=np.column_stack([b*np.cos(t)+r*np.sin(t),b*np.sin(t)-r*np.cos(t),np.zeros(len(t))]) if positive else np.column_stack([b*np.cos(t)-r*np.sin(t),b*np.sin(t)+r*np.cos(t),np.zeros(len(t))])
    tangent=derivative[-1]/np.linalg.norm(derivative[-1]);speed0=derivative[0]/np.linalg.norm(derivative[0]);assert np.linalg.norm(speed0-d)<1e-8
    integral=lambda x:.5*(x*math.sqrt(x*x+b*b)+b*b*math.asinh(x/b))
    spiral_length=(integral(float(r[-1]))-integral(r0))/b
    minimum_R=(r0*r0+b*b)**1.5/(r0*r0+2*b*b);assert minimum_R>=30
    # BUS quarter bends mostly inboard, with4deg upward clock so the full
    # final9 land stays above the actual bank rather than inside its roof.
    clock=3. if fore_bay else 4.
    q,bust,bus_samples,BL=bus_prefix(usb['bus_jacket_mouth_mm'],math.pi/2,math.pi-math.radians(clock))
    bus_grip=None
    if '--bus-prebend-grip' in sys.argv:
        mouth=np.array(usb['bus_jacket_mouth_mm']);axis=np.array([0.,-1.,0]);normal=np.array([-math.cos(math.radians(4)),0,math.sin(math.radians(4))])
        start=mouth+12*axis;v=np.linspace(0,math.pi/2,241)[:,None]
        arc=start+30*np.sin(v)*axis+30*(1-np.cos(v))*normal
        bus_samples=np.vstack([np.linspace(mouth,start,61),arc]);q=arc[-1];bust=normal;BL=12+30*math.pi/2
        bus_grip=[(mouth+3*axis).tolist(),start.tolist()]
    if ('--source-underpass' in sys.argv and '--direct-fore-return' not in sys.argv) or '--socket-underpass' in sys.argv:
        waypoint=np.array([-1.63941691,-13.5762545,92.]);wt=np.array([-.3439621,-.93574768,-.07788684]);wt/=np.linalg.norm(wt)
        if '--socket-underpass' in sys.argv:
            # Witness of the NEW discrete socket, not the old coil's crossing.
            waypoint=np.array([-5.2165739268,6.2071397381,90.])
            witness=biarc_join(points[-1],tangent,q,-bust,ratio)
            # Common downward/negativeY escape at the received crossing.
            wt=np.array([-.58,-.81,-.08]);wt/=np.linalg.norm(wt)
        one=biarc_join(points[-1],tangent,waypoint,wt,1.)
        two=biarc_join(waypoint,wt,q,-bust,ratio)
        if one is None or two is None:return None
        joined=dict(arcs=one['arcs']+two['arcs'],length_mm=one['length_mm']+two['length_mm'],minimum_R_mm=min(one['minimum_R_mm'],two['minimum_R_mm']),
            source_underpass_point_mm=waypoint.tolist(),source_underpass_tangent=wt.tolist())
    else:joined=biarc_join(points[-1],tangent,q,-bust,ratio)
    if joined is None:return None
    L=sum(e['length'] for e in edges)+spiral_length+joined['length_mm']+BL
    return dict(pose=pose,edges=edges,connector_ratio=ratio,BUS_clock_deg=clock,Pi_full9_mm=[grip0.tolist(),grip1.tolist()],Pi_grip_before_bend=before,Pi_first3_mm=entry_after3.tolist(),
        Pi_prefix_length_mm=Pi_prefix_length,spiral=dict(start_mm=spiral_start.tolist(),centre_mm=centre.tolist(),inner_R_mm=r0,
        radial_increase_per_turn_mm=spacing,theta0_rad=theta0,turns=turns,points_mm=points.tolist(),minimum_continuous_R_mm=minimum_R,length_mm=spiral_length),
        connector=joined,BUS_prefix_samples_mm=bus_samples.tolist(),BUS_full9_before_bend_mm=bus_grip,BUS_prefix_length_mm=BL,BUS_exit_mm=q.tolist(),BUS_outgoing_tangent=bust.tolist(),
        whole_external_length_mm=L,minimum_piece_R_mm=min(30.,minimum_R,joined['minimum_R_mm']))


def main():
    tick=time.monotonic();positive='--positive-service-deck' in sys.argv
    coupled='--coupled-connector' in sys.argv
    guarded='--guard-whole-pi' in sys.argv
    dest=OUT/('n01-free-rear-A-port-underpass-usb-plan.json' if '--socket-underpass' in sys.argv else 'n01-free-rear-A-port-whole-usb-plan.json' if '--rear-A-port' in sys.argv else 'n01-whole-Pi-guarded-fore-return-usb-plan.json' if guarded else 'n01-fore-coil-direct-return-usb-plan.json' if '--direct-fore-return' in sys.argv else 'n01-fore-coil-bay-usb-plan.json' if '--fore-coil-bay' in sys.argv else 'n01-common-positive-deck-full-grips-usb-plan.json' if '--bus-prebend-grip' in sys.argv else 'n01-common-upper-deck-underpass-usb-plan.json' if '--source-underpass' in sys.argv else 'n01-common-upper-deck-coupled-spiral-usb-plan.json' if coupled else 'n01-common-upper-deck-positive-spiral-usb-plan.json' if positive else 'n01-underhung-pi-pregrip-spiral-usb-plan.json' if '--prebend-grip' in sys.argv else 'n01-underhung-pi-spiral-usb-plan.json');assert not dest.exists()
    files=[Path(__file__),Path(__file__).with_name('fit_feline_current_usb_space.py'),OUT/'n01-whole-pi-rigid-ports-space.json',OUT/'n01-physical-cable-contract.json']
    if '--rear-A-port' in sys.argv:files.append(OUT/'n01-pi-full-port-contract.json')
    result=dict(status='RUNNING_COMMON_SPIRAL_USB_MATH',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        candidate=None,brackets=[],length_roots=[],N01_complete=False,selected=False,physical_pass=False,
        full_grips_material_roots_all_current_harness_and_exact_BRep_OPEN=True)
    boxes=[]
    if guarded:
        import Part
        p=OUT/'n01-fore-coil-service-deck-received.json';receipt=json.loads(p.read_text())
        arc=ROOT/receipt['changed_geometry_archive'];assert sha(arc)==receipt['changed_geometry_archive_sha256']
        result['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p),arc.relative_to(ROOT).as_posix():sha(arc)})
        with zipfile.ZipFile(arc) as z:
            for row in receipt['geometry']:
                if row['role'] not in ('PiRigid','FR_P','RR_P','P_REAR') or row['name']=='PiBudget:USB_A_data_boot':continue
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());b=s.BoundBox
                boxes.append((row['name'],np.array([b.XMin,b.YMin,b.ZMin]),np.array([b.XMax,b.YMax,b.ZMax])))
        result['guarded_whole_parts']=[r[0] for r in boxes]
        result['conservative_bbox_exclusion_not_actual_collision_verdict']=True
    for ratio in np.geomspace(.1,10,41) if coupled else [1.]:
        previous=None
        for T in np.linspace(.05 if '--direct-fore-return' in sys.argv else .3 if positive or '--prebend-grip' in sys.argv else .75,1.1,81 if positive or '--prebend-grip' in sys.argv else 36):
            c=construct(float(T),ratio=float(ratio));delta=c['whole_external_length_mm']-452
            result['brackets'].append(dict(turns=float(T),ratio=float(ratio),whole_length_mm=c['whole_external_length_mm'],minimum_R_mm=c['minimum_piece_R_mm']))
            if previous and delta*previous[1]<=0:
                root=brentq(lambda v:construct(v,ratio=float(ratio))['whole_external_length_mm']-452,previous[0],float(T),xtol=1e-11)
                c=construct(root,ratio=float(ratio));rec=dict(turns=root,ratio=float(ratio),minimum_R_mm=c['minimum_piece_R_mm'])
                if c['minimum_piece_R_mm']>=30:
                    whole=np.vstack([*(e['samples_mm'] for e in c['edges']),c['spiral']['points_mm'],
                        *[a['points_mm'][::-1] if a['reverse'] else a['points_mm'] for a in c['connector']['arcs']],c['BUS_prefix_samples_mm'][::-1]])
                    along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(whole,axis=0),axis=1))]
                    distance=cdist(whole,whole);distance[np.abs(along[:,None]-along[None,:])<=12]=1e6
                    c['sampled_self_axis_gap_mm']=float(distance.min());c['self_clearance_continuous_and_world_gates_OPEN']=True
                    rec['sampled_self_axis_gap_mm']=c['sampled_self_axis_gap_mm']
                    if c['sampled_self_axis_gap_mm']>=5.2:
                        blockers=[]
                        for name,lo,hi in boxes:
                            gaps=np.linalg.norm(np.maximum(np.maximum(lo-whole,whole-hi),0),axis=1)
                            if gaps.min()<3.86:blockers.append(dict(name=name,sampled_axis_to_box_mm=float(gaps.min())))
                        rec['conservative_whole_part_exclusions']=blockers
                        if not blockers:result['candidate']=c
                result['length_roots'].append(rec)
                if result['candidate']:break
            previous=(float(T),delta)
        if result['candidate']:break
    result['status']='COMPLETE_USB500_SPIRAL_MATH_CANDIDATE_EXACT_GATES_OPEN' if result['candidate'] else 'SPIRAL_USB_COMMON_MATH_REQUIRES_CAUSE_CHANGE_NOT_N01'
    result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    c=result['candidate'];print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],candidate=None if not c else
        dict(length=c['whole_external_length_mm'],R=c['minimum_piece_R_mm'],self_axis=c['sampled_self_axis_gap_mm'],turns=c['spiral']['turns'],centre=c['spiral']['centre_mm']))),flush=True)


if __name__=='__main__':main()

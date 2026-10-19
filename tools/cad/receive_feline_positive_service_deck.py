"""ONE common positive service deck, whole USB and open saddles before N03.

UnderhungPi at roof datum, only3positive upperWAGO one lower level,
all7Pi port prefixes, fullUSB500+2whole openPETG/selectedT18I grip kits.
No cylindrical clamp invented around a flexible cable, no native selection.
"""
import json,math,os,sys,time,zipfile,hashlib
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import make_interp_spline
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_common_space_context import current,is_jacket
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from fit_feline_current_usb_space import planned_pi_transform
from feline_cubic_curvature import extrema


def circle_arc(start,t,n,R,angle):
    p=np.array(start,float);t=np.array(t,float);n=np.array(n,float)
    at=lambda a:p+R*math.sin(a)*t+R*(1-math.cos(a))*n
    return Part.Arc(A.Vector(*p),A.Vector(*at(angle/2)),A.Vector(*at(angle))).toShape()


def pipe(edges,radius):
    path=Part.Wire(edges);t=edges[0].tangentAt(edges[0].FirstParameter);start=edges[0].valueAt(edges[0].FirstParameter)
    s=path.makePipeShell([Part.Wire([Part.makeCircle(radius,start,t)])],True,False)
    expected=math.pi*radius**2*path.Length
    assert s.isValid() and len(s.Solids)==1 and s.Volume>0 and abs(s.Volume-expected)<expected*1e-4,(s.Volume,expected)
    return s,path


def usb_edges(c,contract):
    edges=[]
    for row in c['edges']:
        if row['kind']=='line':e=Part.makeLine(A.Vector(*row['start']),A.Vector(*row['end']))
        else:e=circle_arc(row['start'],row['tangent'],row['normal'],row['R'],row['angle'])
        edges.append(e)
    p=c['spiral'];L=2*math.pi*p['turns'];v=np.linspace(0,L,len(p['points_mm']));r=p['inner_R_mm']+p['radial_increase_per_turn_mm']/(2*math.pi)*v
    b=p['radial_increase_per_turn_mm']/(2*math.pi);a=p['theta0_rad']-v
    derivative=np.column_stack([b*np.cos(a)+r*np.sin(a),b*np.sin(a)-r*np.cos(a),np.zeros(len(a))])
    spline=make_interp_spline(v,p['points_mm'],k=3,bc_type=([(1,derivative[0])],[(1,derivative[-1])]))
    curvature=extrema(spline.t,spline.c);assert curvature['regular'] and curvature['minimum_radius_mm']>=30
    knots,mults=np.unique(spline.t,return_counts=True);curve=Part.BSplineCurve()
    curve.buildFromPolesMultsKnots([A.Vector(*p) for p in spline.c],mults.tolist(),knots.tolist(),False,3)
    edges.append(curve.toShape())
    for row in c['connector']['arcs']:
        e=circle_arc(row['start_mm'],row['start_tangent'],row['normal'],row['R_mm'],row['angle_rad'])
        if row['reverse']:e.reverse()
        edges.append(e)
    mouth=np.array(contract['bus_jacket_mouth_mm']);d=np.array([0.,-1,0]);clock=math.radians(c.get('BUS_clock_deg',4.));n=np.array([-math.cos(clock),0,math.sin(clock)])
    start=mouth+3*d;end=start+30*d+30*n;tip=end+9*n
    bus=[Part.makeLine(A.Vector(*mouth),A.Vector(*start)),circle_arc(start,d,n,30,math.pi/2),Part.makeLine(A.Vector(*end),A.Vector(*tip))]
    for e in bus[::-1]:e=e.copy();e.reverse();edges.append(e)
    return edges,curvature,(end,tip,n)


def open_grip(start,axis,side,band_at):
    """Flat2mmPETG side pad and rectangular tie, not a rigid pipe clamp.

    local X=wire axis, Y=chosen pad/head side, Z=cross-height.
    A5.2mm-high flat side pad gives a7.6mm full band envelope.
    """
    t=np.array(axis,float);t/=np.linalg.norm(t);u=np.array(side,float);u-=t*(u@t);u/=np.linalg.norm(u);v=np.cross(t,u)
    rot=np.column_stack([t,u,v]);tf=placement(rot,np.asarray(start,float))
    def box(lo,hi):
        s=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo));s.Placement=tf*s.Placement;return s
    pad=box([0,2.5,-2.6],[9,4.5,2.6])
    outer=box([band_at-1.25,-3.7,-3.8],[band_at+1.25,5.7,3.8])
    inner=box([band_at-1.35,-2.5,-2.6],[band_at+1.35,4.5,2.6])
    band=outer.cut(inner);assert band.isValid() and len(band.Solids)==1
    head=box([band_at-2.5,5.7,-2.65],[band_at+2.5,10.,2.65])
    return dict(pad=pad,band=band,head=head)


def reused_internal_pair(a,b,roles):
    """Reuse a rigid assembly or one grip kit, NEVER different new cables."""
    return roles[a]==roles[b] and roles[a]!='PiFlexible'


def intentional_mate(a,b):
    for wire,rigid in ((a,b),(b,a)):
        if wire.startswith('PiGPIO:') and rigid in ('PiBudget:GPIO1992OccupiedHousing','PiBudget:GPIO_header'):return True
        if wire.startswith('PiPower:') and rigid=='PiBudget:RetainedK1474Boot':return True
        if wire=='USB500:whole' and rigid in ('PiBudget:USB_A_data_boot','CurrentBUS:USB_C_Overmould'):return True
    return False


def main():
    fore='--fore-bay' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-fore-coil-service-deck-received.json' if fore else 'n01-positive-service-deck-received.json');assert not dest.exists()
    world,parts,meta,pins,docs=current();planfile=OUT/('n01-fore-coil-direct-return-usb-plan.json' if fore else 'n01-common-upper-deck-underpass-usb-plan.json');d=json.loads(planfile.read_text())
    assert d['status']=='COMPLETE_USB500_SPIRAL_MATH_CANDIDATE_EXACT_GATES_OPEN';c=d['candidate']
    contractfile=OUT/'n01-physical-cable-contract.json';contract=json.loads(contractfile.read_text())['usb']
    endfile=OUT/'n01-shared-routing-boundaries.json';ends=json.loads(endfile.read_text())['endpoints']
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (planfile,contractfile,endfile,Path(__file__))})
    groups={'FR_P','RR_P','P_REAR'};pi={n:s for n,s in parts.items() if meta[n].get('group')=='PiUpper'}
    moved={n:s for n,s in parts.items() if meta[n].get('group') in groups};own={**pi,**moved}
    changed={};cm={};roles={};tf=planned_pi_transform(c['pose'],pi['Ref_Material_Pi4NominalPCB_0_0'].BoundBox.Center)
    for n,s in pi.items():
        if is_jacket(n,meta[n]):continue
        q=s.copy();q.Placement=tf*q.Placement;assert q.isValid() and q.Solids
        changed[n]=q;cm[n]=dict(meta[n]);roles[n]='PiRigid'
    for n,s in moved.items():
        q=s.copy();q.translate(A.Vector(0,0,-8));changed[n]=q;cm[n]=dict(meta[n]);roles[n]=meta[n]['group']
    new_ends=[]
    for e in ends:
        if e.get('group')!='Pi4':continue
        name='PiGPIO:'+e['endpoint'] if e.get('endpoint','').startswith('PI.H') else 'PiPower:'+e['wire']
        if name not in pi:continue
        p=e.get('jacket_routing_point_mm',e.get('point_mm'));axis=e.get('jacket_departure_axis',e.get('departure_axis'))
        q=tf.multVec(A.Vector(*p));t=tf.Rotation.multVec(A.Vector(*axis));t.normalize()
        if name.startswith('PiGPIO:'):
            desired=A.Vector(-1,1 if e['endpoint'] in ('PI.H6','PI.H11') else -1,0);R=10.;first=1.5;radius=.7
        else:desired=A.Vector(0,0,-1);R=15.9 if e['wire']=='W079' else 12.4;first=3.;radius=1.05
        # Recover actual current saved jacket radius, never thin it to fit.
        radii=[float(f.Surface.Radius) for f in pi[name].Faces if type(f.Surface).__name__=='Cylinder' and f.Surface.Radius<5]
        if radii:radius=min(radii)
        b=desired-t*desired.dot(t);b.normalize();start=q+t*first;end=start+t*R+b*R;tip=end+b*9
        es=[Part.makeLine(q,start),circle_arc(list(start),list(t),list(b),R,math.pi/2),Part.makeLine(end,tip)]
        s,path=pipe(es,radius);changed[name]=s;cm[name]=dict(kind='proposal_wire',wire=e['wire']);roles[name]='PiFlexible'
        new_ends.append(dict(id=e['id'],point_mm=list(q),axis=list(t),bend=list(b),R_mm=R,radius_mm=radius,first_mm=first,full9_mm=[list(end),list(tip)]))
    assert len(new_ends)==7
    es,curve_proof,bus=usb_edges(c,contract);full,path=pipe(es,2.5);assert abs(path.Length-452)<.001,path.Length
    changed['USB500:whole']=full;cm['USB500:whole']=dict(kind='proposal_wire');roles['USB500:whole']='USB'
    gripdata=[('Pi',c['Pi_full9_mm'][0],np.array(c['Pi_full9_mm'][1])-c['Pi_full9_mm'][0],[1,0,0],4.5),
              ('BUS',bus[0],bus[2],[0,1,0],2.)]
    for label,p,t,side,at in gripdata:
        for suffix,s in open_grip(p,t,side,at).items():
            name='USBGrip:'+label+':'+suffix;changed[name]=s;roles[name]='USBGrip:'+label
            cm[name]=dict(kind='project_stock_reservation' if suffix in ('band','head') else 'proposal_material')
    retired_bus=[n for n in parts if n.startswith('CurrentBUS:USB_C') and is_jacket(n,meta[n])]
    fixed={n:s for n,s in parts.items() if n not in own and n not in retired_bus}
    removed=[]
    if fore:
        # N01 topology proposal only: lower crossbar/root and full backplate
        # remain, the former horizontal upper rail through GPIO is replaced.
        n='CurrentBUS:BUS_UpperPositiveRoot';assert n in fixed
        removed.append(n);fixed.pop(n)
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'));query=SolidQueries()
    result=dict(status='RUNNING_COMMON_POSITIVE_SERVICE_DECK',source_sha256=pins,changed_parts=list(changed),retired_BUS_USB_prefixes=retired_bus,
        moved_positive_WAGO_groups=sorted(groups),negative_WAGO_UNCHANGED=True,Pi_pose=c['pose'],new_Pi_endpoints=new_ends,
        USB_whole_BRep_length_mm=path.Length,USB_spiral_continuous_curvature=curve_proof,USB_full9_Pi=c['Pi_full9_mm'],
        USB_full9_BUS=[bus[0].tolist(),bus[1].tolist()],full_USB_selected_head_mm=[4.3,5.3,5.],grip_type='open2mmPETG_side_pad+full_selected_T18I_band/head',
        checks=[],failures=[],errors=[],N01_complete=False,physical_pass=False,selected=False,native_changed=False,
        all123_capacity_all_roots_head_motion_skin_current_factory_harness_still_OPEN=True,
        changed_printed_supports=removed,BUS_replacement_load_path_qualification_OPEN=bool(removed))
    archive=dest.with_suffix('.breps.zip');result['changed_geometry_archive']=archive.relative_to(ROOT).as_posix();result['geometry']=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(changed.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            result['geometry'].append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=cm[n].get('kind'),role=roles[n]))
    result['changed_geometry_archive_sha256']=sha(archive)
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def check(a,b,gap,minimum):
        r=dict(a=a,b=b,gap_mm=gap,minimum_mm=minimum,ok=bool(gap>=minimum-1e-6));result['checks'].append(r)
        if not r['ok']:result['failures'].append(r)
        save()
    save()
    try:
        for n,s in changed.items():
            if time.monotonic()-tick>235:raise TimeoutError('Changed whole-interface pairs saved; not a rejection')
            cut=s.copy().cut(outer);assert cut.isNull() or cut.isValid()
            if cut.Volume>1e-5:result['failures'].append(dict(a=n,b='outer',outside_volume_mm3=cut.Volume));save()
            else:check(n,'outer',float(s.distToShape(outer.Shells[0])[0]),3.25)
            targets=dict(fixed)
            targets.update({k:v for k,v in changed.items() if k!=n and not reused_internal_pair(n,k,roles)})
            mates={'PiBudget:GPIO1992OccupiedHousing','PiBudget:GPIO_header'} if n.startswith('PiGPIO:') else {'PiBudget:RetainedK1474Boot'} if n.startswith('PiPower:') else {'PiBudget:USB_A_data_boot','CurrentBUS:USB_C_Overmould'} if n=='USB500:whole' else set()
            if n=='USB500:whole':mates|={k for k in changed if k.startswith('USBGrip:') and not k.endswith(':head')}
            if n.startswith('USBGrip:') and not n.endswith(':head'):mates.add('USB500:whole')
            for other,t in targets.items():
                if other in mates or intentional_mate(n,other):continue
                minimum=pair_spacing(n,cm[n],other,cm.get(other,meta.get(other,{})))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                if not t.Solids:
                    result['failures'].append(dict(a=n,b=other,reason='curve-only physical harness budget OPEN, not actual-solid contact'));save();continue
                q=s
                if other==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                check(n,other,query.distance(q,t),minimum)
            for p in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                check(n,'motion:'+p['name']+':'+str(p['pose']),query.distance(q,world.rest[p['name']]),1.25)
            print('COMMON_SERVICE',n,'open_or_failures',len(result['failures']),flush=True)
        result['status']='COMMON_SERVICE_DECK_NEW_INTERFACES_RECEIVED_N01_OPEN' if not result['failures'] else 'COMMON_SERVICE_DECK_NEW_INTERFACES_REQUIRE_CAUSE_REVIEW'
    except Exception as exc:result.update(status='PARTIAL_COMMON_SERVICE_DECK_RECEIPT');result['errors'].append(repr(exc))
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],checks=len(result['checks']),failures=len(result['failures']),errors=result['errors'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()

"""Whole vertical under-bank service bay, not another roof spiral offset.

Retain500mm cable,452 project jacket allowance, R>=30, both full9 grips.
All Pi rigid parts enter proposal guard before selecting a whole curve.
No selected/native geometry or physical qualification is changed.
"""
import json,math,time,zipfile,hashlib,os,sys
from functools import lru_cache
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.optimize import brentq
from scipy.spatial import cKDTree
from fit_feline_current_usb_space import biarc_join
from plan_feline_layout import OUT
from check_main_p0_placement import ROOT,sha
from feline_atomic_save import save_json
from receive_feline_global_case_candidates import placement


@lru_cache(maxsize=1)
def inputs():
    prior=json.loads((OUT/'n01-fore-coil-direct-return-usb-plan.json').read_text())['candidate'];pose=prior['pose']
    usb=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb']
    return pose,usb


def construct(turns,ratio):
    pose,usb=inputs()
    q=np.array(pose['USB_mouth_mm']);d=np.array([-1.,0,0]);beta=math.radians(8)
    normal=np.array([0.,-math.sin(beta),-math.cos(beta)])
    end=q+12*d+30*d+30*normal
    R=35. if '--allocated-70mm-bay' in sys.argv else 30.1
    b=8/(2*math.pi);gamma=beta-math.atan(b/R)
    n=np.array([0.,-math.cos(gamma),math.sin(gamma)])
    v=normal-n*float(normal@n);v/=np.linalg.norm(v);u=np.cross(v,n)
    assert np.allclose((R*v+b*n)/math.hypot(R,b),normal)
    centre=end-R*u;t=np.linspace(0,2*math.pi*turns,1801)
    points=centre+R*(np.cos(t[:,None])*u+np.sin(t[:,None])*v)+b*t[:,None]*n
    tangent=R*(-math.sin(t[-1])*u+math.cos(t[-1])*v)+b*n;tangent/=np.linalg.norm(tangent)
    bus=np.array(usb['bus_jacket_mouth_mm']);out=np.array([0.,-1,0]);clock=math.radians(3)
    bn=np.array([-math.cos(clock),0,math.sin(clock)])
    grip0=bus+33*out+30*bn;grip1=grip0+9*bn
    connector=biarc_join(points[-1],tangent,grip1,-bn,ratio)
    if connector is None:return None
    length=2*(12+30*math.pi/2)+math.hypot(R,b)*2*math.pi*turns+connector['length_mm']
    a=np.linspace(0,math.pi/2,301)[:,None]
    source=np.vstack([np.linspace(q,q+12*d,61),q+12*d+30*np.sin(a)*d+30*(1-np.cos(a))*normal])
    buspoints=np.vstack([np.linspace(bus,bus+3*out,16),bus+3*out+30*np.sin(a)*out+30*(1-np.cos(a))*bn,np.linspace(grip0,grip1,46)])
    return dict(geometry_kind='vertical_helical_service_bay',pose=pose,source_normal=normal.tolist(),source_mouth=q.tolist(),source_helix_start=end.tolist(),
        Pi_full9_mm=[(q+3*d).tolist(),(q+12*d).tolist()],BUS_full9_mm=[grip0.tolist(),grip1.tolist()],BUS_clock_deg=3.,
        helix=dict(R_mm=R,pitch_mm=8.,turns=turns,centre_mm=centre.tolist(),u=u.tolist(),v=v.tolist(),n=n.tolist(),points_mm=points.tolist()),
        connector=connector,source_samples_mm=source.tolist(),BUS_prefix_samples_mm=buspoints.tolist(),
        whole_external_length_mm=length,minimum_piece_R_mm=min(30.,(R*R+b*b)/R,connector['minimum_R_mm']))


def geometry(c,contract):
    from receive_feline_positive_service_deck import circle_arc
    q=np.array(c['source_mouth']);d=np.array([-1.,0,0]);n=np.array(c['source_normal'])
    es=[Part.makeLine(A.Vector(*q),A.Vector(*(q+12*d))),circle_arc(q+12*d,d,n,30,math.pi/2)]
    h=c['helix'];u,v,n=map(np.array,(h['u'],h['v'],h['n']))
    helix=Part.makeHelix(h['pitch_mm'],h['pitch_mm']*h['turns'],h['R_mm'])
    helix.Placement=placement(np.column_stack([u,v,n]),np.array(h['centre_mm']))*helix.Placement
    es.extend(helix.Edges)
    for a in c['connector']['arcs']:
        e=circle_arc(a['start_mm'],a['start_tangent'],a['normal'],a['R_mm'],a['angle_rad'])
        if a['reverse']:e.reverse()
        es.append(e)
    bus=np.array(contract['bus_jacket_mouth_mm']);t=np.array([0.,-1,0]);bn=np.array(c['BUS_full9_mm'][1])-c['BUS_full9_mm'][0];bn/=9
    p=bus+3*t;g0,g1=map(np.array,c['BUS_full9_mm'])
    last=[Part.makeLine(A.Vector(*bus),A.Vector(*p)),circle_arc(p,t,bn,30,math.pi/2),Part.makeLine(A.Vector(*g0),A.Vector(*g1))]
    for e in last[::-1]:e=e.copy();e.reverse();es.append(e)
    return es,dict(regular=True,minimum_radius_mm=c['minimum_piece_R_mm'],method='Analytic circular arcs and circular helix'),(g0,g1,bn)


def main():
    tick=time.monotonic();dest=OUT/('n01-vertical-allocated-70mm-usb-plan.json' if '--allocated-70mm-bay' in sys.argv else 'n01-vertical-service-bay-usb-plan.json');assert not dest.exists()
    source=OUT/'n01-fore-coil-service-deck-received.json';r=json.loads(source.read_text());arc=ROOT/r['changed_geometry_archive'];assert sha(arc)==r['changed_geometry_archive_sha256']
    boxes=[]
    with zipfile.ZipFile(arc) as z:
        for row in r['geometry']:
            if row['role']!='PiRigid' or row['name']=='PiBudget:USB_A_data_boot':continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());bb=s.BoundBox
            boxes.append((row['name'],np.array([bb.XMin,bb.YMin,bb.ZMin]),np.array([bb.XMax,bb.YMax,bb.ZMax])))
    result=dict(status='RUNNING_WHOLE_VERTICAL_USB_BAY',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (source,arc,Path(__file__),OUT/'n01-fore-coil-direct-return-usb-plan.json',OUT/'n01-physical-cable-contract.json')},candidate=None,length_roots=[],N01_complete=False,selected=False,physical_pass=False)
    for ratio in np.geomspace(.1,10,41):
        previous=None
        for turns in np.linspace(.6,1.5,91):
            c=construct(float(turns),float(ratio))
            if c is None:continue
            delta=c['whole_external_length_mm']-452
            if previous and delta*previous[1]<=0:
                root=brentq(lambda t:construct(t,float(ratio))['whole_external_length_mm']-452,previous[0],float(turns),xtol=1e-10)
                c=construct(root,float(ratio));rec=dict(turns=root,ratio=float(ratio),R_mm=c['minimum_piece_R_mm'])
                if c['minimum_piece_R_mm']>=30:
                    whole=np.vstack([c['source_samples_mm'],c['helix']['points_mm'],*[a['points_mm'][::-1] if a['reverse'] else a['points_mm'] for a in c['connector']['arcs']],c['BUS_prefix_samples_mm'][::-1]])
                    along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(whole,axis=0),axis=1))]
                    # KD pairs may include neighbours; exclude only local12mm.
                    pairs=cKDTree(whole).query_pairs(5.5,output_type='ndarray')
                    bad=pairs[np.abs(along[pairs[:,0]]-along[pairs[:,1]])>12] if len(pairs) else pairs
                    rec['nonlocal_near_axis_pairs']=len(bad)
                    blockers=[]
                    if not len(bad):
                        for name,lo,hi in boxes:
                            gap=np.linalg.norm(np.maximum(np.maximum(lo-whole,whole-hi),0),axis=1).min()
                            if gap<3.86:blockers.append(dict(name=name,axis_to_box_mm=float(gap)))
                        rec['conservative_whole_Pi_exclusions']=blockers
                        if not blockers:result['candidate']=c
                result['length_roots'].append(rec)
                if result['candidate']:break
            previous=(float(turns),delta)
        if result['candidate']:break
    result.update(status='COMPLETE_USB500_VERTICAL_MATH_CANDIDATE_EXACT_GATES_OPEN' if result['candidate'] else 'VERTICAL_USB_BAY_NO_WHOLE_CANDIDATE_NOT_INFEASIBILITY',worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    c=result['candidate'];print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],roots=len(result['length_roots']),candidate=None if not c else dict(length=c['whole_external_length_mm'],R=c['minimum_piece_R_mm'],turns=c['helix']['turns']))),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()

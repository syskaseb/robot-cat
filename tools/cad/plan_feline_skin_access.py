"""Shared skin access plan from all36 actual mesh poses and exact witnesses.

Mesh/bounding reservations are DESIGN KEEP-OUTS, never collision proofs.
The next native bay geometry still needs a real-material motion check.
"""
import json,time,pickle,math
from pathlib import Path
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,sha,SavedShapes
from plan_feline_layout import BASE,OUT,STAGES,transforms,apply
from build_feline_torso_panels import TOPS
from build_feline_layout_envelope import STATIONS,section_coefficients


def loft_inside(v,inner=False,margin=0):
    """Halfplanes of actual ruled station polygons; planning only."""
    sections=[];xx=[r[0] for r in STATIONS]
    for (_,w,_),top in zip(STATIONS,TOPS):
        h=top+48;c,z=section_coefficients(w,h);q=np.column_stack((c*w/2,z*h/2))
        if inner:
            offsets=[]
            for i,p in enumerate(q):
                a=p-q[i-1];b=q[(i+1)%len(q)]-p
                n1=np.array([-a[1],a[0]])/np.linalg.norm(a);n2=np.array([-b[1],b[0]])/np.linalg.norm(b)
                offsets.append(np.linalg.solve([n1,n2],[1,1]))
            q=q+2*np.array(offsets)
        q[:,1]+=(top-48)/2;sections.append(q)
    if inner:xx[0]-=3;xx[-1]+=3
    x=v[:,0];valid=(x>=xx[0]+margin)&(x<=xx[-1]-margin)
    y=[np.interp(x,xx,[q[i,0] for q in sections]) for i in range(len(sections[0]))]
    z=[np.interp(x,xx,[q[i,1] for q in sections]) for i in range(len(sections[0]))]
    for i in range(len(y)):
        j=(i+1)%len(y);dy=y[j]-y[i];dz=z[j]-z[i]
        valid&=dy*(v[:,2]-z[i])-dz*(v[:,1]-y[i])>=margin*np.sqrt(dy*dy+dz*dz)-1e-6
    return valid


def skin_band(v):return loft_inside(v,False,-3)&~loft_inside(v,True,3)


def main():
    tick=time.monotonic();motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
    receiptfile=OUT/'torso-panel-interfaces.json';receipt=json.loads(receiptfile.read_text())
    assert receipt['status']=='UNNOTCHED_WALL_REJECTED_PARTIAL_MATRIX_STOPPED'
    assert not receipt['errors'] and not receipt['clearance_failures']
    cachefile=BASE/'phase1-prototype-final/preview/triangulation-cache.pkl';meshes={}
    moving={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    with cachefile.open('rb') as f:
        pickle.load(f)
        while True:
            try:n,m=pickle.load(f)
            except EOFError:break
            if n in moving:meshes[n]=np.unique(m[0].reshape(-1,3),axis=0)
    assert set(meshes)==moving
    axesfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    inventory={r['object']:r for r in motion['inventory']};code_of={n:code for code,g in motion['membership'].items() for ns in g.values() for n in ns}
    report=dict(status='SHARED_SKIN_ACCESS_RESERVATIONS_ONLY',selected=False,physical_pass=False,
        exact_collision_approval=False,leg_bays=[],control_portals=[],tail_portal=None,
        mesh_poses=36,nominal_skin_thickness_mm=2,minimum_3d_thickness_open=True,
        clearance_budget_mm=3,boxes_not_contact_proofs=True)
    for code,g in motion['membership'].items():
        points=[];per_pose=[]
        for index,pose in enumerate(motion['poses'][:36]):
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            tf=transforms(aa,pose['legs'][code]['angles_delta_degrees']);samples=[]
            for stage,t in zip(STAGES,tf):
                for n in g[stage]:
                    v=apply(meshes[n],t);take=skin_band(v)
                    if np.any(take):samples.append(v[take])
            if samples:
                v=np.concatenate(samples);points.append(v);per_pose.append(dict(index=index,design_samples=len(v)))
        # Include actual first2pose positive witnesses; their bounds are
        # conservative cut reservations, not alleged contact locations.
        witnesses=[r for r in receipt['contacts'] if r['scope']=='leg_motion' and code_of.get(r['object'])==code]
        # Do NOT turn conservative BRep witness bboxes into giant apertures.
        # Cached underlying surfaces can substantially exceed trimmed material.
        assert points,code
        v=np.concatenate(points);low=v.min(0)-3;high=v.max(0)+3
        sign=1 if aa[0]['pivot_mm'][1]>0 else -1
        # Each bay only enters the corresponding side; no blind through-cut
        # across the central battery/distribution volume.
        if sign>0:low[1]=max(0,low[1]);high[1]=110
        else:low[1]=-110;high[1]=min(0,high[1])
        low[2]=max(-60,low[2]);high[2]=min(112,high[2])
        report['leg_bays'].append(dict(code=code,physical_leg=aa[0]['physical_leg'],
            design_box_mm=[low.tolist(),high.tolist()],actual_positive_witnesses=len(witnesses),
            mesh_sample_summary=per_pose,shape='One rounded rectangular open-bottom side bay per wholeleg; minimum corner radius6mm, no per-contact notches',
            native_exact_gate='Required after four whole bays built'))
    contacts=receipt['contacts'];reader=SavedShapes()
    nativefile=OUT/'interior-native-checks.json';native_meta=json.loads(nativefile.read_text());native=ROOT/native_meta['native']
    assert sha(native)==native_meta['native_sha256']
    def planned_portal(hits):
        points=[]
        for n in sorted({r['object'] for r in hits}):
            s=reader.shape(native,n);p,f=s.tessellate(.2);v=np.array([list(x) for x in p]);tri=v[np.array(f)]
            samples=np.concatenate([v,tri.mean(1),(tri[:,0]+tri[:,1])/2,(tri[:,1]+tri[:,2])/2,(tri[:,2]+tri[:,0])/2])
            take=skin_band(samples)
            if np.any(take):points.append(samples[take])
        assert points,'No mesh near-wall samples for positive witness; do not use oversized cached bbox'
        v=np.concatenate(points);return [(v.min(0)-3).tolist(),(v.max(0)+3).tolist()]
    for kind,prefixes in [('S0',('Ref_Material_S0_',)),('S1',('Ref_Material_current_S1_',))]:
        hits=[r for r in contacts if r['scope']=='fixed_material' and r['object'].startswith(prefixes)]
        assert hits,kind
        report['control_portals'].append(dict(control=kind,design_box_mm=planned_portal(hits),
            actual_objects=sorted({r['object'] for r in hits}),
            function='Functional control aperture; add common fore-neck cowl protecting terminals, not arbitrary exposed bare conductors'))
    hits=[r for r in contacts if r['scope']=='fixed_material' and r['object'].startswith('Ref_Material_tail_')]
    assert hits
    report['tail_portal']=dict(design_box_mm=planned_portal(hits),
        actual_objects=sorted({r['object'] for r in hits}),function='One tail-root clearance opening plus separate removable root cowl; no body widening')
    report.update(open=['Native rounded bays/control/tail portals','Exact36pose leg and9pose head gate',
        'Fore-neck andtail-root cowls','Panel/frame anchors and seams','Full moving looms and all80nets','Actual3D thickness and print fit'],
        source_sha256={motionfile.relative_to(ROOT).as_posix():sha(motionfile),receiptfile.relative_to(ROOT).as_posix():sha(receiptfile),
            axesfile.relative_to(ROOT).as_posix():sha(axesfile),native.relative_to(ROOT).as_posix():sha(native),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'skin-access-plan.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],leg_bays=[{k:r[k] for k in ('physical_leg','design_box_mm')} for r in report['leg_bays']],
        controls=report['control_portals'],tail=report['tail_portal'],seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()

"""One actual-surface shared-space atlas BEFORE another routing hypothesis.

Surface samples include planar triangle interiors. Distances/4mm grid are
planning screens, never physical collision or full-route acceptance. Keeps
material, reservation, sampled36leg-motion and outer-contour layers separate.
Saves each completed source cloud so an interrupted stage is not all repeated.
"""
import io
import json
import math
import pickle
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
from scipy.spatial import cKDTree
from scipy.ndimage import label
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE,MODEL,STAGES,transforms,apply
from feline_rev3_query_scene import build
from plan_feline_central_pi_wedge import packed
from plan_feline_skin_access import surface_samples
from build_feline_layout_envelope import STATIONS,section_coefficients
from feline_tangent_routes import quarter_prefix,samples


def inside_ruled(v):
    """Ruled source section halfplanes; not a 3D wall-distance proof."""
    xx=[s[0] for s in STATIONS];sections=[]
    for _,w,h in STATIONS:
        y,z=section_coefficients(w,h);sections.append(np.column_stack((y*w/2,z*h/2+32)))
    x=v[:,0];mask=(x>=xx[0])&(x<=xx[-1])
    yy=[np.interp(x,xx,[s[i,0] for s in sections]) for i in range(len(sections[0]))]
    zz=[np.interp(x,xx,[s[i,1] for s in sections]) for i in range(len(sections[0]))]
    for i in range(len(yy)):
        j=(i+1)%len(yy);mask&=(yy[j]-yy[i])*(v[:,2]-zz[i])-(zz[j]-zz[i])*(v[:,1]-yy[i])>=-1e-7
    return mask


def main():
    tick=time.monotonic();dest=OUT/'n01-shared-space-atlas.json';bundle=dest.with_suffix('.zip');field=OUT/'n01-shared-space-atlas-field.npz'
    previous=json.loads(dest.read_text()) if dest.exists() else None
    if previous:assert previous['status'] in ('RUNNING_SHARED_SURFACE_ATLAS','PARTIAL_SHARED_SURFACE_ATLAS'),previous['status']
    report=previous or dict(status='RUNNING_SHARED_SURFACE_ATLAS',selected=False,N01_complete=False,physical_pass=False,
        parts=[],errors=[],source_sha256={},stage='clouds',grid_mm=4,surface_max_triangle_edge_mm=2,
        nominal_tessellation_deflection_mm=.3,source_surface_sampling_budget_mm=2.3,
        source_bboxes_used_only_for_ROI_not_contact=True,
        all123_full_routes_or_tools_or_roots_qualified=False,
        known_unqualified=['P_SYS/full source-port intrinsic stacks and actual delivered fitting',
            'All full middles and connector/service tool paths',
            'Surface-distance grid does not globally classify every solid interior',
            '36pose mesh union is a planning keepout, not continuous swept-volume proof'])
    def save():
        report['worker_seconds_this_run']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>300:raise TimeoutError('300s atlas cap; saved source clouds retained')
    save();scene,meta,pins,bus=build();reader=SavedShapes();envfile=OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd'
    outer=reader.shape(envfile,'TorsoEnvelope');assert outer.isValid()
    manifestfile=envfile.parent/'manifest.json';manifest=json.loads(manifestfile.read_text());assert manifest['sections']==[list(s) for s in STATIONS]
    # Restore the unchanged F_PWM source family omitted by the earlier USB query.
    clockedfile=OUT/'n01-coupled-clocked-joints.json';_,clocked,crows=packed(clockedfile)
    for n,s in clocked.items():
        if crows[n]['group']=='F_PWM':scene[n]=s;meta[n]=crows[n]
    # Current local head/tail sources at BASELINE pose, never inherited Head+35.
    localfile=OUT/'n01-selected-local-head-tail-sources.json';_,locals_,localrows=packed(localfile)
    for n,s in locals_.items():scene[n]=s;meta[n]=localrows[n]
    motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text());axesfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    meshfile=BASE/'phase1-prototype-final/preview/triangulation-cache.pkl';meshes={}
    moving={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    with meshfile.open('rb') as f:
        header=pickle.load(f);assert header['model_sha256']==sha(MODEL)
        for n,h in header['native_pins'].items():assert sha(ROOT/n)==h,n
        while True:
            try:n,m=pickle.load(f)
            except EOFError:break
            if n in moving:meshes[n]=m[0]
    assert set(meshes)==moving
    pins.update(header['native_pins']);pins.update(reader.hashes)
    for p in (Path(__file__),Path(__file__).with_name('plan_feline_skin_access.py'),Path(__file__).with_name('build_feline_layout_envelope.py'),manifestfile,clockedfile,localfile,motionfile,axesfile,meshfile,OUT/'n01-joint-usb-route.json'):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    if previous:
        assert report['source_sha256']==pins,'Changed source, do not reuse atlas silently'
    else:report['source_sha256']=pins
    report['bundle']=bundle.relative_to(ROOT).as_posix();report['source_parts_count']=len(scene);report['retained_leg_source_count']=len(moving)
    done={r['key']:r for r in report['parts']};known={};roi_low=np.array([-147,-104,-54]);roi_high=np.array([189,104,118])
    def write_points(key,pts,category,source,**extra):
        gate()
        if key in done:return
        pts=np.asarray(pts,dtype=np.float32);pts=pts[np.all(pts>=roi_low,axis=1)&np.all(pts<=roi_high,axis=1)]
        if len(pts):pts=np.unique(np.round(pts,4),axis=0)
        entry=f'cloud/{len(report["parts"]):04}.npy';buffer=io.BytesIO();np.save(buffer,pts,allow_pickle=False);raw=buffer.getvalue()
        with zipfile.ZipFile(bundle,'a',zipfile.ZIP_DEFLATED) as z:z.writestr(entry,raw)
        row=dict(key=key,source=source,category=category,entry=entry,sample_count=len(pts),sha256=__import__('hashlib').sha256(raw).hexdigest(),**extra)
        report['parts'].append(row);done[key]=row
        if len(done)%30==0:
            print('Atlas clouds',len(done),'samples',sum(r['sample_count'] for r in report['parts']),flush=True);save()
    try:
        for n,s in scene.items():
            gate()
            if n in moving:continue # Whole36pose union below, not both rest/moved duplicates.
            category='reservation' if ('reservation' in meta[n].get('kind','') or meta[n].get('role')=='ScaffoldPlanning' or n.startswith(('StructureReserve:','PiBudget:'))) else 'material'
            key='static:'+n
            if key in done:continue
            bb=s.BoundBox
            if bb.XMax<roi_low[0] or bb.XMin>roi_high[0] or bb.YMax<roi_low[1] or bb.YMin>roi_high[1] or bb.ZMax<roi_low[2] or bb.ZMin>roi_high[2]:
                write_points(key,np.empty((0,3)),category,n,ROI_disjoint=True);continue
            if not s.Solids:
                pts=[list(p) for e in s.Edges for p in e.discretize(Distance=1)]
                write_points(key,pts,'curve_hold',n,not_full_jacket=True);continue
            if n==bus['name']:
                v,f=bus['original'].tessellate(.3);v=np.array([list(p) for p in v]);v=np.array([list(bus['inverse'].inverse().multVec(A.Vector(*p))) for p in v]);method=bus['method']
            else:
                if not s.isValid():raise ValueError('Invalid source, atlas unknown: '+n)
                v,f=s.tessellate(.3);v=np.array([list(p) for p in v]);method='Actual valid saved BRep surface'
            pts=surface_samples(v[np.asarray(f,dtype=int)],2)
            write_points(key,pts,category,n,method=method)
        v,f=outer.tessellate(.3);v=np.array([list(p) for p in v]);write_points('outer',surface_samples(v[np.asarray(f,dtype=int)],2),'outer','TorsoEnvelope')
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            for stage in STAGES:
                for n in g[stage]:
                    gate()
                    keys=[f'motion:{code}:{i}:{n}' for i in range(36)]
                    if all(k in done for k in keys):continue
                    if n not in known:known[n]=surface_samples(meshes[n],2)
                    for i,pose in enumerate(motion['poses'][:36]):
                        key=keys[i]
                        if key in done:continue
                        tf=transforms(aa,pose['legs'][code]['angles_delta_degrees'])[STAGES.index(stage)]
                        write_points(key,apply(known[n],tf),'motion36',n,leg=code,pose_index=i,stage=stage)
        report['stage']='field';save();clouds={k:[] for k in ('material','reservation','motion36','outer','curve_hold')}
        with zipfile.ZipFile(bundle) as z:
            for r in report['parts']:
                raw=z.read(r['entry']);assert __import__('hashlib').sha256(raw).hexdigest()==r['sha256']
                if r['sample_count']:clouds[r['category']].append(np.load(io.BytesIO(raw),allow_pickle=False))
        # Ownership IDs are indexes of report.parts; preserve nearest source via individual cloud chunks.
        trees={};owners={}
        for category,parts in clouds.items():
            gate()
            if not parts:continue
            vv=np.concatenate(parts);rows=[i for i,r in enumerate(report['parts']) if r['category']==category and r['sample_count']]
            owners[category]=np.concatenate([np.full(report['parts'][i]['sample_count'],i,dtype=np.uint16) for i in rows])
            trees[category]=cKDTree(vv)
            print('Atlas layer',category,len(vv),'samples',flush=True)
        xx=np.arange(-140,181,4,dtype=float);yy=np.arange(-96,97,4,dtype=float);zz=np.arange(-46,111,4,dtype=float)
        grid=np.stack(np.meshgrid(xx,yy,zz,indexing='ij'),axis=-1);points=grid.reshape(-1,3);inside=inside_ruled(points)
        values={};nearest={}
        for cat,tree in trees.items():
            gate();dist,index=tree.query(points,workers=1);values[cat]=dist.astype(np.float32);nearest[cat]=owners[cat][index]
        nominal=inside.copy();conservative=inside.copy()
        for cat in ('material','reservation','motion36'):
            nominal&=values[cat]>=3.75;conservative&=values[cat]>=6.05
        nominal&=values['outer']>=5.75;conservative&=values['outer']>=8.05
        # Curve-only local sources have unknown jackets: keep a separate hold
        # mask rather than asserting their copper curves are the whole cables.
        curve_hold=values.get('curve_hold',np.full(len(points),np.inf))<5.75
        shape=grid.shape[:3];components,count=label(nominal.reshape(shape))
        previousUSB=json.loads((OUT/'n01-joint-usb-route.json').read_text());anchor_components={};anchors=[]
        def nearest_cell(q):
            ix=tuple(int(np.argmin(abs(axis-q[i]))) for i,axis in enumerate((xx,yy,zz)))
            return ix,int(components[ix]),float(np.linalg.norm(grid[ix]-q))
        for owner,p,d in [('PiUSB',previousUSB['start_mm'],(-1,0,0)),('BUSUSB',previousUSB['end_mm'],(0,-1,0))]:
            ids=set()
            for i in range(24):
                a=i*math.pi/12;b=(0,math.cos(a),math.sin(a)) if owner=='PiUSB' else (math.cos(a),0,math.sin(a))
                prefix=quarter_prefix(p,d,b);q=np.array(prefix[-1]['end']);ix,component,gap=nearest_cell(q)
                anchors.append(dict(owner=owner,domain=i,after9_mm=q.tolist(),cell=list(ix),component=component,grid_registration_gap_mm=gap,curve_not_exactly_qualified=True))
                if component:ids.add(component)
            anchor_components[owner]=ids
        shared=sorted(anchor_components['PiUSB']&anchor_components['BUSUSB'])
        np.savez_compressed(field,x=xx,y=yy,z=zz,inside=inside.reshape(shape),nominal=nominal.reshape(shape),
            conservative=conservative.reshape(shape),components=components,curve_hold=curve_hold.reshape(shape),
            **{cat+'_distance':v.reshape(shape) for cat,v in values.items()},**{cat+'_owner':v.reshape(shape) for cat,v in nearest.items()})
        report.update(status='SHARED_ACTUAL_SURFACE_ATLAS_PLANNING_ONLY_NOT_N01',stage='complete',
            grid_shape=list(shape),grid_points=len(points),nominal_candidate_cells=int(nominal.sum()),conservative_candidate_cells=int(conservative.sum()),
            connected_component_count=count,USB_after_grip_anchors=anchors,USB_shared_component_ids=shared,
            graph_connected_not_a_radius_or_length_route=True,curve_only_hold_cells=int(curve_hold.sum()),
            field=field.relative_to(ROOT).as_posix(),field_sha256=sha(field),bundle_sha256=sha(bundle),
            categories_sample_counts={k:sum(r['sample_count'] for r in report['parts'] if r['category']==k) for k in clouds},
            ATO_service_budget='Current source: outward +/-Y extraction60mm through removed side panels; reserve access before route selection, not part of this surface-only field',
            no_third_manual_routing_family=True)
    except Exception as e:
        report['status']='PARTIAL_SHARED_SURFACE_ATLAS';report['errors'].append(repr(e));print('Atlas partial',repr(e),flush=True)
    save();print(json.dumps(dict(status=report['status'],stage=report['stage'],clouds=len(report['parts']),seconds=report['worker_seconds_this_run'],errors=report['errors'])),flush=True)


if __name__=='__main__':main()

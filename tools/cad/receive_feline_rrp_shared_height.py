"""A measured shared gallery ABOVE USB and BELOW Pi, same received grip.

Only four post-grip curves change. Preserve the complete curved grip/tie/head
byte-for-byte and reuse their old static pairs. No scalar angle search.
"""
import gzip, hashlib, json, math, os, time, zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_adjudicated_boundaries import current
from feline_selected_material_contract import load as profiles
from feline_output_composed_context import compose
from feline_received_own_channels import own_channel
from feline_atomic_save import save_json
from receive_feline_underplate_return_gallery import bend, forward, minimum_for
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement


def source_path(q, height, trim=0):
    q=np.array(q,float); d=np.array([0.,-1,0]); R=25.2
    angle=math.acos(1-(q[2]-height)/(2*R)); assert R*angle>=9
    rows=[]; q=forward(rows,q,d,.25)
    if trim:
        rows=[]; a=(trim-.25)/R
        q=q+R*math.sin(a)*d+R*(1-math.cos(a))*np.array([0.,0,-1])
        heading=math.cos(a)*d+math.sin(a)*np.array([0.,0,-1])
        normal=-math.sin(a)*d+math.cos(a)*np.array([0.,0,-1])
        q,heading=bend(rows,q,heading,normal,R,angle-a)
    else:q,heading=bend(rows,q,d,[0,0,-1],R,angle)
    normal=d-heading*float(d@heading); normal/=np.linalg.norm(normal)
    q,heading=bend(rows,q,heading,normal,R,angle)
    assert abs(q[2]-height)<1e-6 and np.linalg.norm(heading-d)<1e-6
    return rows,q,heading


def load(doc):
    archive=ROOT/doc['bundle']; assert sha(archive)==doc['bundle_sha256']; shapes={}
    with zipfile.ZipFile(archive) as z:
        for r in doc['geometry']:
            raw=z.read(r['entry']); assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape(); s.importBrepFromString(raw.decode()); shapes[r['name']]=s
    return shapes


def gallery(parts):
    # Exact clipping of the existing valid USB budget, not a bounding-box
    # intersection/contact test. Its Z maximum is a conservative fit bound.
    roi=Part.makeBox(25.5,18,160,A.Vector(.5,37,0))
    clipped=parts['USB500:whole'].common(roi)
    assert clipped.isValid() and clipped.Solids
    lo=clipped.BoundBox.ZMax+2.1+.2
    hi=parts['PiBudget:AdapterBody'].BoundBox.ZMin-2.1-1.25
    assert hi>lo
    return (lo+hi)/2,dict(USB_local_surface_upper_Z_mm=clipped.BoundBox.ZMax,
        interval_mm=[lo,hi],chosen_midpoint_mm=(lo+hi)/2,wire_radius_mm=2.1,
        wire_wire_gap_mm=.2,foreign_margin_mm=1.25,ROI_project_mm=[[.5,37,0],[26,55,160]],
        bounds_are_fit_constraints_NOT_contact_proof=True)


def main():
    tick=time.monotonic(); sf=OUT/'n01-early-curved-RRP.json'; old=json.loads(sf.read_text())
    assert old['status']=='WHOLE_EARLY_RRP_HOLD_WITNESSES' and len(old['failures'])==3
    for p,h in old['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(old); kinds={r['name']:r for r in old['geometry']}
    _,ends,files=current(); index={e['id']:e for e in ends}; contract,pf,bf=profiles()
    world,fixed,meta,pins,docs=compose(); height,interval=gallery(fixed)
    recipes={};trimmed={};changed=set(old['recipes'])
    for n,r in old['recipes'].items():
        parts,q,d=source_path(r['point_mm'],height); radius=r['project_radius_mm']
        actors[n]=pipe(parts,radius);trimmed[n]=pipe(source_path(r['point_mm'],height,2.5)[0],radius)
        recipes[n]=dict(r,parts=parts,routing_exit_mm=q.tolist(),routing_exit_axis=d.tolist(),
                       project_prefix_length_mm=sum(p['length_mm'] for p in parts))
    for n in old['retired']:assert n in fixed;fixed.pop(n);meta.pop(n)
    previous_file=ROOT/old['pair_rows'];assert sha(previous_file)==old['pair_rows_sha256']
    checks={k:v for k,v in json.loads(gzip.decompress(previous_file.read_bytes())).items()
            if not any(n in k for n in changed)}
    assert all(v['ok'] for v in checks.values()); reused=len(checks)
    sources=(*files,pf,bf,sf,ROOT/old['bundle'],previous_file,Path(__file__))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    dest=OUT/'n01-RRP-shared-height.json';archive=dest.with_suffix('.breps.zip');pairfile=dest.with_suffix('.pairs.json.gz')
    assert not dest.exists(),'Receive the existing result, no same-topology rerun'
    geometry=[]
    with zipfile.ZipFile(ROOT/old['bundle']) as baseline, zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode() if n in changed else baseline.read(kinds[n]['entry'])
            entry=str(i)+'.brep';z.writestr(entry,raw)
            if n not in changed:assert hashlib.sha256(raw).hexdigest()==kinds[n]['sha256']
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=kinds[n]['kind']))
    result=dict(status='RUNNING_RRP_SHARED_GALLERY',source_sha256=pins,recipes=recipes,gallery=interval,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),geometry=geometry,
        unchanged_four_grip_actors=[n for n in actors if n not in changed],reused_static_pairs=reused,
        retired=old['retired'],completed_static=[n for n in actors if n not in changed],completed_motion=[],
        N01_complete=False,native_changed=False,physical_pass=False,roots_AND_assembly_AND_full_middles_OPEN=True)
    def save():
        pairfile.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(pair_rows=pairfile.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pairfile),
            checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    save(); query=SolidQueries(); boxes={n:s.BoundBox for n,s in {**fixed,**actors}.items()}
    for n in changed:
        s=actors[n];checks[n+'|outer']=outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            mr=kinds[m] if m in actors else meta[m]; minimum=minimum_for(n,{'kind':'wire'},m,mr)
            minimum=min(minimum,own_channel(index[recipes[n]['end_id']],m)) if m not in actors else minimum
            if m.startswith('EarlyRR:comb:'):minimum=.15
            if bbox_lower_bound(boxes[n],boxes[m])>=minimum:continue
            tested=trimmed[n] if m=='Station:RR_P:case' else s
            if m==world.bus['name']:
                tested=tested.copy();tested.Placement=docs['inverse']*tested.Placement;t=world.bus['original']
            if t.Solids:
                gap=query.distance(tested,t);check=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
                if m=='Station:RR_P:case':
                    c=s.common(t);assert c.isNull() or c.isValid()
                    check.update(ok=check['ok'] and c.Volume<1e-5,source_port_first2p5_trim=True,whole_case_overlap_mm3=c.Volume)
            else:
                radius=mr.get('nominal_profile_radius_mm') or mr.get('radius_mm')
                check=profile_gap(tested,t,radius,minimum) if radius else dict(ok=False,unresolved_curve_budget=m)
            checks[key]=check
        result['completed_static'].append(n);save();print('RRP shared height',n,'holds',len(result['failures']),flush=True)
    if not result['failures']:
        for n,s in actors.items():
            for pose in world.motion:
                if bbox_lower_bound(boxes[n],A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                q=s.copy();q.Placement=placement(pose['r'],pose['t']).inverse()*q.Placement
                gap=query.distance(q,world.rest[pose['name']]);checks[n+'|motion:'+pose['name']+':'+str(pose['pose'])]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
    result['status']='RRP_SHARED_HEIGHT_HOLD_CHANGE_CAUSE_BEFORE_THIRD' if result['failures'] else 'RRP_SHARED_HEIGHT_STATIC36_RECEIVED_ROOTS_AND_ASSEMBLY_OPEN'
    save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()

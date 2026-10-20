"""Tight clipped-BRep two-portal domain for four complete crowns, fixed AND motion.

Actual clipped material in2mm Z slabs gives conservative sufficient X
separation, NOT contacts or global impossibility. No source/core pose sweep.
Existing10mm grips remain on the identical first arc. Only four wires change.
"""
import copy,itertools,json,math,time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from plan_feline_remaining_factory_inputs import offset
from receive_feline_underplate_return_gallery import forward,minimum_for
from plan_feline_n01_shared import pipe
from plan_feline_factory_joint_bay import subtract
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def plan_parts(recipe):
    d=np.asarray(recipe['axis']);side=np.sign(recipe['point_mm'][1]);rows=copy.deepcopy(recipe['parts'][:3]);q=np.asarray(rows[-1]['end'])
    if d[0]>0:
        length=117.5-q[0];assert length>0;q=forward(rows,q,d,length)
    q=offset(rows,q,d,[0,side*2,0]);crown=copy.deepcopy(recipe['parts'][4:])
    # The old recipe has the computed straight at index3. Put its entire
    # upper crown at portalX=0 and shiftY2; all R and distinct directions stay.
    shift=np.array([-recipe['routing_exit_mm'][0],side*2,0.])
    for p in crown:
        for k in ('start','mid','end'):
            if k in p:p[k]=(np.asarray(p[k])+shift).tolist()
    assert abs(crown[0]['start'][0]+25.2*d[0])<1e-6
    return rows,q,crown


def bbrow(b):return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]


def main():
    tick=time.monotonic();sf=OUT/'n01-MTA-whole-corridor.json';prior=json.loads(sf.read_text())
    assert not prior['failures'] and len(prior['completed_rest'])==64
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    world,parts,meta,pins,docs=compose();kit=load(prior)
    effective={n:s for n,s in parts.items() if n not in prior['retired']};effective.update(kit)
    for n in prior['recipes']:effective.pop(n)
    fm={**meta,**{r['name']:r for r in prior['geometry']}}
    plans={};domains={'positive':[(-1e9,1e9)],'negative':[(-1e9,1e9)]}
    outer=docs['outer'].BoundBox
    for n,r in prior['recipes'].items():
        stem,q,crown=plan_parts(r);d=np.asarray(r['axis']);family='positive' if d[0]>0 else 'negative'
        allowed=[q[0]+25.2,outer.XMax-5.35] if d[0]>0 else [outer.XMin+5.35,q[0]-25.2]
        domains[family]=[(max(a,allowed[0]),min(b,allowed[1])) for a,b in domains[family] if max(a,allowed[0])<min(b,allowed[1])]
        plans[n]=dict(stem_parts=stem,stem_end_mm=q.tolist(),crown_at_portalX0=crown,family=family)
    initial=copy.deepcopy(domains);pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],Path(__file__))})
    dest=OUT/'n01-MTA-tight-crown-domain.json'
    result=dict(status='RUNNING_SHARED_CROWN_DOMAIN',source_sha256=pins,initial_domains_X_mm=initial,domains_X_mm=domains,
        plans=plans,completed_slabs=[],projection_rows=[],actual_clip_queries=0,physical_pass=False,N01_complete=False,
        existing_grips_roots_cases_and_factory_lengths_NOT_changed=True,
        true_outer_and_full_lower_links_and_tool_access_still_OPEN=True,
        tight_clipped_bounds='optimalBoundingBox(False,False), clamped to proven Boolean clip planes; not legacy pole bounds')
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins;domains=result['domains_X_mm']
    def save(status=None):
        if status:result['status']=status
        result.update(domains_X_mm=domains,worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    sources=[(m,s,None,None,fm[m]) for m,s in effective.items()]
    sources.extend(('motion:'+pose['name']+':'+str(pose['pose']),world.rest[pose['name']],pose['bounds'],placement(pose['r'],pose['t']),dict(kind='rigid')) for pose in world.motion)
    for n,p in plans.items():
        crown=pipe(p['crown_at_portalX0'],2.1);cb=crown.BoundBox;family=p['family']
        for z in np.arange(math.floor(cb.ZMin),math.ceil(cb.ZMax),2.):
            key=n+':'+str(z)
            if key in result['completed_slabs']:continue
            slab=crown.common(Part.makeBox(80,200,2,A.Vector(-40,-100,z)))
            assert slab.isNull() or slab.isValid()
            if slab.isNull() or not slab.Solids:result['completed_slabs'].append(key);continue
            b=slab.optimalBoundingBox(False,False)
            b=A.BoundBox(b.XMin,b.YMin,max(b.ZMin,float(z)),b.XMax,b.YMax,min(b.ZMax,float(z+2)))
            # Static parts first narrow the domain before considering motion.
            for m,s,bounds,tf,mr in sources:
                margin=minimum_for(n,dict(kind='actual_wire'),m,mr)
                radius=0 if s.Solids else mr.get('nominal_profile_radius_mm') or mr.get('radius_mm')
                assert radius is not None,('Missing source profile',m)
                margin+=radius
                bnd=bbrow(s.BoundBox) if bounds is None else bounds
                if bnd[1][1]<b.YMin-margin or bnd[0][1]>b.YMax+margin or bnd[1][2]<b.ZMin-margin or bnd[0][2]>b.ZMax+margin:continue
                broad=[bnd[0][0]-b.XMax-margin,bnd[1][0]-b.XMin+margin]
                if not any(a<broad[1] and c>broad[0] for a,c in domains[family]):continue
                lo=min(a for a,c in domains[family])+b.XMin-margin;hi=max(c for a,c in domains[family])+b.XMax+margin
                roi=Part.makeBox(hi-lo,b.YLength+2*margin,b.ZLength+2*margin,A.Vector(lo,b.YMin-margin,b.ZMin-margin))
                if m==world.bus['name']:s=world.bus['original'];tf=docs['inverse'].inverse()
                if tf is not None:roi.Placement=tf.inverse()*roi.Placement
                assert s.isValid(),m
                cut=s.common(roi);assert cut.isNull() or cut.isValid(),m;result['actual_clip_queries']+=1
                if cut.isNull() or not cut.Vertexes:continue
                bb=cut.optimalBoundingBox(False,False)
                if tf is not None:
                    xyz=np.array([list(tf.multVec(A.Vector(*v))) for v in itertools.product((bb.XMin,bb.XMax),(bb.YMin,bb.YMax),(bb.ZMin,bb.ZMax))]);xmin,xmax=xyz[:,0].min(),xyz[:,0].max()
                else:xmin,xmax=bb.XMin,bb.XMax
                xmin=max(xmin,lo);xmax=min(xmax,hi)
                forbidden=[float(xmin-b.XMax-margin),float(xmax-b.XMin+margin)]
                after=subtract(domains[family],forbidden)
                if after!=domains[family]:
                    result['projection_rows'].append(dict(wire=n,source=m,slab_Z_mm=[float(z),float(z+2)],forbidden_portal_X_mm=forbidden,
                        actual_clip_volume_mm3=cut.Volume,actual_clip_bounds_mm=bbrow(bb),bbox_overlap_NOT_contact=True))
                    domains[family]=after;save()
                if not domains[family]:save('NO_CONSERVATIVE_SHARED_CROWN_DOMAIN_NOT_GLOBAL_IMPOSSIBLE');print(result['status'],n,m,flush=True);return
            result['completed_slabs'].append(key);save()
            if time.monotonic()-tick>220:save('PARTIAL_SHARED_CROWN_DOMAIN_SAVED');print(result['status'],len(result['completed_slabs']),flush=True);return
    result['chosen_portals_X_mm']={f:sum(max(v,key=lambda x:x[1]-x[0]))/2 for f,v in domains.items()}
    save('SHARED_FOUR_CROWN_CONSERVATIVE_DOMAIN_CURRENT_WHOLE_SCENE')
    print(result['status'],domains,result['chosen_portals_X_mm'],result['actual_clip_queries'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()

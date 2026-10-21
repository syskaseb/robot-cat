"""Exact full local-link gate on one frozen CURRENT whole scene.

Field holds select proposals, not mechanical rejections. Nothing near a
source is cropped: every full candidate is checked against all neighbours.
Only proved same-wire cap mates receive their ordinary zero-volume joint.
"""
import hashlib,json,math,re,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_common_space_context import is_jacket
from receive_feline_aux_vertical_unit import material_spacing
from receive_feline_jpwm_whole_pose import solid_profile_target
from receive_feline_W024_shared_body import solid
from plan_feline_usb_service_bight import outer_margin


def cap_owner(n,meta,end):
    wire=end['wire'];explicit=[end.get('prefix_geometry_owner'),*end.get('prefix_geometry_owners',[]),*end.get('planned_body_capacity_path_owners',[])]
    if n in explicit:return True
    if any(str(meta.get(k,'')).split('/')[0]==wire for k in ('wire','wire_owner')):return True
    if re.search(r'(^|[:/])'+re.escape(wire)+r'([:/]|$)',n):return True
    if str(end.get('group','')).startswith('WAGO:'):
        return n=='Station:'+end['group'].split(':',1)[1]+':wire:'+str(end.get('role'))
    return False


def run(world,scene,metadata,ends,outer,pins):
    tick=time.monotonic();directory=OUT/'joint-corridor-space-20261021'
    pf=directory/'current-local-exact-link-proposals.json';proposal=json.loads(pf.read_text())
    assert len(proposal['ends'])==246 and proposal['status']=='CURRENT246_CURVED_SOURCE_LINK_DOMAINS_RECORDED_NOT_N01'
    dest=directory/'current-full-source-links-exact.json';byid={e['id']:e for e in ends};bounds={n:s.BoundBox for n,s in scene.items()}
    sources={**pins,pf.relative_to(ROOT).as_posix():sha(pf),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
        'tools/cad/receive_feline_W024_shared_body.py':sha(ROOT/'tools/cad/receive_feline_W024_shared_body.py')}
    result=dict(status='RUNNING_FULL_LOCAL_LINK_STATIC_GATE',source_sha256=sources,ends={},
        current_actor_count=len(scene),N01_complete=False,selected=False,physical_pass=False,
        mutual_links_packing_head_tail_motion_assembly_OPEN=True,no_curve_samples_or_sources_deleted=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==sources
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    query=SolidQueries();profile_targets={};cap_cache={}
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    for eid,row in proposal['ends'].items():
        if eid in result['ends']:continue
        candidates=row.get('field_positive',[])+row.get('near_source_exact_required',[])
        if not candidates:
            result['ends'][eid]=dict(status='RETAINED_'+row['status']);continue
        end=byid[eid];p=A.Vector(*row['point_mm']);radius=row['radius_mm'];owners=[]
        for n,t in scene.items():
            if not cap_owner(n,metadata[n],end) or not t.Solids or bbox_lower_bound(bounds[n],A.BoundBox(p,p))>1e-5:continue
            if n not in cap_cache:
                cap_cache[n]=[(f.CenterOfMass,f.Area) for f in t.Faces if type(f.Surface).__name__=='Plane']
            if any((c-p).Length<1e-5 and abs(area-math.pi*radius**2)<1e-5 for c,area in cap_cache[n]):owners.append(n)
        if not owners:
            result['ends'][eid]=dict(status='SOURCE_CAP_OWNER_UNRESOLVED_NOT_CLEARANCE',point_mm=row['point_mm']);save();continue
        entry=dict(status='EXACT_LOCAL_LINK_DOMAIN_HOLD',source_cap_owners=owners,candidates=[])
        # Two DIFFERENT tangent-heading hypotheses, not a pose/offset sweep.
        ranked=sorted(candidates,key=lambda r:r['length_mm'])[:2]
        for candidate in ranked:
            actor=solid(candidate['parts'],radius);checks={};bb=actor.BoundBox
            for n,t in scene.items():
                required=0. if n in owners else material_spacing('Link:'+eid,dict(kind='wire',wire=end['wire']),n,metadata[n])
                extra=metadata[n].get('nominal_profile_radius_mm',0.) if not t.Solids else 0.
                if bbox_lower_bound(bb,bounds[n])>=required+extra+1e-6:continue
                a=actor;other=t
                if n==world.bus['name']:
                    a=actor.copy();a.Placement=world.bus['inverse']*a.Placement;other=world.bus['original']
                elif not other.Solids:
                    if n not in profile_targets:profile_targets[n]=solid_profile_target(other,metadata[n])
                    other=profile_targets[n]
                gap=query.distance(a,other);check=dict(gap_mm=gap,minimum_mm=required,ok=gap>=required-1e-6)
                if n in owners:
                    # Deep private BRep copies: no shared TShape Boolean mutation.
                    import Part
                    aa=Part.Shape();aa.importBrepFromString(actor.exportBrepToString())
                    tt=Part.Shape();tt.importBrepFromString(t.exportBrepToString())
                    common=aa.common(tt).Volume
                    check.update(common_mm3=common,ok=gap<=1e-6 and common<1e-5)
                checks[n]=check
            boundary=outer_margin(actor,outer)
            received=dict(recipe=candidate,checks=checks,outer=boundary,failures=[n for n,c in checks.items() if not c['ok']])
            entry['candidates'].append(received)
            if not received['failures'] and boundary['ok']:
                entry['status']='FULL_SOURCE_LINK_STATIC_RECEIVED_MOTION_AND_PACKING_OPEN';break
        result['ends'][eid]=entry;save()
        if len(result['ends'])%20==0:print('EXACT_FULL_SOURCE_LINKS',len(result['ends']),'/246',flush=True)
        if time.monotonic()-tick>225:break
    result['status']='CURRENT246_FULL_LOCAL_LINK_STATIC_GATE_RECORDED_NOT_N01' if len(result['ends'])==246 else 'PARTIAL_CURRENT_FULL_LOCAL_LINK_STATIC_GATE'
    save();return result

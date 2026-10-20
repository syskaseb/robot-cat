"""Correct the W066 profile from retained selected HELU, not a bad CAD cap.

Same first9, R25.2,45deg tangent and total length. Only own printed groove
is enlarged. Parent R2 evidence is preserved; recheck changed interfaces.
"""
import hashlib,json,os,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_retention_composed_context import compose
from receive_feline_positive_service_deck import pipe,circle_arc
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from receive_feline_global_case_candidates import placement
from plan_feline_usb_service_bight import outer_margin


def main():
    tick=time.monotonic();pf=OUT/'n01-whole-wire-profile-contract.json';profiles=json.loads(pf.read_text())
    radius=profiles['portions']['W066/retained0']['project_radius_mm'];assert abs(radius-2.1)<1e-5
    world,parts,meta,pins,docs=compose();parent=docs['retention_core'];recipe=parent['recipe']['P_SYS_entry:W066']
    name='P_SYS_entry:W066';comb='Station:P_SYS:common_channelled_cap_exterior'
    p=np.asarray(recipe['start_mm']);d=np.asarray(recipe['start_axis']);land=p+9*d
    edges=[Part.makeLine(A.Vector(*p),A.Vector(*land)),circle_arc(land,d,recipe['normal'],recipe['R_mm'],recipe['angle_rad'])]
    wire,path=pipe(edges,radius);cutter,_=pipe(edges,radius+.15)
    oldcomb=parts[comb];newcomb=oldcomb.cut(cutter).removeSplitter()
    assert newcomb.isValid() and len(newcomb.Solids)==len(oldcomb.Solids)>0
    assert newcomb.cut(oldcomb).Volume<1e-6,'Only own provisional groove may be enlarged'
    assert abs(path.Length-recipe['length_mm'])<1e-6
    assert (path.Vertexes[-1].Point-A.Vector(*recipe['exit_mm'])).Length<1e-5
    parts=dict(parts);parts[name]=wire;parts[comb]=newcomb
    query=SolidQueries();checks={};errors=[];minimums={};bounds={n:s.BoundBox for n,s in parts.items()}
    # The comb is an exact subset; all its unchanged external separations and
    # old frame bearing material remain inherited except the corrected wire.
    for other,t in parts.items():
        if other==name:continue
        minimum=pair_spacing(name,dict(kind='wire'),other,meta[other])
        if other==comb:minimum=.15
        if bbox_lower_bound(wire.BoundBox,bounds[other])>=minimum:continue
        if other==world.bus['name']:
            q=wire.copy();q.Placement=docs['inverse']*q.Placement;gap=query.distance(world.bus['original'],q)
            r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
        elif t.Solids:
            gap=query.distance(wire,t);r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
            if other=='Station:P_SYS:case':
                common=wire.common(t);assert common.isNull() or common.isValid()
                r.update(ok=common.Volume<1e-6,nominal_unchanged_case_mouth_contact_only=True,common_mm3=common.Volume)
        else:
            rr=meta[other].get('nominal_profile_radius_mm');assert rr,('Unknown curve radius',other)
            r=profile_gap(wire,t,rr,minimum)
        checks[other]=r
    checks['outer']=outer_margin(wire,docs['outer'])
    for pose in world.motion:
        if bbox_lower_bound(wire.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
        q=wire.copy();q.Placement=placement(pose['r'],pose['t']).inverse()*q.Placement
        gap=query.distance(q,world.rest[pose['name']]);checks['motion:'+pose['name']+':'+str(pose['pose'])]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
    failures=[dict(owner=n,**r) for n,r in checks.items() if not r['ok']]
    archive=OUT/'n01-psys-selected-wire-profile.breps.zip';geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s,kind) in enumerate(((name,wire,'wire'),(comb,newcomb,'proposal_material'))):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=kind))
    result=dict(status='SELECTED_W066_PROFILE_AND_OWN_GROOVE_RECEIVED' if not failures else 'SELECTED_W066_PROFILE_CHANGED_INTERFACE_HOLDS',
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        checks=checks,failures=failures,errors=errors,corrected_only_W066_and_own_comb=True,
        old_incorrect_cap_radius_mm=recipe['radius_mm'],selected_project_radius_mm=radius,
        unchanged_path_length_mm=path.Length,first9_R25p2_angle45_exit_and_bought_parts_unchanged=True,
        comb_subset_removed_mm3=oldcomb.Volume-newcomb.Volume,
        previous_W066_R2_geometry_receipt_superseded_not_deleted=True,
        source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (pf,Path(__file__))}},
        N01_complete=False,selected=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-psys-selected-wire-profile.json',result)
    print(json.dumps(dict(status=result['status'],checks=len(checks),holds=failures,seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()

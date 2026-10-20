"""Receive four explicitly named EXISTING lower prefixes, build no new wire.

Keep source factory/custom identities and current geometry. Old mouth is the
inlet, not the outlet nine millimetres later. No routing or new grip claim.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_main_hung_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates
from compose_feline_output_boundaries import cap_at
from feline_physical_wire_profiles import load as profiles
from receive_feline_main_ato_gallery import selected
from feline_atomic_save import save_json


def current():
    base,rows,files=parent();f=OUT/'n01-existing-lower-cap-overlay.json';r=json.loads(f.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return base,apply_updates(rows,r['updates']),(*files,f)


def main():
    tick=time.monotonic();base,rows,files=parent();contract,pf,df=profiles()
    sf=OUT/'n01-lower-bay-world-probe.json';wf=OUT/'n01-MAIN-hung-world.json';world=json.loads(wf.read_text())
    assert world['source_sha256'][sf.relative_to(ROOT).as_posix()]==sha(sf)
    names={'CustomPrefix:'+w for w in ('W041','W042','W044','W052')}
    parts,_,pins=selected(sf,'parts',lambda n:n in names);assert set(parts)==names
    updates={};proofs={}
    for w in ('W041','W042','W044','W052'):
        end=w+'/custom/start';e=next(r for r in rows if r['id']==end);n='CustomPrefix:'+w;s=parts[n]
        radius=contract['portions'][e['portion_id']]['project_radius_mm'];p=e['point_mm'];d=e['departure_axis']
        inlet=cap_at(s,p,[-v for v in d],radius)
        # Read the unique outward cap of THIS named producer, never the
        # nearest cap or a fabricated p+9 used for a different prefix type.
        candidates=[]
        for face in s.Faces:
            if not isinstance(face.Surface,Part.Plane) or len(face.Edges)!=1:continue
            c=face.Edges[0].Curve
            if not isinstance(c,Part.Circle) or abs(c.Radius-radius)>1e-5:continue
            u,U,v,V=face.ParameterRange;normal=face.normalAt((u+U)/2,(v+V)/2);centre=face.CenterOfMass
            if not s.isInside(centre-normal*.05,1e-7,False):normal=-normal
            if normal.dot(A.Vector(*d))>1-1e-6:candidates.append(list(centre))
        assert len(candidates)==1,(n,candidates)
        q=candidates[0];length=(A.Vector(*q)-A.Vector(*p)).Length
        outlet=cap_at(s,q,d,radius)
        assert length>=9 and abs(s.Volume-3.141592653589793*radius**2*length)<1e-4
        updates[end]=dict(routing_exit_mm=q,routing_exit_axis=d,prefix_geometry_owner=n,
            source_prefix_length_mm=length,routing_boundary_status='CURRENT_EXISTING_LOWER_PREFIX_OUTLET_RECEIVED_NOT_NEW_GEOMETRY',
            source_existing_brep_radius_mm=radius,selected_project_minimum_R_mm=contract['portions'][e['portion_id']]['minimum_project_R_mm'],
            new_physical_wire_connector_or_cut=False,full_middle_route_accepted=False,independent_relief_root_and_assembly_NOT_inferred=True)
        proofs[end]=dict(owner=n,inlet=inlet,outlet=outlet,actual_volume_mm3=s.Volume,existing_straight_length_mm=length)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (*files,pf,df,wf,Path(__file__),ROOT/'tools/cad/feline_physical_wire_profiles.py')})
    result=dict(status='FOUR_EXISTING_LOWER_CAPS_RECEIVED_REMAINING_N01_OPEN',updates=updates,proofs=proofs,source_sha256=pins,
        geometry_changed=False,physical_portions=123,ends=246,N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-existing-lower-cap-overlay.json',result);print(result['status'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()

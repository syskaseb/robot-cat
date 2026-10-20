"""Small current output-boundary overlay; preserve all123 identities/246ends.

Compose the received upper+retention overlays before new four-output exits.
Validate actual circular BRep caps. Never use the old joint's first9 again.
"""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_selected_material_contract import load as profiles
from feline_output_composed_context import received
from receive_feline_psys_frame_load_paths import load
from compose_feline_integrated_boundaries import apply_updates


def parents():
    ef=OUT/'n01-shared-routing-boundaries.json';uf=OUT/'n01-integrated-upper-boundary-overlay.json';rf=OUT/'n01-current-retention-layout-overlay.json'
    base=json.loads(ef.read_text());upper=json.loads(uf.read_text());retention=json.loads(rf.read_text())
    assert upper['parent_sha256']==retention['base_sha256']==sha(ef)
    assert retention['upper_sha256']==sha(uf)
    return base,apply_updates(apply_updates(base['endpoints'],upper['updates']),retention['updates']),(ef,uf,rf)


def current():
    base,rows,files=parents();of=OUT/'n01-output-boundary-overlay.json';overlay=json.loads(of.read_text())
    for p,h in overlay['source_sha256'].items():assert sha(ROOT/p)==h,p
    return base,apply_updates(rows,overlay['updates']),(*files,of)


def cap_at(s,point,axis,radius):
    p=A.Vector(*point);d=A.Vector(*axis);hits=[]
    for f in s.Faces:
        if not isinstance(f.Surface,Part.Plane) or len(f.Edges)!=1:continue
        c=f.Edges[0].Curve
        if not isinstance(c,Part.Circle) or (c.Center-p).Length>1e-4 or abs(c.Radius-radius)>1e-5:continue
        if abs(f.Area-math.pi*radius**2)>1e-4:continue
        u,U,v,V=f.ParameterRange;n=f.normalAt((u+U)/2,(v+V)/2)
        if not s.isInside(p-n*.05,1e-7,False):n=-n
        if n.dot(d)>1-1e-6 and s.isInside(p-d*.05,1e-7,False):hits.append(f)
    assert len(hits)==1,('Missing or ambiguous real cap',point,axis,radius,len(hits))
    return dict(actual_project_cap_verified=True,point_mm=list(hits[0].CenterOfMass),radius_mm=radius,supplier_dimensions_guaranteed=False)


def main():
    tick=time.monotonic();base,rows,files=parents();index={r['id']:r for r in rows};f,receipt=received();actors=load(receipt,'geometry');contract,pf,bf=profiles();updates={};caps={}
    for w,r in receipt['recipes'].items():
        d=r['d'];opposite=[-v for v in d];factory=r['factory'];custom=r['custom'];radius=contract['portions'][w+'/custom']['project_radius_mm']
        for suffix,point,axis,actor in (
            ('factory/start',factory[0]['start'],opposite,'EndFactory:'+w),
            ('factory/end',factory[-1]['end'],d,'EndFactory:'+w),
            ('custom/start',r['custom_exit'],r['custom_axis'],'EndCustom:'+w)):
            name=w+'/'+suffix;assert name in index;source=actors[actor]
            caps[name]=cap_at(source,point,axis,2.1 if '/factory/' in name else radius)
            routing_axis=d if suffix=='factory/start' else opposite if suffix=='factory/end' else axis
            value=dict(routing_exit_mm=point,routing_exit_axis=routing_axis,prefix_geometry_owner=actor,
                routing_boundary_status='CURRENT_RECEIVED_END_BAY_ACTUAL_CAP',full_middle_route_accepted='/factory/' in name,
                supplier_datum_guaranteed=False,minimum_R_mm=contract['portions'][index[name]['portion_id']].get('minimum_project_R_mm'))
            if suffix=='custom/start':
                value.update(point_mm=custom[0]['start'],departure_axis=d,jacket_routing_point_mm=custom[0]['start'],
                    jacket_grip9_mm=[r['custom_grip'],[r['custom_grip'][0],r['custom_grip'][1],r['custom_grip'][2]+9]],
                    grip_axis=[0,0,1],grip_length_mm=9,initial_jacket_land_mm=.25,
                    source_prefix_length_mm=sum(e['length_mm'] for e in custom),support_owner='EndGrip:Custom:'+w+':pad')
            elif suffix=='factory/end':value.update(point_mm=point,departure_axis=opposite,support_owner='EndGrip:Factory:'+w+':pad')
            updates[name]=value
    resolved=apply_updates(rows,updates);assert len(resolved)==246 and len(base['portions'])==123 and len(updates)==12
    for a,b in zip(rows,resolved):
        if a['point_mm'] is None:assert b['point_mm'] is None
    pins=(*files,f,ROOT/receipt['bundle'],pf,bf,Path(__file__),ROOT/'tools/cad/feline_output_composed_context.py',ROOT/'tools/cad/feline_selected_material_contract.py')
    result=dict(status='CURRENT_OUTPUT_ENDS_COMPOSED_REMAINING_N01_OPEN',updates=updates,actual_cap_receipts=caps,
        physical_portions=123,ordinary_ends=246,identity_and_logical_None_preserved=True,selected_SKU_radii_and_bends_required_for_all_portions=True,
        factory100_is_project_assumption=True,no_new_factory_wire_or_connector=True,only_working_plan_not_selected_native=True,
        N01_complete=False,physical_pass=False,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-output-boundary-overlay.json',result)
    print(json.dumps(dict(status=result['status'],updated=12,actual_caps=len(caps),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()

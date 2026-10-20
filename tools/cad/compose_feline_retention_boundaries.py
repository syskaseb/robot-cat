"""Seven physical exit deltas; preserve the parent246-end electrical register."""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_retention_composed_context import received
from receive_feline_psys_frame_load_paths import load
from compose_feline_integrated_boundaries import apply_updates


def main():
    tick=time.monotonic();cf,gf,core,graph=received();parts=load(core,'geometry')
    ef=OUT/'n01-shared-routing-boundaries.json';base=json.loads(ef.read_text())
    uf=OUT/'n01-integrated-upper-boundary-overlay.json';upper=json.loads(uf.read_text());assert upper['parent_sha256']==sha(ef)
    rows=apply_updates(base['endpoints'],upper['updates']);updates={}
    for endpoint in ('P_SYS.1','P_SYS.2','P_SYS.3','FL_P.1','FL_P.2','FL_P.3','FL_P.4'):
        ee=[e for e in rows if e['endpoint']==endpoint];assert len(ee)==1;old=ee[0]
        name=next(n for n,r in core['recipe'].items() if r.get('source_end')==old['id']) if endpoint.startswith('P_SYS') else 'Station:FL_P:wire:'+endpoint
        shape=parts[name];faces=[f for f in shape.Faces if isinstance(f.Surface,Part.Plane)];assert len(faces)==2
        q=core['recipe'][name]['start_mm'] if endpoint.startswith('P_SYS') else old.get('jacket_routing_point_mm') or old['point_mm']
        assert q is not None,'Never fabricate an internal terminal'
        start=min(faces,key=lambda f:(f.CenterOfMass-A.Vector(*q)).Length);end=max(faces,key=lambda f:(f.CenterOfMass-A.Vector(*q)).Length)
        assert (start.CenterOfMass-A.Vector(*q)).Length<1e-5 and abs(start.Area-end.Area)<1e-5
        u,U,v,V=end.ParameterRange;axis=end.normalAt((u+U)/2,(v+V)/2);point=end.CenterOfMass
        if not shape.isInside(point-axis*.1,1e-7,False):axis=-axis
        assert shape.isInside(point-axis*.1,1e-7,False)
        radius=math.sqrt(end.Area/math.pi)
        change=dict(routing_exit_mm=list(point),routing_exit_axis=list(axis),prefix_geometry_owner=name,
            radius_from_current_source_cap_mm=radius,source_prefix_length_mm=shape.Volume/end.Area,
            routing_boundary_status='CURRENT_RECEIVED_RETENTION_NODE_PREFIX_EXIT',full_middle_route_accepted=False,
            total_factory_or_bought_wire_length_changed=False,supplier_datum_guaranteed=False)
        if endpoint.startswith('FL_P'):
            d=(point-start.CenterOfMass);d.normalize();land=start.CenterOfMass+d*.25
            change.update(jacket_grip9_mm=[list(land),list(land+d*9)],grip_axis=list(d),grip_length_mm=9,
                retained_straight_after_grip_mm=3.,same_actual_case_all_ports_and_selected_T18I_preserved=True)
        else:change.update(retained_original_first9_grip=True,minimum_R_mm=25.2)
        updates[old['id']]=change
    resolved=apply_updates(rows,updates);assert len(resolved)==246 and len(base['portions'])==123
    assert all(a.get('point_mm')==b.get('point_mm') for a,b in zip(rows,resolved))
    result=dict(status='CURRENT_RETENTION_LAYOUT_AND_SEVEN_END_DELTAS_RECEIVED_WHOLE_N01_OPEN',
        base_register=ef.relative_to(ROOT).as_posix(),base_sha256=sha(ef),upper_overlay=uf.relative_to(ROOT).as_posix(),upper_sha256=sha(uf),
        updates=updates,changed_actor_archive=core['bundle'],changed_actor_archive_sha256=core['bundle_sha256'],
        changed_actors=[r['name'] for r in core['geometry']],retired_only=core['retired_only_own_custom_prefix_actors']+[core['retired_printed_support']],
        total_physical_portions=123,total_ordinary_ends=246,logical_None_and_all_case_terminal_points_unchanged=True,
        only_working_plan_overlay_not_selected_native=True,N01_complete=False,selected=False,physical_pass=False,
        whole_corridor_links_packing_other_roots_and_installation_still_OPEN=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (cf,gf,ef,uf,ROOT/core['bundle'],Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-current-retention-layout-overlay.json',result)
    print(json.dumps(dict(status=result['status'],changed_ends=len(updates),actors=len(core['geometry']),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()

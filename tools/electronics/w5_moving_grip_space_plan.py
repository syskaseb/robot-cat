"""One dimensional plan for12source grips, without changing P0 or paths.

Read only saved servo cases/carriers and ownership; no recompute, whole E6
load, collision search or inferred manufacturing approval. Actual planar and
cylindrical faces are mounting inputs, not merely part bounding boxes.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
from check_main_p0_placement import SavedShapes,prop
from check_p0_leg_geometry import world_shape
from w5_leg_corridors_r1 import components

OUT=ROOT/'hardware/electronics/full-cat/w5-moving-grip-space-plan-r1'
ENTRY=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
MAP=ROOT/'hardware/electronics/full-cat/w5-leg-source-map-r1/interface.json'
CORRIDORS=ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r3/intent.json'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    source=json.loads(MAP.read_text(encoding='utf-8'));routes=json.loads(CORRIDORS.read_text(encoding='utf-8'))['routes']
    for rel,digest in source['source_sha256'].items():assert sha(ROOT/rel)==digest,rel
    reader=SavedShapes();objects=reader.doc(ENTRY);component=components(objects)
    members={x.get('value') for x in prop(objects['RobotCatAssembly24'],'Group').findall('.//Link')}
    rows=[]
    def features(s):
        flat=[];holes=[]
        for i,f in enumerate(s.Faces,1):
            surf=f.Surface
            if isinstance(surf,Part.Plane) and f.Area>20:
                p=f.CenterOfMass;u,v=surf.parameter(p);normal=f.normalAt(u,v)
                flat.append(dict(face=i,area_mm2=f.Area,center_mm=list(p),outward_normal=list(normal)))
            elif isinstance(surf,Part.Cylinder) and 1<=surf.Radius<=4:
                holes.append(dict(face=i,radius_mm=surf.Radius,axis=list(surf.Axis),center_mm=list(surf.Center),
                                  fastener_or_external_surface_not_identified=True))
        return dict(planar_mount_inputs=flat,cylindrical_mount_inputs=holes,
                    source_valid=s.isValid(),solid_count=len(s.Solids))
    for row in source['looms']:
        route=next(r for r in routes if r['loom']==row['loom'])
        case=world_shape(reader,ENTRY,objects,row['housing'],members)
        group=component('Rigid_'+row['housing']);assert group==component('Rigid_'+row['pcb']),row['loom']
        carrier_rows=[]
        for wrapper in route['carriers']:
            assert component(wrapper)==group,(row['loom'],wrapper)
            child=prop(objects[wrapper],'Group').findall('.//Link');assert len(child)==1
            name=child[0].get('value');shape=world_shape(reader,ENTRY,objects,name,members)
            carrier_rows.append(dict(wrapper=wrapper,part=name,label=prop(objects[name],'Label')[0].get('value'),
                rigid_component_matches_case_and_PCB=True,features=features(shape)))
        pcbpose=reader.placement(objects['Rigid_'+row['pcb']])*reader.placement(objects[row['pcb']])
        local=case.copy();local.Placement=pcbpose.inverse()*case.Placement
        b=local.BoundBox
        p=A.Vector(*route['waypoints_mm'][0]);direction=A.Vector(*row['cable_exit_world_axis'])
        grip=p+direction*20
        assert (A.Vector(*route['waypoints_mm'][1])-p).Length>=40-1e-6
        rows.append(dict(loom=row['loom'],case=row['housing'],case_and_PCB_rigid_component=group,
            case_in_PCB_frame_bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
            case_surface_inputs_world=features(case),carriers=carrier_rows,
            route_start_mm=list(p),route_exit_axis=list(direction),proposed_source_grip_mm=list(grip),
            proposed_source_grip_in_PCB_frame_mm=list(pcbpose.inverse().multVec(grip)),
            point_on_received_straight_lead=True,proposed_grip_20mm_after_route_start_is_assumption=True,
            source_free_bend_and_connector_assembly_space_pending=True,
            mount_choice='One removable case/carrier clip; use actual face profile with non-slip strap capture, not PCB or plug. Do not add thickness under existing P0 bolts without a separate verified stack.',
            electrical_splices_added=0,P0_mounts_changed=False))
        print('MOVING_GRIP_SPACE',row['loom'],'same_rigid_case_PCB_carrier',flush=True)
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    pins=[Path(__file__),MAP,CORRIDORS,ENTRY,ROOT/'tools/electronics/w5_leg_corridors_r1.py',
          ROOT/'tools/cad/check_main_p0_placement.py',ROOT/'tools/cad/check_p0_leg_geometry.py']
    save(OUT/'plan.json',dict(status='TWELVE_SOURCE_GRIP_DIMENSIONAL_PLAN_NOT_CONSTRUCTION',looms=rows,
        received_routes_unchanged=True,all_case_PCB_carrier_groups_match=True,
        frozen_fixed_frames_unaffected=True,actual_mount_profiles_recorded=True,
        planned_source_grips=12,constructed_source_grips=0,
        native_geometry_complete=False,motion_qualified=False,assembly_qualified=False,
        stock_selected=False,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        next='Choose one clip cross-section and retention/load path from these actual case/carrier faces; jointly include12clips, factory leads, straps, motion and tools before native construction. Source grip datums remain provisional.' ))


if __name__=='__main__':main()

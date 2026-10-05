"""Receive all four hip case/cover sections and rigid ownership first.

No new mount geometry and no position search. Covers may not be captured by
a moving root unless they belong to the SAME existing fixed component.
Bounding ranges allocate a corridor; exact section intersections are evidence.
"""
from pathlib import Path
from datetime import datetime, timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
from check_main_p0_placement import SavedShapes,prop
from w5_leg_corridors_r1 import components
from w5_selected_owners_r52 import cached

BASE=ROOT/'hardware/electronics/full-cat';OUT=BASE/'w5-hip-source-mount-plan-r1'
ENTRY=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
MAP=BASE/'w5-leg-source-map-r1/interface.json'
PROFILE=BASE/'w5-source-mount-full-profile-r1/plan.json'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    r=SavedShapes();objects=r.doc(ENTRY);fixed_group=components(objects)
    members={x.get('value') for x in prop(objects['RobotCatAssembly24'],'Group').findall('.//Link')}
    material,cache=cached()
    wanted={}
    for wrapper in members:
        if not wrapper.startswith('Rigid_'):continue
        group=prop(objects[wrapper],'Group');children=group.findall('.//Link') if group is not None else []
        if len(children)==1:wanted[children[0].get('value')]=wrapper
    source=json.loads(MAP.read_text(encoding='utf-8'))
    profile=json.loads(PROFILE.read_text(encoding='utf-8'))
    looms=[row for row in source['looms'] if row['loom'].endswith('1')];assert len(looms)==4
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    rows=[];sections=[]
    for row in looms:
        prior=next(p for p in profile['rows'] if p['loom']==row['loom'])
        pose=r.placement(objects['Rigid_'+row['pcb']])*r.placement(objects[row['pcb']])
        case_group=fixed_group('Rigid_'+row['housing']);assert case_group==fixed_group('Rigid_'+row['pcb'])
        local={}
        for name,wrapper in wanted.items():
            if name not in material:continue
            s=material[name].copy();s.Placement=pose.inverse()*s.Placement;local[name]=s
        slab=Part.makeBox(6.2,80,70,A.Vector(-7.5,-60,-35))
        sections_for_loom=[];covers=[]
        for name,s in local.items():
            if not s.BoundBox.intersect(slab.BoundBox):continue
            label=prop(objects[name],'Label')[0].get('value')
            if 'Cover' not in label:continue
            c=s.common(slab)
            if c.Volume<=1e-6:continue
            same=case_group==fixed_group(wanted[name])
            covers.append(dict(name=name,label=label,same_rigid_component=same,
                fixed_component=fixed_group(wanted[name]),actual_slab_common_mm3=c.Volume,
                full_bounds_PCB_mm=bounds(s),slab_bounds_PCB_mm=bounds(c)))
            world=c.copy();world.Placement=pose*world.Placement;sections_for_loom.append(world)
        all_case=Part.makeCompound([local[v['name']] for v in prior['complete_case_parts']])
        case_slice=Part.makeCompound([solid.common(slab) for v in prior['complete_case_parts'] for solid in local[v['name']].Solids])
        assert case_slice.Volume>1e-6
        world=case_slice.copy();world.Placement=pose*world.Placement;sections_for_loom.append(world)
        rows.append(dict(loom=row['loom'],pcb=row['pcb'],root_fixed_component=case_group,
            complete_case_slab_bounds_PCB_mm=bounds(case_slice),cover_sections=covers,
            may_capture_cover=all(c['same_rigid_component'] for c in covers),
            cover_present_in_actual_root_slab=bool(covers),
            unchanged_source_saddle_PCB_mm=[-11.55,-50.5,5],
            print_root_slab_x_PCB_mm=[-7.5,-1.3],
            provisional_band_axis_x_PCB_mm=-3.65))
        sections.extend(sections_for_loom)
        print('HIP_MOUNT_PLAN',row['loom'],[(c['label'],c['same_rigid_component'],c['slab_bounds_PCB_mm']) for c in covers],flush=True)
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    geometry=OUT/'FOUR_HIP_CASE_COVER_SECTIONS_WORLD.brep'
    Part.makeCompound(sections).exportBrep(str(geometry))
    pins=[Path(__file__),ENTRY,MAP,PROFILE,ROOT/'tools/electronics/w5_leg_corridors_r1.py',
        BASE/'w5-installed-r52/owners.json',BASE/'w5-installed-r52'/cache['geometry']]
    save(OUT/'plan.json',dict(status='FOUR_HIP_CASE_COVER_OWNERSHIP_AND_SECTIONS_RECEIVED',rows=rows,
        all_covers_share_root_fixed_component=all(row['may_capture_cover'] for row in rows),
        bounds_are_allocation_not_collision_verdict=True,grip_geometry_built=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={**r.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in pins}},
        files={geometry.relative_to(ROOT).as_posix():sha(geometry)}))


if __name__=='__main__':main()

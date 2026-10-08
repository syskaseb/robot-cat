"""CAD-derived ceiling and occupied vertical intervals for the next ONE layout.

These exact ray sections are planning samples, not proof of a full wire or
footprint. Bbox only filters candidates; valid BRep intersections supply data.
Retained structure, movable carrier and service tools have separate ownership.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,time
import FreeCAD as A
import Part
from open_prototype_entry_chambers import MOUNTS,CONTEXT
from open_prototype_wiring_endpoints import ROOT,BASE,read,sha

OUT=BASE/'wiring-checkpoint';DEST=OUT/'routing-space-map.json'


def intervals(shape,ray):
    assert shape.isValid(),'Invalid shape is not a planning obstacle'
    hit=shape.common(ray);assert hit.isValid()
    return [[round(e.BoundBox.ZMin,5),round(e.BoundBox.ZMax,5)]
            for e in hit.Edges if e.Length>1e-7]


def main():
    assert not DEST.exists(),'Use the received map, do not repeat unchanged sections'
    tick=time.monotonic();docs=[A.openDocument(str(p)) for p in (MOUNTS,CONTEXT)]
    mount,ctx=docs;torso=ctx.TorsoEnvelope.Shape
    assert torso.isValid() and len(torso.Solids)==1 and not torso.check(True)
    sources=(MOUNTS,CONTEXT,OUT/'shared-allocation-plan.json',OUT/'complete-main-space-plan.json',Path(__file__))
    result=dict(status='CAD_SECTION_PLANNING_MAP_NOT_ROUTE_ACCEPTANCE',selected=False,
        stage_completed=False,physical_pass=False,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},
        samples=[],station_footprints=[],errors=[],
        constraints=['Torso325x200x160 retained; no height from bbox or added MAIN datum',
            'Intervals are centreline samples; add full conductor/insulation/grip/tool envelope before selection',
            'Minimum sampled ceiling is an upper bound, not a proof of a full case footprint',
            'P0/load path constraints stay; movable carrier cuts need explicit coherent redesign',
            'Service tool intervals are separate; omit only with a documented assembly/service sequence'])
    fixed={}
    for o in ctx.Objects:
        if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
        if o.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) and o.Name!='P0_MG92BMount29':
            ownership='service_tool' if ('driver' in o.Name.lower() or 'key' in o.Name.lower()) else 'retained_P0_or_control'
            fixed[o.Name]=(o.Shape,ownership)
    for o in mount.Objects:
        if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
        if o.Name in ('UpperCarrier','LowerCarrier'):
            fixed[o.Name]=(o.Shape,'movable_carrier_redesign_requires_load_path')
        elif o.Name.endswith('NominalPCB') or o.Name.startswith('BUSsupplier') or o.Name=='U1BoardAllowance':
            fixed[o.Name]=(o.Shape,'U1_delivery_allowance' if o.Name=='U1BoardAllowance' else 'retained_board_reference')
    try:
        for x in (-95,-65,-35,-5,25,55,85,115,145,175):
            for y in (-75,-50,-25,0,25,50,75):
                ray=Part.makeLine(A.Vector(x,y,-3),A.Vector(x,y,159))
                try:
                    body=intervals(torso,ray);occupied=[]
                    for name,(s,owner) in fixed.items():
                        b=s.BoundBox
                        if not (b.XMin-1e-7<=x<=b.XMax+1e-7 and b.YMin-1e-7<=y<=b.YMax+1e-7):continue
                        spans=intervals(s,ray)
                        if spans:occupied.append(dict(part=name,ownership=owner,z_intervals_mm=spans))
                    result['samples'].append(dict(x_mm=x,y_mm=y,torso_z_intervals_mm=body,occupied=occupied))
                except Exception as e:result['errors'].append(dict(x=x,y=y,error=str(e)))
        old=read(OUT/'shared-allocation-plan.json')['distribution']
        new=read(OUT/'complete-main-space-plan.json')['distribution']
        for candidate,row in [('retained_allocation',r) for r in old]+[
                ('rejected_high_galleries',r) for r in new if r['role'] in ('P_SYS','P_REAR','P_FRONT','P_AUX')]:
            x,y,z=row['centre_mm'];width,depth,height=row['size_mm'];ceilings=[];no_section=[]
            for dx in (-width/2,0,width/2):
                for dy in (-depth/2,0,depth/2):
                    ray=Part.makeLine(A.Vector(x+dx,y+dy,-3),A.Vector(x+dx,y+dy,159))
                    spans=intervals(torso,ray)
                    if spans:ceilings.append(max(q[1] for q in spans))
                    else:no_section.append([x+dx,y+dy])
            ceiling=min(ceilings) if ceilings else None
            result['station_footprints'].append(dict(role=row['role'],source=candidate,
                proposed_centre_mm=row['centre_mm'],size_mm=row['size_mm'],
                nine_ray_min_ceiling_mm=ceiling,no_torso_section_xy=no_section,
                maximum_sampled_centre_z_mm=None if ceiling is None else ceiling-height/2,
                current_top_mm=z+height/2,
                rejected_by_ceiling_samples=bool(no_section) or ceiling is None or z+height/2>ceiling,
                full_case_volume_check_required=True))
    finally:
        for d in docs:A.closeDocument(d.Name)
        result.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    assert not result['errors'],result['errors']
    assert all(sha(ROOT/n)==v for n,v in result['source_sha256'].items())
    print(json.dumps(dict(status=result['status'],grid_sections=len(result['samples']),
        footprints=len(result['station_footprints']),rejected_high_galleries=[r for r in result['station_footprints'] if r['source']=='rejected_high_galleries'],
        worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()

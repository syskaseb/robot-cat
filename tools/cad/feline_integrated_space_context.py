"""Compose the received upper layout; reuse only unchanged source voxel cells."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def reusable_cell(name,unchanged_fixed,parent_parts):
    return name in parent_parts and (name.startswith('Rest:') or
        name.startswith('Static:') and name[7:] in unchanged_fixed)


def integrated():
    from plan_feline_long_return import frozen_core
    cf=OUT/'n01-shared-Pi-carrier-r3-core-received.json'
    wf=OUT/'n01-shared-Pi-carrier-r3-world-received.json'
    core=json.loads(cf.read_text());received=json.loads(wf.read_text())
    assert not core['failures'] and not core['errors']
    assert received['status']=='SEPARATED_PORT_BAYS_STATIC36MOTION_RECEIVED_ROOTS_TOOLS_CAPACITY_OPEN'
    assert not received['failures'] and not received['errors']
    assert received['all_motion_received_without_static_deferral']
    world,parts,meta,pins,actors,roles,rows,inverse,outer,_,recipe=frozen_core(core)
    fixed={n:s for n,s in parts.items() if meta[n].get('group')!='PiUpper'
        and meta[n].get('role')!='BUS' and not n.startswith('CurrentBUS:')}
    for n in recipe['fixed_replaced_names']:fixed.pop(n)
    unchanged=set(fixed)-set(actors)
    parts={**fixed,**actors};meta={**{n:meta[n] for n in fixed},**rows}
    parentfile=OUT/'n01-current-signed-space.json';parent=json.loads(parentfile.read_text())
    assert parent['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY'
    assert parent['layer_checkpoint']['motion_count']==len(world.motion)
    assert parent['source_sha256']['tools/cad/feline_signed_voxels.py']==sha(ROOT/'tools/cad/feline_signed_voxels.py')
    for p,h in world.pins.items():assert parent['source_sha256'][p]==h,('Changed motion/fixed source',p)
    for p,h in parent['source_sha256'].items():
        if p=='tools/cad/build_feline_current_signed_space.py':continue
        assert sha(ROOT/p)==h,('Changed original cell source',p)
    archive=ROOT/parent['voxel_source_archive'];field=ROOT/parent['field']
    assert sha(archive)==parent['voxel_source_archive_sha256'] and sha(field)==parent['field_sha256']
    for p in (cf,wf,parentfile,archive,field,ROOT/'tools/cad/feline_integrated_space_context.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    return world,parts,meta,pins,dict(parent=parent,parentfile=parentfile,
        archive=archive,field=field,unchanged=unchanged,inverse=inverse,outer=outer)

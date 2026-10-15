"""Current real scene and thirteen frozen source lands; no old long trees."""
import json,copy
from pathlib import Path
from remaining_source_retention_material import geometry,saddle
from current_mixed_receiver_material import prepare
from current_body_restraint_material import prepare as other_retention
from current_body36_candidates import resolve
from plan_body36_receiver_space import P,C
from check_main_p0_placement import SavedShapes
from plan_remaining_source_retention import land


def context():
    q=geometry();profiles={n:saddle(g) for n,g in q['recipes'].items()}
    proof_file=P.OUT/'remaining-source-retention-checks.json';proof=json.loads(proof_file.read_text())
    assert proof['source_sha256']['tools/cad/remaining_source_retention_material.py']==P.SHA(Path(__file__).with_name('remaining_source_retention_material.py'))
    assert proof['recipes']==q['recipes']
    assert len([r for r in proof['components'] if r['name'].startswith('SourceLacing/') and not r['contacts']])==13
    override_file=P.OUT/'source-retention-seat-overrides.json';override_pins=set()
    if override_file.exists():
        override=json.loads(override_file.read_text());override_pins.add(override_file)
        for gid,o in override['overrides'].items():
            g=copy.deepcopy(q['recipes'][gid]);assert g['wire']==o['wire']
            assert g['centre_world_mm']==o['require_original_centre_mm']
            pf=P.OUT/o['new_source_recipe'];p=json.loads(pf.read_text());override_pins.add(pf)
            route=p['routes'][o['wire']];assert route['radius_mm']==g['project_insulation_radius_mm']
            g.update(land(route['parts'],o['new_part_index'],o['new_land_mm'],o['new_offset_on_part_mm']))
            g.update(normal=o['new_normal'],source_recipe=o['new_source_recipe'],segment=o['new_segment'],
                     geometry_override_basis=o['basis'])
            profiles[gid]=saddle(g);g['saddle']=profiles[gid]['recipe'];q['recipes'][gid]=g
    targets,wires,pins,grips=prepare();extras,ep=other_retention();targets.update(extras);pins.update(ep)
    mf=P.OUT/'body36-shared-macro-layout.json';macro=json.loads(mf.read_text())
    assert not macro['remaining_wire_ids'];routes,_=resolve(macro,P.ROOT)
    wires={n:v for n,v in wires.items() if not n.startswith('body/')}
    wires.update({'body/'+n:(P.wire(r['parts']),1) for n,r in routes.items()})
    reader=SavedShapes();nf=P.OUT/'receiver-supports/manifest.json';native=json.loads(nf.read_text())
    assert native['status']=='FOUR_CURRENT_RECEIVER_FRAMES_SEVEN_CAPS_NATIVE_PREPARED'
    for n,h in native['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    model=P.OUT/'receiver-supports/ReceiverSupportsCurrent.FCStd';parents={}
    for r in native['parts']:
        s=reader.shape(model,r['object']);targets['CurrentNative/'+r['part']]=s
        if r['kind']=='replacement_Frame':parents[r['part']]=s
    for r in native['feed_restraints']:
        name=r['lacing_reference'];targets['CurrentNative/'+name]=reader.shape(model,name)
    parents.update(q['parents'])
    pins.update(reader.hashes);pins.update(q['source_sha256'])
    for p in override_pins|{Path(__file__).with_name('plan_remaining_source_retention.py')}:
        pins[p.relative_to(P.ROOT).as_posix()]=P.SHA(p)
    for f in (Path(__file__),nf,mf,proof_file):pins[f.relative_to(P.ROOT).as_posix()]=P.SHA(f)
    assert len(parents)==7
    return targets,wires,pins,profiles,q['recipes'],parents,grips


def same_parent(owner,name,grips):
    if owner in ('LeftRiser','RightRiser'):return name=='neck/'+owner or name.startswith('neck/'+owner+'/')
    if name=='CurrentNative/'+owner or name.startswith(owner+'/'):return True
    if name.startswith(('Root/'+owner+'/','ReceiverRoot/'+owner+'/','Source/'+owner+'/body/')):return True
    if name.startswith('Group_') and name.endswith('/body'):
        g=grips['groups'].get(name.split('/')[0].removeprefix('Group_'))
        return bool(g and g['owner']==owner)
    return owner=='UpperCarrier001' and name in ('G1/carrier','FixedFeed/Heavy3/body','FixedFeed/BUS_G/body')

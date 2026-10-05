"""Receive only a stepped end of the continuous Cover's south rim.

The prior exact witness occupies X-50.5..-46.5,Y-98..-97,Z130..134.
Step the terminal rim north to Y-96.5; keep its western mount connection,
the two hood-post bridges, all frame/strap geometry and four service bays.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_side_retention_receive as R
from servo_fuse_inputs_r1 import save,sha

C=R.C;ROOT=R.ROOT;OUT=C.R.N.BASE/'w5-side-retention-received-r2'
RIM={'SouthRimWest':[-90,-98,130,-52,-93,134],
     'SouthRimSteppedEnd':[-53,-96.5,130,-43,-93,134]}


def main():
    import FreeCAD as A,Part
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    prior_path=R.OUT/'checks.json';prior=json.loads(prior_path.read_text(encoding='utf-8'))
    assert prior['cover_solids']==1 and prior['protected_interfaces_preserved'] and not prior['errors']
    assert len(prior['hits'])==1 and prior['hits'][0]['part']=='OffsetMountSouthRimReturn' and prior['hits'][0]['owner']=='SourceDeck'
    pins=[Path(__file__),Path(R.__file__),prior_path]
    for rel,digest in {**prior['source_sha256'],**prior['files']}.items():
        assert sha(ROOT/rel)==digest,rel;pins.append(ROOT/rel)
    bp=json.loads((ROOT/prior['native_blueprint']).read_text(encoding='utf-8'))
    del bp['cover_bridges']['OffsetMountSouthRimReturn'];bp['cover_bridges'].update(RIM)
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    core=Part.read(str(C.OUT/'CoverFourSideBays_CANDIDATE_WORLD.brep'))
    bridges={n:box(b) for n,b in bp['cover_bridges'].items()}
    cover=core.multiFuse(list(bridges.values()));bop=cover.check(True) or []
    fixed,printed,_,_,_,loaded,_,_=C.R.S.load(A,Part);pins+=loaded
    central=json.loads(C.R.N.CENTRAL.read_text(encoding='utf-8'))
    for wire,row in central['routes'].items():
        p=ROOT/row['geometry'];fixed[wire]=Part.read(str(p));pins.append(p)
    for owner in ('SourceCarrier','SourceEastHood','SourceWestHood'):
        p=ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1'/(owner+'_CANDIDATE_WORLD.brep')
        printed[owner]=Part.read(str(p));pins.append(p)
    p=ROOT/'hardware/cad/studies/w5-central-retention-native-r1/CentralRetentionDeck_CANDIDATE_WORLD.brep'
    printed['SourceDeck']=Part.read(str(p));pins.append(p)
    for alias in C.R.N.OWNER_ALIASES:printed.pop(alias,None)
    printed.pop('SourceCover',None)
    r4=json.loads(C.R.R.P.CENTRAL.read_text(encoding='utf-8'))
    for name,rel in r4['world_geometries'].items():
        p=ROOT/rel;fixed['CentralRetention/'+name]=Part.read(str(p));pins.append(p)
    side_path=R.OUT/'SideRetention_PROPOSED_WORLD.brep'
    side=Part.read(str(side_path));children=side.childShapes()
    assert len(children)==len(prior['compound_role_order'])
    sides=dict(zip(prior['compound_role_order'],children));pins.append(side_path)
    hits=[];errors=[];pairs=0
    for name in RIM:
        s=bridges[name]
        for owner,t in {**fixed,**printed,**sides}.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            for a in s.Solids:
                for q in t.Solids:
                    if not a.BoundBox.intersect(q.BoundBox):continue
                    pairs+=1
                    if separated(a,q):continue
                    try:
                        common=a.common(q)
                        if common.Volume>1e-6:hits.append(dict(part=name,owner=owner,mm3=common.Volume,bounds_mm=C.bounds(common)))
                    except Exception as e:errors.append(dict(part=name,owner=owner,error=str(e)))
    # No original core material is dropped. Mount/post material was in this
    # core already; inherited interface proof remains valid after adding ribs.
    original_core_retained=core.cut(cover).Volume<1e-5
    rim_join=bridges['SouthRimWest'].common(bridges['SouthRimSteppedEnd']).Volume
    OUT.mkdir(parents=True,exist_ok=True)
    p=OUT/'CoverConnectedBays_CANDIDATE_WORLD.brep';cover.exportBrep(str(p))
    blueprint=OUT/'native-blueprint.json';save(blueprint,bp)
    valid=cover.isValid() and len(cover.Solids)==1 and not bop and original_core_retained and rim_join>1e-6
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='COUPLED_SIDE_RECEIVED_CLEAR_NATIVE_PENDING' if valid and not hits and not errors else 'COUPLED_SIDE_RECEIVE_REJECTED',
        hits=hits,errors=errors,pairs=pairs,inherited_unchanged_pair_receipt=prior_path.relative_to(ROOT).as_posix(),
        cover_valid=cover.isValid(),cover_solids=len(cover.Solids),cover_BOP_errors=bop,cover_after_mm3=cover.Volume,
        original_three_cover_components_retained=original_core_retained,rim_step_join_mm3=rim_join,
        protected_interfaces_preserved=prior['protected_interfaces_preserved'],protected_mount_interfaces=prior['protected_mount_interfaces'],
        native_blueprint=blueprint.relative_to(ROOT).as_posix(),side_geometry=side_path.relative_to(ROOT).as_posix(),
        compound_role_order=prior['compound_role_order'],block_count=8,endpoint_count=35,body_ties=8,insulation_ties=35,
        terminal_rim_Deck_nominal_gap_mm=.5,frozen_37_routes=True,new_screws=0,new_separate_prints=0,
        native_parameter_roots_reopen_mount_motion_stock_pending=True,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p),blueprint.relative_to(ROOT).as_posix():sha(blueprint)}))
    print('SIDE_RECEIVE_R2',pairs,len(hits),len(errors),len(cover.Solids),flush=True)


if __name__=='__main__':main()

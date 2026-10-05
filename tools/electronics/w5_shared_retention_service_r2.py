"""Reconcile current parent ownership before repeating service geometry.

R1 included the retired R52 Deck: two10mm contacts are retained as witnesses,
not used to cut the current Deck. Receive identical new-root comparisons at
2/5/10mm and unchanged fixed-owner pairs; test actual replacement parents
and all higher requested poses. No physical part is omitted for a collision.
"""
from pathlib import Path
SOURCE=Path(__file__).with_name('w5_shared_retention_service.py')
code=SOURCE.read_text(encoding='utf-8')
code=code.replace("OUT=BASE/'w5-shared-retention-service-r1'","OUT=BASE/'w5-shared-retention-service-r2'")
needle="    hits=[];errors=[];pairs=0\n"
replacement="""    prior=read(BASE/'w5-shared-retention-service-r1/checks.json')
    assert not prior['errors'] and len(prior['hits'])==2
    assert all(h['lift_mm']==10 and h['fixed']=='CandidateDeck' for h in prior['hits'])
    for rel,h in prior['source_sha256'].items():assert sha(ROOT/rel)==h,rel
    # These semantic parent identities follow the current native print map,
    # not a choice to remove geometry after seeing a contact.
    overrides={
        'CandidateDeck':'hardware/cad/studies/w5-remote-end-native-r1/CompleteDeck_CANDIDATE_WORLD.brep',
        'hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep':'hardware/cad/studies/w5-side-retention-native-r1/SourceCarrier_CANDIDATE_WORLD.brep',
        'Source/Bridge':'hardware/cad/studies/w5-remote-end-native-r1/SourceBridge_CANDIDATE_WORLD.brep'}
    for owner,rel in overrides.items():
        assert owner in owners,owner
        owners[owner]=load(ROOT/rel)
    aliases=[
        'hardware/electronics/full-cat/tail-ground-direct-r1/CarrierTailPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/tail-central-routes-r3/CarrierTailPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/head-connected-feeds-r8/CarrierPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/aux-converter-routes-r5/Carrier_TWO_PORTS_DIAGNOSTIC.brep']
    for owner in aliases:assert owner in owners;del owners[owner]
    pin53=ROOT/'tools/electronics/w5_r53_owners.py';pins[pin53.relative_to(ROOT).as_posix()]=sha(pin53)
    added_owners={}
    for role in ('FLFixedFrame','FRFixedFrame','RLFixedFrame','RRFixedFrame'):
        added_owners['Current/'+role]=load(ROOT/'hardware/cad/studies/w5-loom-fixed-native-r1'/(role+'_CANDIDATE_WORLD.brep'))
    added_owners['Current/SourcePlatform']=load(ROOT/'hardware/cad/studies/w5-source-platform-native-r4/Platform_WORLD.brep')
    hits=[];errors=[];pairs=0
"""
assert needle in code;code=code.replace(needle,replacement)
code=code.replace("    sampled=[];clear=[]", "    old_fixed.update(added_owners)\n    sampled=[];clear=[]")
code=code.replace("            for key,t in fixed.items():check(dz,name,q,key,t)","            if dz not in (2,5,10):\n                for key,t in fixed.items():check(dz,name,q,key,t)")
code=code.replace("            for key,t in {**old_fixed,**fixed}.items():check(dz,'CoverBridge/'+name,q,key,t)","            for key,t in {**old_fixed,**fixed}.items():\n                if dz in (2,5,10) and key not in overrides and key not in added_owners:continue\n                check(dz,'CoverBridge/'+name,q,key,t)")
code=code.replace("        fixed_new_roots=len(fixed),", "        retired_duplicate_Carrier_aliases=aliases,actual_parent_overrides=overrides,inherited_new_root_poses_mm=[2,5,10],inherited_unchanged_fixed_owner_poses_mm=[2,5,10],\n        fixed_new_roots=len(fixed),")
code=code.replace("source_sha256={**reader.hashes,**pins}","source_sha256={**reader.hashes,**pins,SOURCE.relative_to(ROOT).as_posix():sha(SOURCE)}")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

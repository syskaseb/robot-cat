"""Receive changed upper-front Cover against the existing shared release.

R2 only failed on the two removed rear rims. Receive its unchanged2/5/10mm
pairs; check every new upper connection against ALL retained rigid owners
and roots at each pose. Higher poses remain full changed-root checks. No
rigid obstacle is removed because it collides, no wired withdrawal assumed.
"""
from pathlib import Path
import runpy
R2=Path(__file__).with_name('w5_shared_retention_service_r2.py')
scope=runpy.run_path(str(R2),run_name='service_r2_definition')
code=scope['code'];SOURCE=scope['SOURCE']
code=code.replace("OUT=BASE/'w5-shared-retention-service-r2'","OUT=BASE/'w5-shared-retention-service-r3'")
code=code.replace("prior=read(BASE/'w5-shared-retention-service-r1/checks.json')","prior=read(BASE/'w5-shared-retention-service-r2/checks.json')")
code=code.replace("Cover=load(ROOT/'hardware/cad/studies/w5-side-retention-native-r1/SourceCover_CANDIDATE_WORLD.brep')",
                  "Cover=load(ROOT/'hardware/cad/studies/w5-cover-upper-front-native-r1/SourceCover_CANDIDATE_WORLD.brep')")
old="    additions={k:reader.shape(side,k) for k in bp['cover_bridges']}"
new="""    native=read(BASE/'w5-cover-upper-front-native-r1/checks.json')
    assert native['status']=='UPPER_FRONT_COVER_NATIVE_PARAMETER_EXPORT_REOPEN_COMPLETE'
    assert native['solids']==1 and native['BOP_errors']==0 and native['closed_STLs'] and native['relocated_reopen']
    for rel,h in {**native['source_sha256'],**native['files']}.items():assert sha(ROOT/rel)==h,rel
    newmaster=ROOT/'hardware/cad/studies/w5-cover-upper-front-native-r1/UpperFrontCoverRetention.FCStd'
    additions={k:reader.shape(side,k) for k in native['keep_original_bridges']}
    additions['UpperFrontConnection']=reader.shape(newmaster,'UpperFrontBridgeSlotted')
    pins['tools/electronics/w5_shared_retention_service_r2.py']=sha(ROOT/'tools/electronics/w5_shared_retention_service_r2.py')"""
assert old in code;code=code.replace(old,new)
code=code.replace("if dz in (2,5,10) and key not in overrides and key not in added_owners:continue",
                  "if dz in (2,5,10) and name!='UpperFrontConnection' and key not in overrides and key not in added_owners:continue")
code=code.replace("        fixed_new_roots=len(fixed),", "        received_previous_service='w5-shared-retention-service-r2',removed_rear_cover_bridges=['SouthRimWest','SouthRimSteppedEnd'],new_upper_connection_checked_all_rigid_owners=True,\n        fixed_new_roots=len(fixed),")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

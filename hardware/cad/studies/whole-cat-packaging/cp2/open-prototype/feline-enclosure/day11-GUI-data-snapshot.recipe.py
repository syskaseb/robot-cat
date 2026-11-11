# DATA-ONLY snapshot of retained/current and explicit reference layers. No new geometry.
import json,zipfile,hashlib,time,os
from pathlib import Path
tG=time.monotonic();cG=time.process_time();piG=json.loads((OUT/'day07-removable-Pi-carrier-current-candidate-composition.json').read_bytes());moG=json.loads((OUT/'day07-MODULE-V3-capacity-current-candidate-composition.json').read_bytes());s0G=json.loads((OUT/'day07-S0-C1-current-candidate-composition.json').read_bytes());snapshotpinsG=[]
def getG(ar,entry,sha=None):
 with zipfile.ZipFile(OUT/ar) as z:raw=z.read(entry)
 if sha:assert hashlib.sha256(raw).hexdigest()==sha
 s=Part.Shape();s.importBrepFromString(raw.decode());snapshotpinsG.append(dict(archive=ar,entry=entry,sha256=hashlib.sha256(raw).hexdigest()));return s
effG=dict(Current35);repG=s0G['replace_actual_parent'];effG[repG['actor']]=getG(repG['archive'],repG['geometry']['entry'],repG['geometry']['sha256']);m=moG['scoped_region_override'];effG[m['role']]=getG(m['new_archive'],m['new_geometry']['entry'],m['new_geometry']['sha256'])
with zipfile.ZipFile(OUT/piG['current_W37_source']) as z:gW=json.loads(z.read('manifest.json'))['geometry']
for n in piG['retained_source_cells']:
 g=next(q for q in gW if q['name']==n);effG['CandidateWest:'+n]=getG(piG['current_W37_source'],g['entry'],g['sha256'])
for g in piG['replacement_geometry']:effG['CandidatePi:'+g['name']]=getG(piG['replacement_archive'],g['entry'],g['sha256'])
for g in piG['selected_candidate_retention_geometry']:
 if not g['name'].endswith(':head_budget'):effG['CandidatePi:'+g['name']]=getG(piG['replacement_archive'],g['entry'],g['sha256'])
for g in moG['new_structural_tie_binding']['head_overrides']:effG['CandidatePi:'+g['name']]=getG(moG['new_structural_tie_binding']['head_override_archive'],g['entry'],g['sha256'])
with zipfile.ZipFile(OUT/s0G['add_eight_case_fixing_parts_from_immutable_C0']) as z:gm=json.loads(z.read('manifest.json'))['geometry']
for g in gm[1:9]:effG[g['name']]=getG(s0G['add_eight_case_fixing_parts_from_immutable_C0'],g['entry'],g['sha256'])
assert len(effG)==1311,len(effG)
docG=A.newDocument('N01WorkingUnselected');docG.Label='WORKING_UNSELECTED_N01_0of10 / retained1311 / sourcepins';stat=docG.addObject('App::FeaturePython','N01Status');stat.addProperty('App::PropertyString','Scope');stat.Scope='UNSELECTED whole N01=0/10. Effectivecandidate1311 source1292 def->2d1->a9f. ProposedG4/D5/SOURCE/reference layers not duplicate selectedparents. No geometryPASS.';stat.addProperty('App::PropertyString','ManifestSHA');stat.ManifestSHA='50b731263aa5dd24ecfba8d66d1db398bb3dcb80dcdc29686cc598e71187e20d';stat.addProperty('App::PropertyFloat','MAIN_mm');stat.MAIN_mm=46.52;stat.addProperty('App::PropertyInteger','RetainedCount');stat.RetainedCount=1311;stat.addProperty('App::PropertyString','SourcePartHashes');stat.SourcePartHashes=json.dumps(dict(def3='def3e56a8eca5cc84fe420299f0c4cfe08f0328d212940fb4614b372acf2ade1',module='2d1d8cfa3dfe17add2578abc31473126c39b3e86310d332383fd6365cc70b56e',S0='a9f78e06faa1f57007fb58f4163b72af74f85a752f92713abb57d6fb7647d93a'))
grpG=docG.addObject('App::DocumentObjectGroup','RetainedEffective1311');grpG.Label='CURRENT effective candidate1311 / not whole selected';mapG={}
def addG(group,n,s,role):
 ob=docG.addObject('Part::Feature','Actor'+str(len(mapG)));ob.Label=n;ob.Shape=s.copy();ob.addProperty('App::PropertyString','SourceActor');ob.SourceActor=n;ob.addProperty('App::PropertyString','EvidenceRole');ob.EvidenceRole=role;group.addObject(ob);mapG[n]=ob.Name;return ob
for n,s in effG.items():addG(grpG,n,s,'CURRENT_EFFECTIVE_CANDIDATE_WORLD_ONCE')
refsG=docG.addObject('App::DocumentObjectGroup','ProposedReferences');refsG.Label='PROPOSED alternatives / NEVER additive duplicateparents';rg=docG.addObject('App::DocumentObjectGroup','G4AlternativeReference');refsG.addObject(rg)
for n,s in g4dict15.items():addG(rg,n,s,'ALTERNATIVE_REFERENCE_ONLY replaceU1/FLG aliases whenselected; notphysicalduplicate')
dg=docG.addObject('App::DocumentObjectGroup','D5AlternativeReference');refsG.addObject(dg)
for n,s in d5dict15.items():addG(dg,n,s,'ALTERNATIVE_REFERENCE_ONLY completecaseback/disjointparts; parentexclusion required')
srcg=docG.addObject('App::DocumentObjectGroup','Source21Reference');refsG.addObject(srcg)
for n,s in op15.items():addG(srcg,'SOURCE21:'+n,s,'PROPOSED_MOTION_RL_KNEE_NEUTRAL_REFERENCE')
tmpg=docG.addObject('App::DocumentObjectGroup','Source4TempReference');refsG.addObject(tmpg)
for n,s in temp15.items():addG(tmpg,'SOURCE_TEMP4:'+n,s,'TEMPORARY_INSTALLATION_CAPACITY_NOT_OPERATING')
mg=docG.addObject('App::DocumentObjectGroup','Moving108Reference');refsG.addObject(mg)
for n,s in restMotion.items():addG(mg,'MOVING108:'+n,s,'FROZEN_NEUTRAL_MOVING_REFERENCE_NOT_ADDITIVE_BOM')
bg=docG.addObject('App::DocumentObjectGroup','BoundarySourceReference');refsG.addObject(bg);addG(bg,'ACTUAL_BodyOuter',BodyOuter31,'SOURCE_BOUNDARY_NOT_MATERIAL')
sg=docG.addObject('App::DocumentObjectGroup','SourceSteelReference');refsG.addObject(sg)
for n,s in layers15['ORIGINAL_SOURCE_FRONTL_METAL'].items():addG(sg,'SOURCE_ONLY:'+n,s,'SOURCE_NOMINAL_METAL_REFERENCE_CURRENT_ALIAS_UNRESOLVED_NOT_ADDITIVE_BOM')
docG.recompute();snapG=OUT/'day11-WORKING_UNSELECTED_N01_0of10.FCStd';docG.saveAs(str(snapG));idxG=OUT/'day11-GUI-working-snapshot-source-index.json';idxG.write_bytes((json.dumps(dict(status='DATA_ONLY_CURRENT1311_AND_EXPLICIT_ALTERNATIVE_REFERENCES',document='N01WorkingUnselected',snapshot=snapG.name,snapshot_sha256=hashlib.sha256(snapG.read_bytes()).hexdigest(),actor_names_to_objects=mapG,effective_actor_names=list(effG),current_actor_count=1311,base_source1292_unchanged=True,all_reference_groups_hidden_onGUIopen=True,pins=snapshotpinsG,operation_seconds=time.monotonic()-tG,process_cpu_seconds=time.process_time()-cG,MAIN_mm=46.52),indent=2)+'\n').encode());print('GUI_SNAPSHOT_SAVED',len(effG),len(mapG),snapG,hashlib.sha256(snapG.read_bytes()).hexdigest(),time.monotonic()-tG,flush=True)

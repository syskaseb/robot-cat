import FreeCAD as A,Part,json,math,time,hashlib
from pathlib import Path
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-audio-module-layer');OLD=P.parent/'day15-shared-module-fit';D=A.getDocument('DAY15_AUDIO_MODULE_LAYER');S=A.getDocument('DAY15_SHARED_MODULE_PROPOSAL');V=A.Vector;T=time.perf_counter();CPU=time.process_time()
def sh(n):return D.getObject(n).Shape
def lower(a,b):return math.sqrt(sum(max(l1-h2,l2-h1,0)**2 for l1,h1,l2,h2 in [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)]))
turn=D.getObject('AL_AMP_FREE_TURN_BAY') or D.addObject('PartDesign::Feature','AL_AMP_FREE_TURN_BAY');turn.Shape=Part.makeBox(13.75,13,39,V(-77,21,95.25));turn.ViewObject.ShapeColor=(.9,.58,.17);turn.ViewObject.Transparency=85;D.getObject('AUDIO_CONNECTED_BAYS_SOURCE_PORT_FIT_OPEN').addObject(turn);D.recompute();D.save()
r=dict(status='CHECKING_ONE_WHOLE_AUDIO_LAYER',checks=[],bounds=[],reused=[],not_received=[])
def write():r.update(wall_seconds=time.perf_counter()-T,cpu_seconds=time.process_time()-CPU);(P/'result.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
def add(row,ok=True,a=None,b=None):
 r['checks'].append(row);write()
 if not ok:
  r['status']='HOLD_FIRST_CHANGED_AUDIO_OR_UNRECEIVED_RELATION';r['first_falsifier']=row;write()
  if a is not None:a.exportBrep(str(P/'hazard-operand-A.brep'))
  if b is not None:b.exportBrep(str(P/'hazard-operand-B.brep'))
  raise RuntimeError(json.dumps(row))
base=json.loads((P.parent/'day14-fasttrack-first-fit/layout.json').read_bytes());phys=[x['object'] for x in base['rows'] if x['evidence'] in ['selected_source','nominal_selected_or_extension_installation_envelope'] and D.getObject(x['object']) and 'bracket_space' not in x['object'] and x['object']!='WAVEGO_complete_126_source_solids']
changed=['MAX98357A_amp','Speaker'];unreceived=json.loads((OLD/'whole-material-gate.json').read_bytes())['not_received']
for n in [o.Name for o in S.Objects if o.Name.startswith('CL_')]+['BUS25514_installed','Pi_components_and_cooling','WAVEGO_complete_126_source_solids','P02_front_deck','P03_rear_deck_integrated_load_yoke','P06_S0_shared_panel']:
 a=sh(n);b=S.getObject(n).Shape;ha=hashlib.sha256(a.exportBrepToString().encode()).hexdigest();hb=hashlib.sha256(b.exportBrepToString().encode()).hexdigest();assert ha==hb,n;r['reused'].append(dict(name=n,isSame=a.isSame(b),BRep_SHA256=ha,byte_identity=True,reason='MCPserializationcopies invalidatepointeridentity, identicalworldBRep remainsstrictidentity'))
r['reused_scopes']='4actualrootjaw/wholehardware/source126bounds +BUS31mm cooling exactlysameactors/relativepose. Existing61module-vs-oldmaterialpairs not replayed; changed adds/cut and11missing checked.';write()
def compare(a,b,own=False,kind='CHANGED_FULL_MODULE',sa=None,sb=None):
 s=sa if sa is not None else sh(a);q=sb if sb is not None else sh(b);lb=lower(s.BoundBox,q.BoundBox)
 if lb>=1.25-1e-6:r['bounds'].append(dict(a=a,b=b,lower_mm=lb));return
 gap=s.distToShape(q)[0];c=s.common(q);add(dict(kind=kind,a=a,b=b,gap_mm=gap,common_mm3=c.Volume,valid=s.isValid() and q.isValid() and c.isValid(),own_function='Explicitplannedmatchedboard/bodyseat only, retentionunqualified' if own else None),s.isValid() and q.isValid() and c.isValid() and c.Volume<1e-5 and (own or gap>=1.25-1e-6),s,q)
# Actualfullchangeddevices against all retainedfullbodies, no replayunchanged61pairs.
for a in changed:
 for b in phys:
  if a==b or (a=='Speaker' and b=='MAX98357A_amp'):continue
  compare(a,b)
 for b in ['CF_COMMON_LOAD_ENVELOPE','CF_REMOVABLE_BUS_BRIDGE','AL_REMOVABLE_MIC_TOUCH_FRAME','BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER','Battery_tray_shared','Neck_shared_root']:
  compare(a,b,own=b=='CF_COMMON_LOAD_ENVELOPE',kind='CHANGED_FULL_AUDIO_VS_SUPPORT_AND_PORT_COVERS')
# Addedcommonmembers andnewcap vsretainedbodies; exactonlynearby simplepieces, notwhole126compound.
members=[(o.Name,o.Shape) for o in D.Objects if o.Name.startswith('AL_added_material_') or o.Name.startswith('AL_cap_member_')]
for a,s in members:
 for b in phys:
  own=(a.startswith('AL_added_material_') and b in ['MAX98357A_amp','Speaker']) or (a.startswith('AL_cap_member_') and b in ['ReSpeakerLite_on_REMOVABLE_back','TTP223_touch'])
  compare(a,b,own=own,kind='NEW_AUDIO_LOAD_MEMBER',sa=s)
# Wholemissing11 nowallaccounted againstcurrentload bodies; sourcecover remainsdistinctfromactualbareboard.
for a in unreceived:
 for b in ['CF_COMMON_LOAD_ENVELOPE','AL_REMOVABLE_MIC_TOUCH_FRAME','CF_REMOVABLE_BUS_BRIDGE']:
  compare(a,b,own=b=='AL_REMOVABLE_MIC_TOUCH_FRAME' and a in ['ReSpeakerLite_on_REMOVABLE_back','TTP223_touch'],kind='PREVIOUS_11_UNRECEIVED_MODULE_DELTA')
r['previous11_received']=unreceived
compare('CF_COMMON_LOAD_ENVELOPE','AL_REMOVABLE_MIC_TOUCH_FRAME',own=True,kind='DISTINCT_REMOVABLE_PRINT_ENVELOPES_DISJOINT')
for a,b in [('RS_USB_FULL_SOURCE_COVER','CF_COMMON_LOAD_ENVELOPE'),('RS_USB_FULL_SOURCE_COVER','CF_REMOVABLE_BUS_BRIDGE'),('RS_USB_FULL_SOURCE_COVER','AL_REMOVABLE_MIC_TOUCH_FRAME'),('BNO_FULL_SOURCE_INSTALLATION_COVER','CF_COMMON_LOAD_ENVELOPE')]:compare(a,b,own=a.startswith('RS_') and b=='AL_REMOVABLE_MIC_TOUCH_FRAME',kind='FULL_PROJECT_INSTALLATION_COVER_NOT_BARE_PCB')
# Freefields arecontinuoussharedoccupied bays withproperdeclaredlocalpacking; ownterminalinterfacefield isnotcalled freevolume.
for a in ['AL_I2S_FREE_TOP_BAY','AL_AMP_TO_SPEAKER_SIDE_BAY','AL_AMP_FREE_TURN_BAY']:
 for b in phys+['CF_COMMON_LOAD_ENVELOPE','AL_REMOVABLE_MIC_TOUCH_FRAME','CF_REMOVABLE_BUS_BRIDGE']:
  compare(a,b,kind='CONNECTED_OCCUPIED_AUDIO_FREE_BAY')
for a,b in [('AL_I2S_FREE_TOP_BAY','AL_AMP_FREE_TURN_BAY'),('AL_AMP_TO_SPEAKER_SIDE_BAY','AL_AMP_FREE_TURN_BAY')]:
 c=sh(a).common(sh(b));add(dict(kind='OCCUPIED_REGION_POSITIVE_CONNECTION',a=a,b=b,common_mm3=c.Volume,valid=c.isValid()),c.isValid() and c.Volume>0)
r['status']='ONE_WHOLE_AUDIO_MATERIAL_AND_SHARED_BAYS_SCOPED_CLEAR_READY_FOR_BOUNDED_RISK_READ';r['actual_source_ports_and_stock']='ActualGPIO/AMPpads/USB_AUDIOmouths andleadlengths unqualifiedFIT2. This provesbody+coarsesupport+connectedFREEbay, notmanufacturerend-to-endharness/wholepower/motion.';r['remaining_essential']=['actualprintparting/completejoints/driveraccess/boardedgekeepers/powerbankretention','separateUSB_AUDIOrequiredlead/matingand4fixed220/FHAC/K1474installedlengthslack','actualinitiallinkedkitlay/batteryremoval beforelateclosure','physicalFIT1/2/3'];write();print(json.dumps({'status':r['status'],'checks':len(r['checks']),'bounds':len(r['bounds']),'previous11':len(unreceived),'wall':r['wall_seconds'],'CPU':r['cpu_seconds']}))

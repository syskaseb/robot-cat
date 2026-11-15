import FreeCAD as A,Part,json,time,itertools
from pathlib import Path
from datetime import datetime,timezone
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-audio-region-proof');D=A.getDocument('DAY15_OCCUPIED_AUDIO_REGION');plan=json.loads((P/'proposal.json').read_bytes());t=time.perf_counter();cpu=time.process_time()
targets=['CF_COMMON_LOAD_ENVELOPE','AL_REMOVABLE_MIC_TOUCH_FRAME','CF_REMOVABLE_BUS_BRIDGE','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi4B_actual_PCB','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','MAX98357A_amp','Speaker','BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER']
result=dict(status='RUNNING_NAMED_TRAY_FEED_ONLY',started_utc=datetime.now(timezone.utc).isoformat(),physical_material_changed=False,source_poses_changed=False,rows=[],packing_rows=[],first_falsifier=None,previous_outer_field_raw='gap0/common0 preserved; emptycorner not occupiedwire',whole_harness_pass=False,actual_cut_slack_length=None)
def save():
 result['wall_seconds']=time.perf_counter()-t;result['cpu_seconds']=time.process_time()-cpu;(P/'local-result.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
def run_local_check():
 save()
 for row in plan['profiles']:
  s=D.getObject('COVER_'+row['name']).Shape
  assert s.isValid() and row['coverage_missing_mm3']<1e-5 and row['min_core_R']>=row['required_core_R']
  for target in targets:
   q=D.getObject(target).Shape;assert q.isValid(),target
   gap=s.distToShape(q)[0];r=dict(profile=row['name'],target=target,operand='full_nominal_plus_0p4_continuous_cover',valid=True,gap_mm=gap,required_mm=1.25,pass_scoped=gap>=1.25-1e-6);result['rows'].append(r)
   if not r['pass_scoped']:
    c=s.common(q);r['common_mm3']=c.Volume;r['common_valid']=c.isValid();result['first_falsifier']=r;result['status']='OCCUPIED_REGION_ALLOCATION_HOLD';save();print(json.dumps(result));return
   save()
 section=Part.read(str(P/'feed-full7-capacity.brep'));q=D.getObject('CF_COMMON_LOAD_ENVELOPE').Shape;gap=section.distToShape(q)[0];result['feed_section']=dict(valid=section.isValid(),gap_mm=gap,required_mm=1.25,actual_count=2,capacity_count=7,pass_scoped=gap>=1.25-1e-6)
 if gap<1.25-1e-6:
  result['first_falsifier']=result['feed_section'];result['status']='FEED_CAPACITY_HOLD';save();print(json.dumps(result));return
 for a,b in itertools.combinations(plan['profiles'],2):
  sa=D.getObject('WIRE_'+a['name']).Shape;sb=D.getObject('WIRE_'+b['name']).Shape;gap=sa.distToShape(sb)[0];r=dict(a=a['name'],b=b['name'],gap_mm=gap,required_mm=.2,pass_scoped=gap>=.2-1e-6);result['packing_rows'].append(r)
  if not r['pass_scoped']:
   result['first_falsifier']=r;result['status']='LOCAL_BRANCH_PACKING_HOLD';save();print(json.dumps(result));return
  save()
 result['status']='LOCAL_OCCUPIED_AUDIO_REGION_CLEAR_SCOPED';result['minimum_foreign_gap_mm']=min(r['gap_mm'] for r in result['rows']);result['minimum_nominal_interprofile_gap_mm']=min(r['gap_mm'] for r in result['packing_rows']);result['minimum_core_radius_mm']=min(r['min_core_R'] for r in plan['profiles']);result['consequence']='Current architecture can retain this local open-feed/upper-branch allocation, conditional on actual AMP/Pi/speaker end frames and leadstock FIT. No new support material justified by old empty reserve corner.';save();print(json.dumps(result))
run_local_check()

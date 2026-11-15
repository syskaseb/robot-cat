import FreeCAD as A,Part,json,time,math
from pathlib import Path
from datetime import datetime,timezone
D=A.getDocument('DAY15_ESSENTIAL_SHARED_FRAME');P=Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-essential-shared-frame');T=time.perf_counter();CPU=time.process_time();r=dict(status='RUNNING_ONLY_CHANGED_INTERFACES',started_utc=datetime.now(timezone.utc).isoformat(),rows=[],lower_bounds=[],own_bearing=[],first_falsifier=None,old_matrices_replayed=False)
def save():
 r['wall_seconds']=time.perf_counter()-T;r['cpu_seconds']=time.process_time()-CPU;(P/'frame-result.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
def lower(a,b):
 a=a.BoundBox;b=b.BoundBox;return math.sqrt(sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in 'XYZ'))
def gate(name,s,target,q,kind='foreign',limit=1.25):
 lb=lower(s,q)
 if lb>=limit+1e-5:r['lower_bounds'].append(dict(a=name,b=target,lower_mm=lb,limit=limit));return True
 assert s.isValid() and q.isValid(),(name,target)
 gap=s.distToShape(q)[0];row=dict(a=name,b=target,kind=kind,gap_mm=gap,required_mm=limit,valid=True,pass_scoped=gap>=limit-1e-6);r['rows'].append(row)
 if not row['pass_scoped']:
  c=s.common(q);row.update(common_mm3=c.Volume,common_valid=c.isValid());r['first_falsifier']=row;r['status']='CHANGED_INTERFACE_HOLD';s.exportBrep(str(P/'frame-falsifier-a.brep'));q.exportBrep(str(P/'frame-falsifier-b.brep'));save();return False
 return True
def run():
 save();steel=D.getObject('ESSENTIAL_NEW_STANDARD_STEEL').Group
 retained=[]
 for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  if o.Name.startswith(('Ola_','MG92B_')) and ('ENVELOPE' in o.Name or 'bracket' in o.Name):continue
  if o.Name in ['Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits','Neck_shared_root','Battery_tray_shared']:continue
  if o.Name=='WAVEGO_complete_126_source_solids':
   for i,s in enumerate(o.Shape.Solids):retained.append(('WAVEGO_source_solid_'+str(i),s))
  else:retained.append((o.Name,o.Shape))
 retained += [(n,D.getObject(n).Shape) for n in ['BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER']]
 for o in steel:
  for n,q in retained:
   if not gate(o.Name,o.Shape,n,q):return
  save()
 # Entire steel sets must lie in modeled own clearances, except intentional nut/bolt engagement.
 parts=D.getObject('ESSENTIAL_REAL_PRINT_PARTS').Group
 for o in steel:
  for p in parts:
   if lower(o.Shape,p.Shape)>0.01:continue
   common=o.Shape.common(p.Shape);assert common.isValid()
   r['own_bearing'].append(dict(steel=o.Name,print=p.Name,penetration_mm3=common.Volume,intentional_surface_area_mm2=common.Area if common.Volume<1e-6 else None))
   if common.Volume>1e-5:
    r['first_falsifier']=dict(a=o.Name,b=p.Name,kind='OWN_PRINT_UNMODELED_PENETRATION',common_mm3=common.Volume);r['status']='OWN_INTERFACE_HOLD';save();return
 # Only added material against current neighbors; unchanged/subset structure reuses scoped proofs.
 old=[D.getObject(n).Shape for n in ['CF_COMMON_LOAD_ENVELOPE','AL_REMOVABLE_MIC_TOUCH_FRAME','CF_REMOVABLE_BUS_BRIDGE']]
 for p in parts:
  if p.Name.startswith(('P16','P17')):continue
  added=p.Shape
  for q in old:added=added.cut(q)
  if added.Volume<1e-6:continue
  added.exportBrep(str(P/(p.Name+'-added-only.brep')))
  for n,q in retained:
   if not gate(p.Name+'_added',added,n,q):return
  for o in D.getObject('OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN').Group:
   if not gate(p.Name+'_added',added,o.Name,o.Shape,'allocated_audio_margin'):return
  save()
 r['status']='CHANGED_STEEL_MATERIAL_AND_AUDIO_DELTA_CLEAR_SCOPED';r['retained_target_count']=len(retained);r['new_steel_pieces']=len(steel);r['physical_pass']=False;save()
run();print(json.dumps({'status':r['status'],'exact_rows':len(r['rows']),'bounds':len(r['lower_bounds']),'own_rows':len(r['own_bearing']),'first_falsifier':r['first_falsifier'],'seconds':r['wall_seconds']}))

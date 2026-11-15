import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.getDocument('DAY15_POWER_CAPACITY');P=Path(D.FileName).parent;OLD=P.parent/'day15-frame-fastening';T=time.perf_counter();r=dict(status='RUNNING_ONLY_UNRECEIVED',power_bounds=0,power_checks=[],added_bounds=0,added_checks=[],reused_old_positive_pairs=0,first_falsifier=None)
oldres=json.loads((OLD/'delta-result.json').read_bytes());reuse={(x['a'],x['b'],x['kind']) for x in oldres['bounds']};reuse.update((x['a'],x['b'],x['kind']) for x in oldres['material_checks'] if x['gap']>=1.25)
def save():
 r['seconds']=time.perf_counter()-T;(P/'missing-result.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def lower(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
def gate(n,s,m,q,kind):
 lb=lower(s,q)
 if lb>=1.25001:r[kind+'_bounds']+=1;return True
 gap=s.distToShape(q)[0];row=dict(a=n,b=m,gap=gap,limit=1.25);r[kind+'_checks'].append(row)
 if gap<1.25-1e-6:
  c=s.common(q);row.update(common_mm3=c.Volume,valid=c.isValid());r['first_falsifier']=row;r['status']='ONE_NEW_ALLOCATION_OR_MATERIAL_HOLD';s.exportBrep(str(P/'missing-witness-a.brep'));q.exportBrep(str(P/'missing-witness-b.brep'));save();return False
 return True
targets=[];skip={'XT60H_mated_with_boots','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'}
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name in skip or o.Name.startswith('Ola_'):continue
 if o.Name=='WAVEGO_complete_126_source_solids':targets.extend(('WAVEGOsolid'+str(i),s) for i,s in enumerate(o.Shape.Solids))
 else:targets.append((o.Name,o.Shape))
rigid=targets+[(o.Name,o.Shape) for o in D.getObject('FASTENING_REAL_PRINT_PARTS').Group]+[(o.Name,o.Shape) for o in D.getObject('OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN').Group]
jointplan=json.loads((OLD/'whole-fastening-plan.json').read_bytes());metalnames=[n for j in jointplan['joints'] for n in j['objects']]
rigid.extend((n,D.getObject(n).Shape) for n in metalnames)
rigid.extend((n,D.getObject(n).Shape) for n in ['BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER'])
def run():
 # FullXT60/first localprofile alreadyreceived. Only unchanged upperarc was not checked by first oldfield gate.
 fields=[D.getObject('P12_UNCHANGED_R24_UPPER_ARC_REGION')]+[o for o in D.getObject('CONNECTED_POWER_CAPACITY_NOT_RIGID_WIRES').Group if o.Name!='POWER_BAT2_VERTICAL_AND_NORTH_TURN']
 for o in fields:
  for n,q in rigid:
   if not gate(o.Name,o.Shape,n,q,'power'):return
  save()
 r['power_complete']=True;save()
 # Old addedmaterial positive keys remain valid: source/prints unchanged. Recompute only missing keys.
 targets2=[(n,q) for n,q in targets if n not in ['Neck_shared_root','Battery_tray_shared'] and 'bracket_space' not in n]
 targets2.extend((n,D.getObject(n).Shape) for n in ['BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER'])
 old=[D.getObject(n).Shape for n in ['CF_COMMON_LOAD_ENVELOPE','AL_REMOVABLE_MIC_TOUCH_FRAME','CF_REMOVABLE_BUS_BRIDGE']]
 for p in D.getObject('FASTENING_REAL_PRINT_PARTS').Group:
  if p.Name.startswith(('P16','P17','P18')):continue
  if (OLD/(p.Name+'-added.brep')).exists():s=Part.Shape();s.read(str(OLD/(p.Name+'-added.brep')))
  else:
   s=p.Shape
   for q in old:s=s.cut(q)
  if s.Volume<1e-5:continue
  for k,s1 in enumerate(s.Solids):
   n=p.Name+'_added'+str(k)
   for m,q in targets2:
    key=(n,m,'added_material_foreign')
    if key in reuse:r['reused_old_positive_pairs']+=1;continue
    if not gate(n,s1,m,q,'added'):return
   for o in D.getObject('OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN').Group:
    if (n,o.Name,'added_material_vs_accepted_audio') in reuse:r['reused_old_positive_pairs']+=1;continue
    if not gate(n,s1,o.Name,o.Shape,'added'):return
  save()
 r['status']='RECEIVED_POWER_AND_MISSING_ADDED_MATERIAL_AUDIO_CLEAR_SCOPED';save()
run();print(json.dumps(r))

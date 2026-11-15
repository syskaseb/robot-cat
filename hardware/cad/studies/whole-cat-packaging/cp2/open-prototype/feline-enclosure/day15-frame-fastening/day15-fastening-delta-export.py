import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,time,math,shutil,hashlib
from pathlib import Path
from datetime import datetime,timezone
D=A.getDocument('DAY15_FRAME_FASTENING');P=Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-frame-fastening');OLD=P.parent/'day15-essential-shared-frame';T=time.perf_counter();CPU=time.process_time();material=json.loads((P/'material-result.json').read_bytes());plan=json.loads((P/'whole-fastening-plan.json').read_bytes());r=dict(status='MISSING_DELTA_RUNNING',tool_checks=[],material_checks=[],bounds=[],first_falsifier=None)
def save():r.update(wall_seconds=time.perf_counter()-T,cpu_seconds=time.process_time()-CPU);(P/'delta-result.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def lower(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in 'XYZ'))
def gate(n,s,m,q,limit,kind):
 lb=lower(s,q)
 if lb>limit+1e-5:r['bounds'].append(dict(a=n,b=m,lower=lb,kind=kind));return True
 gap=s.distToShape(q)[0];c=s.common(q);row=dict(a=n,b=m,gap=gap,common_mm3=c.Volume,valid=c.isValid(),limit=limit,kind=kind);r['tool_checks' if kind.startswith('tool') else 'material_checks'].append(row)
 ok=c.isValid() and (c.Volume<1e-5 if limit==0 else gap>=limit-1e-6)
 if not ok:r['first_falsifier']=row;r['status']='NEW_DELTA_HOLD';s.exportBrep(str(P/'delta-falsifier-a.brep'));q.exportBrep(str(P/'delta-falsifier-b.brep'));save();return False
 return True
parts=D.getObject('FASTENING_REAL_PRINT_PARTS').Group
def run():
 if material['first_falsifier']:r['status']='MATERIAL_HOLD_INHERITED';r['first_falsifier']=material['first_falsifier'];save();return
 save()
 for j in plan['joints']:
  s=D.getObject('KEY_'+j['tag']).Shape
  for p in parts:
   if not gate('KEY_'+j['tag'],s,p.Name,p.Shape,0,'tool_bare_frame_before_PCB_bank_battery'):return
  if not gate('KEY_'+j['tag'],s,j['objects'][0],D.getObject(j['objects'][0]).Shape,0,'tool_matched_hexsocket'):return
  save()
 targets=[]
 for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  if o.Name.startswith('Ola_') or 'bracket_space' in o.Name or o.Name in ['Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits','Neck_shared_root','Battery_tray_shared']:continue
  if o.Name=='WAVEGO_complete_126_source_solids':targets.extend([('WAVEGOsolid'+str(i),s) for i,s in enumerate(o.Shape.Solids)])
  else:targets.append((o.Name,o.Shape))
 targets.extend([(n,D.getObject(n).Shape) for n in ['BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER']]);old=[D.getObject(n).Shape for n in ['CF_COMMON_LOAD_ENVELOPE','AL_REMOVABLE_MIC_TOUCH_FRAME','CF_REMOVABLE_BUS_BRIDGE']]
 for p in parts:
  if p.Name.startswith(('P16','P17','P18')):continue
  s=p.Shape
  for q in old:s=s.cut(q)
  if s.Volume<1e-5:continue
  s.exportBrep(str(P/(p.Name+'-added.brep')))
  for k,s1 in enumerate(s.Solids):
   for n,q in targets:
    if not gate(p.Name+'_added'+str(k),s1,n,q,1.25,'added_material_foreign'):return
   for o in D.getObject('OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN').Group:
    if not gate(p.Name+'_added'+str(k),s1,o.Name,o.Shape,1.25,'added_material_vs_accepted_audio'):return
  save()
 r['status']='CHANGED_MATERIAL_TOOLS_AND_AUDIO_DELTA_CLEAR_SCOPED';save()
run()
# Export usable source-frozen material even on HOLD; release remains explicitly conditional.
for row in material['parts']:
 n=row['name'];s=D.getObject(n).Shape;local=s.copy()
 if n in ['P10_front_gate','P11_rear_gate']:local.rotate(A.Vector(),A.Vector(0,1,0),90)
 elif n=='P13_BUS_bridge':local.rotate(A.Vector(),A.Vector(1,0,0),180)
 b=local.BoundBox;local.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin));b=local.BoundBox;row['print_size_mm']=[b.XLength,b.YLength,b.ZLength];assert max(row['print_size_mm'])<256
 if n.startswith(('P16','P17','P18')):shutil.copyfile(OLD/(n+'.stl'),P/(n+'.stl'));row['unchanged_source_STL_sha256']=hashlib.sha256((P/(n+'.stl')).read_bytes()).hexdigest()
 else:MeshPart.meshFromShape(Shape=local,LinearDeflection=.15,AngularDeflection=.2,Relative=False).write(str(P/(n+'.stl')))
material['print_release']='CONDITIONAL_UNPOWERED_STRUCTURAL_FIT_ONLY' if r['status']=='CHANGED_MATERIAL_TOOLS_AND_AUDIO_DELTA_CLEAR_SCOPED' else 'HOLD_NO_PRINT_RELEASE';(P/'material-result.json').write_bytes((json.dumps(material,ensure_ascii=False,indent=2)+'\n').encode());D.recompute();D.save();print(json.dumps({'status':r['status'],'first_falsifier':r['first_falsifier'],'tool_checks':len(r['tool_checks']),'newmat_checks':len(r['material_checks']),'bounds':len(r['bounds']),'STL':9,'seconds':r['wall_seconds']}))

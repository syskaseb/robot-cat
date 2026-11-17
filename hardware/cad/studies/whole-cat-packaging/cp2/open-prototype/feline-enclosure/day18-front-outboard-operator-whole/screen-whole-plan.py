from pathlib import Path
import json,math,itertools,datetime
P=Path(__file__).parent;src=json.loads((P/'source-current-metadata.json').read_text());C={o['name']:dict(o) for o in src};spec=json.loads((P/'whole-transform-spec.json').read_text())
def rot(p,axis,deg):
 x,y,z=p;c=math.cos(math.radians(deg));s=math.sin(math.radians(deg));return [x,c*y-s*z,s*y+c*z] if axis=='X' else [c*x+s*z,y,-s*x+c*z] if axis=='Y' else [c*x-s*y,s*x+c*y,z]
def tp(p,s):
 v=[p[k]-s['old'][k] for k in range(3)]
 if s['pre']:v=rot(v,*s['pre'])
 v=rot(v,s['axis'],s['angle']);return [v[k]+s['new'][k] for k in range(3)]
for s in spec:
 for n in s['names']:
  if n not in C:continue
  b=C[n]['bounds'];v=[tp(x,s) for x in itertools.product(*[(b[k],b[k+3]) for k in range(3)])];C[n]['bounds']=[min(x[k] for x in v) for k in range(3)]+[max(x[k] for x in v) for k in range(3)]
(P/'numeric-allocated-bounds.json').write_bytes((json.dumps(C,indent=2)+'\n').encode('utf-8'))
major=['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','CF17_POL1992_FULL_MATED_BODY','CF17_POL1992_FACTORY_END_REGION','CF17_POWER_DELOCK60047_APPROX_FULL','CF17_POWER_K1474_SEALED_BOOT_FULL','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed','MAIN_Pololu4853','AUX_FULL9p5_POPULATED_SCOPE','Speaker','BNO085','MAX98357A_amp','ReSpeakerLite_on_REMOVABLE_back','TTP223_touch','Battery_GEA223S30X6GT','F0_FHAC0002_30A','XT60H_mated_with_boots','OP_S1_PRIMARY_CASE_CONSERVATIVE']+[n for n in C if n.startswith(('S0_','PBAY_','Motor_ATO4A_','NIGHT_INLINE_')) or (n.startswith('WAGO415_data') and C[n]['visible']) or n.startswith('WAGO615_power_0_')]
cands=[]
for i,n in enumerate(major):
 for m in major[i+1:]:
  if n.startswith('S0_') and m.startswith('S0_'):continue
  b=C[n]['bounds'];c=C[m]['bounds'];ov=[min(b[k+3],c[k+3])-max(b[k],c[k]) for k in range(3)]
  if min(ov)>1e-6:cands.append(dict(a=n,b=m,bbox_overlap=ov,status='CANDIDATE_ONLY'))
(P/'finite-before-material-cull.json').write_bytes((json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),module_fields=len(major),candidates=cands),indent=2)+'\n').encode('utf-8'))
print(json.dumps(cands));print(datetime.datetime.now(datetime.timezone.utc).isoformat())

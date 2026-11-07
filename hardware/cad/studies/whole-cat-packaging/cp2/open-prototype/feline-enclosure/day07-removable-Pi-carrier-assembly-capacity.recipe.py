import time,json,hashlib,os
t50=time.monotonic();c50=time.process_time();own50=[]
for name,s in new49.items():
 if ':band_budget' not in name:continue
 for target,q in [('receiver',receiver49),('moving_foot',foot49),('unchanged_column_below',clip49)]:
  gap=s.distToShape(q)[0];co=s.common(q);own50.append(dict(stock=name,target=target,gap_mm=gap,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,ok=co.isValid() and co.Volume<1e-7,classification='Actual structural pressure strap on its own mount; no material intrusion, not a general foreignwaiver'))
guide50=[dict(guide=i,bar_gap_mm=bar49.distToShape(q)[0],foot_gap_mm=foot49.distToShape(q)[0]) for i,q in enumerate(guides49)]
capacity50=[]
for region in ['Flat:MODULE:5','V:common_region']:
 q=Current35[region]
 for n,s in new49.items():
  lb=bbox_lower_bound(s.BoundBox,q.BoundBox);rr=dict(new=n,region=region,bbox_separation_lower_mm=lb)
  if lb>=1.25-1e-7:rr['status']='NO_ADDED_OCCUPANCY_BY_COMPLETE_POSITIVE_BOUND'
  else:
   g=s.distToShape(q)[0];rr.update(gap_mm=g,status='NO_ADDED_OCCUPANCY_BY_ACTUAL_SEPARATION' if g>=1.25-1e-7 else 'CHANGED_ALLOCATED_CAPACITY_HOLD_NOT_WIRECONTACT')
  capacity50.append(rr)
foot_entry50=[]
for k,q in fixed47.items():
 if k=='C1:west_bank_gap_column':continue
 b=foot49.BoundBox;cover=box49([b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax+35]);lb=bbox_lower_bound(cover.BoundBox,q.BoundBox)
 if lb>1.25:continue
 g=foot49.distToShape(q)[0];H=min(35,max(0,q.BoundBox.ZMax-foot49.BoundBox.ZMin));l=g-H
 foot_entry50.append(dict(other=k,current_gap_mm=g,possible_height_reduction_mm=H,continuous_lower_mm=l,status='CONTINUOUS_EXTRA_FOOT_CLEAR125' if l>=1.25-1e-7 else 'FOOT_ENTRY_OPEN_NOT_CONTACT'))
r50=dict(id='day07-removable-Pi-carrier-joint-assembly-capacity-delta',status='JOINT_ASSEMBLY_RECEIVED_SCOPED' if all(r['ok'] for r in own50) and all(r['bar_gap_mm']>=.2-1e-7 and r['foot_gap_mm']>=.2-1e-7 for r in guide50) and all(r['status']=='CONTINUOUS_EXTRA_FOOT_CLEAR125' for r in foot_entry50) else 'JOINT_ASSEMBLY_FUNCTION_HOLD',own_structural_strap_material=own50,guide_and_unchanged_return_access=guide50,extra_foot_vertical_entry=foot_entry50,capacity_delta=capacity50,
 source_retention='PAS:band/head is one additional sourceT18I power2 unit from actual constructor, beyond four Pi36sourceunits; retain full source kit. Structural joint adds TWO independent100units. No source tie declared releasable, no physicalcut/trim, no stockavailabilitycredit.',
 current_scope='Phi/PAS/4M2 kit seat is locally mountable without moving S0/JPWM/U1/solderedMODULE/SOURCE. Initial fourPi mating units and all loose stock remain accounted but their existing access/globalinvalid3/regioncapacity gates stayOPEN; do not claim wholeassembly. Rare repair is the stated reverse with source mating release and disturbed ties renewed, not fullN08 trajectory.',
 unchanged_holds=['Original FlatMODULE5gap1.025706 and Vallocatedcommon80.64 are not repaired by this mounting interface; sourcecolumn below104.1 unchanged. No old2 pair replay.','R6 withdraw/parking and3invalidUSBsourcecovers OPEN unchanged; no invalid geometry treated as contact','S0 currentselected retention/actualfixing interface remains globalOPEN, not assumed supported by rail9.389353749 away'],
 source_pins=[dict(path=n,sha256=hashlib.sha256((OUT/n).read_bytes()).hexdigest()) for n in ['day07-removable-Pi-carrier-top-entry-first-gate.json','day07-removable-Pi-carrier-bearing-functional-correction1-gate.json','day07-S0-current-retention-interface-gate.json']],operation_seconds=time.monotonic()-t50,process_cpu_seconds=time.process_time()-c50,pid=os.getpid(),session_id=46493,selected=False,N01_complete=False)
p50=OUT/'day07-removable-Pi-carrier-joint-assembly-capacity-delta.json';assert not p50.exists();p50.write_bytes((json.dumps(r50,ensure_ascii=False,indent=2)+'\n').encode());print('JOINT50_ASSEMBLY_CAPACITY',r50['status'],own50,guide50,foot_entry50,sorted(set(r['status'] for r in capacity50)),r50['operation_seconds'],r50['process_cpu_seconds'],hashlib.sha256(p50.read_bytes()).hexdigest(),flush=True)

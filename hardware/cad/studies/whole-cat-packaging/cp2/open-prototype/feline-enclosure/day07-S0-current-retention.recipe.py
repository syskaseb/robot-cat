import time,json,hashlib,zipfile,os
t45=time.monotonic();c45=time.process_time();case45=Current35['Ref_Material_S0_body_CP2_0_0'];rail45=Current35['CurrentFoundation:FoundationRail:-1']
candidates45=[n for n,s in Current35.items() if not n.startswith('Ref_Material_S0') and bbox_lower_bound(case45.BoundBox,s.BoundBox)<=3.25]
va45,vb45=case45.isValid(),rail45.isValid();g45,w45,_=case45.distToShape(rail45);co45=case45.common(rail45) if g45<1e-7 else None
ar45=OUT/'day07-S0-current-retention-inputs.breps.zip';assert not ar45.exists();ge45=[]
with zipfile.ZipFile(ar45,'w',zipfile.ZIP_DEFLATED) as z:
 for i,n in enumerate(['Ref_Material_S0_body_CP2_0_0',*candidates45]):
  s=Current35[n];raw=s.exportBrepToString().encode('utf-8');e=str(i)+'.brep';z.writestr(e,raw);ge45.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),source=Sources35.get(n)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge45,scope='One current S0 support-interface read, no body motion or old pair replay'),indent=2)+'\n').encode('utf-8'))
r45=dict(id='day07-S0-current-retention-interface-gate',status='CURRENT_SELECTED_S0_LATE_ASSEMBLY_NOT_ESTABLISHED',N01_complete=False,selected=False,
 current_case_valid=va45,current_rail_valid=vb45,actual_case_rail_gap_mm=g45,actual_common_valid=co45.isValid() if co45 is not None else None,actual_common_mm3=co45.Volume if co45 is not None and co45.isValid() else 0 if co45 is None else None,witnesses=[[list(a),list(b)] for a,b in w45[:1]],
 full_current_neighbor_bounds_selection=dict(total_current=1292,criterion='all non-S0 actor bounds within3.25 of entire current selected S0 family case',candidates=candidates45),
 current_S0_actor_count=len([n for n in Current35 if n.startswith('Ref_Material_S0')]),current_explicit_S0_M6_mount_actors=[n for n in Current35 if 'S0' in n and any(x in n for x in ['M6','Mount','mount'])],
 source_function='Selected historical retention uses twoM6 case fixings plus separate M10 ring/stud hardware. Current11 S0 actors are body/neck/key and8terminal/stud/washer/nut actors; terminal nuts are NOT case fixings. Old Foundation panel source twoM6 axes[-96,-58],Y16,Z105 and native Deck/M2 allocation do not prove mounting of this rotated/relocated currentcase.',
 decision='Cannot qualify S0-after-Pi by excluding S0 from fixed. Current usable case-fixing/panel axis and driver dependency are not established by the available current source pin. This is missing mounting evidence, not proof of a mechanically impossible late mount, nor permission to erase selected S0 or its family reserve.',
 causal_alternative='Keep S0 and full U1/MODULE/SOURCE dock installed. Make the upper Pi/own-rail carrier a vertically removable bearing-and-two-tie interface at the existing west-column top; maintain the already proved lower root and all unchanged installed cable endpoints. Prove first top-entry fullcarrier space before support details. No thirdscalarpark/PCBpose.',
 archive=ar45.name,archive_sha256=hashlib.sha256(ar45.read_bytes()).hexdigest(),geometry=ge45,operation_seconds=time.monotonic()-t45,process_cpu_seconds=time.process_time()-c45,pid=os.getpid(),session_id=46493)
p45=OUT/'day07-S0-current-retention-interface-gate.json';assert not p45.exists();p45.write_bytes((json.dumps(r45,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));print('S0_MOUNT45',g45,r45['actual_common_mm3'],candidates45,r45['operation_seconds'],r45['process_cpu_seconds'],hashlib.sha256(p45.read_bytes()).hexdigest(),flush=True)

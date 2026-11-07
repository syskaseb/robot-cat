import json,time,hashlib,os
t207=time.monotonic();c207=time.process_time()
baseline207=band206.common(kit199['Neck']);headgap207=head206.distToShape(kit199['Neck'])[0];combcontained207=comb206.cut(Current35['Station:FR_G:shared_near_root'])
parts207={'ACTUAL_R4_BANK_PAD':pad206,'PROPOSED_FULL_R3_TAIL_CAPACITY':turn206,'ACTUAL_RETAINED_FRG_LOOP_HEAD':current206,'PROPOSED_CASEBACK_NECK':kit199['Neck'],'ACTUAL_FRG_ROOT':Current35['Station:FR_G:shared_near_root'],'ACTUAL_PAUX_ROOT':Current35['Station:P_AUX:shared_near_root'],'ACTUAL_SHARED_BASE':Current35['SharedRetention:lower_common_flange_base'],**{'FOUR_CURRENT_SOURCE_NINE_'+n:s for n,s in profiles206}}
sections207=[]
for view,vs in [('XZ_FRG_STOCK_PLANE',[A.Vector(24,-53.75,36),A.Vector(96,-53.75,36),A.Vector(96,-53.75,58),A.Vector(24,-53.75,58)]),('XY_CURRENT_STOCK_NECK_BASELINE',[A.Vector(24,-61,40.515),A.Vector(60,-61,40.515),A.Vector(60,-46,40.515),A.Vector(24,-46,40.515)])]:
    plane=Part.Face(Part.makePolygon(vs+[vs[0]]))
    for n,s in parts207.items():
        sec=s.section(plane);curves=[]
        for e in sec.Edges:
            pts=e.discretize(Deflection=.04);curves.append([[q.x,q.z] if view.startswith('XZ') else [q.x,q.y] for q in pts])
        sections207.append(dict(view=view,actor=n,edges=len(sec.Edges),curves=curves))
p207=OUT/'day07-caseback-FRG-actual-loop-function-and-stock-sections.json';assert not p207.exists()
r207=dict(id=p207.stem,status='ACTUAL_ONE_FRG_ROLE_SOURCE_BASELINE_RETAINED_NEW_WHOLESTOCK_HOLD',source_loop_newNeck_baseline=dict(common_valid=baseline207.isValid(),allocated_nylon_material_common_mm3=baseline207.Volume if baseline207.isValid() else None,head_to_newNeck_gap_mm=headgap207,meaning='NewNeck remains incompatible with ACTUALreplacementbottomribbon until purposefulmodeledfeedchannel. Old.2aliasnegative noterased, currentrealstocknotacceptedbyaliasretirement. No physicaldeliverednyloncontactclaim.'),all4_current_comb_inside_current_root=dict(missing_valid=combcontained207.isValid(),missing_mm3=combcontained207.Volume if combcontained207.isValid() else None,not_two_physical_combs=True),sections=sections207,first_whole_stock_falsifier=first206,no_channel_print_geometry_built=True,no_new_stock_route_afterfirst_falsifier=True,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t207,process_cpu_seconds=time.process_time()-c207,pid=os.getpid(),session_id=46493);p207.write_bytes((json.dumps(r207,indent=2)+'\n').encode());print('FRG_ONE_ROLE_BASELINE',r207['source_loop_newNeck_baseline'],'comb',r207['all4_current_comb_inside_current_root'],'edges',sum(q['edges'] for q in sections207),'wall',r207['operation_seconds'],'CPU',r207['process_cpu_seconds'],hashlib.sha256(p207.read_bytes()).hexdigest(),flush=True)

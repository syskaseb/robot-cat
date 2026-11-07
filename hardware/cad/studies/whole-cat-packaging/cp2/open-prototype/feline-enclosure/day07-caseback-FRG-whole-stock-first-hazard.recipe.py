import json,time,hashlib,os,zipfile,math
t206=time.monotonic();c206=time.process_time();pp206=OUT/'day07-caseback-FRG-whole-feed-pressure-and-stock-interface-proposal.json';prop206=json.loads(pp206.read_bytes())
oldband206=Current35['Station:FR_G:band_budget'];oldhead206=Current35['Station:FR_G:head_budget'];current206=Current35['Station:FR_G:shared_near_tie'];band206=oldband206.copy();band206.translate(A.Vector(0,-2,0));head206=oldhead206.copy();head206.translate(A.Vector(0,-2,0));sourceunit206=band206.fuse(head206)
lost206=sourceunit206.cut(current206);extra206=current206.cut(sourceunit206)
alias206=dict(source_original_band='Station:FR_G:band_budget',source_original_head='Station:FR_G:head_budget',actual_retained_replacement='Station:FR_G:shared_near_tie',source_rigid_translation_mm=[0,-2,0],actual_original_transformed_missing_valid=lost206.isValid(),actual_original_transformed_missing_mm3=lost206.Volume,actual_replacement_extra_valid=extra206.isValid(),actual_replacement_extra_mm3=extra206.Volume,source_explicit_retired_names=True,source_qty_added=0,classification='SameONEphysicalclosurefunction proof bysourceclone/retirement+actualmaterialbothways; NOTdeletebyname/bbox. Oldband.2rawnegativepreservedsourcewitness, notsecondindependentstockunit.')
aliasok206=lost206.isValid() and extra206.isValid() and lost206.Volume<1e-7 and extra206.Volume<1e-7
loop206=band206.Volume/(2.5*1.2);remainder206=145-loop206;free206=remainder206-5.3
ports206=[];profiles206=[]
comb206=Current35['Station:FR_G:split_common_comb'];holes206=sorted(set(round(f.Surface.Center.x,8) for f in comb206.Faces if type(f.Surface).__name__=='Cylinder'))
for q in prop206['all4_ports']:
    x,y,z=q['actual_project_port_mm'];s=Part.makeCylinder(q['project_radius_mm'],9,A.Vector(x,-56.25,z),A.Vector(0,1,0));profiles206.append((q['wire'],s));ports206.append(dict(**q,actual_native_channel_axis_confirmed=round(x,8) in holes206,reference_full9_valid=s.isValid(),not_new_route_or_length_credit=True))
assert len(holes206)==4 and all(q['actual_native_channel_axis_confirmed'] for q in ports206)
first206=None
if not aliasok206:first206=dict(stage='SOURCE_CURRENT_SINGLE_CLOSURE_ALIAS_NOT_QUALIFIED',row=alias206)
# Named ONLYlocaltailhazard: currenthead+Z nominalexit -> R3rise nearR4padcorner.
# Exactquarterannularprism is a FULLallocated3.3x2 capacity, NOTactualnyloncurve.
CX206=27.475;CZ206=47.91;yy206=-55.4
at206=lambda r,t:A.Vector(CX206+r*math.cos(t),yy206,CZ206+r*math.sin(t))
outer206=Part.Arc(at206(4,0),at206(4,math.pi/4),at206(4,math.pi/2)).toShape();inner206=Part.Arc(at206(2,math.pi/2),at206(2,math.pi/4),at206(2,0)).toShape()
wire206=Part.Wire([outer206,Part.makeLine(at206(4,math.pi/2),at206(2,math.pi/2)),inner206,Part.makeLine(at206(2,0),at206(4,0))]);turn206=Part.Face(wire206).extrude(A.Vector(0,3.3,0));assert turn206.isValid() and len(turn206.Solids)==1
expected206=3.3*math.pi/4*(16-4);assert abs(turn206.Volume-expected206)<1e-6
padname206='CurrentFoundation:BankPad:Ref_Material_F_R4_CP2_Housing_0_0:0';pad206=Current35[padname206]
ga206,ww206,_=turn206.distToShape(pad206);analytic206=math.hypot(29.5-CX206,52-CZ206)-4
row206=dict(field='FULL_ALLOCATED_FRG_TAIL_HEAD_RISE_R3_PROFILE3p3x2',current_actor=padname206,actual_gap_mm=ga206,analytic_current_corner_lower_mm=analytic206,required_foreign_mm=1.25,witnesses=[[list(x),list(y)] for x,y in ww206[:1]],actual_current_pad_valid=pad206.isValid(),status='ALLOCATED_STOCK_REGION_MARGIN_HOLD_NOT_PHYSICAL_CONTACT' if ga206<1.25-1e-7 else 'LOCAL_STOCK_CAPACITY_SEPARATED125')
if ga206<1e-7:
    co=turn206.common(pad206);row206.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
if first206 is None and ga206<1.25-1e-7:first206=dict(stage='WHOLE_STOCK_FIRST_NAMED_LOCAL_HEAD_RISE_HAZARD',row=row206)
ar206=OUT/'day07-caseback-FRG-full-unit-source-and-first-stock-gate.breps.zip';assert not ar206.exists();ge206=[]
objs206={'SOURCE_ORIGINAL_BAND_WITNESS':oldband206,'SOURCE_ORIGINAL_HEAD_WITNESS':oldhead206,'ACTUAL_RETAINED_ONE_SHARED_TIE':current206,'ACTUAL_CURRENT_COMB':comb206,'ACTUAL_CURRENT_FRG_CASE':Current35['Station:FR_G:case'],'PROPOSED_FULL_TAIL_R3_HEAD_RISE_CAPACITY':turn206,'ACTUAL_CURRENT_R4_BANK_PAD':pad206,**{'SOURCE_REFERENCE_NINE_'+n:s for n,s in profiles206}}
with zipfile.ZipFile(ar206,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(objs206.items()):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge206.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge206,currentworld_no_XML=True),indent=2))
p206=OUT/'day07-caseback-FRG-full-unit-source-and-first-stock-gate.json';assert not p206.exists()
r206=dict(id=p206.stem,status='ONE_SHARED_LOAD_RETENTION_WHOLE_STOCK_FIRST_HAZARD_HOLD_NO_CHANNEL_BUILT' if first206 else 'WHOLE_STOCK_FIRST_LOCAL_CAPACITY_SCOPED_RECEIVED_OTHERFIELDS_OPEN',proposal=pp206.name,proposal_sha256=hashlib.sha256(pp206.read_bytes()).hexdigest(),actual_single_stock_alias_relation=alias206,same_one_unit_alias_retirement_qualified=aliasok206,all4_actual_case_channel_port_binding=ports206,whole_selected_145_stock=dict(sku='111-02370 T18I145',quantity_one_existing_role_no_addition=True,inventory=None,loop_from_actual_V_div_WT_mm=loop206,full_uncut_remainder_including_head_mm=remainder206,head_transit_once_mm=5.3,remaining_free_uncut_capacity_mm=free206,pull25_within_remaining=True,length_check_sum_mm=loop206+5.3+free206,physicalcut=None),first_local_capacity_quality=dict(valid=turn206.isValid(),solids=len(turn206.Solids),volume_mm3=turn206.Volume,analytic_volume_mm3=expected206,analytic_full_bounds_mm=[[27.475,-55.4,47.91],[31.475,-52.1,51.91]],actual_bounds_mm=saved_bounds(turn206),centreline_R_mm=3,full_profile_mm=[3.3,2],not_torus_default_BBox=True),local_named_hazard=row206,first_falsifier=first206,new_hazard_cursor=1,new_unreceived=['Restofconnected83.3head-feed-and-free-tailbay','Completefunctionalbottomstockfeed/root/casepressure/antirotation','CasebackD5/FRGcommonroot fullstock/currentneighbors/assembly/motionoutline'],no_new_channel_or_FRG_halves_built=True,no_newhead_tail_case_wire_pose_after_falsifier=True,oldcaseback_D_C1_M3_145_sourceunchanged=True,selected=False,N01_complete=False,actualcut=None,archive=ar206.name,archive_sha256=hashlib.sha256(ar206.read_bytes()).hexdigest(),geometry=ge206,operation_seconds=time.monotonic()-t206,process_cpu_seconds=time.process_time()-c206,pid=os.getpid(),session_id=46493)
p206.write_bytes((json.dumps(r206,indent=2)+'\n').encode());print('FRG_WHOLE_UNIT_FIRST',r206['status'],'alias',alias206,'loop',loop206,'uncut',remainder206,'free',free206,'4ports',len(ports206),'first',first206,'wall',r206['operation_seconds'],'CPU',r206['process_cpu_seconds'],hashlib.sha256(p206.read_bytes()).hexdigest(),flush=True)

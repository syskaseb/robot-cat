import json,time,hashlib,os,math
t177=time.monotonic();c177=time.process_time()
recipes177=CurrentCanon31['current_foreign_complete_receiver_prefix_gate']['recipes'];stock177=CurrentCanon31['current_foreign_complete_receiver_stock_gate']['stock']['DFL'];d177={}
for tag,wire in [('DFL1','W002'),('DFL5','W007')]:
    spec=recipes177[tag];P=np.array(spec['actual_port']);axis=np.array(spec['axis']);theta=9/spec['R_mm'];end=P+.25*axis+np.array([spec['R_mm']*math.sin(theta),0,spec['R_mm']*(1-math.cos(theta))]);tan=[math.cos(theta),0,math.sin(theta)]
    d177[tag]=dict(wire=wire,source_recipe=spec,current_world_project_port_mm=P.tolist(),start_axis=axis.tolist(),held_full9_plus_preline_mm=9.25,held9_end_mm=end.tolist(),held9_tangent=tan,free_after_held_mm=spec['prefix_length_mm']-9.25,source_binding='Exactcurrentcap09 normalizedidentity 004e69/e67 source is alreadyreceived; constructor literalDFL1/5+currentcanonrecipes frompinnedgate. No oldD2..4 checks or caprebuild/worldtransform repeated.',supplier_mouth_or_exit_guaranteed=False)
ctx177=dict(context160);retired177=[]
for n in ['Underdeck:PositiveFoundation','FLG:print','CurrentFLG:split_common_comb','CurrentFLG:band_budget','CurrentFLG:head_budget']:
    if n in ctx177:del ctx177[n];retired177.append(n)
ctx177.update({'G4C1:PrimaryU1CasecupAndPressure':primary170,'G4C1:RemovableUpper':up170,'G4C1:PressureBand':pb170,'G4C1:PressureHead':head170});ctx177.update({'G4C1capacity:'+n:s for n,s in tail171})
# This context is PROPOSED ONLY and explicitly replaces the wholeU1/G4 parent.
roi177=np.array([[-145,-62,-35],[145,96.75,108.75]],float);b177={};sel177={}
for n,s in ctx177.items():
    if n in bounds126:bb=bounds126[n];bb=np.array([[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]])
    else:bb=np.array(saved_bounds(s))
    if np.all(bb[1]>=roi177[0]) and np.all(bb[0]<=roi177[1]):b177[n]=bb;sel177[n]=s
critical177=['Station:D_FL:case','Station:D_FR:case','Station:P_SYS:case','CurrentFoundation:BankBedCurrent:1','CurrentDFL:permanent','CurrentDFL:removable','CurrentDFL:DFL:cap','CurrentDFL:DFL:band','CurrentDFL:DFL:head']+[n for n in Current35 if n.startswith('D_FR:first9:')]
p177=OUT/'day07-D15-current-binding-and-receiver-context-sections.json';assert not p177.exists();views177=[('D3_XZ_Yminus16p25',1,-16.25,Part.makePlane(290,143.75,A.Vector(-145,-16.25,108.75),A.Vector(0,1,0),A.Vector(1,0,0)),[0,2]),('G4_XY_Z45p52',2,45.52,Part.makePlane(290,158.75,A.Vector(-145,-62,45.52),A.Vector(0,0,1),A.Vector(1,0,0)),[0,1]),('V2_YZ_Xminus16',0,-16,Part.makePlane(158.75,143.75,A.Vector(-16,-62,-35),A.Vector(1,0,0),A.Vector(0,1,0)),[1,2])]
r177=dict(id=p177.stem,status='D1_D5_CURRENT_PROJECT_BINDING_AND_ACTUAL_RECEIVER_SECTION_READ_NOT_CLEARANCE_PASS',D1_D5=d177,all5_D_shared_stock=stock177,existing_D2_D3_D4_not_replayed=True,current_DFR_case_bounds=saved_bounds(Current35['Station:D_FR:case']),current_DFR_all5_full9_bounds={n:saved_bounds(Current35[n]) for n in Current35 if n.startswith('D_FR:first9:')},W007_other_end='CurrentD_FRhardwarepose differsfromoldboundarymetadata. Nativefirst9:5..9 worldports nowoncaseY-.5/Z-8.5. ExactW007toonecurrentnativefield identity/wholefreepath/currentdebit NOTnewlyasserted; preserveall5andselectedunit. Need sourceassignmenttrace before any change/lengthcredit.',W002_BUS_D_W003mate='SelectedoneBUS_DGfactoryunit unchanged. SourceBUSend9/currentTailCarrierclampstock retained; wholemiddle path notnewlyqualified.',candidate_context=dict(count=len(ctx177),roi_bounds_mm=roi177.tolist(),broadphase_selected=len(sel177),retired_for_this_PROPOSED_context_only=retired177,no_duplicate_oldU1_plus_primary=True,new_G4_is_PROPOSED_not_current=True,allrest108_newSRC21_neutral_retained=True,oldW068_andproposedcrown_dependencies_not_silently_erased=True),selected_actor_bounds_mm={n:b.tolist() for n,b in b177.items()},critical_source_bounds_mm={n:saved_bounds(ctx177[n]) for n in critical177 if n in ctx177},sections=[],section_errors=[],sections_not_volume_or_empty_space_proof=True,no_new_print_or_wire_geometry=True,pid=os.getpid(),session_id=46493)
def save177():
    r177['operation_seconds']=time.monotonic()-t177;r177['process_cpu_seconds']=time.process_time()-c177;q=p177.with_suffix('.tmp');q.write_bytes((json.dumps(r177,indent=2)+'\n').encode());os.replace(q,p177)
save177()
for vn,axis,pos,plane,proj in views177:
    vv=dict(name=vn,axis=axis,position_mm=pos,projection_axes=proj,actor_curves=[])
    for n,s in sel177.items():
        bb=b177[n]
        if not bb[0,axis]-1e-7<=pos<=bb[1,axis]+1e-7:continue
        try:
            cut=s.section(plane);curves=[]
            for e in cut.Edges:
                pts=e.discretize(Deflection=.18);curves.append([[list(v)[proj[0]],list(v)[proj[1]]] for v in pts])
            if curves:vv['actor_curves'].append(dict(actor=n,curves=curves,kind=('allocated_tailcapacity' if n.startswith('G4C1capacity:') else 'new_G4_candidate' if n.startswith('G4C1:') else 'moving_neutral_only' if n in moving115 else 'retained_actual_native_context')))
        except Exception as e:r177['section_errors'].append(dict(view=vn,actor=n,error=str(e)[:160],not_contact_or_emptyspace_proof=True))
    r177['sections'].append(vv);save177()
    if time.monotonic()-t177>12:break
print('D15_CONTEXT_RECEIVED',len(r177['sections']),len(sel177),len(r177['section_errors']),r177['operation_seconds'],r177['process_cpu_seconds'],hashlib.sha256(p177.read_bytes()).hexdigest(),'OWNER80_READ_IDLE',os.getpid(),flush=True)

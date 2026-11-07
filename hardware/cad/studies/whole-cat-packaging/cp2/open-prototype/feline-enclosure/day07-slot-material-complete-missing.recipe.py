import time,json,hashlib
t97=time.monotonic();cpu97=time.process_time();rows97=[];tasks97=tasks96[len(foreign96):]
for k in tasks97:
    q=ctx83[k];r=dict(other=k,source_valid=q.isValid())
    if q.isValid():
        gap,w,_=worldholder96.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='CHANGED_WHOLE_CARRIER_SEPARATED125' if gap>=1.25-1e-7 else 'CHANGED_WHOLE_CARRIER_HOLD')
        if gap<1e-7:
            co=worldholder96.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows97.append(r);print('SLOT97',r,flush=True)
    if r['status']!='CHANGED_WHOLE_CARRIER_SEPARATED125':break
feed97=[]
for d in proposal93['structural145']:
    u,v=d['u'],d['v_leg'];f=Part.Face(Part.makePolygon([A.Vector(x,y,0) for x,y in [(u-1.65,v-1),(u+1.65,v-1),(u+1.65,v+1),(u-1.65,v+1),(u-1.65,v-1)]]));lost=f.cut(winlocal92);assert lost.isValid();feed97.append(dict(u=u,v=v,full_capacity_mm=[3.3,2],outside_actual_window_mm2=lost.Area))
heads97=[]
for n,s in heads94.items():
    co=s.common(loops94[n]);gap,_,_=s.distToShape(loops94[n]);heads97.append(dict(unit=n,head_band_gap_mm=gap,common_valid=co.isValid(),material_common_mm3=co.Volume if co.isValid() else None,mechanical_interface='Fullselectedheadreserve seatsagainstownclosedband. Dimensionsnominal/projectheight; deliveredlatch/feedfitphase2, not ownershipbyname.'))
profile97=[]
for n,q in profiles93.items():
    co=holder96.common(q);assert co.isValid();profile97.append(dict(profile=n,allocated_common_mm3=co.Volume,source_scope='Samefive9/20groovebeds+pressurefingers transformed together withfullprofilegroup; intentionalgeometryfunction unchanged, allnewmaterialaddedmustnotpenetratefullprofile.'))
bay97=[]
for n,s in [('lower',frame96),('upper',cap96)]:
    for k,q in covers90.items():
        low=bbox_lower_bound(s.BoundBox,q.BoundBox)
        if low>=1.25:r=dict(target=n,cover=k,lower_mm=low,status='CONTINUOUS_MATERIAL_COVER_SEPARATED125_BY_BOUNDS')
        else:
            gap,_,_=s.distToShape(q);r=dict(target=n,cover=k,gap_mm=gap,status='CONTINUOUS_MATERIAL_COVER_SEPARATED125' if gap>=1.25-1e-7 else 'CONSERVATIVE_MATERIAL_COVER_HOLD_NOT_CONTACT')
        bay97.append(r)
matrix97=foreign96+rows97;ok97=len(matrix97)==len(tasks96) and all(r['status']=='CHANGED_WHOLE_CARRIER_SEPARATED125' for r in matrix97) and all(r['outside_actual_window_mm2']<1e-6 for r in feed97) and all(r['allocated_common_mm3']<1e-5 for r in profile97) and all(not r['status'].startswith('CONSERVATIVE') for r in bay97)
r97=dict(id='day07-SOURCE-slot-material-completion',status='SLOT_CARRIER_MATERIAL_FUNCTION_SCOPE_RECEIVED_WHOLE_TRANSPORT_OPEN' if ok97 else 'SLOT_CARRIER_LOCAL_FUNCTION_OR_FOREIGN_HOLD',received_only_missing_rows=rows97,reused_unchanged_first_case_row=foreign96,full_foreign_count=len(matrix97),total=len(tasks96),unreceived=len(tasks96)-len(matrix97),actual_new_feed_footprints=feed97,all4_heads_function=heads97,material_vs_full_profiles=profile97,continuous_material_Ankle_rows=bay97,
 initial_assembly='BenchprepareexistingSOURCEsplicesOFFPETG afterdryfit; feed2uncinched145throughactualnativewindow. Seatreal2feet/crosshead/sidecar. Layfull3profiles/3sleeves/full9lands intoopenlowerbeds, placeupperpressurecover. Thread2selected100aroundwholelandinterfaces. Close4sourceheadsusing25pullonce; alluncuttails enterupperopenaxialendportals into2layersunderthepressure-roof BEFOREoutercoversclose. T18tiesoneway; laterrenewalnotphantomrelease, quantitiesnotclaimedinstock. Initialmoving-modulefactoryends/9transport/allphysicalbudgets stillneedwholequalification; no virtualunsoldering/detachintegralLink.',
 scoped_loadpath='ActualLinkunderside mechanicalbearing22.287799/22.284860mm2 + actualnativewindow2fullfeeds;2sameconformingpolygonfeet/crossheads/continuouspositive-sidecarspine/5supported9/20beds. Pressure5fingers/lowerplate/2walls/roof18positivejunctions, plannedbandchannelswithintendedmaterialcoverage19members. BoughtLinkneverfused. Prototypefunction not FEM/productionstrength/deliveredlatchcertification.',
 new_source_A_U_fit_slack=None,bodylanding_actualroot='NOT_RUN',source_end_length_and_motion_outline='OPEN',selected=False,N01_complete=False,current1292_effective1311_rest108_unchanged=True,operation_seconds=time.monotonic()-t97,process_cpu_seconds=time.process_time()-cpu97,pid=os.getpid(),session_id=46493)
p97=OUT/'day07-SOURCE-slot-material-completion.json';assert not p97.exists();p97.write_bytes((json.dumps(r97,ensure_ascii=False,indent=2)+'\n').encode());print('SLOT97_FINAL',r97['status'],len(matrix97),len(tasks96),feed97,heads97,profile97,r97['operation_seconds'],r97['process_cpu_seconds'],hashlib.sha256(p97.read_bytes()).hexdigest(),flush=True)

import time,json,hashlib,zipfile,math,os
# ONE full-group return turn, not 9 whole wire axes.
t110=time.monotonic();cpu110=time.process_time();assert len(doneposes108)==36 and first108 is None
c110=A.Vector(-84.1,67,38.75);outer110=Part.makeCylinder(39.8,10.5,c110,A.Vector(0,0,1),90);outer110.rotate(c110,A.Vector(0,0,1),-90);inner110=Part.makeCylinder(30.4,10.7,A.Vector(-84.1,67,38.65));turn110=outer110.cut(inner110);assert turn110.isValid() and len(turn110.Solids)==1
expected110=math.pi/4*(39.8**2-30.4**2)*10.5;assert abs(turn110.Volume-expected110)<1e-5
startface110=turn110.section(Part.makePlane(30,30,A.Vector(-84.1,20,30),A.Vector(1,0,0)));endface110=turn110.section(Part.makePlane(30,30,A.Vector(-65,67,30),A.Vector(0,1,0)))
seam110=turn110.common(guide101);assert seam110.isValid();assert seam110.Volume<1e-7
ctx110=dict(fixed106);ctx110.update(restMotion);ctx110.update(proposed99);tasks110=[n for n,s in ctx110.items() if bbox_lower_bound(turn110.BoundBox,s.BoundBox)<1.25];tasks110.sort(key=lambda n:(0 if n=='Underdeck:PositiveFoundation' else 1,n));rows110=[];first110=None;common110=None
for n in tasks110:
    s=ctx110[n];row=dict(target='FULL9_FIXED_RETURN_R35p1',other=n,source_valid=s.isValid(),capacity_valid=turn110.isValid())
    if row['source_valid']:
        gap,w,_=turn110.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(aa),list(bb)] for aa,bb in w[:1]])
        if gap<1e-7:
            co=turn110.common(s);row.update(common_valid=co.isValid(),allocated_capacity_common_mm3=co.Volume if co.isValid() else None);common110=co
        row['status']='FULL_GROUP_ALLOCATED_REGION_SEPARATED125' if gap>=1.25-1e-7 else 'FULL_GROUP_ALLOCATED_REGION_HOLD_NOT_PHYSICAL_WIRECONTACT'
    else:row['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
    rows110.append(row)
    if row['status']!='FULL_GROUP_ALLOCATED_REGION_SEPARATED125':first110=row;break
sections110=[]
for y in [50.6,55,60,67]:
    plane=Part.makePlane(200,200,A.Vector(-170,y,-50),A.Vector(0,1,0))
    for n,s in [('full9_R35p1_return_capacity',turn110),('actual_current_U1carrier',ctx110['Underdeck:PositiveFoundation']),('new_complete_BankBed_guide',whole105)]:
        sec=s.section(plane);curves=[]
        for e in sec.Edges:
            ps=e.discretize(Deflection=.12)
            if len(ps)>1:curves.append([[v.x,v.z] for v in ps])
        sections110.append(dict(axis='Y',value_mm=y,name=n,curves_xz=curves))
ar110=OUT/'day07-SOURCE-external-loop-return-capacity-first-gate.breps.zip';assert not ar110.exists();ge110=[]
with zipfile.ZipFile(ar110,'w',zipfile.ZIP_DEFLATED) as z:
    its=[('FULL9_RETURN_CAPACITY_R35p1',turn110),('ACTUAL_CURRENT_U1carrier',ctx110['Underdeck:PositiveFoundation'])]
    if common110 is not None:its.append(('ALLOCATED_REGION_CURRENT_COMMON_NOT_ACTUALWIRE',common110))
    its.extend([('NEW_SOURCE_LOWER_POSE35',lastmoved108['PROPOSED_SOURCE_KNEE:lower']),('NEW_SOURCE_UPPER_POSE35',lastmoved108['PROPOSED_SOURCE_KNEE:upper'])])
    for i,(n,s) in enumerate(its):
        raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);ge110.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge110,scope='Newgroupcapacityfirstfalsifier+newSource2printPOSE35 only; sourceworldonce/currentU1override.'),indent=2)+'\n').encode())
r110=dict(id='day07-SOURCE-external-loop-return-capacity-first-gate',status='EXTERNAL_LOOP_SOUTH_RETURN_ALLOCATED_GROUP_REGION_HOLD' if first110 else 'LOCAL_FULL9_RETURN_CAPACITY_RECEIVED_SCOPED_NOT_WHOLE_LOOP',proposal='day07-SOURCE-external-loop-south-merge9-whole-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-external-loop-south-merge9-whole-proposal.json').read_bytes()).hexdigest(),capacity=dict(centre_radius_mm=35.1,radial_width_mm=9.4,vertical_depth_mm=10.5,inner_capacity_radius_mm=30.4,outer_capacity_radius_mm=39.8,group_neutral_axis_length_mm=35.1*math.pi/2,bounds_mm=saved_bounds(turn110),valid=True,actual_volume_mm3=turn110.Volume,analytic_volume_mm3=expected110,entry_mm=[-84.1,31.9,44],entry_tangent=[1,0,0],exit_mm=[-49,67,44],exit_tangent=[0,1,0],full_existing_guide_seam_common_mm3=seam110.Volume,no_extra9or_newterminal=True),rows=rows110,cursor=len(rows110),total=len(tasks110),unreceived=len(tasks110)-len(rows110),first_falsifier=first110,meaning='Fullallocated9groupregion H0 is thislayoutcapacityHOLD, NOTactualinstalledwirecontact/allmanualpathimpossibility. Do notfreezeillustrativeflexpaths. FullactualU1carrier currentmaterial/functionpreserved; NO own-by-name. IfHOLD stopbranchbeforeotherpairs/freewires/supportdetail. Root105+26.25 remainsacceptedlocalonly.',all_source_A_U_fit_slack=None,sections=sections110,archive=ar110.name,archive_sha256=hashlib.sha256(ar110.read_bytes()).hexdigest(),geometry=ge110,operation_seconds=time.monotonic()-t110,process_cpu_seconds=time.process_time()-cpu110,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p110=OUT/'day07-SOURCE-external-loop-return-capacity-first-gate.json';assert not p110.exists();p110.write_bytes((json.dumps(r110,indent=2)+'\n').encode())
f108=OUT/'day07-SOURCE-new21-motion36-complete-scoped.json';assert not f108.exists();d=save108();d['id']=f108.stem;d['archive_of_last_new_pose']=ar110.name;d['archive_sha256']=r110['archive_sha256'];d['newly_received_pair_count']=len(rows108)-len(r106['actual_candidate_rows']);d['no_replayed_received19']=True;d['BodyOuter_3p25']='StillOPEN forwholebodyplan; movingmechanicallegattachment scope NOTautomaticbodyshellPASS.';f108.write_bytes((json.dumps(d,indent=2)+'\n').encode())
print('SOURCE110_GATE',r110['status'],first110,'cursor',r110['cursor'],'total',r110['total'],'timing',r110['operation_seconds'],r110['process_cpu_seconds'],hashlib.sha256(p110.read_bytes()).hexdigest(),flush=True);print('SOURCE108_COMPLETE',len(doneposes108),len(rows108),len(floors108),min(q['conservative_ground_lower_mm'] for q in floors108),sum(q['operation_seconds'] for q in chunks108),sum(q['process_cpu_seconds'] for q in chunks108),hashlib.sha256(f108.read_bytes()).hexdigest(),flush=True)

import time,json,hashlib,zipfile,os,math
t233=time.monotonic();c233=time.process_time();pp233=OUT/'day07-WHOLE9-north-entry-vertical-before-foreturn-whole-plan.json';pr233=json.loads(pp233.read_bytes());oldlane233=json.loads((OUT/'day07-SOURCE-ninecore-left-entry-lane-roll-whole-proposal.json').read_bytes());fields233={};paths233={};bb233={};quality233=[];points233={}
for row in pr233['rows']:
    n=row['wire'];x,y,z=row['source_passage_P'];R1=row['XZ_S_R1_mm'];R2=row['XZ_S_R2_mm'];Cz=5.6;Y2=y-R1-R2;Rxy=row['XY_R_mm'];Cx=-94.9;zl=Cz-R2;P=A.Vector(x,y,z);M=A.Vector(x,y-R1,Cz);N=A.Vector(x,Y2,zl);Q=A.Vector(Cx,Y2-Rxy,zl)
    e1=Part.Arc(P,A.Vector(x,y-R1/math.sqrt(2),Cz+R1/math.sqrt(2)),M).toShape();e2=Part.Arc(M,A.Vector(x,Y2+R2/math.sqrt(2),Cz-R2/math.sqrt(2)),N).toShape();e3=Part.Arc(N,A.Vector(Cx-Rxy/math.sqrt(2),Y2-Rxy/math.sqrt(2),zl),Q).toShape();path=Part.Wire([e1,e2,e3]);r=next(q['profile_radius_mm'] for q in oldlane233['rows'] if q['wire']==n)+.4;s=path.makePipeShell([Part.Wire([Part.makeCircle(r,P,A.Vector(0,-1,0))])],True,False);assert s.isValid();expected=math.pi*r*r*(R1+R2+Rxy)*math.pi/2;assert abs(s.Volume-expected)<1e-4
    lo=[x-r,Y2-Rxy-r,zl-r];hi=[Cx+r,y+r,z+r];cover=box153([lo,hi]);mis=s.cut(cover);assert mis.isValid() and mis.Volume<1e-7
    fields233[n]=s;paths233[n]=path;points233[n]=(P,Q);bb233[n]=cover.BoundBox;quality233.append(dict(wire=n,valid=True,solids=len(s.Solids),R_mm=[R1,R2,Rxy],guide_mm=path.Length,expected_guide_mm=(R1+R2+Rxy)*math.pi/2,volume_mm3=s.Volume,expected_volume_mm3=expected,analytic_bounds_mm=[lo,hi],actual_outside_used_bounds_mm3=mis.Volume))
rows233=[];contour233=[];first233=None;nom233=None;nomco233=None
for n,s in fields233.items():
    v=context230['Ref_Material_S0_body_CP2_0_0'];g=s.distToShape(v)[0];row=dict(field=n,other='Ref_Material_S0_body_CP2_0_0',gap_mm=g,required_mm=1.25,status='S0_SOURCE_BODY_SCOPED_CLEAR' if g>=1.25-1e-7 else 'S0_SOURCE_BODY_NEW_ORDER_HOLD');rows233.append(row)
    if g<1.25-1e-7:first233=row;break
s0received233=len(rows233);tasks233=[]
if first233 is None:
    for n,s in fields233.items():
        r=next(q['profile_radius_mm'] for q in oldlane233['rows'] if q['wire']==n)+.4;P,Q=points233[n];thick=paths233[n].makePipeShell([Part.Wire([Part.makeCircle(r+3.25,P,A.Vector(0,-1,0))])],True,False);assert thick.isValid()
        # Thick tube + endpoint balls cover the complete3.25 Euclidean offset; check every piece independently, no hidden Boolean union.
        for role,p in [('THICK_PIPE',thick),('ENTRY_BALL',Part.makeSphere(r+3.25,P)),('EXIT_BALL',Part.makeSphere(r+3.25,Q))]:
            outside=p.cut(BodyOuter31);assert outside.isValid();q=dict(wire=n,part=role,required_mm=3.25,valid=True,outside_actual_BodyOuter_mm3=outside.Volume);contour233.append(q)
            if outside.Volume>1e-7:first233=dict(stage='ACTUAL_ALLOCATED_BODY_CONTOUR',row=q,meaning='Chosenwholepacket capacity notwithinactualBodyOuter3.25. Not actualwirecontact/allentriesimpossible.');break
        if first233:break
if first233 is None:
    tasks233=[(n,k) for n,s in fields233.items() for k,v in context230.items() if k!='Ref_Material_S0_body_CP2_0_0' and bbox_lower_bound(bb233[n],v.BoundBox)<1.25];tasks233.sort(key=lambda q:(0 if q[1].startswith('Ref_Material_P0_') else 1 if q[1].startswith('Ref_Material_') else 2,q[1],q[0]))
    for n,k in tasks233:
        s=fields233[n];v=context230[k];valid=v.isValid();q=dict(field=n,other=k,source_valid=valid,required_mm=1.25,classification='FLEXIBLE_SELECTED_SOURCE_FUNCTION_NEEDS_COALLOCATION_IF_HOLD' if k=='W026:custom:fullsolid' else 'REAL_RETAINED_SOURCE_OR_FUNCTIONAL_STOCK');
        if not valid:q['status']='SOURCE_INVALID_OPEN_NOT_CONTACT';rows233.append(q);first233=q;break
        g,ww,_=s.distToShape(v);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='NEW_ORDER_NEUTRAL_CAPACITY_SCOPED_CLEAR' if g>=1.25-1e-7 else 'NEW_ORDER_ALLOCATED_CAPACITY_HOLD')
        if g<1.25-1e-7:
            co=s.common(v);assert co.isValid();q.update(common_valid=True,allocated_common_mm3=co.Volume)
            if k.startswith('Ref_Material_'):
                rr=next(row['profile_radius_mm'] for row in oldlane233['rows'] if row['wire']==n);P=points233[n][0];nom233=paths233[n].makePipeShell([Part.Wire([Part.makeCircle(rr,P,A.Vector(0,-1,0))])],True,False);assert nom233.isValid();nomco233=nom233.common(v);assert nomco233.isValid();q.update(named_local_nominal_common_mm3=nomco233.Volume,nominal_gap_mm=nom233.distToShape(v)[0],meaning='Onlynamednewwholepacket mandatoryhazard; no deliveredcontact/all3Dspace/stockshortage claim.')
        rows233.append(q)
        if g<1.25-1e-7:first233=q;break
ar233=OUT/'day07-WHOLE9-vertical-before-S0-order-first-gate.breps.zip';assert not ar233.exists();ge233=[]
with zipfile.ZipFile(ar233,'w',zipfile.ZIP_DEFLATED) as z:
    ss=[('WHOLE9_VERTICAL_BEFORE_XY:'+n,s) for n,s in fields233.items()]
    if first233 and 'other' in first233:ss.append(('FIRST_CURRENT_SOURCE:'+first233['other'],context230[first233['other']]))
    if nom233 is not None:ss.extend([('ONLY_NAMED_NOMINAL_PROFILE',nom233),('VALID_NOMINAL_COMMON_WITNESS',nomco233)])
    for i,(n,s) in enumerate(ss):
        f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat93-first-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();en=str(i)+'.brep';z.writestr(en,raw);ge233.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge233),indent=2)+'\n').encode())
p233=OUT/'day07-WHOLE9-vertical-before-S0-order-first-gate.json';r233=dict(id=p233.stem,status='NEW_WHOLE9_ENTRY_ORDER_FIRST_HOLD' if first233 else 'NEW_WHOLE9_ENTRY_ORDER_NEUTRAL_STATIC_AND_ACTUAL_CONTOUR_CLOSED_SCOPED',proposal=pp233.name,proposal_sha256=hashlib.sha256(pp233.read_bytes()).hexdigest(),quality=quality233,S0_full_body_received=s0received233,S0_full_body_total=9,rows=rows233,actual_contour_rows=contour233,remaining_current_candidate_count=max(0,len(tasks233)-(len(rows233)-s0received233)),current_candidate_count=len(tasks233),first_falsifier=first233,context_count=len(context230),source21_rest108_context_unchanged=True,body_entry_selected_for_moving_delta=False,moving_delta_NEW_not_yet_received=True,newmoving_free_leg_Li_and55usable_reserve_OPEN=True,actual_A_U_fit_slack=None,actualcut=None,no_new_material_or_parts=True,no_old_case_or_matrix_replays=True,selected=False,N01_complete=False,archive=ar233.name,archive_sha256=hashlib.sha256(ar233.read_bytes()).hexdigest(),geometry=ge233,operation_seconds=time.monotonic()-t233,process_cpu_seconds=time.process_time()-c233,pid=os.getpid(),session_id=46493);p233.write_bytes((json.dumps(r233,indent=2)+'\n').encode());print('ENTRY233_NEW_ORDER',r233['status'],first233,'S0',s0received233,'contour',len(contour233),'rows',len(rows233),'tasks',len(tasks233),'seconds',r233['operation_seconds'],r233['process_cpu_seconds'],'OWNER93_SAVED_IDLE',os.getpid(),flush=True)

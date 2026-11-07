import time,json,hashlib,zipfile,os,math
t83=time.monotonic();cpu83=time.process_time();mat83=A.Matrix()
for j,v in enumerate([axis81,side81,normal81]):
    for i in range(3):setattr(mat83,'A'+str(i+1)+str(j+1),v[i])
placement83=A.Placement(base81,A.Rotation(mat83))
def local83(s):s.Placement=placement83*s.Placement;return s
patches83=[];coupons83={};pads83={}
for k,x in enumerate([-15,15]):
    roi=local83(Part.makeBox(4,4,.5,A.Vector(x-2,-2,-.5)));coupon=link81.common(roi);pad=local83(Part.makeBox(4,4,2,A.Vector(x-2,-2,0)));pc=pad.common(link81);pf=local83(Part.Face(Part.makePolygon([A.Vector(a,b,0) for a,b in [(x-2,-2),(x+2,-2),(x+2,2),(x-2,2),(x-2,-2)]])));fc=pf.common(face81);gap=pad.distToShape(link81)[0]
    patches83.append(dict(name='pad'+str(k),actual_source_actor=stage_link81,source_coupon_valid=coupon.isValid(),actual_available_source_volume_mm3=coupon.Volume,expected_full_coupon_volume_mm3=8,actual_contact_face_area_mm2=fc.Area,expected_contact_area_mm2=16,new_pad_source_common_valid=pc.isValid(),new_pad_material_intrusion_mm3=pc.Volume,new_pad_actual_source_gap_mm=gap,source_point_world_mm=list(placement83.multVec(A.Vector(x,0,0))),status='SOURCE_CONTACT_PATCH_RECEIVED_NOT_PRINT_FUSION' if coupon.isValid() and abs(coupon.Volume-8)<1e-5 and abs(fc.Area-16)<1e-5 and pc.Volume<1e-5 and gap<1e-6 else 'ACTUAL_LINK_CONTACT_PATCH_HOLD_NO_ROOT_ASSUMPTION'))
    coupons83['source_coupon_'+str(k)]=coupon;pads83['proposed_contact_pad_'+str(k)]=pad
holderalloc83=local83(Part.makeBox(86,14,8,A.Vector(-43,-7,0)));baseplate83=local83(Part.makeBox(86,14,2,A.Vector(-43,-7,0)))
sourcebounds83=[]
for c in json.loads(p82.read_bytes())['actual_face_curves_axis_transverse_mm']:sourcebounds83.extend(c)
width83=max(p[1] for p in sourcebounds83)-min(p[1] for p in sourcebounds83);depth83=1.5+8;tiepathbound83=2*(width83+depth83+1.2);tie83=dict(structural_sku='111-02370 T18I145',quantity=2,one_tie_per_independent_structural_joint=True,selected_nominal_length_mm=145,source_width_mm=2.5,source_thickness_mm=1.2,whole_source_face_transverse_extent_mm=width83,maximum_holder_plus_single_link_thickness_mm=depth83,conservative_rectangle_centreline_bound_mm=tiepathbound83,closure_pull_allowance_mm=25,total_unit_required_upper_if_this_return_accessible_mm=tiepathbound83+25,source_unit_residual_mm=145-tiepathbound83-25,actual_feed_path_or_retained_tail_not_yet_received=True,manufacturer_head_mm=[4.8,4.5,3.5],planned_head_capacity_mm=[5.3,5,5],no_claim_freestock=True)
rootok83=all(p['status']=='SOURCE_CONTACT_PATCH_RECEIVED_NOT_PRINT_FUSION' for p in patches83)
ctx83=dict(effective62);ctx83.update(restMotion);own83=holderalloc83.common(link81);assert own83.isValid();tasks83=[n for n,s in ctx83.items() if n!=stage_link81 and bbox_lower_bound(holderalloc83.BoundBox,s.BoundBox)<1.25];tasks83.sort(key=lambda n:(0 if n in MotionSource31['membership']['RL']['Knee'] else 1,n));rows83=[]
if rootok83 and own83.Volume<1e-5:
    for n in tasks83:
        s=ctx83[n];r=dict(other=n,valid=s.isValid())
        if s.isValid():
            gap,w,_=holderalloc83.distToShape(s);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
            if gap<1e-7:
                co=holderalloc83.common(s);r.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
            r['status']='FULL_HOLDER_ALLOCATION_SEPARATED125' if gap>=1.25-1e-7 else 'FULL_HOLDER_ALLOCATION_HOLD_NOT_ACTUAL_WIRE_CONTACT'
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        rows83.append(r);print('SOURCE_HOLDER83',r,flush=True)
        if r['status']!='FULL_HOLDER_ALLOCATION_SEPARATED125' or time.monotonic()-t83>12:break
ar83=OUT/'day07-SOURCE-Knee-link-actual-mount-first-gate.breps.zip';assert not ar83.exists();ge83=[]
with zipfile.ZipFile(ar83,'w',zipfile.ZIP_DEFLATED) as z:
    items=[(stage_link81,link81),('SOURCE:actual_outer_contact_face',face81),*coupons83.items(),*pads83.items(),('SOURCE:86x14x8_full_holder_ALLOCATION',holderalloc83),('SOURCE:proposed_2mm_baseplate',baseplate83)]+[(r['other'],ctx83[r['other']]) for r in rows83]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);b=s.optimalBoundingBox();ge83.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge83,scope='One actualSOURCEholdermountpreflight: realcontact/tieconditionalbound/full86allocation; no legmotionoroldtests/newV3bracket.'),indent=2)+'\n').encode())
r83=dict(id='day07-SOURCE-Knee-link-actual-mount-first-gate',status='ACTUAL_KNEE_LINK_CONTACT_OR_FULL_HOLDER_FIRST_GATE_HOLD' if not rootok83 or own83.Volume>1e-5 or len(rows83)<len(tasks83) or any(r['status']!='FULL_HOLDER_ALLOCATION_SEPARATED125' for r in rows83) else 'ACTUAL_KNEE_LINK_CONTACT_FULL_HOLDER_STATIC_RECEIVED_TIE_ACCESS_NEXT',proposal=p81.name,proposal_sha256=hashlib.sha256(p81.read_bytes()).hexdigest(),source_face=stage_link81,source_owner='Motion_RL_Knee',physical_contact_not_fusion=True,patches=patches83,whole_holder_to_actual_owner=dict(common_valid=own83.isValid(),material_intrusion_mm3=own83.Volume,source_touch_intentional_withoutprintedfusion=True),selected_tie_conditional_unit_bound=tie83,full_context_fixed_and_neutral_moving=len(ctx83),criterion='CompleteholderallocatedvolumeR/ends/sleeves beforedetail; broadphaseallcurrent1311+108, exactonlycandidatepairs. Ownerlinkisphysicalcontactnotforeigncollision; allotherKnee/Anklecases/metal remainforeign.',rows=rows83,cursor=len(rows83),total=len(tasks83),unreceived=len(tasks83)-len(rows83),archive=ar83.name,archive_sha256=hashlib.sha256(ar83.read_bytes()).hexdigest(),geometry=ge83,all9_original_and_donor_current_minimum_mm=None,actual_A_U_mm=None,current1292_effective1311_rest108_unchanged=True,new_holder_not_added_or_selected=True,no_newsplice_or_wirecut=True,no_old_238_14_37_replay=True,operation_seconds=time.monotonic()-t83,process_cpu_seconds=time.process_time()-cpu83,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p83=OUT/'day07-SOURCE-Knee-link-actual-mount-first-gate.json';assert not p83.exists();p83.write_bytes((json.dumps(r83,ensure_ascii=False,indent=2)+'\n').encode());print('SOURCE_HOLDER_FINAL83',r83['status'],patches83,own83.Volume,len(rows83),len(tasks83),tiepathbound83+25,r83['operation_seconds'],r83['process_cpu_seconds'],hashlib.sha256(p83.read_bytes()).hexdigest(),flush=True)

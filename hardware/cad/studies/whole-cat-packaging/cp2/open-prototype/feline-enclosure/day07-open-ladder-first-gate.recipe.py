import time,json,hashlib,zipfile,os,math
t86=time.monotonic();cpu86=time.process_time();wirelocal86={}
for name,y,r in [('D',-2.85,1.55),('V',0,1.0),('G',2.85,1.55)]:
    s=Part.makeCylinder(r,86,A.Vector(-43,y,4),A.Vector(1,0,0))
    if name=='V':s=s.fuse(Part.makeCylinder(1.1,20,A.Vector(-10,y,4),A.Vector(1,0,0)))
    wirelocal86[name]=s
def grooved86(s):
    for w in wirelocal86.values():s=s.cut(w)
    return s
lower86={};upper86={};beds86=[('source_land9',-43,9),('D_sleeve20',-32,20),('V_sleeve20',-10,20),('G_sleeve20',12,20),('donor_land9',34,9)]
for i,x in enumerate([-15,15]):
    lower86['foot_'+str(i)]=conforming84['actual_shape_contact_foot_'+str(i)].copy()
    lower86['crosshead_'+str(i)]=local83(Part.makeBox(4,14,1,A.Vector(x-2,-7,1)))
for label,y in [('left',-7),('right',5)]:lower86['continuous_'+label+'_beam']=local83(Part.makeBox(86,2,4.25,A.Vector(-43,y,1.75)))
for name,x,L in beds86:
    lower86[name+'_bearing_bed']=local83(grooved86(Part.makeBox(L,10.5,1.75,A.Vector(x,-5.25,1.75))))
    upper86[name+'_pressure_finger']=local83(grooved86(Part.makeBox(L,9.6,1.75,A.Vector(x,-4.8,4.5))))
upper86['continuous_cap_plate']=local83(Part.makeBox(86,14,2,A.Vector(-43,-7,6)))
def fuse_checked86(parts):
    result=None
    for name,s in parts.items():
        assert s.isValid() and len(s.Solids)==1,name
        result=s if result is None else result.fuse(s)
    return result
frame86=fuse_checked86(lower86);cap86=fuse_checked86(upper86);coverage86=[]
for typ,parts,whole in [('lower',lower86,frame86),('upper',upper86,cap86)]:
    for name,s in parts.items():
        missing=s.cut(whole);coverage86.append(dict(part=typ,name=name,missing_valid=missing.isValid(),missing_mm3=missing.Volume))
joints86=[]
jointtasks86=[('foot_'+str(i),'crosshead_'+str(i)) for i in [0,1]]+[(c,b) for c in ['crosshead_0','crosshead_1'] for b in ['continuous_left_beam','continuous_right_beam']]+[(name+'_bearing_bed',b) for name,x,L in beds86 for b in ['continuous_left_beam','continuous_right_beam']]
for a,b in jointtasks86:
    common=lower86[a].common(lower86[b]);joints86.append(dict(a=a,b=b,valid=common.isValid(),common_mm3=common.Volume,positive=common.isValid() and common.Volume>1e-6))
for name in upper86:
    if name=='continuous_cap_plate':continue
    common=upper86[name].common(upper86['continuous_cap_plate']);joints86.append(dict(a=name,b='continuous_cap_plate',valid=common.isValid(),common_mm3=common.Volume,positive=common.isValid() and common.Volume>1e-6))
supports86=[]
for label,x,L in beds86:
    a=lower86[label+'_bearing_bed'];b=upper86[label+'_pressure_finger'];surfaces={}
    for side,s in [('lower',a),('upper',b)]:
        area=sum(f.Area for f in s.Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Axis.dot(axis81))>.999)
        surfaces[side+'_nominal_cylindrical_support_area_mm2']=area
    supports86.append(dict(role=label,full_axial_length_mm=L,**surfaces,actual_nominal_support_not_air=all(v>0 for v in surfaces.values())))
wireproof86=[];wireworld86={}
for name,s in wirelocal86.items():
    world=local83(s.copy());wireworld86[name]=world
    lo=frame86.common(world);up=cap86.common(world);wireproof86.append(dict(core=name,lower_material_common_valid=lo.isValid(),lower_material_common_mm3=lo.Volume,upper_material_common_valid=up.isValid(),upper_material_common_mm3=up.Volume,lower_gap_mm=frame86.distToShape(world)[0],upper_gap_mm=cap86.distToShape(world)[0],scope='Exactnominalfullconservativeinsulation/sleevePROFILEwithprintedbearingfaces, notdeliveredwireOD/strainreliefpressurePASS.'))
seam86=frame86.common(cap86);framemissing86=frame86.cut(holderalloc83);capmissing86=cap86.cut(holderalloc83);holder86=Part.makeCompound([frame86,cap86])
materialok86=frame86.isValid() and cap86.isValid() and len(frame86.Solids)==len(cap86.Solids)==1 and all(r['missing_valid'] and r['missing_mm3']<1e-5 for r in coverage86) and all(r['positive'] for r in joints86) and all(r['actual_nominal_support_not_air'] for r in supports86) and all(r['lower_material_common_valid'] and r['upper_material_common_valid'] and r['lower_material_common_mm3']<1e-5 and r['upper_material_common_mm3']<1e-5 for r in wireproof86) and seam86.isValid() and seam86.Volume<1e-5
ar86=OUT/'day07-SOURCE-open-ladder-C1-material.breps.zip';assert not ar86.exists();ge86=[]
with zipfile.ZipFile(ar86,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('LOWER:'+n,s) for n,s in lower86.items()]+[('UPPER:'+n,s) for n,s in upper86.items()]+[('SOURCE:C1_complete_lower_ladder',frame86),('SOURCE:C1_removable_pressure_half',cap86)]+[('NOMINAL_OCCUPIED_PROFILE:'+n,s) for n,s in wireworld86.items()]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);b=s.optimalBoundingBox();ge86.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge86,scope='ONEC1SAMEsourceframe/joints; real2pieceopenladder/5supportedbeds/pressurehalf. Newcandidateonlynotcurrent. Componentcoverageandpositivejunctionschecked.'),indent=2)+'\n').encode())
rows86=[];pending86=[n for n in tasks83 if n!='Ref_Material_P0_Part__Feature056_0_0'];pending86.sort(key=lambda n:(0 if n=='Ref_Material_P0_Part__Feature058_0_0' else 1,n))
if materialok86:
    for n in pending86:
        s=ctx83[n];r=dict(other=n,valid=s.isValid())
        if s.isValid():
            gap,w,_=holder86.distToShape(s);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
            if gap<1e-7:
                c=holder86.common(s);r.update(common_valid=c.isValid(),common_mm3=c.Volume if c.isValid() else None)
            r['status']='C1_REAL_HOLDER_SEPARATED125' if gap>=1.25-1e-7 else 'C1_REAL_HOLDER_FOREIGN_HOLD'
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        rows86.append(r);print('SOURCE_LADDER86',r,flush=True)
        if r['status']!='C1_REAL_HOLDER_SEPARATED125' or time.monotonic()-t86>25:break
r86=dict(id='day07-SOURCE-open-ladder-C1-material-and-neighbor-first-gate',status='C1_REAL_OPEN_LADDER_MATERIAL_OR_NEIGHBOR_HOLD' if not materialok86 or len(rows86)<len(pending86) or any(r['status']!='C1_REAL_HOLDER_SEPARATED125' for r in rows86) else 'C1_REAL_OPEN_LADDER_MATERIAL_FULL10_NEIGHBORS_RECEIVED_SELECTED_TIE_ACCESS_NEXT',proposal='day07-SOURCE-open-ladder-C1-whole-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-open-ladder-C1-whole-proposal.json').read_bytes()).hexdigest(),material_ok=materialok86,lower_valid=frame86.isValid(),lower_solids=len(frame86.Solids),upper_valid=cap86.isValid(),upper_solids=len(cap86.Solids),intended_member_coverage=coverage86,positive_material_junctions=joints86,actual_bearing_supports=supports86,nominal_full_profiles=wireproof86,removable_half_functional_seam=dict(common_valid=seam86.isValid(),material_common_mm3=seam86.Volume,mechanical_contact_area_mm2=seam86.Area,not_silent_print_fusion=True,retained_by_full4selected_ties_pending=True),useful_sections=dict(each_long_sidebeam_mm=[2,4.25],area_mm2_each=8.5,crosshead_to_sidebeam_positive_overlap_n_mm=.25,minimum_groove_floor_mm=.7,scope='Measurednominalgeometry/prototypesection; notFEM/productionstrength/actualwirecompressioncertificate.'),subset_for_reuse=dict(lower_missing_valid=framemissing86.isValid(),lower_outside_old_fullalloc_mm3=framemissing86.Volume,upper_missing_valid=capmissing86.isValid(),upper_outside_old_fullalloc_mm3=capmissing86.Volume,reused_current056_gap_mm=11.999999999999922,reused_only_if_both_outside_zero=True),rows=rows86,cursor=len(rows86),total=len(pending86),unreceived=len(pending86)-len(rows86),full_original_neighbor_set=10,unchanged056_reused=1,source_contact_footprints_reused=[15.666835302964219,16],no_bought_material_fusion=True,archive=ar86.name,archive_sha256=hashlib.sha256(ar86.read_bytes()).hexdigest(),geometry=ge86,tie_stock_heads_feed_tail_access='NEXT_ONLY_IF_FIRSTGATE_PASSES',current1292_effective1311_rest108_unchanged=True,no_source_joint_pose_or_profile_offset=True,no_V3_or_old_tests=True,actual_source_A_U_minimum_fit_slack=None,operation_seconds=time.monotonic()-t86,process_cpu_seconds=time.process_time()-cpu86,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p86=OUT/'day07-SOURCE-open-ladder-C1-material-and-neighbor-first-gate.json';assert not p86.exists();p86.write_bytes((json.dumps(r86,ensure_ascii=False,indent=2)+'\n').encode());print('SOURCE_LADDER_FINAL86',r86['status'],materialok86,len(rows86),len(pending86),r86['operation_seconds'],r86['process_cpu_seconds'],hashlib.sha256(p86.read_bytes()).hexdigest(),flush=True)

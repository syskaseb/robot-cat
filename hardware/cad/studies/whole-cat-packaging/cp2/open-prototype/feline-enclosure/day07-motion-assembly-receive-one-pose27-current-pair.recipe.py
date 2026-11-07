import json,time,hashlib,zipfile,os
t212=time.monotonic();c212=time.process_time();pending212=mpending210[0];assert pending212['part']=='FRG_FULL83p3_UNCUT_CAPACITY' and pending212['pose']==27 and pending212['index']==119
n212=names175[119];src212=moving115[n212];code212,j212=owners115[n212];R212,T212=transforms175[27][code212][j212];assert np.linalg.norm(R212.T@R212-np.eye(3))<1e-10 and abs(np.linalg.det(R212)-1)<1e-10
posed212=src212.copy();posed212.Placement=placement106(R212,T212)*posed212.Placement
quality212=dict(source_valid=src212.isValid(),posed_valid=posed212.isValid(),source_volume_mm3=src212.Volume,posed_volume_mm3=posed212.Volume,delta_volume_mm3=abs(src212.Volume-posed212.Volume),method='SAMEfrozenproperTopLocworldmotion placement106(R,T)*source.Placement ONCE; no transformGeometry/no XML',owner=[code212,j212],R=R212.tolist(),T=T212.tolist(),source_bounds_mm=saved_bounds(src212),posed_bounds_mm=saved_bounds(posed212))
row212=dict(key=[pending212['part'],27,n212],previous_bounds_lower_mm=pending212['bounds_lower_mm'],required_foreign_mm=1.25)
if not quality212['source_valid'] or not quality212['posed_valid'] or quality212['delta_volume_mm3']>1e-5:row212['status']='SOURCE_OR_RIGID_COPY_INTEGRITY_OPEN_NOT_CONTACT'
else:
    ga,ww,_=tail208.distToShape(posed212);row212.update(actual_gap_mm=ga,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='EXACT_NEW_POSE27_FULL_CAPACITY_SEPARATED125' if ga>=1.25-1e-7 else 'EXACT_NEW_POSE27_ALLOCATED_STOCK_CAPACITY_HOLD_NOT_DELIVERED_CONTACT')
    if ga<1e-7:
        co=tail208.common(posed212);row212.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
ar212=OUT/'day07-FRG-open-current-one-pose27-exact-gate.breps.zip';assert not ar212.exists();ge212=[]
with zipfile.ZipFile(ar212,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('CURRENT_FULL83p3_ALLOCATED_CAPACITY',tail208),('ACTUAL_FEATURE116_POSE27_PROPER_RIGID',posed212)]):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge212.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge212),indent=2))
p212=OUT/'day07-FRG-open-current-one-pose27-exact-gate.json';assert not p212.exists();r212=dict(id=p212.stem,status=row212['status'],scope='ONLYONEpendingnewFRGcapacity/currentFeature116pose27, no21542replay ornewgeometryfamily',parent=p210.name,parent_sha256=hashlib.sha256(p210.read_bytes()).hexdigest(),actual_operand=row212,proper_rigid_source_quality=quality212,previous21542_bounds_separations_not_replayed=True,other1032_newpairs_unreceived=True,entire_D5_caseback_effectivity_motion_OPEN=True,no_newgeometry_after_actual_falsifier=True,selected=False,N01_complete=False,actualcut=None,archive=ar212.name,archive_sha256=hashlib.sha256(ar212.read_bytes()).hexdigest(),geometry=ge212,operation_seconds=time.monotonic()-t212,process_cpu_seconds=time.process_time()-c212,pid=os.getpid(),session_id=46493);p212.write_bytes((json.dumps(r212,indent=2)+'\n').encode());print('ONE_CURRENT_EXACT_MOTION',row212,'rigidvalid',quality212['posed_valid'],'volumedelta',quality212['delta_volume_mm3'],'wall',r212['operation_seconds'],'CPU',r212['process_cpu_seconds'],hashlib.sha256(p212.read_bytes()).hexdigest(),flush=True)

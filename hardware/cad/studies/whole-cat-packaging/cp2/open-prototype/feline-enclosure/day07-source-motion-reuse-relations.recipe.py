import time,json,hashlib
t107=time.monotonic();cpu107=time.process_time();relations107=[]
for name,stage in [('Ref_Material_P0_Part__Feature063_0_0','Knee'),('Ref_Material_P0_Part__Feature109_0_0_0','Ankle')]:
    s=restMotion[name];a=next(q for q in axes if q['code']=='RL' and q['stage']==stage);axis=A.Vector(*a['axis']);pivot=A.Vector(*a['pivot_mm']);faces=[]
    for i,f in enumerate(s.Faces):
        su=f.Surface;kind=type(su).__name__;ok=False;record=dict(face=i,type=kind)
        try:
            if kind=='Plane':
                align=abs(su.Axis.dot(axis));ok=align>1-1e-9;record['axis_parallel']=align
            elif kind in ['Cylinder','Cone','Toroid']:
                align=abs(su.Axis.dot(axis));off=(su.Center-pivot).cross(axis).Length;ok=align>1-1e-9 and off<1e-5;record.update(axis_parallel=align,axis_offset_mm=off)
            elif kind=='Sphere':
                off=(su.Center-pivot).cross(axis).Length;ok=off<1e-5;record['centre_axis_offset_mm']=off
        except Exception as exc:record['source_metadata_error']=type(exc).__name__
        record['coaxial_rotation_invariant_face']=ok;faces.append(record)
    relations107.append(dict(actor=name,source_owner=owners106[name],relative_axis=stage,valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,all_faces_rotation_invariant=all(q['coaxial_rotation_invariant_face'] for q in faces),faces=faces,meaning='Closedvalidsolidboundedonlybycoaxialsurfaces+normalplanes isaxiallyrotation-invariant. Notinferredfromidenticalsamplegaps; actualsurface/axisdataabove. ReuseONLYalreadyseparatednewSourcepair atpose1/2undercommonrigidtransform; no allotherlegwaiver.'))
r107=dict(id='day07-SOURCE-new-motion-reuse-relations',relations=relations107,Ankle_Foot123=dict(source_cover_receipt='day07-SOURCE-Ankle-functional-bay-and-full-stock.json',source_full_volume17420p0085287359_preserved=True,source_uncovered_mm3=0,range_degrees=[0,endangle88],new21_geometry_coverage_receipts=['day07-SOURCE-slot-retention-functional-first-gate.json','day07-SOURCE-slot-whole-tail-bearing-gate.json','day07-SOURCE-slot-full-stock-completion.json','day07-SOURCE-slot-material-completion.json','day07-SOURCE-slot-crosshead-functional-grooves.json'],scope='Full5continuouscovers actualFoot overrelativeAnkleangle andexactNEWsidecar+stock+material/subset proof. NOToldoriginal3.117330claim.'),raw106partial_preserved=True,operation_seconds=time.monotonic()-t107,process_cpu_seconds=time.process_time()-cpu107,selected=False,N01_complete=False)
p107=OUT/'day07-SOURCE-new-motion-reuse-relations.json';assert not p107.exists();p107.write_bytes((json.dumps(r107,ensure_ascii=False,indent=2)+'\n').encode());print('REL107',[(q['actor'],q['all_faces_rotation_invariant'],[(f['type'],f['coaxial_rotation_invariant_face']) for f in q['faces']]) for q in relations107],r107['operation_seconds'],r107['process_cpu_seconds'],hashlib.sha256(p107.read_bytes()).hexdigest(),flush=True)

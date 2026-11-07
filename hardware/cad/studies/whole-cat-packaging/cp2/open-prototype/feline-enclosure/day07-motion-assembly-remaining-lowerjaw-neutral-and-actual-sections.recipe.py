import json,time,hashlib,os
t218=time.monotonic();c218=time.process_time();jaw218=kit199['LowerJaw'];targets218={**context210,'CURRENT_WHOLE_PERMANENT_FRAME':newframe209,'CURRENT_D5_REMOVABLE_CAPTURE':up202,'CURRENT_FRG_REMOVABLE_UPPER':newup209};rows218=[];bb218=0;first218=None
for n,s in targets218.items():
    if n=='Ref_Material_P0_SideRight22_0_0' or n.startswith('NEW_CLAMP3_Hardware:'):continue
    lo=bbox_lower_bound(jaw218.BoundBox,bounds126[n] if n in bounds126 else s.BoundBox)
    if lo>=1.25-1e-7:bb218+=1;continue
    ga,ww,_=jaw218.distToShape(s);row=dict(actor=n,source_valid=s.isValid(),gap_mm=ga,required_mm=1.25,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='ONLY_MISSING_LOWERJAW_NEUTRAL_SEPARATED125' if ga>=1.25-1e-7 and s.isValid() else 'ONLY_MISSING_LOWERJAW_NEUTRAL_HOLD')
    if ga<1e-7:
        co=jaw218.common(s);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
    rows218.append(row)
    if row['status']!='ONLY_MISSING_LOWERJAW_NEUTRAL_SEPARATED125':first218=row;break
parts218={'CURRENT_FINAL_D5_CASE':case216,'PORTSIDE_INTERMEDIATE_CASE':shift216,'TOP_INTERMEDIATE_CASE':upcase216,'CURRENT_INTEGRAL_LOWER_PRESSURE':lower216,'CURRENT_PERMANENT_TOP_KEEPER_LIPS':lip216,'CURRENT_PERMANENT_FRAME':newframe209}
sections218=[]
for view,vs in [('XZ_PORTSIDE_ENTRY',[A.Vector(32,-23.375,38),A.Vector(75,-23.375,38),A.Vector(75,-23.375,57),A.Vector(32,-23.375,57)]),('YZ_TOP_ENTRY',[A.Vector(45,-35,40),A.Vector(45,3,40),A.Vector(45,3,57),A.Vector(45,-35,57)])]:
    plane=Part.Face(Part.makePolygon(vs+[vs[0]]))
    for n,s in parts218.items():
        sec=s.section(plane);lines=[]
        for e in sec.Edges:
            pts=e.discretize(Deflection=.04);lines.append([[q.x,q.z] if view.startswith('XZ') else [q.y,q.z] for q in pts])
        sections218.append(dict(view=view,actor=n,curves=lines,edges=len(sec.Edges)))
bodybb218=BodyOuter31.BoundBox;boxvol218=bodybb218.XLength*bodybb218.YLength*bodybb218.ZLength
p218=OUT/'day07-current-caseback-neutral-missing-jaw-and-installation-sections.json';assert not p218.exists()
r218=dict(id=p218.stem,status='ONLY_MISSING_LOWERJAW_NEUTRAL_SCOPE_RECEIVED' if not first218 else 'ONLY_MISSING_LOWERJAW_NEUTRAL_HOLD',lowerjaw_new_neutral_rows=rows218,fullbounds_separated=bb218,first_neutral_falsifier=first218,reused_matched_native_P0_bearing='Actualreceived65mm2/0common fromp199, notrerun',unchanged_own_M3_relative_fit='ALL8stackparts sameproperrigidtranslationdx-38.25 sourcep199; actual4metal neutral125/10neighbors andsamebores reused, no newmetalpart/cut/deletion.',sections=sections218,source_body_is_axisaligned_box=dict(face_count=len(BodyOuter31.Faces),vertex_count=len(BodyOuter31.Vertexes),actual_volume_mm3=BodyOuter31.Volume,bounding_box_volume_mm3=boxvol218,box_equality=abs(BodyOuter31.Volume-boxvol218)<1e-5 and len(BodyOuter31.Faces)==6 and len(BodyOuter31.Vertexes)==8),whole_D5_initial_installation_still_HOLD=r216['first_installation_falsifier'],no_new_strategy_built=True,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t218,process_cpu_seconds=time.process_time()-c218,pid=os.getpid(),session_id=46493);p218.write_bytes((json.dumps(r218,indent=2)+'\n').encode());print('MISSING_NEUTRAL_JAW_AND_VIEW',r218['status'],'actual',len(rows218),'first',first218,'edges',sum(q['edges'] for q in sections218),'bodybox',r218['source_body_is_axisaligned_box'],'wall',r218['operation_seconds'],'CPU',r218['process_cpu_seconds'],hashlib.sha256(p218.read_bytes()).hexdigest(),flush=True)

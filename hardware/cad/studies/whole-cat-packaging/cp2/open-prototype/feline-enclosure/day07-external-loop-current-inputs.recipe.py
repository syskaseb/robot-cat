import json,hashlib,os
p109=OUT/'day07-SOURCE-external-loop-current-neighborhood-inputs.json';assert not p109.exists()
roi109=Part.makeBox(145,110,140,A.Vector(-165,-5,-35));bb109=roi109.BoundBox;near109=[]
for n,s in fixed106.items():
    if bbox_lower_bound(bb109,s.BoundBox)>0:continue
    near109.append(dict(actor=n,bounds_mm=saved_bounds(s),kind='current_fixed_actor_or_capacity_unclassified_not_contact'))
for n,s in restMotion.items():
    if bbox_lower_bound(bb109,s.BoundBox)>0:continue
    near109.append(dict(actor=n,bounds_mm=saved_bounds(s),owner=owners106[n],kind='current_moving_source_neutral_only'))
d109=dict(id=p109.stem,roi_bounds_mm=saved_bounds(roi109),rows=near109,source='Alreadycurrentfixed106includescompleteBankBed+passiveguideoverride; rest108 actualownerbounds; no materialscan/contactproof/newbodyplacement.',source_Knee36_port_frames=p106.name,all_A_U_fit_slack=None)
p109.write_bytes((json.dumps(d109,indent=2)+'\n').encode());print('NEIGHBOR109_SAVED',len(near109),hashlib.sha256(p109.read_bytes()).hexdigest(),flush=True)

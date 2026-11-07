import time,json,hashlib,os
t232=time.monotonic();c232=time.process_time();roi232=[[-137.45,-1.75,-38.05],[-128.05,78.95,49.25]];box232=box153(roi232);parts232=[];sections232=[]
for n,s in context230.items():
    if bbox_lower_bound(box232.BoundBox,s.BoundBox)>1e-7:continue
    parts232.append(dict(actor=n,bounds_mm=saved_bounds(s),source_function='CURRENT_RETAINED_REAL_SOURCE_OR_TYPED_STOCK_NOT_FREE_SPACE',current1292_identity=n in Current35 and s.isSame(Current35[n])))
for xx in [-135.5,-130.]:
    pl=Part.makePlane(95,105,A.Vector(xx,-10,-45),A.Vector(1,0,0),A.Vector(0,1,0))
    for q in parts232:
        n=q['actor'];s=context230[n]
        if not (n.startswith('Ref_Material_') or n in ['Underdeck:RestoredBank','PROPOSED_SHARED_CURRENT_DISJOINT_FIXED_FRAME']):continue
        if s.BoundBox.XMin>xx or s.BoundBox.XMax<xx:continue
        sec=s.section(pl);lines=[]
        for e in sec.Edges:lines.append([[p.y,p.z] for p in e.discretize(Deflection=.15)])
        if lines:sections232.append(dict(X_mm=xx,actor=n,curves_yz=lines))
p232=OUT/'day07-WHOLE9-before-S0-current-vertical-entry-space-read.json';assert not p232.exists();r232=dict(id=p232.stem,status='ACTUAL_CURRENT_LEFT_ENTRY_P0_S0_AND_FLOOR_NEIGHBOR_READ_NOT_EMPTYSPACE_PROOF',roi_mm=roi232,parts=parts232,actual_YZ_sections=sections232,proposed_entry_start='NorthY77 boundary of1697 accountingfield; wholepacketdescendsBEFOREforeXYturn. Existingfieldnotterminal/no mandatory37.75wire credit.',BodyOuter_actual_available=True,purchasedparts_not_moved_or_cut=True,no_old_accepted_pairs_repeated=True,operation_seconds=time.monotonic()-t232,process_cpu_seconds=time.process_time()-c232,pid=os.getpid(),session_id=46493);p232.write_bytes((json.dumps(r232,indent=2)+'\n').encode());print('ENTRY232_REAL_READ',len(parts232),len(sections232),[q['actor'] for q in parts232],r232['operation_seconds'],r232['process_cpu_seconds'],'OWNER93_IDLE',os.getpid(),flush=True)

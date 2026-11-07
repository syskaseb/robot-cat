import time,json,hashlib
inter161=dict(id='day07-SOURCE-sidebay-adaptive-bounds-interruption-receipt',status='EXECUTION_BROADPHASE_COST_REPAIRED_SAME_GEOMETRY_NO_DESIGN_FAILURE',stage='KeyboardInterruptatbbox_lower_bound during repeatedcurrentBoundBoxlookup BEFOREanynewdistance rows',new_cells_in_RAM=len(cells161),new_exact_distance_rows_before_interrupt=len(rows161),partial_candidate_keys_discarded=len(tasks161),same_family_and_source_geometry=True,no_C0_C1_design_counter_increment=True,wall_to_recovery_snapshot_seconds=time.monotonic()-st161,process_CPU_to_recovery_snapshot_seconds=time.process_time()-cp161,repair='Useexistingstablecachedcurrentbounds126 andnumericarraybboxlower for SAMEcell/sourcegeometry; notnewsolver/variant/sourceimport oroldacceptedpairreplay.',interruption_trace='KeyboardInterrupt robot-cat74-sidebay-adaptive-E55-E65-cover.py line12 bbox_lower_bound')
assert len(rows161)==0
pin161=OUT/(inter161['id']+'.json');assert not pin161.exists();pin161.write_bytes((json.dumps(inter161,indent=2)+'\n').encode());print('SAME_FAMILY_BOUNDS_REPAIR_SAVED',inter161['wall_to_recovery_snapshot_seconds'],inter161['process_CPU_to_recovery_snapshot_seconds'],flush=True)
resume161_t=time.monotonic();resume161_c=time.process_time();keys161=list(context160);cached161=[]
for k in keys161:
 bb=bounds126[k] if k in bounds126 else context160[k].BoundBox;cached161.append([[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]])
arr161=np.array(cached161);tasks161=[];minbbox161=1e9
for row in bounds161:
 lo,hi=np.array(row['bounds_mm']);d=np.maximum(0,np.maximum(lo-arr161[:,1],arr161[:,0]-hi));lower=np.linalg.norm(d,axis=1);ids=np.nonzero(lower<1.25)[0];tasks161.extend((row['name'],keys161[i]) for i in ids);positive=lower[lower>=1.25]
 if len(positive):minbbox161=min(minbbox161,float(positive.min()))
print('SAME_FAMILY_CANDIDATES',len(tasks161),'cachedseconds',time.monotonic()-resume161_t,flush=True)
src=(Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat74-sidebay-adaptive-E55-E65-cover.py')).read_text();tail=src[src.index('lookup161=dict(cells161)'):];tail=tail.replace('time.monotonic()-st161','time.monotonic()-resume161_t').replace('time.process_time()-cp161','time.process_time()-resume161_c');exec(compile(tail,'SAMEadaptivefamilycachedbounds_no_replayed_receiveddistances','exec'))

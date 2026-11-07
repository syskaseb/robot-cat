import json,time,hashlib,os
t191=time.monotonic();c191=time.process_time();assert first190
piece191=[]
for n,target in [('ONLY_NEW_POSITIVE_PRIMARY',newdelta184),('RETAINED_SOURCE_PIER_AFTER_CURRENT_CHANNELS',newfoot181),('RETAINED_SOURCE_BANKLEDGE3',Current35['CurrentFoundation:BankLedge:3'])]:
    co=lastmouth190.common(target);piece191.append(dict(source_component=n,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,partition_not_summed_because_members_may_overlap=True))
plane191=Part.makePlane(65,55,A.Vector(50,-45,48.5),A.Vector(0,0,1),A.Vector(1,0,0));sections191=[]
for n,s in [('actual_new_primary',base181),('actual_new_upper',up181),('first_proposed_free_jacket',lastmouth190),('retained_source_pier',newfoot181)]:
    sect=s.section(plane191);curves=[[[v.x,v.y] for v in e.discretize(Deflection=.08)] for e in sect.Edges];sections191.append(dict(actor=n,curves_xy=curves))
p191=OUT/'day07-SOURCE-fore-mouth-first-falsifier-material-causality.json';assert not p191.exists();r191=dict(id=p191.stem,status='FIRST_FORE_MOUTH_ALLOCATED_JACKET_PRINT_FALSIFIER_CAUSAL_SOURCE_READ_ONLY',source_firstgate=p190.name,source_firstgate_sha256=hashlib.sha256(p190.read_bytes()).hexdigest(),first_falsifier=first190,material_cause_parts=piece191,sections_Z48p5=sections191,no_newprint_or_next_family_built=True,not_actualdeliveredwirecontact_or_allescapeimpossible=True,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t191,process_cpu_seconds=time.process_time()-c191,pid=os.getpid(),session_id=46493);p191.write_bytes((json.dumps(r191,indent=2)+'\n').encode());print('FORE_MOUTH_CAUSE',piece191,r191['operation_seconds'],r191['process_cpu_seconds'],hashlib.sha256(p191.read_bytes()).hexdigest(),'OWNER82_IDLE',os.getpid(),flush=True)

import math,time,json,hashlib,zipfile,os
t93=time.monotonic();cpu93=time.process_time();proposal93=json.loads((OUT/'day07-SOURCE-slot-bearing-retention-whole-proposal.json').read_bytes())
def rounded93(u,y0,y1,n0,n1,r):
    assert min(y1-y0,n1-n0)>=2*r-1e-8
    def v(y,n):return A.Vector(u,y,n)
    edges=[]
    def line(a,b):edges.append(Part.makeLine(v(*a),v(*b)))
    def arc(a,m,b):edges.append(Part.Arc(v(*a),v(*m),v(*b)).toShape())
    h=r/math.sqrt(2)
    line((y0+r,n0),(y1-r,n0));arc((y1-r,n0),(y1-r+h,n0+r-h),(y1,n0+r))
    line((y1,n0+r),(y1,n1-r));arc((y1,n1-r),(y1-r+h,n1-r+h),(y1-r,n1))
    line((y1-r,n1),(y0+r,n1));arc((y0+r,n1),(y0+r-h,n1-r+h),(y0,n1-r))
    line((y0,n1-r),(y0,n0+r));arc((y0,n0+r),(y0+r-h,n0+r-h),(y0+r,n0))
    w=Part.Wire(edges);assert w.isValid() and w.isClosed();return Part.Face(w)
def band93(u,y0,y1,n0,n1,t):
    outer=rounded93(u-1.25,y0-t,y1+t,n0-t,n1+t,3+t);inner=rounded93(u-1.25,y0,y1,n0,n1,3)
    s=outer.cut(inner).extrude(A.Vector(2.5,0,0));assert s.isValid() and len(s.Solids)==1;return s
loops93={};heads93={};pulls93={};units93=[]
for i,d in enumerate(proposal93['structural145']):
    s=band93(d['u'],d['v_leg']+.6,d['v_outer']-.6,-1.5,10.6,1.2);n='145_'+str(i);loops93[n]=s
    if i==0:
        heads93[n]=Part.makeBox(5.3,5,5,A.Vector(d['u']-2.65,d['v_outer']+.6,1));pulls93[n]=Part.makeBox(7,7,25,A.Vector(d['u']-3.5,d['v_outer']+.6,6))
    else:
        heads93[n]=Part.makeBox(5.3,5,5,A.Vector(d['u']-2.65,6,11.8));pulls93[n]=Part.makeBox(7,7,25,A.Vector(d['u']-3.5,5,16.8))
    units93.append(dict(name=n,sku='111-02370',L=145,loop_mm=s.Volume/(2.5*1.2),pull_head_once_mm=25,required_mm=s.Volume/(2.5*1.2)+25,uncut_tail_mm=145-s.Volume/(2.5*1.2),inner_corner_R_mm=3,plastic_R_assumption=True))
for i,u in enumerate([-38.5,38.5]):
    s=band93(u,3.05,16,1.75,10.6,1);n='100_'+str(i);loops93[n]=s;heads93[n]=Part.makeBox(5.3,5,5,A.Vector(u-2.65,6,11.6));pulls93[n]=Part.makeBox(7,7,25,A.Vector(u-3.5,5,16.6));units93.append(dict(name=n,sku='111-01910',L=100,loop_mm=s.Volume/2.5,pull_head_once_mm=25,required_mm=s.Volume/2.5+25,uncut_tail_mm=100-s.Volume/2.5,inner_corner_R_mm=3,plastic_R_assumption=True))
profiles93={}
for n,s in wirelocal86.items():
    q=s.copy();q.translate(A.Vector(0,8.5,0));assert q.isValid() and abs(q.Volume-s.Volume)<1e-6;profiles93[n]=q
own93=[];stop93=False
for n,s in list(loops93.items())[:2]:
    co=s.common(linklocal93);gap,w,_=s.distToShape(linklocal93);row=dict(loop=n,other='actual_Link117',loop_valid=s.isValid(),source_valid=linklocal93.isValid(),common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,common_area_mm2=co.Area if co.isValid() else None,gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
    row['status']='OWN_BAND_LINK_ZERO_PENETRATION_BEARING_SCOPED' if co.isValid() and co.Volume<1e-5 and gap<1e-6 else 'ACTUAL_NATIVE_LINK_SLOT_RETURN_HOLD_NO_KEEPER';own93.append(row);print('SLOT93_OWN',row,flush=True)
    if row['status'].endswith('NO_KEEPER'):stop93=True;break
profilefit93=[]
if not stop93:
    for n,s in loops93.items():
        for k,q in profiles93.items():
            co=s.common(q);gap,w,_=s.distToShape(q);r=dict(loop=n,profile=k,common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None,gap_mm=gap,status='OWN_FULL_PROFILE_NO_MATERIAL_OVERLAP' if co.isValid() and co.Volume<1e-5 else 'OWN_PROFILE_ALLOCATION_HOLD_NOT_ACTUALWIRECONTACT');profilefit93.append(r)
            if r['status']!='OWN_FULL_PROFILE_NO_MATERIAL_OVERLAP':stop93=True;break
        if stop93:break
bay93=[];rows93=[];tasks93=[];functional93={**{'LOOP:'+n:s for n,s in loops93.items()},**{'HEAD:'+n:s for n,s in heads93.items()},**{'PULL:'+n:s for n,s in pulls93.items()},**{'FULL_PROFILE:'+n:s for n,s in profiles93.items()}}
if not stop93:
    for n,s in functional93.items():
        for k,q in covers90.items():
            low=bbox_lower_bound(s.BoundBox,q.BoundBox)
            if low>=1.25:r=dict(target=n,cover=k,lower_mm=low,status='CONTINUOUS_COVER_SEPARATED125_BY_BOUNDS')
            else:
                gap,w,_=s.distToShape(q);r=dict(target=n,cover=k,gap_mm=gap,status='CONTINUOUS_COVER_SEPARATED125' if gap>=1.25-1e-7 else 'CONTINUOUS_COVER_HOLD_NOT_CONTACT')
            bay93.append(r)
    world93={n:local83(s.copy()) for n,s in functional93.items()}
    for n,s in world93.items():
        for k,q in ctx83.items():
            if k==stage_link81 or bbox_lower_bound(s.BoundBox,q.BoundBox)>=1.25:continue
            tasks93.append((n,k))
    tasks93.sort(key=lambda z:(0 if z[0].startswith('LOOP:') else 1,z[0],z[1]))
    for n,k in tasks93:
        s=world93[n];q=ctx83[k];r=dict(target=n,other=k,source_valid=q.isValid())
        if q.isValid():
            gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='ACTUAL_CHANGED_FUNCTIONAL_SEPARATED125' if gap>=1.25-1e-7 else 'ACTUAL_CHANGED_FUNCTIONAL_HOLD')
            if gap<1e-7:
                co=s.common(q);r.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        rows93.append(r);print('SLOT93_FOREIGN',r,flush=True)
        if r['status']!='ACTUAL_CHANGED_FUNCTIONAL_SEPARATED125' or time.monotonic()-t93>20:break
ar93=OUT/'day07-SOURCE-slot-retention-functional-first-gate.breps.zip';assert not ar93.exists();ge93=[]
items93=[('LOCAL:actual_Link117',linklocal93),('LOCAL:actual_native_window',winlocal92)]+[('LOCAL:'+n,s) for n,s in functional93.items()]
with zipfile.ZipFile(ar93,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(items93):
        assert s.isValid();raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);ge93.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge93,scope='New whole slot clamp / sidecar functional capacity; local frame only. No new keeper/fork material or current overlay.'),indent=2)+'\n').encode())
r93=dict(id='day07-SOURCE-slot-retention-functional-first-gate',proposal='day07-SOURCE-slot-bearing-retention-whole-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-slot-bearing-retention-whole-proposal.json').read_bytes()).hexdigest(),status='FUNCTIONAL_SLOT_RETENTION_FIRST_FALSIFIER_HOLD' if stop93 or any(r['status']!='ACTUAL_CHANGED_FUNCTIONAL_SEPARATED125' for r in rows93) else 'FUNCTIONAL_SLOT_RETENTION_RECEIVED_SCOPE_TAIL_TRANSPORT_OPEN',source_link_valid=linklocal93.isValid(),source_rigid_volume_preserved=abs(linklocal93.Volume-link81.Volume)<1e-6,source_link_volume_mm3=linklocal93.Volume,own_link_rows=own93,full_profile_fit_rows=profilefit93,continuous_bay_rows=bay93,continuous_bay_open=[r for r in bay93 if r['status'].startswith('CONTINUOUS_COVER_HOLD')],all4_units=units93,all4_source_lengths_fit=all(d['required_mm']<=d['L'] for d in units93),changed_foreign_rows=rows93,cursor=len(rows93),total=len(tasks93),unreceived=len(tasks93)-len(rows93),fulltail_connected_transport_and_keeper='NOT_RUN_AFTER_FIRST_FALSIFIER' if stop93 else 'OPEN_NO_INSTALL_ACCEPTANCE',new_material_built=False,current1292_effective1311_rest108_unchanged=True,new_all3_original_donor_transport_A_U_fit_slack=None,geometry=ge93,archive=ar93.name,archive_sha256=hashlib.sha256(ar93.read_bytes()).hexdigest(),operation_seconds=time.monotonic()-t93,process_cpu_seconds=time.process_time()-cpu93,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p93=OUT/'day07-SOURCE-slot-retention-functional-first-gate.json';assert not p93.exists();p93.write_bytes((json.dumps(r93,ensure_ascii=False,indent=2)+'\n').encode());print('SLOT93_FINAL',r93['status'],[(d['name'],d['required_mm'],d['uncut_tail_mm']) for d in units93],len(profilefit93),len(rows93),len(tasks93),r93['operation_seconds'],r93['process_cpu_seconds'],hashlib.sha256(p93.read_bytes()).hexdigest(),flush=True)

import time,json,hashlib,zipfile,math
t95=time.monotonic();cpu95=time.process_time();transport95={};transportfix95=[]
for n,pts in paths94.items():
    pieces=[]
    for a,b in zip(pts,pts[1:]):
        va=A.Vector(*a);v=A.Vector(*b)-va;pieces.append(Part.makeCylinder(2.0,v.Length,va,v.normalize()))
    for p in pts[1:-1]:pieces.append(Part.makeSphere(4.65,A.Vector(*p)))
    s=Part.makeCompound(pieces);assert s.isValid();transport95[n]=s;transportfix95.append(dict(name=n,straight_cylinder_radius_mm=2.0,required_corner_radius_mm=math.hypot(1.65,1),full3p3x2_capacity_contained=True,old_radius1p75_does_not_enclose_declared_rectangle=True,meaning='Conservativecoverinputcorrection, notdesignoffset oractualtailreroute. Allpoints/sourcewidth/thickness/loop/stockunchanged. Old5transportclearancesnotreused; exactchangedcapacitypairsreceivedbelow.'))
world95={n:local83(s.copy()) for n,s in transport95.items()};tasks95=[('TAIL_TRANSPORT:'+n,k) for n,s in world95.items() for k,q in ctx83.items() if k!=stage_link81 and bbox_lower_bound(s.BoundBox,q.BoundBox)<1.25]+tasks94[len(rows94):];rows95=[]
for n,k in tasks95:
    s=world95[n.split(':',1)[1]] if n.startswith('TAIL_TRANSPORT:') else world94[n];q=ctx83[k];r=dict(target=n,other=k,source_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='FULL_CURRENT_STOCK_SEPARATED125' if gap>=1.25-1e-7 else 'FULL_CURRENT_STOCK_REGION_HOLD_NOT_ALL_HANDLAY')
        if gap<1e-7:
            co=s.common(q);r.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows95.append(r);print('SLOT95',r,flush=True)
    if r['status']!='FULL_CURRENT_STOCK_SEPARATED125' or time.monotonic()-t95>15:break
profile95=[]
if len(rows95)==len(tasks95) and all(r['status']=='FULL_CURRENT_STOCK_SEPARATED125' for r in rows95):
    for n,s in loops94.items():
        for k,q in profiles93.items():
            co=s.common(q);assert co.isValid();profile95.append(dict(loop=n,profile=k,allocated_common_mm3=co.Volume,status='FULL_CHANGED_LOOP_PROFILE_NO_OVERLAP' if co.Volume<1e-5 else 'OWN_SOURCE_PROFILE_CAPACITY_HOLD'))
bay95=[]
for n,s in transport95.items():
    for k,q in covers90.items():
        low=bbox_lower_bound(s.BoundBox,q.BoundBox)
        if low>=1.25:r=dict(target=n,cover=k,lower_mm=low,status='CONTINUOUS_COVER_SEPARATED125_BY_BOUNDS')
        else:
            gap,_,_=s.distToShape(q);r=dict(target=n,cover=k,gap_mm=gap,status='CONTINUOUS_COVER_SEPARATED125' if gap>=1.25-1e-7 else 'CONSERVATIVE_TRANSPORT_COVER_HOLD_NOT_CONTACT')
        bay95.append(r)
ar95=OUT/'day07-SOURCE-slot-full-stock-completion.breps.zip';assert not ar95.exists();ge95=[]
with zipfile.ZipFile(ar95,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(transport95.items()):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge95.append(dict(name='LOCAL:TAIL_TRANSPORT:'+n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge95,scope='Onlychangedfull3.3x2transportcovers, no print/material/currentoverlay'),indent=2)+'\n').encode())
reused95=[r for r in rows94 if not r['target'].startswith('TAIL_TRANSPORT')];ok95=len(rows95)==len(tasks95) and all(r['status']=='FULL_CURRENT_STOCK_SEPARATED125' for r in rows95) and len(profile95)==12 and all(r['allocated_common_mm3']<1e-5 for r in profile95) and all(not r['status'].startswith('CONSERVATIVE') for r in bay95)
r95=dict(id='day07-SOURCE-slot-full-stock-completion',status='WHOLE_FUNCTIONAL_STOCK_SCOPE_RECEIVED_MATERIAL_NOT_BUILT' if ok95 else 'WHOLE_FUNCTIONAL_STOCK_OPEN_NO_MATERIAL',raw94_receipt='day07-SOURCE-slot-whole-tail-bearing-gate.json',raw94_count_disposition='Raw94statusRECEIVED_SCOPEdidNOTmeanall13received:9of13+4unreceived. Belowreceivesonlymissing4pluschangedtransportcoverinputs, no unchangedpairreplay.',transport_cover_correction=transportfix95,rows=rows95,cursor=len(rows95),total=len(tasks95),unreceived=len(tasks95)-len(rows95),reused_unchanged_rows=reused95,complete_matrix_count=len(rows95)+len(reused95),profile_rows=profile95,continuous_changed_transport=bay95,sourceunit_budgets=r94['all4_units'],tailtransport_budgets=r94['tail_connected_transport'],actual_source_bearing=r94['actual_bearing'],all_material_requires_actual_member_coverage=True,new_material_built=False,new_all3_original_donor_transport_A_U_fit_slack=None,archive=ar95.name,archive_sha256=hashlib.sha256(ar95.read_bytes()).hexdigest(),geometry=ge95,operation_seconds=time.monotonic()-t95,process_cpu_seconds=time.process_time()-cpu95,selected=False,N01_complete=False)
p95=OUT/'day07-SOURCE-slot-full-stock-completion.json';assert not p95.exists();p95.write_bytes((json.dumps(r95,ensure_ascii=False,indent=2)+'\n').encode());print('SLOT95_FINAL',r95['status'],len(rows95),len(tasks95),len(reused95),len(profile95),[r for r in bay95 if r['status'].startswith('CONSERVATIVE')],r95['operation_seconds'],r95['process_cpu_seconds'],hashlib.sha256(p95.read_bytes()).hexdigest(),flush=True)

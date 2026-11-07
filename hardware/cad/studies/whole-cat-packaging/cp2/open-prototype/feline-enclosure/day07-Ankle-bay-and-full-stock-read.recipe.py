import time,json,hashlib,zipfile,os,math
t90=time.monotonic();cpu90=time.process_time();footrigid90=foot88.copy();footrigid90.Placement=A.Placement(inv85)*footrigid90.Placement;assert footrigid90.isValid() and abs(footrigid90.Volume-foot88.Volume)<1e-6;bb90=footrigid90.optimalBoundingBox();p90=pivotlocal90
central90=Part.makeCylinder(12.000001,bb90.ZLength+.2,A.Vector(p90.x,p90.y,bb90.ZMin-.1),A.Vector(0,0,1));remainder90=footrigid90.cut(central90);central_actual90=footrigid90.common(central90);assert remainder90.isValid() and central_actual90.isValid();volume_lost90=footrigid90.Volume-remainder90.Volume-central_actual90.Volume
sourcecover90=central90.fuse(remainder90);uncovered90=footrigid90.cut(sourcecover90);assert sourcecover90.isValid() and uncovered90.isValid() and uncovered90.Volume<1e-5
rb90=remainder90.optimalBoundingBox();end90=math.radians(endangle88);covers90={'source_Ankle_coaxial_R12_full_normals':central90};covermeta90=[]
def trigext90(a,b,lo,hi):
    vals=[a*math.cos(q)+b*math.sin(q) for q in [lo,hi]];base=math.atan2(b,a)
    for k in range(-2,4):
        q=base+k*math.pi
        if lo<=q<=hi:vals.append(a*math.cos(q)+b*math.sin(q))
    return min(vals),max(vals)
for i in range(4):
    lo=end90*i/4;hi=end90*(i+1)/4;xx=[];yy=[]
    for x in [rb90.XMin,rb90.XMax]:
        for y in [rb90.YMin,rb90.YMax]:
            xlim=trigext90(x-p90.x,-(y-p90.y),lo,hi);ylim=trigext90(y-p90.y,x-p90.x,lo,hi);xx.extend(p90.x+q for q in xlim);yy.extend(p90.y+q for q in ylim)
    x0,x1=min(xx)-1e-5,max(xx)+1e-5;y0,y1=min(yy)-1e-5,max(yy)+1e-5;z0,z1=rb90.ZMin-1e-5,rb90.ZMax+1e-5
    name='Ankle_remainder_continuous_interval_'+str(i);covers90[name]=Part.makeBox(x1-x0,y1-y0,z1-z0,A.Vector(x0,y0,z0));covermeta90.append(dict(name=name,angle_degrees=[math.degrees(lo),math.degrees(hi)],bounds_mm=[[x0,y0,z0],[x1,y1,z1]],scope='ContinuousanalyticcornerextremaofrotatedTIGHTremainderbbox; not4sampledposes orcollisionclaim.'))
stocklocal90={};tieunits90=[]
for i,(kind,x,L,t) in enumerate([('structural145',-15,145,1.2),('structural145',15,145,1.2),('source_land100',-38.5,100,1),('donor_land100',38.5,100,1)]):
    if '145' in kind:
        slab=local83(Part.makeBox(2.5,100,10,A.Vector(x-1.25,-50,-5)));src=link81.common(slab);sl=src.copy();sl.Placement=A.Placement(inv85)*sl.Placement;assert sl.isValid();box=sl.optimalBoundingBox();y0,y1=min(-7,box.YMin),max(7,box.YMax);n0=box.ZMin
    else:y0,y1,n0=(-6.4,6.4,1.75) if x<0 else (-7,7,1.75)
    n1=10.6;outer=Part.makeBox(2.5,y1-y0+2*t,n1-n0+2*t,A.Vector(x-1.25,y0-t,n0-t));inner=Part.makeBox(2.5,y1-y0,n1-n0,A.Vector(x-1.25,y0,n0));band=outer.cut(inner);assert band.isValid();loop=band.Volume/(2.5*t);head=Part.makeBox(5.3,5,5,A.Vector(x-2.65,-2.5,10.6));pull=Part.makeBox(7,7,25,A.Vector(x-3.5,-3.5,15.6));prefix='FULL_SELECTED_TIE_'+str(i)+':'+kind
    stocklocal90[prefix+':loop']=band;stocklocal90[prefix+':head']=head;stocklocal90[prefix+':bench_pull25']=pull
    tieunits90.append(dict(name=prefix,sku='111-02370' if '145' in kind else '111-01910',full_unit_length_mm=L,width_mm=2.5,thickness_mm=t,actual_loop_capacity_length_mm=loop,correct_analytic_rectangle_length_mm=2*((y1-y0)+(n1-n0)+2*t),closure_pull_head_once_mm=25,wholeunit_required_mm=loop+25,remaining_after_loop_pull_mm=L-loop-25,full_untrimmed_tail_upper_mm=L-loop,source_length_fits=loop+25<=L,inner_n=[n0,n1],inner_y=[y0,y1],tailstack_height_included_mm=2.6,no_physicalcut_or_new_stock=True))
for name,y in [('left',-5.3),('right',2.8)]:stocklocal90['FULL4_TAILS:'+name+'_two_layer_capacity']=Part.makeBox(86,2.5,2.6,A.Vector(-43,y,8))
functional90={**{'SOURCE_PROFILE:'+n:s for n,s in wirelocal86.items()},**stocklocal90};bayrows90=[]
for n,s in functional90.items():
    for k,c in covers90.items():
        low=bbox_lower_bound(s.optimalBoundingBox(),c.optimalBoundingBox())
        if low>=1.25:r=dict(target=n,cover=k,lower_mm=low,status='CONTINUOUS_COVER_SEPARATED125_BY_BOUNDS')
        else:
            gap,w,_=s.distToShape(c);r=dict(target=n,cover=k,gap_mm=gap,status='CONTINUOUS_COVER_SEPARATED125' if gap>=1.25-1e-7 else 'CONSERVATIVE_BAY_COVER_OVERLAP_OR_CLEARANCE_OPEN_NOT_CONTACT',witnesses=[[list(a),list(b)] for a,b in w[:1]])
        bayrows90.append(r)
bayopen90=[r for r in bayrows90 if r['status'].startswith('CONSERVATIVE')];print('BAY90',len(bayrows90),len(bayopen90),bayopen90[:3],flush=True)
worldstock90={n:local83(s.copy()) for n,s in stocklocal90.items()};tasks90=[];stockrows90=[]
for n,s in worldstock90.items():
    for k,q in ctx83.items():
        if k==stage_link81 or bbox_lower_bound(s.BoundBox,q.BoundBox)>=1.25:continue
        tasks90.append((n,k))
tasks90.sort(key=lambda p:(0 if ':head' in p[0] else 1 if ':loop' in p[0] else 2,p[0],p[1]))
for n,k in tasks90:
    s=worldstock90[n];q=ctx83[k];r=dict(stock=n,other=k,valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            co90=s.common(q);r.update(common_valid=co90.isValid(),allocated_common_mm3=co90.Volume if co90.isValid() else None)
        r['status']='FULL_STOCK_NEUTRAL_SEPARATED125' if gap>=1.25-1e-7 else 'FULL_STOCK_CAPACITY_OR_HEAD_FEED_HOLD_NOT_ALL_HANDLAY_IMPOSSIBLE'
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    stockrows90.append(r);print('STOCK90',r,flush=True)
    if r['status']!='FULL_STOCK_NEUTRAL_SEPARATED125' or time.monotonic()-t90>20:break
ar90=OUT/'day07-SOURCE-Ankle-functional-bay-and-full-stock.breps.zip';assert not ar90.exists();ge90=[]
with zipfile.ZipFile(ar90,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('LOCAL:actual_Foot123',footrigid90),('LOCAL:actual_Foot_remainder',remainder90)]+[('LOCAL_COVER:'+n,s) for n,s in covers90.items()]+[('LOCAL_FUNCTIONAL:'+n,s) for n,s in functional90.items()]+[(k,ctx83[k]) for k in sorted({r['other'] for r in stockrows90})]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);b=s.optimalBoundingBox();ge90.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge90,scope='FUNCTIONALbay+whole4selectedstock BEFOREnewforkmaterial. LOCALholderframegeometrylabelled; worldneighborslabelled separately. No oldmotion/modeltests.'),indent=2)+'\n').encode())
r90=dict(id='day07-SOURCE-Ankle-functional-bay-and-full-stock',status='FUNCTIONAL_CONTINUOUS_BAY_AND_STOCK_SCOPE_RECEIVED' if not bayopen90 and len(stockrows90)==len(tasks90) and all(r['status']=='FULL_STOCK_NEUTRAL_SEPARATED125' for r in stockrows90) else 'FUNCTIONAL_BAY_OR_STOCK_ALLOCATION_OPEN_NO_FORK_MATERIAL',proposal='day07-SOURCE-Ankle-facing-open-fork-whole-proposal.json',proposal_sha256=hashlib.sha256((OUT/'day07-SOURCE-Ankle-facing-open-fork-whole-proposal.json').read_bytes()).hexdigest(),source_Foot_coaxial_radii_mm=[5.399999,10.5,12],actual_Foot_volume_mm3=footrigid90.Volume,actual_source_coverage_valid=uncovered90.isValid(),actual_source_uncovered_mm3=uncovered90.Volume,rigid_frame_source_volume_preserved=True,actual_remainder_volume_mm3=remainder90.Volume,source_volume_decomposition_error_mm3=volume_lost90,remainder_tight_bounds_mm=[[rb90.XMin,rb90.YMin,rb90.ZMin],[rb90.XMax,rb90.YMax,rb90.ZMax]],continuous_cover_intervals=covermeta90,continuous_bay_rows=bayrows90,continuous_bay_open_rows=bayopen90,continuous_bay_covers_NOT_actualcontact=True,all4_full_tie_units=tieunits90,full_tail_lifecycle='Allfull145/100uncut; L-loop includes25pull/headsegmentonce. Two2.5wideouterlanes/two1.2layers+.2gap=2.6 tailstackoncap; actualloopsinsideN10.6clampstockandcap. Headfull5at10.6..15.6andbench25feedabove. ConnectedturnR3plastic andmanualpark/cinchremainphase2prototypefit; notmanufacturerwirebendclaim.',stock_rows=stockrows90,stock_cursor=len(stockrows90),stock_total=len(tasks90),stock_unreceived=len(tasks90)-len(stockrows90),archive=ar90.name,archive_sha256=hashlib.sha256(ar90.read_bytes()).hexdigest(),geometry=ge90,new_fork_material_built=False,current1292_effective1311_rest108_unchanged=True,new_source_A_U_minimumfit_slack=None,operation_seconds=time.monotonic()-t90,process_cpu_seconds=time.process_time()-cpu90,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p90=OUT/'day07-SOURCE-Ankle-functional-bay-and-full-stock.json';assert not p90.exists();p90.write_bytes((json.dumps(r90,ensure_ascii=False,indent=2)+'\n').encode());print('BAY_STOCK_FINAL90',r90['status'],len(bayopen90),len(stockrows90),len(tasks90),[(r['sku'],r['wholeunit_required_mm']) for r in tieunits90],r90['operation_seconds'],r90['process_cpu_seconds'],hashlib.sha256(p90.read_bytes()).hexdigest(),flush=True)

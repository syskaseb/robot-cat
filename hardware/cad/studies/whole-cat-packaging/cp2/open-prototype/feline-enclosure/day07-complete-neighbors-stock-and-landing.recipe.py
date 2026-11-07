import time,json,hashlib,zipfile,os,math
t87=time.monotonic();cpu87=time.process_time();newrows87=[]
for n in pending86[len(rows86):]:
    s=ctx83[n];r=dict(other=n,valid=s.isValid())
    if s.isValid():
        gap,w,_=holder86.distToShape(s);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
        if gap<1e-7:
            c=holder86.common(s);r.update(common_valid=c.isValid(),common_mm3=c.Volume if c.isValid() else None)
        r['status']='C1_REAL_HOLDER_SEPARATED125' if gap>=1.25-1e-7 else 'C1_REAL_HOLDER_FOREIGN_HOLD'
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    newrows87.append(r);print('LADDER_MISSING_ONLY87',r,flush=True)
    if r['status']!='C1_REAL_HOLDER_SEPARATED125':break
allstatic87=rows86+newrows87;staticok87=len(allstatic87)==len(pending86) and all(r['status']=='C1_REAL_HOLDER_SEPARATED125' for r in allstatic87)
tieparts87={};ties87=[];tiegeometry87=[];stockrows87=[];stocktasks87=[];landing87=None;sourcefoot87=[lower86['foot_'+str(i)].Volume/2 for i in [0,1]]
if staticok87:
    for i,(kind,x,L,t) in enumerate([('structural145',-15,145,1.2),('structural145',15,145,1.2),('land100',-38.5,100,1),('land100',38.5,100,1)]):
        if kind=='structural145':
            slab=local83(Part.makeBox(2.5,100,10,A.Vector(x-1.25,-50,-5)));source=link81.common(slab);sl=source.transformGeometry(inv85);bb=sl.optimalBoundingBox();y0=min(-7,bb.YMin);y1=max(7,bb.YMax);z0=bb.ZMin;z1=8.
        else:y0,y1,z0,z1=-7.,7.,1.75,8.
        outer=Part.makeBox(2.5,y1-y0+2*t,z1-z0+2*t,A.Vector(x-1.25,y0-t,z0-t));inner=Part.makeBox(2.5,y1-y0,z1-z0,A.Vector(x-1.25,y0,z0));band=outer.cut(inner);assert band.isValid();loop=band.Volume/(2.5*t);required=loop+25;tailmax=L-loop;head=Part.makeBox(5.3,5,5,A.Vector(x-2.65,-2.5,8));pull=Part.makeBox(7,7,25,A.Vector(x-3.5,-3.5,13))
        prefix='SOURCE_TIE_'+str(i)+':'+kind;tieparts87[prefix+':complete_loop_capacity']=local83(band);tieparts87[prefix+':full_head_capacity']=local83(head);tieparts87[prefix+':bench_pull25_capacity']=local83(pull)
        ties87.append(dict(name=prefix,sku='111-02370' if kind=='structural145' else '111-01910',full_source_length_mm=L,width_mm=2.5,thickness_mm=t,actual_band_capacity_length_mm=loop,assembly_closure_pull_mm=25,wholeunit_required_mm=required,remaining_after_loop_and_pull_mm=L-required,untrimmed_tail_upper_including_pull_head_mm=tailmax,source_length_fits=required<=L,source_single_link_wrap_no_source_fusion=True,shape_scope='Completeconservativeplasticloopcapacitynotexactcinchedcornergeometry; actualheadbindingfullsource/projectheight100unknownphase2. Alluntrimmedtailunitsretainedinsharedstorageplan/no cut.',old111bound_superseded_if_structural=(kind=='structural145')))
    # Full4tailcapacity avoidscentralheadbudget via2outerlanes and2layers; not4rigidwirecurves.
    for side,ya in [('left',-5.3),('right',2.8)]:
        tieparts87['SOURCE_TAILS:'+side+':two_layers_capacity']=local83(Part.makeBox(86,2.5,2.6,A.Vector(-43,ya,8)))
    # Allnewstockoperands vsfullcurrentfixed+all108neutralmoving; ownholdernotincontext, linkonlyhasintentionalbandcontact.
    for n,s in tieparts87.items():
        for k,q in ctx83.items():
            if k==stage_link81 or bbox_lower_bound(s.BoundBox,q.BoundBox)>=1.25:continue
            stocktasks87.append((n,k))
    stocktasks87.sort(key=lambda p:(0 if ':full_head_capacity' in p[0] else 1 if ':complete_loop_capacity' in p[0] else 2,p[0],p[1]))
    for n,k in stocktasks87:
        s=tieparts87[n];q=ctx83[k];r=dict(stock=n,other=k,valid=q.isValid())
        if q.isValid():
            gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]])
            if gap<1e-7:
                co=q.common(s);r.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
            r['status']='FULL_TIE_STOCK_ALLOCATION_SEPARATED125' if gap>=1.25-1e-7 else 'TIE_STOCK_FEED_HEAD_OR_TAIL_ALLOCATION_HOLD_NOT_ALL_HANDLAY_IMPOSSIBLE'
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        stockrows87.append(r);print('SOURCE_STOCK87',r,flush=True)
        if r['status']!='FULL_TIE_STOCK_ALLOCATION_SEPARATED125' or time.monotonic()-t87>18:break
    stockok87=len(stockrows87)==len(stocktasks87) and all(r['status']=='FULL_TIE_STOCK_ALLOCATION_SEPARATED125' for r in stockrows87) and all(r['source_length_fits'] for r in ties87)
    if stockok87:
        bank87=effective62['CurrentFoundation:BankBedCurrent:1'];roi87=Part.makeBox(9,9,.5,A.Vector(-54.5,69.5,52));coupon87=bank87.common(roi87);bottomfaces=[f for f in coupon87.Faces if type(f.Surface).__name__=='Plane' and f.normalAt(0,0).z<-.999];surface87=sum(f.Area for f in bottomfaces);point=A.Vector(-50,74,52);landing87=dict(actual_actor='CurrentFoundation:BankBedCurrent:1',current_pin='bf0311c029d0caa23b28387114a5b8f0621cfd0c79ec72a25074733e5c80ff99',roi=[[ -54.5,69.5,52],[-45.5,78.5,52.5]],coupon_valid=coupon87.isValid(),actual_contact_material_volume_mm3=coupon87.Volume,actual_underside_face_area_mm2=surface87,point_inside_above=bank87.isInside(point+A.Vector(0,0,.05),1e-6,False),point_outside_below=not bank87.isInside(point-A.Vector(0,0,.05),1e-6,False),newrootbuilt=False,scope='ActualmaterialREADonly, notwhole9wirelandingroot/regionassemblyPASS. No oldBankBedsourceancestor/rootreplay.');tieparts87['SOURCE:actual_BankBed_underside_coupon']=coupon87
else:stockok87=False
ar87=OUT/'day07-SOURCE-open-ladder-C1-stock-and-missing-neighbors.breps.zip';assert not ar87.exists();ge87=[]
with zipfile.ZipFile(ar87,'w',zipfile.ZIP_DEFLATED) as z:
    items=list(tieparts87.items())+[(k,ctx83[k]) for k in sorted({r['other'] for r in newrows87+stockrows87})]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);b=s.optimalBoundingBox();ge87.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge87,scope='SAMEopenladderC1: only3missingstaticneighbors+4fullselectedtiecapacity/heads/feed/tails andconditionalbodyrootREAD. No newpose/oldtests.'),indent=2)+'\n').encode())
r87=dict(id='day07-SOURCE-open-ladder-C1-full-static-and-selected-stock',status='C1_HOLDER_STATIC_RECEIVED_SELECTED_STOCK_OR_FEED_ALLOCATION_HOLD' if staticok87 and not stockok87 else 'C1_STATIC_AND_SELECTED_STOCK_RECEIVED_BODY_ROOT_READ_RECEIVED' if staticok87 and stockok87 else 'C1_STATIC_MISSING_NEIGHBOR_HOLD',raw_material_receipt=p86.name,raw_material_sha256=hashlib.sha256(p86.read_bytes()).hexdigest(),raw_HOLD_status='Raw86HOLDincludedboundedpending3neighbors, notactualfailure; receiveONLYthese3now.',new_static_rows=newrows87,new_static_cursor=len(allstatic87),new_static_total=len(pending86),new_static_unreceived=len(pending86)-len(allstatic87),unchanged056_reused_by_subset_mm=11.999999999999922,full10_static_scoped_received=staticok87,corrected_source_conforming_foot_areas_mm2=sourcefoot87,raw_source_contact_footprints_reused_staticlist_was_nominal_square_metric=True,feet_metric_scope='ActualcurrentconformingextrusionsVolume/2 gives15.668353/16; rawplaneintersection15.666835 isdifferentBReptrimread, notmissingroot. Preservebothrecords, no rootgeometryrerun/move/strengthclaim.',tie_units=ties87,tie_source145_centreline_formula_correction='UseactualbandcapacityVolume/(width*thickness); old111.054757 conditionalbound countedthicknessoffsetonceinsteadtwice. No sourceunitshrink; oldrawkept. Both145sourcefitmustuseactualcurrentpersectionwidth.',full_stock_rows=stockrows87,stock_cursor=len(stockrows87),stock_total=len(stocktasks87),stock_unreceived=len(stocktasks87)-len(stockrows87),stock_scope_ok=stockok87,full_stock_tail_lifecycle='Full145/100keptuncut; retainedtailupper=L-loop includes25pull/headsegment (notaddedtwice). 4fullplasticprofiles in2outerlanesx2layers, R3tieparkingdesignassumption(noncopperwire) and2selectedloopcontact mustbeassembledbeforecovers. Tailconnectedtransport/headturn/holdnotprovenbyvolumecapacityalone; phase2fitexplicit.',bodylanding_actual_read=landing87,archive=ar87.name,archive_sha256=hashlib.sha256(ar87.read_bytes()).hexdigest(),geometry=ge87,new_source_current_A_U_fit_slack=None,all9_whole_source_lengths_still_unreceived=True,current1292_effective1311_rest108_unchanged=True,changed36_motion='NOT_RUNuntilsourceholderretentionstockaccessaccepted',selected=False,N01_complete=False,operation_seconds=time.monotonic()-t87,process_cpu_seconds=time.process_time()-cpu87,pid=os.getpid(),session_id=46493)
p87=OUT/'day07-SOURCE-open-ladder-C1-full-static-and-selected-stock.json';assert not p87.exists();p87.write_bytes((json.dumps(r87,ensure_ascii=False,indent=2)+'\n').encode());print('SOURCE_COMPLETION87',r87['status'],len(allstatic87),len(pending86),len(stockrows87),len(stocktasks87),[(r['name'],r['wholeunit_required_mm']) for r in ties87],landing87,r87['operation_seconds'],r87['process_cpu_seconds'],hashlib.sha256(p87.read_bytes()).hexdigest(),flush=True)

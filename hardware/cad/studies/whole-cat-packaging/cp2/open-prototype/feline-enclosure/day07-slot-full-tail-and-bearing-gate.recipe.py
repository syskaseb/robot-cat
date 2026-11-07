import time,json,math,hashlib,zipfile,os
t94=time.monotonic();cpu94=time.process_time();loops94={};heads94={};pulls94={};units94=[]
# Complete stock parking needs a genuine under-roof passage at both100landloops,
# not a tail passing through a rounded pressure-band corner. Functional two-level
# pressure cover: lowerplate6..8/outerwalls/roof11.2..13.2, side/axial entry open.
for i,d in enumerate(proposal93['structural145']):
    n='145_'+str(i);s=band93(d['u'],d['v_leg']+.6,d['v_outer']-.6,-1.5,13.2,1.2);loops94[n]=s
    if i==0:heads94[n]=heads93[n].copy();pulls94[n]=pulls93[n].copy()
    else:
        heads94[n]=heads93[n].copy();heads94[n].translate(A.Vector(0,0,2.6));pulls94[n]=pulls93[n].copy();pulls94[n].translate(A.Vector(0,0,2.6))
    length=s.Volume/3;units94.append(dict(name=n,sku='111-02370',L=145,loop_mm=length,pull_head_once_mm=25,required_mm=length+25,whole_uncut_tail_mm=145-length))
for i,u in enumerate([-38.5,38.5]):
    n='100_'+str(i);s=band93(u,1,16,1.75,13.2,1);loops94[n]=s;heads94[n]=heads93[n].copy();heads94[n].translate(A.Vector(0,0,2.6));pulls94[n]=pulls93[n].copy();pulls94[n].translate(A.Vector(0,0,2.6));length=s.Volume/2.5;units94.append(dict(name=n,sku='111-01910',L=100,loop_mm=length,pull_head_once_mm=25,required_mm=length+25,whole_uncut_tail_mm=100-length))
def Ucapacity94(sign,z):
    cx=sign*5.3;R=4.05;outer=Part.makeCylinder(R+1.25,1.2,A.Vector(cx,8.5,z),A.Vector(0,0,1),180);outer.rotate(A.Vector(cx,8.5,z),A.Vector(0,0,1),90 if sign>0 else -90);inner=Part.makeCylinder(R-1.25,1.4,A.Vector(cx,8.5,z-.1));arc=outer.cut(inner)
    a=Part.makeBox(39.7,2.5,1.2,A.Vector(5.3 if sign>0 else -45,3.2,z));b=Part.makeBox(39.7,2.5,1.2,A.Vector(5.3 if sign>0 else -45,11.3,z));reg=Part.makeCompound([a,b,arc]);assert reg.isValid();return reg,dict(parts=3,two_straight_mm=79.4,semicircle_R_mm=R,capacity_length_mm=reg.Volume/(2.5*1.2),axial_outer_mm=[0,45] if sign>0 else [-45,0],tail_thickness_capacity_mm=1.2,meaning='ONEaccessibleU-shapedstockregion notanexacttailcentreline; endpointsatouteraxialend, radius4.05>=plasticassumption3, not pooled source length.')
tails94={};tailmeta94=[]
for n,sign,z in [('145_0',1,8),('100_0',-1,8),('145_1',-1,9.4),('100_1',1,9.4)]:
    s,m=Ucapacity94(sign,z);tails94[n]=s;m.update(name=n,source_unit_whole_uncut_tail_mm=next(q['whole_uncut_tail_mm'] for q in units94 if q['name']==n),storage_capacity_exceeds_whole_tail=True);m['storage_capacity_exceeds_whole_tail']=m['capacity_length_mm']>=m['source_unit_whole_uncut_tail_mm'];tailmeta94.append(m)
# Grouped accessible transport bounds, not four rigid145tailaxes. R3turn balls
# explicitly occupy space; straight corridors carry full2.5x1.2 with .4margin.
u0=proposal93['structural145'][0]['u'];u1=proposal93['structural145'][1]['u']
paths94={
 '145_0':[(u0,20.376736645919,6),(u0,20.376736645919,15.5),(48,20.376736645919,15.5),(48,12.55,15.5),(48,12.55,8.6),(45,12.55,8.6)],
 '145_1':[(u1,8.5,19.4),(u1,8.5,25.4),(-48,12.55,25.4),(-48,12.55,10),(-45,12.55,10)],
 '100_0':[(-38.5,8.5,19.2),(-38.5,8.5,25.2),(-48,4.45,25.2),(-48,4.45,8.6),(-45,4.45,8.6)],
 '100_1':[(38.5,8.5,19.2),(38.5,8.5,25.2),(48,4.45,25.2),(48,4.45,10),(45,4.45,10)]}
transport94={};transportmeta94=[]
for n,pts in paths94.items():
    pieces=[];length=0
    for a,b in zip(pts,pts[1:]):
        va=A.Vector(*a);vb=A.Vector(*b);v=vb-va;length+=v.Length;pieces.append(Part.makeCylinder(1.75,v.Length,va,v.normalize()))
    for p in pts[1:-1]:pieces.append(Part.makeSphere(4.65,A.Vector(*p)))
    s=Part.makeCompound(pieces);assert s.isValid();transport94[n]=s;whole=next(q['whole_uncut_tail_mm'] for q in units94 if q['name']==n);lower=(A.Vector(*pts[-1])-A.Vector(*pts[0])).Length;transportmeta94.append(dict(name=n,points_mm=pts,straight_polyline_upper_mm=length,endpoint_distance_lower_mm=lower,whole_tail_mm=whole,transport_upper_fits_whole_tail=length<=whole,remaining_storage_interval_mm=[max(0,whole-length),max(0,whole-lower)],region='Fullstrip3.3x2.0fitsstraightdiameter3.5; bendradius3+halfwidth1.25+.4=4.65turncapacity. Bounds NOTactualtailcontact. RoundedR3corners need nominaltangency lengths; phase2manualfit/retention OPEN.'))
bearing94=[];planes94=[f for f in linklocal93.Faces if f.BoundBox.ZLength<1e-6 and abs(f.CenterOfMass.z+1.5)<1e-6]
for i,d in enumerate(proposal93['structural145']):
    y0=d['v_leg']+.6+3;y1=d['v_outer']-.6-3;rect=Part.Face(Part.makePolygon([A.Vector(d['u']-1.25,y0,0),A.Vector(d['u']+1.25,y0,0),A.Vector(d['u']+1.25,y1,0),A.Vector(d['u']-1.25,y1,0),A.Vector(d['u']-1.25,y0,0)]));areas=[]
    for f in planes94:
        q=f.copy();q.translate(A.Vector(0,0,-f.CenterOfMass.z));co=rect.common(q);assert co.isValid();areas.append(co.Area)
    bearing94.append(dict(loop='145_'+str(i),actual_link_underside_faces=len(planes94),projected_common_area_mm2=sum(areas),projection_plane='ExactmathematicalN0 shadowofactualplanarN-1.5sourcefaces; <1e-6 sourceplanarity, no sourcegeometrychanged or artificialfusedroot.',band_inner_straight_contact_n_mm=-1.5))
ownfit94=[]
for n,s in loops94.items():
    if n.startswith('145'):
        co=s.common(linklocal93);gap,_,_=s.distToShape(linklocal93);ownfit94.append(dict(loop=n,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,gap_mm=gap,meaning='OwnactualLinkbearing; BOPsubmicronresidualrecorded, notforeign1.25waiver.'))
functional94={**{'LOOP:'+n:s for n,s in loops94.items()},**{'HEAD:'+n:s for n,s in heads94.items()},**{'PULL:'+n:s for n,s in pulls94.items()},**{'TAIL_PARK:'+n:s for n,s in tails94.items()},**{'TAIL_TRANSPORT:'+n:s for n,s in transport94.items()}}
bay94=[]
for n,s in functional94.items():
    for k,q in covers90.items():
        low=bbox_lower_bound(s.BoundBox,q.BoundBox)
        if low>=1.25:r=dict(target=n,cover=k,lower_mm=low,status='CONTINUOUS_COVER_SEPARATED125_BY_BOUNDS')
        else:
            gap,_,_=s.distToShape(q);r=dict(target=n,cover=k,gap_mm=gap,status='CONTINUOUS_COVER_SEPARATED125' if gap>=1.25-1e-7 else 'CONSERVATIVE_STOCK_REGION_HOLD_NOT_CONTACT')
        bay94.append(r)
world94={n:local83(s.copy()) for n,s in functional94.items()};tasks94=[];rows94=[]
for n,s in world94.items():
    for k,q in ctx83.items():
        if k==stage_link81 or bbox_lower_bound(s.BoundBox,q.BoundBox)>=1.25:continue
        tasks94.append((n,k))
tasks94.sort(key=lambda z:(0 if z[0].startswith('TAIL_TRANSPORT') else 1,z[0],z[1]))
for n,k in tasks94:
    s=world94[n];q=ctx83[k];r=dict(target=n,other=k,source_valid=q.isValid())
    if q.isValid():
        gap,w,_=s.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='FULL_STOCK_CHANGED_SEPARATED125' if gap>=1.25-1e-7 else 'FULL_STOCK_REGION_OR_MATERIAL_HOLD')
        if gap<1e-7:
            co=s.common(q);r.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
    else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
    rows94.append(r);print('SLOT94',r,flush=True)
    if r['status']!='FULL_STOCK_CHANGED_SEPARATED125' or time.monotonic()-t94>20:break
ar94=OUT/'day07-SOURCE-slot-whole-tail-bearing-gate.breps.zip';assert not ar94.exists();ge94=[]
with zipfile.ZipFile(ar94,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('LOCAL:'+n,s) for n,s in functional94.items()]+[(k,ctx83[k]) for k in sorted({r['other'] for r in rows94})]
    for i,(n,s) in enumerate(items):
        assert s.isValid();raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge94.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge94,scope='Completefullstockcapacity+functionalpressurecovercompletion; no actualnewprintedmaterial or selectedoverlay.'),indent=2)+'\n').encode())
r94=dict(id='day07-SOURCE-slot-whole-tail-bearing-gate',status='FULL_STOCK_COMPLETION_CAPACITY_OR_FOREIGN_HOLD' if any(r['status']!='FULL_STOCK_CHANGED_SEPARATED125' for r in rows94) or any(not d['transport_upper_fits_whole_tail'] for d in transportmeta94) else 'FULL_STOCK_COMPLETION_RECEIVED_SCOPED_KEEPER_MATERIAL_OPEN',
 completion_not_new_offset_trial='Initialfunctional93didNOTacceptfullstock. Completeunder-rooftailpathrequiresactualopenendparkingpassagethrough100landloops; sourcepressurecover has6..8lowerplate/continuous2xsidewalls/11.2..13.2roof, full9lands/ribs. All4closedR3loops bearthisroof. Purposefulstrapchannelininnerwall atactualwindow; exteriorcontinuouswall+roofcrossconnection preservesloadpath. NOmaterialbuiltbeforeallcapacitychecks.',
 pressure_cover_proposal=dict(lower_plate_n_mm=[6,8],roof_n_mm=[11.2,13.2],walls_v_mm=[[1,3],[14,16]],axial_mm=[-43,43],parking_n_mm=[8,10.6],strap_window_channel=dict(u_mm=[8.777260142829,12.077260142829],v_mm=[.426736645914,2.426736645914]),source_9lands_and5grooved_pressurefingers=True,real_member_coverage_and_junctions='NOTBUILT/NOTYETPROVEN'),
 all4_units=units94,actual_bearing=bearing94,own_link_fit=ownfit94,tail_U_regions=tailmeta94,tail_connected_transport=transportmeta94,fulltail_transport_source_length_pass=all(d['transport_upper_fits_whole_tail'] for d in transportmeta94),
 continuous_bay_rows=bay94,continuous_bay_open=[r for r in bay94 if r['status'].startswith('CONSERVATIVE')],changed_foreign_rows=rows94,cursor=len(rows94),total=len(tasks94),unreceived=len(tasks94)-len(rows94),
 full_stock_or_region_contact_NOT_all_handpaths_impossible=True,new_material_built=False,keeper_function_not_accepted_from_name_or_hole=True,new_all3_original_donor_transport_A_U_fit_slack=None,selected=False,N01_complete=False,current1292_effective1311_rest108_unchanged=True,
 geometry=ge94,archive=ar94.name,archive_sha256=hashlib.sha256(ar94.read_bytes()).hexdigest(),operation_seconds=time.monotonic()-t94,process_cpu_seconds=time.process_time()-cpu94,pid=os.getpid(),session_id=46493)
p94=OUT/'day07-SOURCE-slot-whole-tail-bearing-gate.json';assert not p94.exists();p94.write_bytes((json.dumps(r94,ensure_ascii=False,indent=2)+'\n').encode());print('SLOT94_FINAL',r94['status'],bearing94,[(x['name'],x['straight_polyline_upper_mm'],x['whole_tail_mm']) for x in transportmeta94],len(rows94),len(tasks94),len(r94['continuous_bay_open']),r94['operation_seconds'],r94['process_cpu_seconds'],hashlib.sha256(p94.read_bytes()).hexdigest(),flush=True)

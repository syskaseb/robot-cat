import time,json,hashlib,zipfile,math
t96=time.monotonic();cpu96=time.process_time();assert r95['status']=='WHOLE_FUNCTIONAL_STOCK_SCOPE_RECEIVED_MATERIAL_NOT_BUILT'
def tolocal96(s):
    q=s.copy();q.Placement=A.Placement(inv85)*q.Placement;assert q.isValid() and abs(q.Volume-s.Volume)<1e-5;return q
lower96={n:tolocal96(s) for n,s in conforming84.items()}
for i,u in enumerate([-15,15]):lower96['crosshead_'+str(i)]=Part.makeBox(4,17.5,1.75,A.Vector(u-2,-2,1.75))
lower96['continuous_sidecar_spine']=Part.makeBox(86,2,4.25,A.Vector(-43,13.5,1.75))
for n,s in lower86.items():
    if n.endswith('_bed'):
        q=tolocal96(s);v=q.Volume;q.translate(A.Vector(0,8.5,0));assert q.isValid() and abs(q.Volume-v)<1e-5;lower96[n]=q
upper96={}
for n,s in upper86.items():
    q=tolocal96(s);v=q.Volume;q.translate(A.Vector(0,8.5,0));assert q.isValid() and abs(q.Volume-v)<1e-5;upper96[n]=q
upper96['tail_parking_roof']=Part.makeBox(86,15,2,A.Vector(-43,1,11.2));upper96['inner_wall']=Part.makeBox(86,2,3.7,A.Vector(-43,1,7.75));upper96['outer_wall']=Part.makeBox(86,2,3.7,A.Vector(-43,14,7.75))
clips96=[]
for d in proposal93['structural145']:
    u=d['u'];inside=rounded93(u-1.65,d['v_leg']+.6,d['v_outer']-.6,-1.5,13.2,3).extrude(A.Vector(3.3,0,0));slab=Part.makeBox(3.3,80,45,A.Vector(u-1.65,-30,-10));clips96.append(slab.cut(inside))
for u in [-38.5,38.5]:
    inside=rounded93(u-1.65,1,16,1.75,13.2,3).extrude(A.Vector(3.3,0,0));slab=Part.makeBox(3.3,80,45,A.Vector(u-1.65,-30,-10));clips96.append(slab.cut(inside))
cutrecords96=[]
for group,parts in [('lower',lower96),('upper',upper96)]:
    for n,s in list(parts.items()):
        original=s.Volume
        for cutter in clips96:s=s.cut(cutter)
        assert s.isValid();parts[n]=s;cutrecords96.append(dict(group=group,member=n,raw_volume_mm3=original,intended_after_functional_band_channels_mm3=s.Volume,designed_channel_removed_mm3=original-s.Volume,nonempty=s.Volume>1e-5))
def union96(parts):
    values=list(parts.values());s=values[0]
    for q in values[1:]:s=s.fuse(q)
    return s
frame96=union96(lower96);cap96=union96(upper96);coverage96=[]
for group,parts,whole in [('lower',lower96,frame96),('upper',upper96,cap96)]:
    for n,s in parts.items():
        lost=s.cut(whole);coverage96.append(dict(group=group,member=n,source_valid=s.isValid(),missing_valid=lost.isValid(),missing_mm3=lost.Volume if lost.isValid() else None,bounds_mm=saved_bounds(s)))
junctions96=[]
edges96=[]
for i in range(2):edges96 += [('lower','actual_shape_contact_foot_'+str(i),'crosshead_'+str(i)),('lower','crosshead_'+str(i),'continuous_sidecar_spine')]
edges96 += [('lower',n,'continuous_sidecar_spine') for n in lower96 if n.endswith('_bed')]
edges96 += [('upper',n,'continuous_cap_plate') for n in upper96 if n.endswith('_finger')]
edges96 += [('upper','continuous_cap_plate','inner_wall'),('upper','continuous_cap_plate','outer_wall'),('upper','inner_wall','tail_parking_roof'),('upper','outer_wall','tail_parking_roof')]
for group,a,b in edges96:
    parts=lower96 if group=='lower' else upper96;co=parts[a].common(parts[b]);junctions96.append(dict(group=group,a=a,b=b,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,positive=co.isValid() and co.Volume>1e-5))
materialok96=frame96.isValid() and cap96.isValid() and len(frame96.Solids)==len(cap96.Solids)==1 and all(r['missing_valid'] and r['missing_mm3']<1e-5 for r in coverage96) and all(r['positive'] for r in junctions96)
holder96=Part.makeCompound([frame96,cap96]);ownstock96=[];firstown96=None
if materialok96:
    for n,s in {**{'LOOP:'+n:s for n,s in loops94.items()},**{'TAIL_PARK:'+n:s for n,s in tails94.items()},**{'TAIL_TRANSPORT:'+n:s for n,s in transport95.items()}}.items():
        co=holder96.common(s);assert co.isValid();gap,_,_=holder96.distToShape(s);r=dict(region=n,allocated_common_mm3=co.Volume,gap_mm=gap,status='OWN_FUNCTIONAL_MATERIAL_CLEAR_OR_BEARING' if co.Volume<1e-5 else 'OWN_FULL_STOCK_REGION_HOLD_NOT_PHYSICAL_TAIL_CONTACT');ownstock96.append(r)
        if co.Volume>=1e-5:firstown96=r;break
foreign96=[];tasks96=[];worldholder96=local83(holder96.copy())
if materialok96 and firstown96 is None:
    tasks96=[k for k,q in ctx83.items() if k!=stage_link81 and bbox_lower_bound(worldholder96.BoundBox,q.BoundBox)<1.25];tasks96.sort(key=lambda k:(0 if 'Feature058_' in k else 1,k))
    for k in tasks96:
        q=ctx83[k];r=dict(other=k,source_valid=q.isValid())
        if q.isValid():
            gap,w,_=worldholder96.distToShape(q);r.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='CHANGED_WHOLE_CARRIER_SEPARATED125' if gap>=1.25-1e-7 else 'CHANGED_WHOLE_CARRIER_HOLD')
            if gap<1e-7:
                co=worldholder96.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        else:r['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
        foreign96.append(r);print('SLOT96_FOREIGN',r,flush=True)
        if r['status']!='CHANGED_WHOLE_CARRIER_SEPARATED125' or time.monotonic()-t96>20:break
sections96=[]
for u in [proposal93['structural145'][0]['u'],proposal93['structural145'][1]['u'],-38.5]:
    pl=Part.Face(Part.makePolygon([A.Vector(u,y,n) for y,n in [(-8,-6),(26,-6),(26,30),(-8,30),(-8,-6)]]))
    for name,s in [('actual_Link117',linklocal93),('new_lower_sidecar',frame96),('new_pressure_roof',cap96),('full3_source_profiles',Part.makeCompound(list(profiles93.values()))),('full4_selected_loops',Part.makeCompound(list(loops94.values())))]:
        sec=s.section(pl);curves=[[[p.y,p.z] for p in e.discretize(Deflection=.07)] for e in sec.Edges];sections96.append(dict(axial_mm=u,name=name,curves=curves))
ar96=OUT/'day07-SOURCE-slot-carrier-first-material.breps.zip';assert not ar96.exists();ge96=[]
with zipfile.ZipFile(ar96,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('LOCAL:whole_lower',frame96),('LOCAL:whole_upper',cap96)]+[('LOCAL:lower:'+n,s) for n,s in lower96.items()]+[('LOCAL:upper:'+n,s) for n,s in upper96.items()]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge96.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge96,scope='ONEpurposeful native-window clamp / positive-sidecar land tray, actualmaterial initialgate; NOTselectedoverlay'),indent=2)+'\n').encode())
r96=dict(id='day07-SOURCE-slot-carrier-first-material',status='MATERIAL_MEMBER_OR_LOADPATH_HOLD' if not materialok96 else 'OWN_STOCK_REGION_MATERIAL_HOLD' if firstown96 else 'MATERIAL_NEIGHBOR_GATE_RECEIVED_SCOPED' if len(foreign96)==len(tasks96) and all(r['status']=='CHANGED_WHOLE_CARRIER_SEPARATED125' for r in foreign96) else 'MATERIAL_FOREIGN_OR_PENDING_HOLD',material_ok=materialok96,lower_valid=frame96.isValid(),lower_solids=len(frame96.Solids),upper_valid=cap96.isValid(),upper_solids=len(cap96.Solids),functional_channel_cuts=cutrecords96,intended_member_coverage=coverage96,positive_junctions=junctions96,own_stock_rows=ownstock96,first_own_stock_falsifier=firstown96,foreign_rows=foreign96,cursor=len(foreign96),total=len(tasks96),unreceived=len(tasks96)-len(foreign96),sections=sections96,new_source_A_U_fit_slack=None,bodylanding_actualroot='NOT_RUN',full_motion_outline_initialassembly='OPEN',source_root_feet='Sameactualconformingpolygonfeet/worldframe, rigidcopypreserved; actualLinkneverfused.',geometry=ge96,archive=ar96.name,archive_sha256=hashlib.sha256(ar96.read_bytes()).hexdigest(),operation_seconds=time.monotonic()-t96,process_cpu_seconds=time.process_time()-cpu96,selected=False,N01_complete=False,current1292_effective1311_rest108_unchanged=True)
p96=OUT/'day07-SOURCE-slot-carrier-first-material.json';assert not p96.exists();p96.write_bytes((json.dumps(r96,ensure_ascii=False,indent=2)+'\n').encode());print('SLOT96_FINAL',r96['status'],materialok96,len(coverage96),len(junctions96),firstown96,len(foreign96),len(tasks96),r96['operation_seconds'],r96['process_cpu_seconds'],hashlib.sha256(p96.read_bytes()).hexdigest(),flush=True)

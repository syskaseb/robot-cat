import time,json,hashlib,zipfile
t98=time.monotonic();cpu98=time.process_time();lower98={n:s.copy() for n,s in lower96.items()};removed98=[]
for n in ['crosshead_0','crosshead_1']:
    s=lower98[n];before=s.Volume
    for q in profiles93.values():s=s.cut(q)
    assert s.isValid();lower98[n]=s;removed98.append(dict(member=n,removed_for_same_full_profiles_mm3=before-s.Volume,same_pose_and_extent=True,minimum_groove_floor_mm=.7))
frame98=union96(lower98);holder98=Part.makeCompound([frame98,cap96]);coverage98=[]
for n,s in lower98.items():
    q=s.cut(frame98);coverage98.append(dict(member=n,missing_valid=q.isValid(),missing_mm3=q.Volume if q.isValid() else None,bounds_mm=saved_bounds(s)))
outside98=frame98.cut(frame96);assert outside98.isValid();junctions98=[]
for group,a,b in edges96:
    if group!='lower':continue
    co=lower98[a].common(lower98[b]);junctions98.append(dict(a=a,b=b,valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,positive=co.isValid() and co.Volume>1e-5))
profiles98=[]
for n,q in profiles93.items():
    co=holder98.common(q);assert co.isValid();profiles98.append(dict(profile=n,material_common_mm3=co.Volume))
ok98=frame98.isValid() and len(frame98.Solids)==1 and outside98.Volume<1e-5 and all(r['missing_valid'] and r['missing_mm3']<1e-5 for r in coverage98) and all(r['positive'] for r in junctions98) and all(r['material_common_mm3']<1e-5 for r in profiles98)
sections98=[]
for u in [proposal93['structural145'][0]['u'],proposal93['structural145'][1]['u'],-15]:
    pl=Part.Face(Part.makePolygon([A.Vector(u,y,n) for y,n in [(-8,-6),(26,-6),(26,30),(-8,30),(-8,-6)]]))
    for name,s in [('actual_Link117',linklocal93),('new_lower_sidecar',frame98),('new_pressure_roof',cap96),('full3_source_profiles',Part.makeCompound(list(profiles93.values()))),('full4_selected_loops',Part.makeCompound(list(loops94.values())))]:
        sec=s.section(pl);sections98.append(dict(axial_mm=u,name=name,curves=[[[p.y,p.z] for p in e.discretize(Deflection=.07)] for e in sec.Edges]))
ar98=OUT/'day07-SOURCE-slot-crosshead-functional-grooves.breps.zip';assert not ar98.exists();ge98=[]
with zipfile.ZipFile(ar98,'w',zipfile.ZIP_DEFLATED) as z:
    items=[('LOCAL:corrected_whole_lower',frame98),('LOCAL:unchanged_whole_upper',cap96)]+[('LOCAL:corrected_'+n,lower98[n]) for n in ['crosshead_0','crosshead_1']]
    for i,(n,s) in enumerate(items):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge98.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume,valid=s.isValid()))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge98,scope='Samewholewindowclamp/sidecar correctedomitted3fullprofilegroovesin2crossheads; upperunchanged. AllsameSOURCEjoints/profiles/stock/sourcefeet.'),indent=2)+'\n').encode())
r98=dict(id='day07-SOURCE-slot-crosshead-functional-grooves',status='SLOT_RETENTION_AND_CARRIER_LOCAL_FUNCTION_RECEIVED_WHOLE_SOURCE_TRANSPORT_OPEN' if ok98 else 'SLOT_CROSSHEAD_FUNCTIONAL_GROOVE_CORRECTION_HOLD',
 raw_negative=dict(receipt='day07-SOURCE-slot-material-completion.json',D_mm3=18.00924734392912,V_mm3=4.913478794435012,G_mm3=18.00924734392912,disposition='Omitted3fullwiregroovesin2NEWcrossheads; realimplementedmaterialintersectsallocatedprofiles. SamefunctionalSOURCEplan corrected withproperopencomb channels, notsourceprofile/holderposeoffset. Rawnegativepreserved, no counterreset.'),
 correction=removed98,source_profile_radius_R_unchanged=True,lower_valid=frame98.isValid(),lower_solids=len(frame98.Solids),intended_lower10_member_coverage=coverage98,positive_lower_junctions=junctions98,upper9_member_9_junction_reuse='Unchangedcap96/wholeupper in new archive; r96uppercoverage9+junction9 reused byte/sourcegeometry unchanged.',
 material_subset_proof=dict(valid=outside98.isValid(),new_lower_outside_received_full_lower_mm3=outside98.Volume,foreign_reuse='All5validreceivedcarrier/currentforeignpairs gaps1.35/2.35/8.35/1.8969285/1.3289122 lowerbounds preservedbyactualnewmaterialsubset. Allownstock12clear andmaterialAnkle10coverlowerbounds similarlypreserved; no oldpairreplay.'),
 full3_profiles=profiles98,full4_stock_and_actual_link_bearing_scope='r95complete13matrix/full4units/fulltails/actualLink22.2877994+22.2848598; r97newfull3.3x2feedsoutside0/0+4headtobandactualgap0/common0. Scopeprototypefixedstockspace not manufacturerlatch/strength orN09.',
 whole_source_dependency='Wholejointlandframeproposed+Y8.5 sidecar; all9 IDs/12portions/4physicalMAX3 currentsource/factoryplug/3x8/3x20/stagger/2x9/14/11/lap4/850/900 preserved. NEW ALL3original+donor A/U/fit/slack must be recomputed fromsameKnee-ownedsourcejointplan and actualBankBed1 landing. No creditoldGdelta orold181/205/225. No V3 detail untilqualified.',
 source_A_U_fit_slack=None,bodylanding_actualroot='NOT_RUN',initialassembly_required='BenchexistingSOURCEspliceassemblyOFFPETG; openbeds/pressurehalf before4onewaytiesclosed. Tailspark throughaxialports beforeoutercovers; fullmovingmodulefactoryend/transport/stock/motion/outline qualificationstillOPEN.',selected=False,N01_complete=False,current1292_effective1311_rest108_unchanged=True,sections=sections98,archive=ar98.name,archive_sha256=hashlib.sha256(ar98.read_bytes()).hexdigest(),geometry=ge98,operation_seconds=time.monotonic()-t98,process_cpu_seconds=time.process_time()-cpu98,pid=os.getpid(),session_id=46493)
p98=OUT/'day07-SOURCE-slot-crosshead-functional-grooves.json';assert not p98.exists();p98.write_bytes((json.dumps(r98,ensure_ascii=False,indent=2)+'\n').encode());print('SLOT98_FINAL',r98['status'],len(coverage98),len(junctions98),outside98.Volume,profiles98,r98['operation_seconds'],r98['process_cpu_seconds'],hashlib.sha256(p98.read_bytes()).hexdigest(),flush=True)

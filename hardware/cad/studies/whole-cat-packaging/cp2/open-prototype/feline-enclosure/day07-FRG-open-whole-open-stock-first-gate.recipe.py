import json,time,hashlib,os,zipfile,math
t208=time.monotonic();c208=time.process_time();pp208=OUT/'day07-FRG-open-front-keyed-closure-underbank-whole-proposal.json';pr208=json.loads(pp208.read_bytes());Y208=-47.7;dy208=Y208+53.75
band208=band206.copy();band208.translate(A.Vector(0,dy208,0));head208=head206.copy();head208.translate(A.Vector(0,dy208,0))
def arcfield208(cx,cz,a,b):
    at=lambda r,t:A.Vector(cx+r*math.cos(t),Y208-1.65,cz+r*math.sin(t))
    e=[Part.Arc(at(4,a),at(4,(a+b)/2),at(4,b)).toShape(),Part.makeLine(at(4,b),at(2,b)),Part.Arc(at(2,b),at(2,(a+b)/2),at(2,a)).toShape(),Part.makeLine(at(2,a),at(4,a))]
    return Part.Face(Part.Wire(e)).extrude(A.Vector(0,3.3,0))
q208=arcfield208(27.475,42.61,0,-math.pi/2);u208=arcfield208(-15.75,42.61,-math.pi/2,-3*math.pi/2)
lengths208=dict(first_quarter=3*math.pi/2,lower_straight=43.225,upper_turn=3*math.pi);lengths208['upper_straight']=83.3-sum(lengths208.values());end208=-15.75+lengths208['upper_straight']
lo208=box153([[-15.75,Y208-1.65,38.61],[27.475,Y208+1.65,40.61]]);hi208=box153([[-15.75,Y208-1.65,44.61],[end208,Y208+1.65,46.61]])
tail208=q208.multiFuse([lo208,u208,hi208]);assert tail208.isValid() and len(tail208.Solids)==1 and abs(tail208.Volume-83.3*3.3*2)<1e-5
quality208=dict(valid=tail208.isValid(),solids=len(tail208.Solids),source_full_uncut_remainder_capacity_mm=83.3,profile_mm=[3.3,2],plastic_centreline_R_mm=3,lengths_mm=lengths208,length_sum_mm=sum(lengths208.values()),full_volume_mm3=tail208.Volume,analytic_volume_mm3=83.3*3.3*2,actual_bounds_mm=saved_bounds(tail208),analytic_bounds_mm=[[-19.75,-49.35,38.61],[31.475,-46.05,46.61]],is_capacity_not_rigid_actualtail=True,no_headlength_credit=True)
ownroot208=Current35['Station:FR_G:shared_near_root'];owncomb208=Current35['Station:FR_G:split_common_comb'];stock208={'FRG_ENTIRE_SELECTED_BAND':band208,'FRG_FULL_HEAD':head208,'FRG_FULL83p3_UNCUT_CAPACITY':tail208}
wire208=[];extra3profiles208=[]
for n,s in profiles206:
    x=s.BoundBox.Center.x;z=45.26;extra3profiles208.append((n,Part.makeCylinder(1.55,9.8,A.Vector(x,-56.25,z),A.Vector(0,1,0))))
first208=None
for sn,a in stock208.items():
    for wn,b in extra3profiles208:
        co=a.common(b);row=dict(stock=sn,wire=wn,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None);wire208.append(row)
        if not co.isValid() or co.Volume>1e-7:first208=dict(stage='WHOLE_SELECTED_UNIT_FOUR_PROFILE_NONPENETRATION',row=row);break
    if first208:break
retire208=['Station:FR_G:band_budget','Station:FR_G:head_budget','Station:FR_G:shared_near_tie'];context208={n:s for n,s in neigh199.items() if n not in retire208}
context208.update({'PROPOSED_D5_C1_WHOLE_CASE_CARRIER':base201,'PROPOSED_D5_WHOLE_UPPER':up202,'PROPOSED_D5_WHOLE145LOOP':band181,'PROPOSED_D5_FULLHEAD':head181,'PROPOSED_D5_FULLTAIL_CAPACITY':tailfield181,**{'NEW_CLAMP3_'+n:s for n,s in kit199.items() if n.startswith('Hardware:')}})
ownnames208={'Station:FR_G:shared_near_root','Station:FR_G:split_common_comb','PROPOSED_D5_C1_WHOLE_CASE_CARRIER'}
tasks208=[];bbox208=0;rows208=[];pendingown208=[]
for sn,a in stock208.items():
    for n,b in context208.items():
        bb=bounds126[n] if n in bounds126 else b.BoundBox;lo=bbox_lower_bound(a.BoundBox,bb)
        if lo>=1.25-1e-7:bbox208+=1;continue
        if n in ownnames208:
            co=a.common(b);allow=ownroot208 if n.startswith('Station:FR_G:') else kit199['Neck'];ex=co.cut(allow)
            pendingown208.append(dict(stock=sn,actor=n,actual_common_valid=co.isValid(),actual_common_mm3=co.Volume,common_outside_planned_modified_material_mm3=ex.Volume,scope='MATCHEDFUNCTIONALPRINT_CHANNEL_NOTBUILT_NOT_ACCEPTED; actualstock/newNeck-or-FRGroot onlyplannedmodification'))
            if ex.Volume>1e-7:tasks208.append((0,sn,n,a,b,lo))
            continue
        priority=0 if (n.startswith('Ref_Material_P0_') or n.endswith(':case') or 'Housing' in n or 'Screw' in n or 'Nut' in n) else 1
        tasks208.append((priority,sn,n,a,b,lo))
tasks208.sort(key=lambda q:(q[0],q[1],q[2]));wita208=None;witb208=None
if first208 is None:
    for _,sn,n,a,b,lo in tasks208:
        ga,ww,_=a.distToShape(b);row=dict(stock=sn,actor=n,source_valid=b.isValid(),actual_gap_mm=ga,required_foreign_mm=1.25,witnesses=[[list(x),list(y)] for x,y in ww[:1]])
        if ga<1e-7:
            co=a.common(b);row.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
        row['status']='NEW_WHOLE_STOCK_ALLOCATED_HOLD_NOT_DELIVERED_CONTACT' if ga<1.25-1e-7 or not b.isValid() else 'FULL_SELECTED_STOCK_FOREIGN_SEPARATED125';rows208.append(row)
        if row['status']!='FULL_SELECTED_STOCK_FOREIGN_SEPARATED125':first208=dict(stage='WHOLE_CLOSURE_AND83p3_CAPACITY_FIRST_CURRENT_NEIGHBOR',row=row);wita208=a;witb208=b;break
        if time.monotonic()-t208>10:break
ar208=OUT/'day07-FRG-open-front-whole-stock-first-gate.breps.zip';assert not ar208.exists();ge208=[]
exps208={**stock208,'FIRST_DOWN_QUARTER_CAPACITY':q208,'OPEN_UNDERBANK_RETURN_CAPACITY':u208,**{'CURRENT_FOUR_FULL9p8_REFERENCE_'+n:s for n,s in extra3profiles208}}
if witb208 is not None:exps208['FIRST_ACTUAL_NEIGHBOR']=witb208
with zipfile.ZipFile(ar208,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(exps208.items()):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge208.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge208),indent=2))
p208=OUT/'day07-FRG-open-front-whole-stock-first-gate.json';assert not p208.exists()
r208=dict(id=p208.stem,status='OPEN_FRONT_WHOLE_PRESSURE_LOAD_STOCK_FIRST_FALSIFIER_STOP' if first208 else 'OPEN_FRONT_WHOLE_STOCK_SCOPED_OTHER_PRINT_CHANNEL_PENDING',proposal=pp208.name,proposal_sha256=hashlib.sha256(pp208.read_bytes()).hexdigest(),whole83p3_capacity_quality=quality208,wholeunit_fourlead_rows=wire208,planned_actual_own_print_channel_interfaces_NOTqualified=pendingown208,only_alias_effectivity=retire208,foreign_rows=rows208,foreign_cursor=len(rows208),foreign_total=len(tasks208),foreign_unreceived=[[sn,n] for _,sn,n,a,b,lo in tasks208[len(rows208):]],fullbounds_separated=bbox208,first_falsifier=first208,no_newmaterial_or_pressurekeys_built=True,no_boughtcase_or_framecut=True,no_secondfamily=True,selected=False,N01_complete=False,actualcut=None,currentbase_unchanged=True,archive=ar208.name,archive_sha256=hashlib.sha256(ar208.read_bytes()).hexdigest(),geometry=ge208,operation_seconds=time.monotonic()-t208,process_cpu_seconds=time.process_time()-c208,pid=os.getpid(),session_id=46493)
p208.write_bytes((json.dumps(r208,indent=2)+'\n').encode());print('FRG_OPEN_WHOLE_STOCK',r208['status'],'83.3',quality208,'wire',len(wire208),'ownpending',len(pendingown208),'foreign',len(rows208),'of',len(tasks208),'first',first208,'wall',r208['operation_seconds'],'CPU',r208['process_cpu_seconds'],hashlib.sha256(p208.read_bytes()).hexdigest(),flush=True)

"""Bounded BOTH-end USB curve allocation against REV3 shared neighbours.

Read-only source scene; no native changes, supplier healing, SKU changes or
selection. The 452mm outside length is a PROJECT allowance (500-26-22).
This domain search is not an exhaustive proof that no other route exists.
"""
import hashlib
import json
import math
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from feline_current_scene import load
from plan_feline_central_pi_wedge import packed
from check_feline_shared_space import tube_prefix
from feline_tangent_routes import add,mul,sub,norm,biarc,quarter_prefix,reverse,samples,length,min_radius


def wire(parts):
    edges=[]
    for s in parts:
        p=A.Vector(*s['start']);q=A.Vector(*s['end'])
        if s['kind']=='line':edges.append(Part.makeLine(p,q))
        else:
            a=s['angle']/2
            mid=p+A.Vector(*s['tangent'])*(s['radius']*math.sin(a))+A.Vector(*s['bend'])*(s['radius']*(1-math.cos(a)))
            edges.append(Part.Arc(p,mid,q).toShape())
    w=Part.Wire(edges)
    assert w.isValid() and abs(w.Length-length(parts))<1e-6
    return w


def main():
    tick=time.monotonic();dest=OUT/'n01-joint-usb-route.json';assert not dest.exists()
    files={k:OUT/n for k,n in dict(plan='n01-coupled-allocation-plan.json',
        boundary='n01-component-boundary-contract.json',pi='n01-pi-full-port-contract.json',
        clocked='n01-coupled-clocked-joints.json',bus='n01-bus-both-plugs-plan-r3.json').items()}
    docs={k:json.loads(p.read_text()) for k,p in files.items()};plan=docs['plan'];assert plan['profile_revision']==3
    assert plan['USB500']['conservative_external_wire_capacity_target_mm']==452
    report=dict(status='RUNNING_BOUNDED_BOTH_END_USB',selected=False,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__),Path(__file__).with_name('feline_tangent_routes.py'))},
        catalog_total_mm=500,project_external_target_mm=452,mould_allowances_mm=[26,22],
        supplier_bare_length_guaranteed=False,new_SKU_or_extension=False,math_candidates=0,
        target_length_candidates=0,radius_candidates=0,outer_sample_candidates=0,exact_candidates=[],
        errors=[],accepted_route=None,whole_wiring_or_mounts_qualified=False,
        scope='USB route planning query only. Shared REV3 cases/station first profiles/Pi full budgets; changed PCA bare/jacket forms, all123 middles, root/tool/motion remain OPEN.',
        search_is_not_exhaustive=True)
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();scene,meta,templates,data,pins,_=load();report['source_sha256'].update(pins)
    stations={r['ref']:r for r in data['ports']['stations']};moved={s['current_group'] for s in stations.values() if s['ref']!='P_SYS'}
    invalidated={e['id'] for e in data['packet']['endpoints'] if e['group'] in moved or e['group'] in ('Pi4','PWM9685')}
    retired=[]
    for n in list(scene):
        role=meta[n].get('role','')
        if role in moved or role in ('Pi4','PWM9685') or (n.startswith('End:') and n[4:] in invalidated) or n.startswith(('StructureReserve:PCBrootPi4','StructureReserve:PCBrailPi4','StructureReserve:PCBrootPWM9685','StructureReserve:PCBrailPWM9685','StructureReserve:PWMForeBranch')) or (n.startswith('CurrentBUS:USB') and 'Overmould' not in n):
            retired.append(n);scene.pop(n);meta.pop(n)
    # Current Pi full moulds, official port budgets, source hardware and concentric power.
    _,clocked,crows=packed(files['clocked'])
    for n,s in clocked.items():
        if crows[n]['group']!='PiCoupled' or n.startswith('PiUSBData'):continue
        scene[n]=s;meta[n]=crows[n]
    pwm=plan['PWM9685'];rot=A.Rotation(A.Vector(0,1,0),pwm['rotation_about_world_Y_degrees'])
    tf=A.Placement(A.Vector(*pwm['target_PCB_bottom_datum_mm'])-rot.multVec(A.Vector(*pwm['source_PCB_bottom_datum_mm'])),rot)
    # Retrieve source PWM hardware again, applying the single correct datum transform.
    original,originalmeta,_,_,_,_=load()
    for n,s in original.items():
        if originalmeta[n].get('role')=='PWM9685':
            s=s.copy();s.Placement=tf*s.Placement;scene[n]=s;meta[n]=originalmeta[n]
    del original
    for row in plan['WAGO_station_rows']:
        for ref,x,sign in zip(row['refs'],row['centres_X_mm'],row['departure_X_signs']):
            st=stations[ref];n=next(n for n,r in originalmeta.items() if r.get('role')==st['current_group'])
            # Exact source case from its frozen bundle, not a generic bbox.
            source=next(r for key in ('extra','common','lower','scene') for r in data[key]['parts'] if r['name']==n)
            key=next(key for key in ('scene','lower','common','extra') if source in data[key]['parts'])
            with zipfile.ZipFile(ROOT/data[key]['bundle']) as z:raw=z.read(source['entry'])
            assert hashlib.sha256(raw).hexdigest()==source['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode())
            p=A.Vector(*st['prototype']['port_pitch_vector_mm']);p.normalize();d=A.Vector(*st['prototype']['departure_axis']);d.normalize()
            h=1 if p.cross(d).z>0 else -1
            targets=[A.Vector(0,0,h*sign*row['side']),A.Vector(sign,0,0),A.Vector(0,row['side'],0)]
            sourcebasis=[p,d,A.Vector(0,0,1)];m=A.Matrix()
            for i in range(3):
                for j in range(3):setattr(m,f'A{i+1}{j+1}',sum(t[i]*v[j] for t,v in zip(targets,sourcebasis)))
            r=A.Rotation(m);s0=s.copy();s0.Placement=A.Placement(A.Vector(),r)*s0.Placement;bb=s0.BoundBox
            centre=A.Vector(x,row['side']*(plan['WAGO_case_inner_face_abs_Y_mm']+bb.YLength/2),row['case_top_Z_mm']-bb.ZLength/2)
            t=A.Placement(centre-r.multVec(s.BoundBox.Center),r);s.Placement=t*s.Placement;scene[n]=s;meta[n]=dict(kind='actual_source_case')
            for e in st['occupied_ports']:
                en='REV3Station:'+e['endpoint'];scene[en]=tube_prefix(list(t.multVec(A.Vector(*e['point_mm']))),list(r.multVec(A.Vector(*e['departure_axis']))),2.1,row['bend_unit_mm'],12.4,3)
                meta[en]=dict(kind='wire')
    for spec in plan['FHAC']+[dict(role='Monitor5015',**plan['Monitor5015'])]:
        n,s,r=templates[spec['role']];s=s.copy();rot=A.Rotation(A.Vector(0,1,0),-90) if spec['role']!='Monitor5015' else A.Rotation(A.Vector(1,0,0),spec['rotation_about_X_degrees'])
        s.Placement=A.Placement(A.Vector(*spec['centre_mm'])-rot.multVec(s.BoundBox.Center),rot)*s.Placement
        scene['REV3:'+spec['role']]=s;meta['REV3:'+spec['role']]=dict(kind='actual_source_case')
    # Test unchanged head at baseline. Do not import HeadRaised from rejected snapshots.
    reader=SavedShapes();envfile=OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd';outer=reader.shape(envfile,'TorsoEnvelope')
    assert outer.isValid() and len(outer.Solids)==1;surface=Part.makeCompound(outer.Faces)
    report['source_sha256'].update(reader.hashes)
    pi=docs['pi'];r=A.Rotation(A.Vector(0,0,1),180)*A.Rotation(A.Vector(1,0,0),-12)
    pose=A.Placement(A.Vector(*plan['Pi']['source_PCB_bottom_target_mm'])-r.multVec(A.Vector(0,0,47.72)),r)
    start=list(pose.multVec(A.Vector(*pi['USB_A_data_plug_budget']['source_wire_mouth_mm'])))
    end=next(x['parts'][0]['start'] for x in docs['bus']['routes'] if x['wire']=='USB_CableFirst')
    report.update(start_mm=start,end_mm=end,retired_old_interfaces=retired,scene_count=len(scene))
    print('Shared REV3 query scene',len(scene),'USB',start,end,flush=True);save()
    ratios=[2**(i/2) for i in range(-8,9)];candidates=[]
    def make(a,b,rho):
        pre=quarter_prefix(start,(-1,0,0),(0,math.cos(a),math.sin(a)))
        post=quarter_prefix(end,(0,-1,0),(math.cos(b),0,math.sin(b)))
        middle=biarc(pre[-1]['end'],(0,math.cos(a),math.sin(a)),post[-1]['end'],(-math.cos(b),0,-math.sin(b)),rho)
        return pre+middle+[reverse(s) for s in post[::-1]]
    for ia in range(24):
        a=ia*math.pi/12
        for ib in range(24):
            b=ib*math.pi/12;previous=None
            for rho in ratios:
                try:parts=make(a,b,rho)
                except ValueError:previous=None;continue
                report['math_candidates']+=1;L=length(parts)
                if previous and (previous[1]-452)*(L-452)<=0:
                    lo,hi=previous[0],rho;lowvalue=previous[1]-452
                    try:
                        for _ in range(32):
                            mid=(lo+hi)/2;trial=make(a,b,mid);value=length(trial)-452
                            if lowvalue*value<=0:hi=mid
                            else:lo=mid;lowvalue=value
                        trial=make(a,b,(lo+hi)/2);report['target_length_candidates']+=1
                        if min_radius(trial)>=30-1e-7:
                            report['radius_candidates']+=1
                            pts=[q for s in trial for q in samples(s,5)]
                            # Actual connected curve must later stay >=5.75 from ALL outer faces.
                            if all(-141.5<q[0]<183.5 and abs(q[1])<98 and -48<q[2]<112 for q in pts):
                                if all(outer.isInside(A.Vector(*q),1e-6,True) for q in pts):
                                    report['outer_sample_candidates']+=1
                                    candidates.append((max(abs(q[1]) for q in pts),ia,ib,(lo+hi)/2,trial))
                    except ValueError:pass
                previous=(rho,L)
        print('Tangent domains',ia+1,'/24','length',report['target_length_candidates'],'R30',report['radius_candidates'],'inside',report['outer_sample_candidates'],flush=True);save()
        if time.monotonic()-tick>120:break
    report['source_sha256'].update(reader.hashes)
    bounds={n:s.BoundBox for n,s in scene.items()};valid={};seen=[]
    for _,ia,ib,rho,parts in sorted(candidates)[:24]:
        if time.monotonic()-tick>180:break
        w=wire(parts);row=dict(Pi_domain=ia,BUS_domain=ib,ratio=rho,length_mm=w.Length,min_R_mm=min_radius(parts),failures=[],invalid_holds=[],pairs=0)
        if not outer.isInside(A.Vector(*parts[0]['start']),1e-6,True):row['failures'].append(dict(outer='Start outside'))
        gap=w.distToShape(surface)[0];row['outer_surface_gap_mm']=gap
        if gap<5.75-1e-6:row['failures'].append(dict(outer_gap_mm=gap,required_mm=5.75))
        if not row['failures']:
            bb=w.BoundBox
            from check_feline_all_current_lands import near
            for n,s in scene.items():
                if not s.Solids or not near(bb,bounds[n],3.75):continue
                if time.monotonic()-tick>180:row['invalid_holds'].append('Time cap before all pairs');break
                if n not in valid:valid[n]=s.isValid()
                if not valid[n]:row['invalid_holds'].append(n);continue
                ownboot=n in ('PiBudget:USB_A_data_boot','CurrentBUS:USB_C_Overmould')
                test=wire(parts[1:-1]) if ownboot else w
                required=2.5 if ownboot else 2.7 if ('wire' in meta[n].get('kind','') or n.startswith(('End:','BankFullPrefix:','Factory:'))) else 3.75
                d=test.distToShape(s)[0];row['pairs']+=1
                if d<required-1e-6:
                    row['failures'].append(dict(name=n,gap_mm=d,required_mm=required,reservation='reservation' in meta[n].get('kind','')))
                    break # Rejected candidate: no unchanged expensive remaining pairs.
        report['exact_candidates'].append(row);save()
        print('Exact route',ia,ib,'pairs',row['pairs'],'fail',row['failures'][:1],'holds',row['invalid_holds'],flush=True)
        if not row['failures'] and not row['invalid_holds']:
            report['accepted_route']=dict(parts=parts,**row)
            # A source-pinned CURVE is not a native editable mounting assembly.
            raw=w.exportBrepToString().encode();bundle=dest.with_suffix('.zip')
            with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('USB_curve.brep',raw)
            report.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),curve_sha256=hashlib.sha256(raw).hexdigest())
            break
    report['status']='USB_CURVE_CURRENT_QUERY_CLEAR_FULL_NEIGHBOURS_ROOTS_MOTION_OPEN' if report['accepted_route'] else 'BOUNDED_USB_DOMAIN_NO_QUALIFIED_ROUTE_NOT_INFEASIBILITY_PROOF'
    report['open']=['Full changed PCA forms/FHAC factory sleeves and station after9mm grips/middles not all included in this query',
        'Both USB independent9mm grips need load-bearing roots/tools/removal',
        'Known invalid BUS source needs inverse-valid-source query if encountered; never heal or skip',
        'Exact vendor mould/available bare cable length remains delivery fit assumption',
        'All36leg poses and remaining123external portions remain N01 requirements']
    save();print(json.dumps(dict(status=report['status'],math=report['math_candidates'],length=report['target_length_candidates'],R30=report['radius_candidates'],inside=report['outer_sample_candidates'],exact=len(report['exact_candidates']),seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()

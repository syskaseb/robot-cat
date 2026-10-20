"""One input-bay revision: four end saddles, retained rework, rooted panels.

Move the TWO complete fore joints by the calculated length deficit+1mm,
not a case-pose search. Retire eight redundant factory seats, retain all
custom-side grips and bought SKUs. Planning solids only, not N03/native.
"""
import gzip,hashlib,json,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from plan_feline_remaining_factory_inputs import offset,forward,samples
from plan_feline_factory_links import scurve
from plan_feline_n01_shared import pipe
from receive_feline_positive_service_deck import open_grip
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_underplate_return_gallery import minimum_for
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json

WIRES=('W041','W042','W044','W052')
CASES=dict(W041='FL',W042='FR',W044='RL',W052='RR')


def box(lo,hi):return Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))


def build(parts,meta,plan):
    actors={};ameta={};owners={};original={};retired=set();recipes={};roots={};unchanged=set()
    # Shared1mm length reserve in the inherited100mm project assumption.
    need=max(plan['routes'][w]['guide_mm']+21 for w in WIRES[:2])
    shift=np.ceil((need-100+1)*10)/10
    assert shift==6.7
    for w in WIRES:
        delta=np.array([-shift,0,0]) if w in WIRES[:2] else np.zeros(3)
        for n,s in parts.items():
            if n.startswith(('Seat:'+w+':factory:','TieLoop:Seat:'+w+':factory:','TieHead:Seat:'+w+':factory:')):
                retired.add(n)
            same=n in ('Ref_Material_'+w+'_Joint_0_0','CaseBase:'+w+'_Joint','CaseCap:'+w+'_Joint','CustomPrefix:'+w) or n.startswith(('CapScrew:'+w+'_Joint:','CapNut:'+w+'_Joint:','Seat:'+w+':custom','TieLoop:Seat:'+w+':custom','TieHead:Seat:'+w+':custom'))
            if same and (np.linalg.norm(delta)>0 or n=='CaseBase:'+w+'_Joint'):
                retired.add(n);actors[n]=s.copy();actors[n].translate(A.Vector(*delta));ameta[n]=meta[n];owners[n]=w;original[n]=n
        n='Factory:'+w;retired.add(n)
        old=plan['routes'][w]['parts'];p=np.array(old[0]['start']);target=np.array(old[-1]['end'])+delta
        d=np.array([1.,0,0]) if w in WIRES[:2] else np.array([-1.,0,0])
        if w in WIRES[:2]:
            rows=[];q=forward(rows,p,d,3);q=offset(rows,q,d,[0,target[1]-p[1],-6]);q=offset(rows,q,d,[0,0,target[2]-q[2]])
            rest=float((target-q)@d);assert rest>2.5;forward(rows,q,d,rest)
        else:rows,_=scurve(p,target,d,R=25.2,land=0);unchanged.add(n)
        L=sum(r['length_mm'] for r in rows);assert L+11+10<100
        actors[n]=pipe(rows,2.1);ameta[n]=dict(kind='actual_wire');owners[n]=w;original[n]=n
        # One independent full9mm jacket arc interval near the joint. The
        # flat pad covers its complete axial projection, not a rigid bore.
        side=np.array([0.,np.sign(target[1]),0]);start=target-10.25*d
        kit=open_grip(start,d,side,4.5);pad=kit['pad'];b=pad.BoundBox
        # Last2mm axial end avoids the full band's3.25..5.75 interval.
        xx=sorted((float(start[0]+7*d[0]),float(start[0]+9*d[0])))
        root=box([xx[0],b.YMin,-43.3],[xx[1],b.YMax,b.ZMin+1])
        kit['pad']=pad.fuse(root)
        panel='LowerBay:'+('ForePanel' if target[0]<20 else 'RearPanel')
        union=kit['pad'].common(parts[panel]);assert union.isValid() and union.Volume>1e-5,(w,panel,'No actual foot material')
        roots[w]=dict(parent=panel,positive_common_mm3=union.Volume,full9_arclength_interval_mm=[L-10.25,L-1.25],
            source_has_no_extra_invented_grip=True,source_boot_straight_mm=rows[0]['length_mm'])
        for k,s in kit.items():
            assert s.isValid() and len(s.Solids)==1,(w,k)
            name='InputGrip:'+w+':'+k;actors[name]=s;owners[name]=w
            ameta[name]=dict(kind='proposal_material' if k=='pad' else 'project_stock_reservation')
            if k!='pad':ameta[name]['material_role']='selected_T18I_nylon_budget'
        # Replace the old0.30mm proximity with an explicit1.25mm channel in
        # THIS printed shoe only. Preserve its bought case and fasteners.
        base='CaseBase:'+w+'_Joint';oldbase=actors[base].copy();cut=pipe(rows,3.35)
        actors[base]=oldbase.cut(cut)
        assert actors[base].isValid() and len(actors[base].Solids)==1,base
        assert actors[base].cut(oldbase).Volume<1e-5
        recipes[w]=dict(parts=rows,radius_mm=2.1,R_mm=25.2,guide_mm=L,strip_mm=11,rework_mm=10,
            project_factory100_margin_mm=100-L-21,joint_translation_mm=delta.tolist(),root=roots[w],
            factory_actual_length_and_fit_after_delivery=True,selected_parts_changed=False)
    assert sum(n.startswith('Seat:') for n in retired)==10 #8factory+2translatedcustom
    for n,s in actors.items():assert s.isValid() and s.Solids,n
    return actors,ameta,owners,original,retired,recipes,roots,unchanged


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    source=OUT/'n01-remaining-factory-input-plan.json';plan=json.loads(source.read_text())
    actors,ameta,owners,original,retired,recipes,roots,unchanged=build(parts,meta,plan)
    fixed={n:s for n,s in parts.items() if n not in retired};query=SolidQueries()
    dest=OUT/'n01-factory-saddle-plan.json';pf=dest.with_suffix('.pairs.json.gz');archive=dest.with_suffix('.breps.zip')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (source,Path(__file__))})
    geometry=[];print_members={}
    for panel in ('LowerBay:ForePanel','LowerBay:RearPanel'):
        members=[panel]
        for w in WIRES:
            if roots[w]['parent']!=panel:continue
            members+=['CaseBase:'+w+'_Joint','InputGrip:'+w+':pad']
            joint=actors['CaseBase:'+w+'_Joint'];common=joint.common(parts[panel])
            assert common.isValid() and common.Volume>1e-5,(w,'Joint shoe root')
            roots[w]['case_shoe_panel_common_mm3']=common.Volume
        unit=parts[panel].multiFuse([actors[n] for n in members[1:]])
        assert unit.isValid() and len(unit.Solids)==1,(panel,'Disconnected planned unit')
        b=unit.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
        print_members[panel]=members
    if not dest.exists():
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(n,s) in enumerate(actors.items()):
                raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
                geometry.append(dict(ameta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    checks={};result=dict(status='RUNNING_FACTORY_SHARED_SADDLES',source_sha256=pins,geometry=geometry,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),actor_meta=ameta,actor_owner=owners,
        retired=sorted(retired),recipes=recipes,positive_roots=roots,completed_static=[],completed_motion=[],
        N01_complete=False,native_changed=False,physical_pass=False,assembly_access_still_OPEN=True,
        connected_single_print_groups=print_members)
    priorfile=OUT/'n01-remaining-factory-space.json';prior=json.loads(priorfile.read_text());priorpf=ROOT/prior['pair_rows']
    assert sha(priorpf)==prior['pair_rows_sha256'];oldchecks=json.loads(gzip.decompress(priorpf.read_bytes()))
    result['unchanged_rear_curve_pairs_reused']=0
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(archive)==result['bundle_sha256'] and sha(pf)==result['pair_rows_sha256']
        checks=json.loads(gzip.decompress(pf.read_bytes()))
        with zipfile.ZipFile(archive) as z:
            for row in result['geometry']:
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());actors[row['name']]=s
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    for n,s in actors.items():
        if n in result['completed_static']:continue
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            if any(n in group and m in group for group in print_members.values()):
                checks[key]=dict(ok=True,member_of_proven_connected_single_print=True);continue
            same=owners[n]==owners.get(m);wire=n.startswith('Factory:');otherwire=m.startswith('Factory:')
            w=owners[n];mr=ameta[m] if m in actors else meta[m]
            minimum=minimum_for(n,ameta[n],m,mr)
            if same and n in original and m in original and not(wire or otherwire):
                checks[key]=dict(ok=True,same_received_rigid_kit_or_print_shoe_subset=True);continue
            if same and (n.startswith('InputGrip:') or m.startswith('InputGrip:')):
                if wire or otherwire:minimum=.2
                elif n.startswith('InputGrip:') and m.startswith('InputGrip:'):minimum=.15
            if n.endswith(':pad') and m==roots[w]['parent']:
                checks[key]=dict(ok=True,actual_positive_load_union_mm3=roots[w]['positive_common_mm3']);continue
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            if n in unchanged and m in fixed and key in oldchecks and oldchecks[key]['ok']:
                checks[key]=dict(oldchecks[key],unchanged_received_pair=True);result['unchanged_rear_curve_pairs_reused']+=1;continue
            a=s
            owncase=wire and m in ('Ref_Material_MTA_'+CASES[w]+'_0_0','Ref_Material_'+w+'_Joint_0_0')
            if owncase:
                c=s.common(t);assert c.isNull() or c.isValid();mouth=recipes[w]['parts'][0]['start'] if 'MTA_' in m else recipes[w]['parts'][-1]['end']
                direction=np.array([1.,0,0]) if w in WIRES[:2] else np.array([-1.,0,0])
                if 'MTA_' not in m:direction=-direction
                a=s.cut(Part.makeCylinder(3.,2.5,A.Vector(*mouth),A.Vector(*direction)))
                assert a.isValid() and a.Solids
            if m==world.bus['name']:
                a=a.copy();a.Placement=docs['inverse']*a.Placement;t=world.bus['original']
            row=dict(ok=(gap:=query.distance(a,t))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if t.Solids else profile_gap(a,t,mr.get('nominal_profile_radius_mm') or mr.get('radius_mm'),minimum)
            if owncase:row.update(ok=row['ok'] and c.Volume<1e-5,whole_nominal_mouth_contact_mm3=c.Volume,trimmed_only_own_first_or_last2p5=True)
            if same and n.startswith('InputGrip:') and m.startswith('InputGrip:'):
                c=s.common(t);assert c.isNull() or c.isValid();row.update(ok=c.Volume<1e-5,same_selected_tie_kit_nonpenetration_mm3=c.Volume)
            if not row['ok'] and t.Solids:
                _,pts,_=a.distToShape(t);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
            checks[key]=row
        result['completed_static'].append(n);save();print(n,'holds',len(result['failures']),flush=True)
        if time.monotonic()-tick>240:result['status']='PARTIAL_FACTORY_SADDLES_SAVED';save();return
    if not result['failures']:
        for n,s in actors.items():
            if n in result['completed_motion']:continue
            for pose in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                key=n+'|motion:'+pose['name']+':'+str(pose['pose']);a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
    result['status']='FACTORY_SHARED_SADDLES_HOLDS' if result['failures'] else 'FOUR_FACTORY_ROOTED_SADDLES_STATIC36_RECEIVED_ACCESS_OPEN'
    result['sampled_motion_not_continuous']=True;save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()

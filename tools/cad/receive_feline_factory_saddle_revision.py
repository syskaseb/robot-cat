"""Receive one causal whole-kit delta; keep R1 curves/parts and its evidence.

Rear bands lie after the fore crossing; their roots use the opposite end.
Two complete fore joint bays lose only non-floor raised ribs. No case-pose
iteration, new SKU, reduced foreign margin or native production claim.
"""
import gzip,hashlib,json,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_factory_saddle_plan import WIRES,CASES,box
from receive_feline_rrp_shared_height import load
from receive_feline_positive_service_deck import open_grip
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_underplate_return_gallery import minimum_for
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def owner(n):
    for w in WIRES:
        if n in ('Factory:'+w,'CustomPrefix:'+w,'Ref_Material_'+w+'_Joint_0_0','CaseBase:'+w+'_Joint','CaseCap:'+w+'_Joint') or n.startswith(tuple(p+w+s for p,s in [('CapScrew:', '_Joint:'),('CapNut:', '_Joint:'),('Seat:', ':'),('TieLoop:Seat:', ':'),('TieHead:Seat:', ':'),('InputGrip:', ':')])):return w


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-factory-saddle-plan.json';prior=json.loads(sf.read_text())
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    old=load(prior);actors={n:s.copy() for n,s in old.items()};ameta=prior['actor_meta'];recipes=prior['recipes']
    retired=set(prior['retired']);fixed={n:s for n,s in parts.items() if n not in retired}
    changed=set();panel='LowerBay:RearPanel';cutters=[]
    for w in WIRES[:2]:
        side=np.sign(recipes[w]['parts'][-1]['end'][1]);case=actors['Ref_Material_'+w+'_Joint_0_0'];b=case.BoundBox
        seat=actors['Seat:'+w+':custom'].BoundBox
        # Entire joint/custom-clamp X span, not a witness-sized nibble.
        y=sorted((side*26,side*28));cutters.append(box([b.XMin-1.25,y[0],-42],[seat.XMax+1.25,y[1],-37]))
    actors[panel]=parts[panel].cut(cutters[0]).cut(cutters[1]);ameta[panel]=meta[panel];changed.add(panel);retired.add(panel);fixed.pop(panel)
    assert actors[panel].isValid() and len(actors[panel].Solids)==1
    assert actors[panel].cut(parts[panel]).Volume<1e-5
    for w in WIRES[2:]:
        end=np.array(recipes[w]['parts'][-1]['end']);d=np.array([-1.,0,0]);side=np.array([0.,np.sign(end[1]),0]);start=end-10.25*d
        kit=open_grip(start,d,side,6.5);b=kit['pad'].BoundBox;xx=sorted((start[0],start[0]+2*d[0]))
        kit['pad']=kit['pad'].fuse(box([xx[0],b.YMin,-43.3],[xx[1],b.YMax,b.ZMin+1]))
        for k,s in kit.items():n='InputGrip:'+w+':'+k;actors[n]=s;changed.add(n);assert s.isValid() and len(s.Solids)==1
    printgroups={};rootproof={}
    for parent in ('LowerBay:ForePanel','LowerBay:RearPanel'):
        base=actors.get(parent,parts[parent]);members=[parent]
        for w in WIRES:
            if recipes[w]['root']['parent']!=parent:continue
            members+=['CaseBase:'+w+'_Joint','InputGrip:'+w+':pad']
            custom='Seat:'+w+':custom'
            if custom in actors:members.append(custom)
        unit=base.multiFuse([actors.get(n,parts.get(n)) for n in members[1:]])
        assert unit.isValid() and len(unit.Solids)==1,parent
        b=unit.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
        printgroups[parent]=members
        for n in members[1:]:
            c=actors.get(n,parts.get(n)).common(base);assert c.isValid() and c.Volume>1e-5,(n,parent)
            rootproof[n]=dict(parent=parent,actual_common_mm3=c.Volume)
    pf0=ROOT/prior['pair_rows'];assert sha(pf0)==prior['pair_rows_sha256'];previous=json.loads(gzip.decompress(pf0.read_bytes()))
    dest=OUT/'n01-factory-saddles-received.json';pf=dest.with_suffix('.pairs.json.gz');archive=dest.with_suffix('.breps.zip')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],pf0,Path(__file__))})
    checks={};result=dict(status='RUNNING_FACTORY_KIT_DELTA',source_sha256=pins,retired=sorted(retired),recipes=recipes,
        actor_meta=ameta,changed=sorted(changed),positive_roots=rootproof,single_connected_print_groups=printgroups,
        reused_unchanged_pairs=0,completed_static=[],completed_motion=[],N01_complete=False,physical_pass=False,native_changed=False,
        source_assumed_100mm_not_supplier_claim=True,assembly_access_still_OPEN=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pf)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));actors=load(result)
    else:
        geometry=[]
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(n,s) in enumerate(actors.items()):
                raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(ameta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        result.update(geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save();query=SolidQueries()
    for n,s in actors.items():
        if n in result['completed_static']:continue
        checks[n+'|outer']=previous[n+'|outer'] if n not in changed else outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            if any(n in g and m in g for g in printgroups.values()):checks[key]=dict(ok=True,proven_connected_print_features=True);continue
            aowner,bowner=owner(n),owner(m);same=aowner is not None and aowner==bowner
            wire=n.startswith('Factory:') or m.startswith('Factory:')
            if same and not wire and not n.startswith('InputGrip:') and not m.startswith('InputGrip:'):
                # Rigid-transform/source-shoe-subset proof. Changing the
                # prototype floor does NOT waive any new foreign material.
                checks[key]=dict(ok=True,unchanged_received_rigid_unit_or_own_shoe_material_subset=True);continue
            if n not in changed and m not in changed and key in previous and previous[key]['ok']:
                checks[key]=dict(previous[key],unchanged_pair_reused=True);result['reused_unchanged_pairs']+=1;continue
            mr=ameta[m] if m in actors else meta[m];minimum=minimum_for(n,ameta[n],m,mr)
            if same and (n.startswith('InputGrip:') or m.startswith('InputGrip:')):minimum=.2 if wire else .15
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            a,b=s,t;whole_common=None
            wn=n if n.startswith('Factory:') else m if m.startswith('Factory:') else None
            cn=m if wn==n else n;w=owner(wn) if wn else None
            ownmouth=wn and cn in ('Ref_Material_MTA_'+CASES[w]+'_0_0','Ref_Material_'+w+'_Joint_0_0')
            if ownmouth:
                cable=actors[wn];case=actors.get(cn,fixed.get(cn));whole_common=cable.common(case)
                d=np.array([1.,0,0]) if w in WIRES[:2] else np.array([-1.,0,0]);at=recipes[w]['parts'][0]['start']
                if 'MTA_' not in cn:at=recipes[w]['parts'][-1]['end'];d=-d
                a=cable.cut(Part.makeCylinder(3.,2.5,A.Vector(*at),A.Vector(*d)));b=case
            if m==world.bus['name']:
                a=a.copy();a.Placement=docs['inverse']*a.Placement;b=world.bus['original']
            row=dict(ok=(gap:=query.distance(a,b))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if b.Solids else profile_gap(a,b,mr.get('nominal_profile_radius_mm') or mr.get('radius_mm'),minimum)
            if ownmouth:assert whole_common.isNull() or whole_common.isValid();row.update(ok=row['ok'] and whole_common.Volume<1e-5,whole_mouth_contact_mm3=whole_common.Volume,only_nominal_own2p5mm_cap_trimmed=True)
            if same and n.startswith('InputGrip:') and m.startswith('InputGrip:'):
                c=s.common(t);assert c.isNull() or c.isValid();row.update(ok=c.Volume<1e-5,same_selected_nylon_kit_common_mm3=c.Volume)
            if not row['ok'] and b.Solids:
                _,pts,_=a.distToShape(b);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
            checks[key]=row
        result['completed_static'].append(n);save();print(n,'holds',len(result['failures']),flush=True)
        if time.monotonic()-tick>220:result['status']='PARTIAL_FACTORY_KIT_DELTA_SAVED';save();return
    if not result['failures']:
        for n,s in actors.items():
            if n in result['completed_motion']:continue
            for pose in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                if key in checks:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
            if time.monotonic()-tick>220:result['status']='PARTIAL_FACTORY_KIT_DELTA_SAVED';save();return
    result['status']='FACTORY_KIT_DELTA_HOLDS' if result['failures'] else 'FOUR_FACTORY_SADDLES_STATIC36_RECEIVED_ACCESS_OPEN'
    result['sampled_motion_not_continuous']=True;save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()

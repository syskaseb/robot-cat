"""One whole rear-joint bay chosen by the shared motion/length domain.

Move28 parts as complete kits, lengthen only two factory last straights,
root custom clamps by two2.5mm floor fingers. No further corner variants,
source-case moves, production native detail or blanket collision exemptions.
"""
import copy,gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_revision import owner
from receive_feline_factory_saddle_plan import CASES,box
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_underplate_return_gallery import minimum_for
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-factory-inputs-current-received.json';prior=json.loads(sf.read_text());old=load(prior);actors={n:s.copy() for n,s in old.items()}
    df=OUT/'n01-factory-rear-joint-bay-plan.json';domain=json.loads(df.read_text())
    for f in (prior,domain):
        for p,h in f['source_sha256'].items():assert sha(ROOT/p)==h,p
    delta=domain['chosen_whole_kit_shift_X_mm'];assert delta is not None and any(a<delta<b for a,b in domain['shared_intervals_X_mm'])
    members=set(domain['full_rear_kit_members']);assert len(members)==28
    effective={n:s for n,s in parts.items() if n not in prior['retired']};effective.update(actors)
    ameta=copy.deepcopy(prior['actor_meta']);recipes=copy.deepcopy(prior['recipes']);retired=set(prior['retired']);changed=set(members);roots={}
    for n in members:
        s=effective[n].copy();s.translate(A.Vector(delta,0,0));actors[n]=s
        ameta[n]=ameta.get(n,meta.get(n));retired.add(n)
    ext={}
    panel='LowerBay:ForePanel';floor=parts[panel].copy()
    for w in ('W044','W052'):
        p=recipes[w];last=p['parts'][-1];assert last['kind']=='line'
        oldtip=A.Vector(*last['end']);last['end'][0]+=delta;last['length_mm']-=delta
        p['guide_mm']-=delta;p['project_factory100_margin_mm']+=delta;p['joint_translation_mm']=[delta,0,0]
        assert p['project_factory100_margin_mm']>=1
        p['root']['full9_arclength_interval_mm']=[p['guide_mm']-10.25,p['guide_mm']-1.25]
        n='Factory:'+w;actors[n]=pipe(p['parts'],2.1);changed.add(n)
        ext[n]=Part.makeCylinder(2.1,-delta+.25,oldtip+A.Vector(.25,0,0),A.Vector(-1,0,0))
        assert old[n].cut(actors[n]).Volume<1e-5
        assert actors[n].cut(old[n].fuse(ext[n])).Volume<1e-5
        seat=actors['Seat:'+w+':custom'].BoundBox;side=1 if w=='W044' else -1
        yy=sorted((side*32,side*34.5));finger=box([seat.XMin-.25,yy[0],-44.3],[-49.25,yy[1],-42])
        assert finger.common(floor).Volume>1e-5
        floor=floor.fuse(finger)
    assert floor.isValid() and len(floor.Solids)==1;assert parts[panel].cut(floor).Volume<1e-5
    actors[panel]=floor;ameta[panel]=meta[panel];retired.add(panel);changed.add(panel)
    group=[panel]
    for w in ('W044','W052'):
        for n in ('CaseBase:'+w+'_Joint','Seat:'+w+':custom','InputGrip:'+w+':pad'):
            c=actors[n].common(floor);assert c.isValid() and c.Volume>1e-5,(n,'Missing rooted moved kit')
            roots[n]=dict(parent=panel,actual_common_mm3=c.Volume);group.append(n)
    unit=floor.multiFuse([actors[n] for n in group[1:]]);assert unit.isValid() and len(unit.Solids)==1
    b=unit.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
    fixed={n:s for n,s in parts.items() if n not in retired};query=SolidQueries()
    pf0=ROOT/prior['pair_rows'];assert sha(pf0)==prior['pair_rows_sha256'];previous=json.loads(gzip.decompress(pf0.read_bytes()))
    # Whole shifted kit has a sufficient positive separation certificate
    # for every current sampled motion; do not rerun its thousands of pairs.
    dest=OUT/'n01-factory-bay-layout-received.json';pf=dest.with_suffix('.pairs.json.gz');archive=dest.with_suffix('.breps.zip')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,pf0,ROOT/prior['bundle'],df,Path(__file__))})
    checks={};result=dict(status='RUNNING_WHOLE_FACTORY_BAY_LAYOUT',source_sha256=pins,recipes=recipes,
        retired=sorted(retired),actor_meta=ameta,changed=sorted(changed),positive_roots=roots,
        chosen_complete_rear_kit_shift_X_mm=delta,motion_domain_receipt=df.relative_to(ROOT).as_posix(),
        motion_domain_members=sorted(members),full_shifted_kit_motion_certified_by_actual_projection=True,
        connected_fore_panel_unit_solids=1,combined_print_envelope_mm=[b.XLength,b.YLength,b.ZLength],
        completed_static=[],completed_motion=[],reused_pairs=0,N01_complete=False,physical_pass=False,native_changed=False,
        factory100_is_project_assumption_not_supplier=True,assembly_tools_and_full_shared123_still_OPEN=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pf)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));actors=load(result)
    else:
        geometry=[]
        with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(n,s) in enumerate(actors.items()):
                oldrow=next((r for r in prior['geometry'] if r['name']==n),None)
                raw=src.read(oldrow['entry']) if n not in changed else s.exportBrepToString().encode()
                entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(ameta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        result.update(geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    for n,s in actors.items():
        if n in result['completed_static']:continue
        checks[n+'|outer']=previous[n+'|outer'] if n not in changed else outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            if n not in changed and m not in changed and key in previous:
                assert previous[key]['ok'],key;checks[key]=dict(previous[key],unchanged_pair_reused=True);result['reused_pairs']+=1;continue
            if n in group and m in group:checks[key]=dict(ok=True,proven_connected_print_features=True);continue
            aowner,bowner=owner(n),owner(m);same=aowner and aowner==bowner;wire=n.startswith('Factory:') or m.startswith('Factory:')
            if same and not wire:checks[key]=dict(ok=True,whole_received_kit_rigidly_translated=True);continue
            mr=ameta[m] if m in actors else meta[m];minimum=minimum_for(n,ameta[n],m,mr)
            if same and (n.startswith('InputGrip:') or m.startswith('InputGrip:')):minimum=.2
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            a,bb=s,t;wn=n if n.startswith('Factory:') else m if m.startswith('Factory:') else None;cn=m if wn==n else n;w=owner(wn) if wn else None
            ownmouth=wn and cn in ('Ref_Material_MTA_'+CASES[w]+'_0_0','Ref_Material_'+w+'_Joint_0_0')
            if ownmouth:
                a=actors[wn];bb=actors.get(cn,fixed.get(cn));c=a.common(bb);assert c.isNull() or c.isValid()
                at=recipes[w]['parts'][0]['start'];d=A.Vector(1,0,0) if w in ('W041','W042') else A.Vector(-1,0,0)
                if 'MTA_' not in cn:at=recipes[w]['parts'][-1]['end'];d=-d
                a=a.cut(Part.makeCylinder(3,2.5,A.Vector(*at),d))
            if m==world.bus['name']:a=a.copy();a.Placement=docs['inverse']*a.Placement;bb=world.bus['original']
            row=dict(ok=(gap:=query.distance(a,bb))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if bb.Solids else profile_gap(a,bb,mr.get('nominal_profile_radius_mm') or mr.get('radius_mm'),minimum)
            if ownmouth:row.update(ok=row['ok'] and c.Volume<1e-5,whole_nominal_mouth_contact_mm3=c.Volume)
            if n==panel or m==panel:
                pn,other=(n,m) if n==panel else (m,n)
                # New fingers lie outside all pre-existing named mates;
                # preserve the parent's known print/bearing interfaces only.
                oldkey=pn+'|'+other
                if other in prior['single_connected_print_groups'].get(panel,[]):row.update(ok=True,retained_parent_connected_print=True)
                elif other.startswith(('RootWebReserve1','RootWebReserve2','EndBay:CaseBase:W026','EndBay:CaseBase:W037','EndGrip:Factory:W026:pad','EndGrip:Factory:W037:pad')):
                    base=parts[panel].common(t if pn==n else s);new=(s if pn==n else t).common(t if pn==n else s)
                    assert new.isNull() or new.isValid();assert base.isNull() or base.isValid();row.update(ok=base.cut(new).Volume<1e-5 and new.Volume>1e-5,retained_print_root_common_mm3=new.Volume)
            if not row['ok'] and bb.Solids:
                _,pts,_=a.distToShape(bb);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
            checks[key]=row
        result['completed_static'].append(n);save();print(n,'holds',len(result['failures']),flush=True)
        if time.monotonic()-tick>220:result['status']='PARTIAL_WHOLE_FACTORY_BAY_SAVED';save();return
    if not result['failures']:
        for n in sorted(changed):
            if n in result['completed_motion']:continue
            if n in members:result['completed_motion'].append(n);continue
            s=ext.get(n,actors[n])
            for pose in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                if key in checks:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
            if time.monotonic()-tick>220:result['status']='PARTIAL_WHOLE_FACTORY_BAY_SAVED';save();return
    result['status']='WHOLE_FACTORY_BAY_HOLDS' if result['failures'] else 'WHOLE_FOUR_FACTORY_INPUT_BAY_STATIC36_RECEIVED_ACCESS_OPEN'
    result['motion_is_sampled_not_continuous']=True;save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()

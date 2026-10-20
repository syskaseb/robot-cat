"""Prototype case retention, not adhesive wire strain relief.

Retain selected VHB4905 .5mm and separate full wire grips. Two rear T18I
become spares; bought SKUs/order units stay unchanged. Delivered plastic
adhesion/temperature/pull qualification is mandatory phase2, not claimed here.
"""
import copy,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_plan import box
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def cradle(b,cap_bottom):
    floor=-44.3;top=cap_bottom-1.5;y0,y1=b.YMin,b.YMax;x0,x1=b.XMin,b.XMax
    features=[box([x0-2.6,y0-2.6,floor],[x1+2.6,y0-.2,top]),
        box([x0-2.6,y1+.2,floor],[x1+2.6,y1+2.6,top])]
    for a,c in ((x0+1,x0+4),(x1-4,x1-1)):
        features.append(box([a,y0-2.6,floor],[c,y1+2.6,b.ZMin-.2]))
    for a,c in ((x0-2.6,x0-.2),(x1+.2,x1+2.6)):
        for d,e in ((y0-2.6,y0+3),(y1-3,y1+2.6)):
            features.append(box([a,d,floor],[c,e,top]))
    s=features[0].multiFuse(features[1:]);assert s.isValid() and len(s.Solids)==1
    return s


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-body-head-clock.json';r=json.loads(sf.read_text());actors=load(r)
    observed=sf.with_name(sf.stem+'-scene.json');old=json.loads(observed.read_text())
    for record in (r,old):
        for p,h in record['source_sha256'].items():assert sha(ROOT/p)==h,p
    selection=BASE/'phase1-material-selection-r4.json';selected=json.loads(selection.read_text())
    stock=next(p for p in selected['materials'] if p['sku']=='3M VHB4905')
    assert selected['selected'] and stock['case_only'] and stock['nominal_installed_thickness_mm']==.5
    assert stock['selected_width_mm']==12 and stock['selected_length_mm']==33000 and stock['selected_roll_count']==1
    assert stock['additional_patch_mm']==[8,18,.5]
    removed={t[k] for code,t in r['body_ties'].items() if code in ('RL','RR') for k in ('band','head')}
    assert len(removed)==4
    for n in removed:actors.pop(n)
    floor='LowerBay:RearPanel';original=actors[floor].copy();newfloor=original.copy();recipes={};newnames=set()
    fm={p['name']:p for p in r['geometry']};groups=copy.deepcopy(r['print_groups']);query=SolidQueries()
    contracts={k:v for k,v in r['named_interface_pairs'].items() if not removed.intersection(k.split('|'))}
    for code,wire in (('RL','W041'),('RR','W042')):
        t=r['body_ties'][code];case=parts[t['case']];b=case.optimalBoundingBox(False,False);x,y=b.Center.x,b.Center.y
        pn='MTABond:'+code;cn='MTACradle:'+code
        patch=box([x-4,y-9,b.ZMin-.5],[x+4,y+9,b.ZMin])
        newfloor=newfloor.cut(box([x-4,y-9,b.ZMin-.5],[x+4,y+9,b.ZMin+.1]))
        actors[pn]=patch;actors[cn]=cradle(b,actors['CaseCap:'+wire+'_Joint'].BoundBox.ZMin)
        fm[pn]=dict(kind='adhesive_reservation',selected_SKU='3M VHB4905',body_retention_NOT_wire_strain_relief=True)
        fm[cn]=dict(kind='proposal_material',material_role='PETG_case_only_cradle')
        newnames.update((pn,cn));groups[floor].append(cn)
        topcoupon=box([x-4,y-9,b.ZMin],[x+4,y+9,b.ZMin+.01])
        recipes[code]=dict(case=t['case'],patch=pn,cradle=cn,patch_mm=[8,18,.5],nominal_bond_area_mm2=144,
            actual_case_land_coupon_area_mm2=case.common(topcoupon).Volume/.01,
            case_land_is_nominal_model_NOT_manufacturer_adhesion=True,selected_bought_SKUs_or_order_units_changed=False,
            adhesion_cleaning_peel_temperature_and_actual_plastic_phase2_gate=True,
            independent_wire_grips_unchanged=True,uninstalled_T18I_count_to_spares=1)
        assert abs(recipes[code]['actual_case_land_coupon_area_mm2']-144)<1e-4
    assert newfloor.isValid() and len(newfloor.Solids)==1
    added=newfloor.cut(original);assert (added.isNull() or added.isValid()) and added.Volume<1e-5
    actors[floor]=newfloor
    for code,p in recipes.items():
        patch=actors[p['patch']];b=patch.BoundBox
        coupon=box([b.XMin,b.YMin,b.ZMin-.01],[b.XMax,b.YMax,b.ZMin])
        p['actual_floor_land_coupon_area_mm2']=newfloor.common(coupon).Volume/.01
        p['minimum_local_floor_thickness_mm']=b.ZMin-newfloor.BoundBox.ZMin
        assert abs(p['actual_floor_land_coupon_area_mm2']-144)<1e-4
        assert p['minimum_local_floor_thickness_mm']>=1.8-1e-6
        root=actors[p['cradle']].common(newfloor);assert root.isValid() and root.Volume>1e-5
        p['cradle_floor_positive_overlap_mm3']=root.Volume
        for a,b,minimum in ((p['patch'],p['case'],0),(p['patch'],floor,0),(p['cradle'],p['case'],.2)):
            aa=actors[a];bb=actors.get(b,parts.get(b));c=aa.common(bb);assert c.isNull() or c.isValid()
            gap=query.distance(aa,bb);assert c.Volume<1e-5 and gap>=minimum-1e-6,(a,b,gap,c.Volume)
            contracts['|'.join(sorted((a,b)))]=dict(ok=True,gap_mm=gap,minimum_mm=minimum,whole_common_mm3=c.Volume,
                exact_case_bond_or_insulating_cradle_pair=[a,b],foreign_margin_NOT_changed_mm=1.25)
    for n,p in r['positive_roots'].items():
        if p['parent']==floor:assert actors['ArcGrip:'+n+':pad'].common(newfloor).Volume>1e-5
    unit=newfloor.multiFuse([actors[n] if n in actors else parts[n] for n in groups[floor] if n!=floor])
    assert unit.isValid() and len(unit.Solids)==1;ub=unit.BoundBox;assert max(ub.XLength,ub.YLength,ub.ZLength)<250
    dest=OUT/'n01-MTA-bonded-cradles.json';assert not dest.exists();archive=dest.with_suffix('.breps.zip')
    changed={floor}|newnames|removed;before={p['name']:p for p in r['geometry']};geometry=[]
    with zipfile.ZipFile(ROOT/r['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as target:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode() if n in changed else src.read(before[n]['entry'])
            if n not in changed:assert hashlib.sha256(raw).hexdigest()==before[n]['sha256']
            entry=str(i)+'.brep';target.writestr(entry,raw);geometry.append(dict(fm[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/r['bundle'],observed,ROOT/old['pair_rows'],selection,Path(__file__))})
    result=dict(r,status='RUNNING_BONDED_CRADLE_REST',source_sha256={**r['source_sha256'],**pins},geometry=geometry,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),changed_actors=sorted(changed),removed_actor_aliases=sorted(removed),
        print_groups=groups,body_ties={c:t for c,t in r['body_ties'].items() if c not in recipes},bonded_rear_cases=recipes,
        additional_selected_VHB_draw_mm=36,selected_VHB_roll_count_NOT_changed=1,uninstalled_rear_T18I_to_spares=2,
        floor_change_material_subset=True,floor_new_material_mm3=added.Volume,rear_print_union_solids=1,
        rear_print_envelope_mm=[ub.XLength,ub.YLength,ub.ZLength],named_interface_pairs=contracts,
        byte_identical_actors_from_prior=67,reuse_scene=dict(path=observed.relative_to(ROOT).as_posix(),sha256=sha(observed)),
        completed_rest=[n for n in r['completed_rest'] if n not in removed],completed_static=[],completed_motion=[],rest_checks={},outline_checks={},failures=[],
        digital_nominal_retention_NOT_adhesive_strength_qualification=True,N01_complete=False,native_changed=False,physical_pass=False)
    for n in sorted(newnames):
        s=actors[n];result['outline_checks'][n]=outer_margin(s,docs['outer'])
        if not result['outline_checks'][n]['ok']:result['failures'].append(n+'|outer');break
        for name,material in world.rest.items():
            if bbox_lower_bound(s.BoundBox,material.BoundBox)>=1.25:continue
            gap=query.distance(s,material);key=n+'|rest:'+name
            result['rest_checks'][key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:result['failures'].append(key);break
        if result['failures']:break
        result['completed_rest'].append(n)
    result.update(status='BONDED_CRADLE_OUTLINE_OR_REST_HOLD' if result['failures'] else 'COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN',
        checks=len(result['rest_checks']),worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],len(actors),'rest',len(result['completed_rest']),result['failures'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()

"""One common four-body T18I contract, FL alternate collar/outboard head.

Old case-band models used .8mm despite selected1.2mm nominal stock. Correct
four complete loops/head budgets together. Only FL collar/head placement
changes; bought cases, all wires, M2 and feet remain rigidly unchanged.
"""
import copy,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_plan import box
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,_=compose()
    sf=OUT/'n01-MTA-full-band-slots.json';prior=json.loads(sf.read_text());actors=load(prior)
    scene=sf.with_name(sf.stem+'-scene.json');observed=json.loads(scene.read_text())
    assert observed['failures']==['CaseCap:W044_Joint|CaseTie:FL']
    for record in (prior,observed):
        for p,h in record['source_sha256'].items():assert sha(ROOT/p)==h,p
    ref=ROOT/'hardware/reference/cable-ties/t18i-111-02370/head-envelope.json';stock=json.loads(ref.read_text())
    assert stock['nominal_page_mm']['strap_width']==2.5 and stock['nominal_page_mm']['strap_thickness']==1.2
    effective={n:s for n,s in parts.items() if n not in prior['retired']};effective.update(actors)
    fm={**meta,**{r['name']:r for r in prior['geometry']}};retired=set(prior['retired']);changed=set();ties={};contracts={}
    query=SolidQueries();target=effective['CaseTie:FR'].BoundBox.Center.x
    for code in ('FL','FR','RL','RR'):
        name='CaseTie:'+code;head=name+'Head';case='Ref_Material_MTA_'+code+'_0_0';b=effective[case].optimalBoundingBox(False,False)
        station=target if code=='FL' else effective[name].BoundBox.Center.x
        assert b.XMin+1.25<station<b.XMax-1.25
        outer=box([station-1.25,b.YMin-1.4,b.ZMin-1.4],[station+1.25,b.YMax+1.4,b.ZMax+1.4])
        inner=box([station-1.45,b.YMin-.2,b.ZMin-.2],[station+1.45,b.YMax+.2,b.ZMax+.2])
        band=outer.cut(inner);assert band.isValid() and len(band.Solids)==1
        outward=code=='FL';side=1 if b.Center.y>0 else -1
        # Retain three original inboard head sides; FL changes to outboard
        # so the two fore heads do not collide at the same axial collar.
        radial=side if outward else -side
        face=b.YMax+1.4 if radial>0 else b.YMin-1.4
        ylo,yhi=(face,face+4.3) if radial>0 else (face-4.3,face)
        h=box([station-2.5,ylo,b.Center.z-2.65],[station+2.5,yhi,b.Center.z+2.65])
        union=band.fuse(h);assert union.isValid() and len(union.Solids)==1
        c=band.common(h);assert c.isNull() or c.isValid();assert c.Volume<1e-5
        perimeter=2*(b.YLength+b.ZLength+3.2);assert perimeter<=stock['existing_working_loop_budget_mm']
        parent='LowerBay:'+('ForePanel' if b.Center.x<20 else 'RearPanel')
        for n,s in ((name,band),(head,h)):
            actors[n]=s;effective[n]=s;changed.add(n);retired.add(n)
            fm[n]=dict(kind='tie_reservation',material_role='selected_T18I_nylon_budget',retention_owner=case)
        ties[code]=dict(band=name,head=head,case=case,parent=parent,station_X_mm=station,
            previous_station_X_mm=parts[name].BoundBox.Center.x,head_radial_sign=radial,
            selected_stock=stock['selected_part'],selected_quantity_NOT_changed=True,
            band_nominal_thickness_mm=1.2,band_nominal_width_mm=2.5,
            full_head_budget_mm=[5,4.3,5.3],nominal_rectangular_centreline_loop_mm=perimeter,
            loop_budget_mm=stock['existing_working_loop_budget_mm'],stock_length_NOT_usable_loop_mm=145,
            body_tightening_tolerance_and_actual_lid_service_phase2=True)
        contracts['|'.join(sorted((name,head)))]=dict(ok=True,minimum_mm=0,whole_common_mm3=c.Volume,
            exact_same_T18I_budget_unit=[name,head],unit_fuse_solids=1,foreign_margin_NOT_changed_mm=1.25)
        for n in (name,head):
            common=actors[n].common(effective[case]);assert common.isNull() or common.isValid()
            gap=query.distance(actors[n],effective[case]);assert common.Volume<1e-5 and gap>=.2-1e-6
            contracts['|'.join(sorted((n,case)))]=dict(ok=True,gap_mm=gap,minimum_mm=.2,whole_common_mm3=common.Volume,
                exact_own_body_insulating_retention_pair=[n,case],foreign_margin_NOT_changed_mm=1.25)
    roots=copy.deepcopy(prior['positive_roots']);floor_proofs={}
    for parent,members in prior['print_groups'].items():
        before=actors[parent];floor=before.copy()
        for tie in ties.values():
            if tie['parent']!=parent:continue
            for n in (tie['band'],tie['head']):
                b=actors[n].BoundBox;floor=floor.cut(box([b.XMin-.2,b.YMin-.2,b.ZMin-.2],[b.XMax+.2,b.YMax+.2,b.ZMax+.2]))
        assert floor.isValid() and len(floor.Solids)==1
        added=floor.cut(before);assert added.isNull() or added.isValid();assert added.Volume<1e-5
        actors[parent]=floor;effective[parent]=floor;changed.add(parent)
        unit=floor.multiFuse([effective[n] for n in members if n!=parent]);assert unit.isValid() and len(unit.Solids)==1
        b=unit.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
        floor_proofs[parent]=dict(new_material_outside_old_mm3=added.Volume,removed_mm3=before.cut(floor).Volume,
            connected_print_solids=1,print_envelope_mm=[b.XLength,b.YLength,b.ZLength],rest_clearance_inherited_by_material_subset=True)
        for w,p in roots.items():
            if p['parent']!=parent:continue
            c=actors['ArcGrip:'+w+':pad'].common(floor);assert c.isValid() and c.Volume>1e-5;p['parent_actual_overlap_mm3']=c.Volume
            for suffix in ('band','head'):
                n='ArcGrip:'+w+':'+suffix;c=actors[n].common(floor);assert c.isNull() or c.isValid()
                gap=query.distance(actors[n],floor);assert c.Volume<1e-5 and gap>=.2-1e-6
                contracts['|'.join(sorted((n,parent)))]=dict(ok=True,gap_mm=gap,minimum_mm=.2,whole_common_mm3=c.Volume,
                    exact_own_nylon_slot_pair=[n,parent],foreign_margin_NOT_changed_mm=1.25)
        for tie in ties.values():
            if tie['parent']!=parent:continue
            for n in (tie['band'],tie['head']):
                c=actors[n].common(floor);assert c.isNull() or c.isValid();gap=query.distance(actors[n],floor)
                assert c.Volume<1e-5 and gap>=.2-1e-6
                contracts['|'.join(sorted((n,parent)))]=dict(ok=True,gap_mm=gap,minimum_mm=.2,whole_common_mm3=c.Volume,
                    exact_own_body_retention_slot_pair=[n,parent],foreign_margin_NOT_changed_mm=1.25)
    dest=OUT/'n01-MTA-body-retention.json';assert not dest.exists();archive=dest.with_suffix('.breps.zip');geometry=[]
    previous={r['name']:r for r in prior['geometry']}
    with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode() if n in changed else src.read(previous[n]['entry'])
            if n not in changed:assert hashlib.sha256(raw).hexdigest()==previous[n]['sha256']
            entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(fm[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],scene,ROOT/observed['pair_rows'],ref,Path(__file__))})
    result=dict(prior,status='RUNNING_MTA_BODY_RETENTION_REST',source_sha256={**prior['source_sha256'],**pins},geometry=geometry,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),positive_roots=roots,retired=sorted(retired),
        named_interface_pairs=contracts,changed_actors=sorted(changed),body_ties=ties,floor_subset_proofs=floor_proofs,
        reuse_scene=dict(path=scene.relative_to(ROOT).as_posix(),sha256=sha(scene)),
        completed_rest=list(prior['completed_rest']),completed_static=[],completed_motion=[],checks=0,failures=[],rest_checks={},
        physical_aliases_replaced_not_new_parts=sorted(n for n in changed if n.startswith('CaseTie:')),
        N01_complete=False,native_changed=False,physical_pass=False)
    for n in sorted(n for n in changed if n.startswith('CaseTie:')):
        for m,s in world.rest.items():
            if bbox_lower_bound(actors[n].BoundBox,s.BoundBox)>=1.25:continue
            gap=query.distance(actors[n],s);result['rest_checks'][n+'|rest:'+m]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:result['failures'].append(n+'|rest:'+m);break
        if result['failures']:break
        result['completed_rest'].append(n)
    result['status']='MTA_BODY_RETENTION_REST_HOLD' if result['failures'] else 'COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN'
    result.update(checks=len(result['rest_checks']),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    print(result['status'],len(actors),len(result['completed_rest']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()

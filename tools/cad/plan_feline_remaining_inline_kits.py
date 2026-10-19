"""Two actual retained FHAC cases with BOTH factory/custom exits together.

Complete four independent9mm jacket grips on each side of the20mm splice
sleeve; no invented connector at the solder overlap. OD/R/adhesive/load and
delivered factory length remain explicit prototype assumptions/fit gates.
This plan does not award N01 or change selected native/bought parts.
"""
import hashlib,json,math,os,sys,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_atomic_save import save_json
from feline_s1_flexible_fans import saddle_shapes
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement,matrix_rotation
from feline_common_retention_roots import archived
from feline_bank_selected_t18i import dimensions


def material(upper=False,selected_head=False,body_closure=False):
    proof=json.loads((OUT/'n01-global-case-candidates-received.json').read_text())
    contract=json.loads((OUT/'n01-all-extra-interface-contract.json').read_text())
    ends={e['endpoint']:e for s in contract['sections'] for e in s['ends']}
    _,source,rows=packed(OUT/'n01-fore-service-macro.json');parts={};kinds={};recipes=[]
    for cid,role in ((2,'F_HP'),(3,'F_TY')):
        case=source['RearFHAC:'+role];r=next(r for r in proof['completed_candidates'] if r['id']==cid)
        rot=matrix_rotation(r['source_axis_to_world_axis']);centre=np.asarray(r['centre_mm'])
        assert np.allclose(list(case.BoundBox.Center),centre)
        for side in ('in','out'):
            endpoint=role+'.'+side;e=ends[endpoint];q=centre+rot@e['local_point_mm'];d=rot@e['departure_axis']
            b=np.array([0.,0.,1.]) if upper else np.array([0.,-1. if centre[1]>0 else 1.,0.]);assert abs(d@b)<1e-6
            theta=math.radians(60);R=6.;start=q+9*d
            at=lambda t:start+R*math.sin(t)*d+R*(1-math.cos(t))*b
            end=at(theta);tangent=math.cos(theta)*d+math.sin(theta)*b;tip=end+14*tangent
            path=Part.Wire([Part.makeLine(A.Vector(*q),A.Vector(*start)),Part.Arc(A.Vector(*start),A.Vector(*at(theta/2)),A.Vector(*end)).toShape(),Part.makeLine(A.Vector(*end),A.Vector(*tip))])
            factory=path.makePipeShell([Part.Wire([Part.makeCircle(1.7,A.Vector(*q),A.Vector(*d))])],True,False)
            # The physical8mm lap is inside the20mm insulating sleeve.
            sleeve=Part.makeCylinder(2.4,20,A.Vector(*end),A.Vector(*tangent))
            custom=Part.makeCylinder(1.55,26,A.Vector(*(tip-8*tangent)),A.Vector(*tangent))
            prefix=endpoint+':'
            def put(n,s,kind):
                assert s.isValid() and s.Solids;parts[prefix+n]=s;kinds[prefix+n]=kind
            put('factory',factory,'proposal_wire');put('sleeve',sleeve,'insulation_reservation');put('custom',custom,'proposal_wire')
            for which,p,axis,radius in (('factory',q,d,1.7),('custom',tip+9*tangent,tangent,1.55)):
                row=dict(grip_start_mm=p.tolist(),grip_axis=axis.tolist(),jacket_radius_mm=radius,head_follows_strap=True)
                # One common opposite closing face for all four CUSTOM
                # grips; no scalar nudge or wire/case/radius change.
                kit=saddle_shapes(row,0,270 if body_closure and which=='custom' else 90)
                if selected_head:
                    # Full selected drawing maxima in the ACTUAL strap frame.
                    # Source stock145x2.5 is unchanged, never a smaller SKU.
                    D,H,E=dimensions();old=kit['head_budget'];land=A.Vector(*p)+A.Vector(*axis)*4.5
                    radial=old.Solids[0].CenterOfMass-land;t=A.Vector(*axis)
                    radial=radial-t*radial.dot(t);distance=radial.Length;radial.normalize();head_tangent=t.cross(radial)
                    m=A.Matrix()
                    for i in range(3):
                        for j,col in enumerate((radial,head_tangent,t)):setattr(m,f'A{i+1}{j+1}',col[i])
                    head=Part.makeBox(D,H,E,A.Vector(-D/2,-H/2,-E/2));head.Placement=A.Placement(land+radial*(distance-3+D/2),A.Rotation(m))
                    outside=head.copy().cut(old.copy());assert outside.isNull() or outside.isValid();assert outside.Volume<1e-7
                    kit['head_budget']=head
                for n,s in kit.items():put(which+':'+n,s,'project_stock_reservation' if 'budget' in n else 'proposal_material')
            recipes.append(dict(endpoint=endpoint,case='RearFHAC:'+role,point_mm=q.tolist(),departure_axis=d.tolist(),bend_unit=b.tolist(),
                factory_OD_project_mm=3.4,custom_OD_project_mm=3.1,minimum_R_project_mm=R,first_mm=9,sweep_degrees=60,
                factory_grip9_mm=[q.tolist(),start.tolist()],sleeve20_mm=[end.tolist(),(end+20*tangent).tolist()],
                custom_grip9_mm=[(tip+9*tangent).tolist(),(tip+18*tangent).tolist()],routing_exit_mm=(tip+18*tangent).tolist(),routing_exit_axis=tangent.tolist(),
                nominal_external_factory_cut_mm=9+R*theta+14,available_factory_min_reference_mm=84.5,
                family='ALL_FOUR_EXITS_UPPER_PLANE' if upper else 'ALL_FOUR_EXITS_INBOARD_PLANE',
                factory_cut_not_all_available_length_coiled=True,solder_overlap_mm=8,actual_supplier_OD_R_and_cuttable_length_delivery_gate=True))
    assert len(recipes)==4
    # Before loading/querying the large world, qualify all unchanged own
    # jacket/stock interfaces together. The8mm solder lap and sleeve are
    # intentional envelopes, not foreign clearances.
    for recipe in recipes:
        names=[n for n in parts if n.startswith(recipe['endpoint']+':')]
        for i,n in enumerate(names):
            for other in names[i+1:]:
                if kinds[n] in ('proposal_wire','insulation_reservation') and kinds[other] in ('proposal_wire','insulation_reservation'):continue
                if bbox_lower_bound(parts[n].BoundBox,parts[other].BoundBox)>1e-7:continue
                common=parts[n].copy().common(parts[other].copy());assert common.isNull() or common.isValid()
                assert common.Volume<1e-7,('Intrinsic source-kit material interference',n,other,common.Volume)
    return parts,kinds,recipes


def main():
    tick=time.monotonic();body_closure='--body-closure' in sys.argv;selected='--selected-head' in sys.argv or body_closure;upper='--upper' in sys.argv or selected
    parts,kinds,recipes=material(upper,selected,body_closure);world,fixed=world_context()
    current=OUT/'n01-shared54-current.json';doc=json.loads(current.read_text());proposal=archived(doc,'parts')
    frame=OUT/'n01-channelled-foundation-static.json';f=json.loads(frame.read_text());assert f['status']=='COMMON_FOUNDATION_CLEAR_NOT_ALL_ROOTS'
    obstacles={**fixed,**proposal,**{'CurrentFoundation:'+n:s for n,s in archived(f,'geometry').items()}}
    for n in ('StructureReserve:BankBed-1','StructureReserve:BankBed1'):obstacles.pop(n,None)
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'));query=SolidQueries()
    files=(current,frame,Path(__file__),OUT/'n01-global-case-candidates-received.json',OUT/'n01-all-extra-interface-contract.json',OUT/'n01-fore-service-macro.json')
    files=files+(ROOT/'hardware/reference/cable-ties/t18i-111-02370/head-envelope.json',Path(__file__).with_name('feline_t18i_selected_head.py'),Path(__file__).with_name('feline_bank_selected_t18i.py'))
    if selected:files=files+(OUT/('n01-remaining-inline-selected-full-kits.json' if body_closure else 'n01-remaining-inline-upper-full-kits.json'),)
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files};dest=OUT/('n01-remaining-inline-body-closure.json' if body_closure else 'n01-remaining-inline-selected-full-kits.json' if selected else 'n01-remaining-inline-upper-full-kits.json' if upper else 'n01-remaining-inline-full-kits.json')
    result=dict(status='RUNNING_TWO_WHOLE_INLINE_KITS',source_sha256=pins,world_source_sha256=world.pins,
        parts={},recipes=recipes,errors=[],N01_complete=False,physical_pass=False,native_changed=False,selected=False)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins and result['world_source_sha256']==world.pins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    elif selected:
        parent_file=OUT/('n01-remaining-inline-selected-full-kits.json' if body_closure else 'n01-remaining-inline-upper-full-kits.json');parent=json.loads(parent_file.read_text())
        assert parent['recipes']==recipes and parent['world_source_sha256']==world.pins
        for p in files:
            n=p.relative_to(ROOT).as_posix()
            if p==Path(__file__) or n not in parent['source_sha256']:continue
            assert parent['source_sha256'][n]==sha(p),n
        oldparts,_,oldrecipes=material(True,body_closure,False);assert oldrecipes==recipes
        changed={n for n in parts if n.endswith(':head_budget') and (not body_closure or ':custom:' in n)}
        equivalence=[]
        for n,s in parts.items():
            old=oldparts[n];outside=s.copy().cut(old.copy());assert outside.isNull() or outside.isValid()
            if not body_closure or n not in changed:assert outside.Volume<1e-7
            if n not in changed:
                removed=old.copy().cut(s.copy());assert removed.isNull() or removed.isValid();assert removed.Volume<1e-7
            equivalence.append(dict(name=n,source_outside_parent_mm3=outside.Volume,changed_only_full_selected_head=n in changed))
            prior=parent['parts'][n]
            # Both source and every changed target are unchanged or subsets.
            # Reuse positives only; every former negative remains a new query.
            result['parts'][n]=dict(kind=kinds[n],pairs={k:v for k,v in prior['pairs'].items() if v['ok'] and not (body_closure and (n in changed or k.removeprefix('fixed:NewInline:') in changed))},
                positive_parent_receipts_only=True)
            if 'failure' in prior and prior['failure'] is None and not (body_closure and n in changed):result['parts'][n]['failure']=None
        result['geometry_reuse']=dict(parent=parent_file.relative_to(ROOT).as_posix(),parent_sha256=sha(parent_file),
            parts=equivalence,unchanged=32 if body_closure else 28,selected_head_subsets=0 if body_closure else 8,
            complete_changed_heads_recheck=4 if body_closure else 0,negative_receipts_never_promoted=True)
        result['source_sha256'][parent_file.relative_to(ROOT).as_posix()]=sha(parent_file)
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def check(name,s,r):
        pairs=r.setdefault('pairs',{})
        def get(k,op):
            if time.monotonic()-tick>235:raise TimeoutError('Completed actual inline part interfaces saved')
            if k not in pairs:pairs[k]=op();save()
            return pairs[k]['ok']
        def skin():
            common=s.copy().cut(outer);assert common.isNull() or common.isValid();gap=s.distToShape(outer.Shells[0])[0]
            return dict(ok=common.Volume<1e-5 and gap>=3.25-1e-6,outside_mm3=common.Volume,gap_mm=gap)
        if not get('outer',skin):return 'outer'
        own=next(x for x in recipes if name.startswith(x['endpoint']+':'))
        for n,t in {**obstacles,**{'NewInline:'+k:v for k,v in parts.items() if k!=name}}.items():
            # The sleeve intentionally encloses the factory/custom8mm lap;
            # saddles are still tested against their full jackets and stock.
            other=n.removeprefix('NewInline:');same=other.startswith(own['endpoint']+':')
            if same and ({name.split(':')[-1],other.split(':')[-1]} & {'sleeve'}) and kinds[name] in ('proposal_wire','insulation_reservation') and kinds.get(other) in ('proposal_wire','insulation_reservation'):continue
            if same and {name.split(':')[-1],other.split(':')[-1]}=={'factory','custom'}:continue
            minimum=pair_spacing('Inline:'+name,dict(kind=kinds[name]),n,dict(kind=kinds.get(other,world.meta.get(n,{}).get('kind','proposal_material'))))
            # Deliberate no-penetration start mate at this OWN case face;
            # never waive the other fuse, other hardware or a root loadpath.
            if n==own['case']:minimum=0
            # SAME physical grip: nylon touches its own jacket/saddle and
            # head meets its band. Check actual no penetration, not an airgap.
            # Every foreign wire/stock/component retains its normal margin.
            if same:minimum=0
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>max(minimum,1e-7):continue
            def exact():
                q,target=s,t
                if n==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;target=world.bus['original']
                if minimum==0:
                    common=q.copy().common(target.copy());assert common.isNull() or common.isValid()
                    return dict(ok=common.Volume<1e-7,positive_common_mm3=common.Volume,required_mm=0,interface='own_whole_jacket_or_stock_no_penetration')
                gap=query.distance(q,target);return dict(ok=gap>=minimum-1e-6,gap_mm=gap,required_mm=minimum)
            if not get('fixed:'+n,exact):return 'fixed:'+n
        for p in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            def moving():
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement;gap=query.distance(q,world.rest[p['name']])
                return dict(ok=gap>=1.25-1e-6,gap_mm=gap,required_mm=1.25)
            if not get('motion:'+p['name']+':'+str(p['pose']),moving):return 'motion:'+p['name']+':'+str(p['pose'])
        return None
    try:
        for n,s in parts.items():
            row=result['parts'].setdefault(n,dict(kind=kinds[n]))
            if 'failure' not in row:row['failure']=check(n,s,row);save();print('Whole inline',n,row['failure'],flush=True)
        result['status']='TWO_WHOLE_INLINE_KITS_RECEIVED_ROOTS_CORRIDORS_OPEN' if all(r['failure'] is None for r in result['parts'].values()) else 'TWO_WHOLE_INLINE_KITS_REJECTED_REASSESS_WHOLE_SOURCE_BAY'
    except TimeoutError as exc:result.update(status='PARTIAL_TWO_WHOLE_INLINE_KITS',slice_note=str(exc))
    except Exception as exc:result['status']='TWO_WHOLE_INLINE_KITS_ERROR';result['errors'].append(repr(exc))
    if result['status']=='TWO_WHOLE_INLINE_KITS_RECEIVED_ROOTS_CORRIDORS_OPEN':
        archive=dest.with_suffix('.breps.zip');geometry=[]
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for n,s in parts.items():
                raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
                geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=kinds[n]))
        result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),geometry=geometry)
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],errors=result['errors'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()

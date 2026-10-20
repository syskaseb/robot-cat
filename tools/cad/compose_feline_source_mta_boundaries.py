"""Current source/MTA overlay over the immutable246-end register.

Read only received BReps, no new routes/supports and no N01 point. In
particular a source wire cap does NOT qualify the still-held shared shelf.
"""
import json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_existing_lower_caps import current as parent
from compose_feline_integrated_boundaries import apply_updates
from compose_feline_output_boundaries import cap_at
from receive_feline_rrp_shared_height import load
from receive_feline_access_stack_motion import shapes
from feline_source_saddles import segment
from feline_atomic_save import save_json


def current():
    base,rows,files=parent();f=OUT/'n01-current-source-MTA-boundary-overlay.json';r=json.loads(f.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return base,apply_updates(rows,r['updates']),(*files,f)


def main():
    tick=time.monotonic();dest=OUT/'n01-current-source-MTA-boundary-overlay.json'
    assert not dest.exists(),'Receive existing overlay, do not regenerate'
    base,rows,files=parent();index={e['id']:e for e in rows}
    sf=OUT/'n01-F0-access-stack.json';src=json.loads(sf.read_text());assert not src['failures']
    wf=OUT/'n01-F0-access-stack-motion.json';motion=json.loads(wf.read_text());assert not motion['failures'] and len(motion['completed_motion'])==7
    mf=OUT/'n01-MTA-low-stop-cradles.json';m=json.loads(mf.read_text());assert not m['failures']
    mwf=OUT/'n01-MTA-low-stop-cradles-scene.json';mw=json.loads(mwf.read_text())
    assert not mw['failures'] and len(mw['completed_static'])==len(mw['completed_motion'])==72
    assert mw['source_sha256'][mf.relative_to(ROOT).as_posix()]==sha(mf)
    actors={**shapes(src),**load(m)};updates={};proofs={}
    def put(eid,owner,parts,radius,whole,grip=None):
        assert eid in index;side=eid.rsplit('/',1)[1];first,last=segment(parts[0]),segment(parts[-1])
        p=first.valueAt(first.FirstParameter);q=last.valueAt(last.LastParameter)
        d=first.tangentAt(first.FirstParameter);t=last.tangentAt(last.LastParameter)
        mouth=p if side=='start' else q;departure=d if side=='start' else -t
        cap=cap_at(actors[owner],list(mouth),list(-d if side=='start' else t),radius)
        if not whole:cap_at(actors[owner],list(q),list(t),radius)
        updates[eid]=dict(point_mm=list(mouth),departure_axis=list(departure),
            routing_exit_mm=list(mouth if whole else q),routing_exit_axis=list(departure if whole else t),
            prefix_geometry_owner=owner,source_prefix_length_mm=actors[owner].Volume/(3.141592653589793*radius**2),
            actual_saved_cap_radius_mm=radius,grip_length_mm=9,
            routing_boundary_status='CURRENT_RECEIVED_COMPLETE_FACTORY_SOURCE' if whole else 'CURRENT_RECEIVED_SOURCE_OR_MTA_PREFIX_EXIT',
            full_middle_route_accepted=whole,nominal_supplier_fit_still_phase2=True,
            source_restraint_shared_shelf_NOT_accepted=True)
        if grip:updates[eid]['support_owner']=grip
        proofs[eid]=cap
    for w,r in m['factory_recipes'].items():
        for side in ('start','end'):put(w+'/factory/'+side,'Factory:'+w,r['parts'],2.1,True)
        c=m['recipes']['CustomPrefix:'+w]
        put(w+'/custom/start','CustomPrefix:'+w,c['parts'],2.1,False,'ArcGrip:'+w+':pad')
    for stem,owner,whole,radius,grip in (
        ('W075/retained0','W075_factory',True,1.55,'SourceGrip:W075:pad'),
        ('W076/retained0','W076_factory',True,1.55,'SourceGrip:F0OUT:pad'),
        ('W001/retained0','W001_ground_prefix',False,1.55,'SourceGrip:GROUND:pad'),
        ('W076/retained1','W076_custom_prefix',False,2.1,'SourceGrip:POSTOUT:pad')):
        for side in (('start','end') if whole else ('start',)):
            put(stem+'/'+side,owner,src['recipes'][owner]['parts'],radius,whole,grip)
    resolved=apply_updates(rows,updates)
    assert len(resolved)==246 and len(base['portions'])==123 and len(updates)==18
    assert [e['id'] for e in resolved]==[e['id'] for e in rows]
    sources=(*files,sf,wf,ROOT/src['bundle'],mf,mwf,ROOT/m['bundle'],Path(__file__))
    r=dict(status='CURRENT_SOURCE_AND_MTA_CAPS_COMPOSED_NOT_FULL_N01',updates=updates,
        actual_cap_proofs=proofs,all123_identities_preserved=True,all246_end_ids_preserved=True,
        logical_None_boundaries_not_invented=True,selected_SKUs_changed=False,native_changed=False,
        support_assembly_corridor_capacity_OPEN=True,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,r);print(r['status'],len(updates),r['worker_seconds'],flush=True)


if __name__=='__main__':main()

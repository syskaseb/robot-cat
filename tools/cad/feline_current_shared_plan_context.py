"""One reproducible CURRENT N01 planning scene, not N01 acceptance.

The main-hung parent alone omits later MTA/source/U1/HP layers. Keep their
identity/retirement graph explicit, bind every loaded archive, and refresh
metadata bounds from actual shapes. Never copy old R5 bounds onto new wires.
"""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from receive_feline_existing_hp_source_delta import RETIRED as HP_RETIRED


def compose(base_context=None):
    if base_context is None:
        from feline_main_hung_context import compose as parent
        base_context=parent()
    world,base,oldmeta,pins,docs=base_context
    parts=dict(base);meta={n:dict(r) for n,r in oldmeta.items()};pins=dict(pins);owners={}
    def overlay(filename,retire=(),data=None):
        f=OUT/filename;r=json.loads(f.read_text());packet=data(r) if data else r
        assert not r.get('failures'),filename
        actors=load(packet)
        for n in retire or r.get('retired',[]):parts.pop(n,None);meta.pop(n,None)
        records={g['name']:g for g in packet['geometry']}
        for n,s in actors.items():
            parts[n]=s;meta[n]=dict(records[n]);owners[n]=f.relative_to(ROOT).as_posix()
        pins[f.relative_to(ROOT).as_posix()]=sha(f);archive=ROOT/packet['bundle']
        assert sha(archive)==packet['bundle_sha256'];pins[archive.relative_to(ROOT).as_posix()]=sha(archive)
        return r
    mta=overlay('n01-MTA-low-stop-cradles.json')
    def source_packet(r):
        records=[]
        for n,v in r['geometry'].items():
            rec=r.get('recipes',{}).get(n,{})
            row=dict(oldmeta.get(n,{}),name=n,**v)
            if n.startswith('W'):
                row.update(kind='wire',wire=n.split('_')[0])
                radius=rec.get('radius_mm',rec.get('radius'))
                if radius is not None:row['nominal_profile_radius_mm']=radius
            if n=='F0SideServiceBudget':row['kind']='service_reservation'
            records.append(row)
        return dict(geometry=records,bundle=r['bundle'],bundle_sha256=r['bundle_sha256'])
    overlay('n01-F0-access-stack.json',data=source_packet)
    fm=OUT/'n01-F0-access-stack-motion.json';fr=json.loads(fm.read_text())
    assert fr['status']=='ACCESS_STACK_SEVEN_ACTORS36MOTION_RECEIVED_FULL_RESTRAINTS_AND_SHARED123_OPEN' and not fr['failures']
    assert fr['source_sha256'][(OUT/'n01-F0-access-stack.json').relative_to(ROOT).as_posix()]==sha(OUT/'n01-F0-access-stack.json')
    pins[fm.relative_to(ROOT).as_posix()]=sha(fm)
    overlay('n01-source-restraints-head-case-bypass.json')
    overlay('n01-current-source-MTA-boundary-overlay.json',data=lambda r:dict(
        geometry=r['U1_local_geometry'],bundle=r['U1_local_bundle'],bundle_sha256=r['U1_local_bundle_sha256']))
    up=overlay('n01-U1-frontband-common-plan.json')
    uf=OUT/'n01-U1-frontband-common-received.json';ur=json.loads(uf.read_text())
    assert ur['status']=='U1_FIVE_COMMON_RESTRAINTS_STATIC36_RECEIVED_FULL123_ASSEMBLY_OPEN' and not ur['failures']
    assert ur['source_sha256'][(OUT/'n01-U1-frontband-common-plan.json').relative_to(ROOT).as_posix()]==sha(OUT/'n01-U1-frontband-common-plan.json')
    pins[uf.relative_to(ROOT).as_posix()]=sha(uf)
    overlay('n01-common-head-root-JR-neck-received.json',retire=HP_RETIRED)
    hp=overlay('n01-HP-selected-R12p6-received.json')
    assert hp['status']=='HP_SELECTED_R12p6_STATIC36_RECEIVED_HEAD_SKIN_MOTION_OPEN'
    for n,s in parts.items():
        b=s.BoundBox;meta.setdefault(n,{})['bounds_mm']=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
        if n in owners:meta[n]['current_geometry_owner_receipt']=owners[n]
    pins['tools/cad/feline_current_shared_plan_context.py']=sha(ROOT/'tools/cad/feline_current_shared_plan_context.py')
    info=dict(parent_docs=docs,current_overlay_owners=owners,
        scope='Current planned shapes; scoped receipts are NOT whole N01/static/assembly selection',
        MTA_status=mta['status'],head_motion_skin_assembly_OPEN=True,N01_complete=False,
        actual_current_bounds_refreshed=True,cached_BUS_queries_require_valid_original_frame=True)
    return world,parts,meta,pins,info

"""All-neighbour map of inherited local source geometry, no route trials.

Accept the already loaded immutable world so one source-family inspection
does not rebuild it for every question. Results never select N01 or a part.
"""
import hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap


U1_SEATS = {w:'Ref_Material_U1_Anchor'+('Right' if w=='XL10' else 'Left')+'_0_0'
            for w in ('XL01','XL10','XL07','XL02','XL08','XL09','XS11','XS21','XS31')}


def inherited_u1_limit(name,other):
    """Existing named solder assembly is not a foreign 1.25mm keepout.

    This rule is used ONLY after exact native-seat identity and unchanged
    source-recipe provenance have been established by reconcile_existing_u1.
    Zero-distance intended seats still need a zero-common-volume proof.
    It is not electrical clearance, a new wire route or a blanket module waiver.
    """
    if not name.startswith('U1Local:'):return 1.25,None
    fields=name.split(':')
    if len(fields)!=3 or fields[1] not in U1_SEATS:return 1.25,None
    if fields[2]=='jacket' and other==U1_SEATS[fields[1]]:return 0.,'existing exact insulation bearing seat'
    if other.startswith('Ref_Material_U1_'):return .2,'unchanged intrinsic solder-assembly geometry, not foreign keepout'
    return 1.25,None


def reconcile_existing_u1(fixed):
    """Receive the previous77 queries; correct only their false own-mate policy."""
    import copy,subprocess
    from check_main_p0_placement import SavedShapes
    from plan_feline_layout import BASE
    from receive_feline_rrp_shared_height import load
    tick=time.monotonic();src=OUT/'n01-inherited-local-source-neighbor-map.json'
    dest=OUT/'n01-U1-intrinsic-mates-reconciled.json';assert not dest.exists()
    prior=json.loads(src.read_text());registry=OUT/'n01-current-source-MTA-boundary-overlay.json';reg=json.loads(registry.read_text())
    own=Path(__file__).relative_to(ROOT).as_posix()
    oldcode=subprocess.run(['git','show','cf6ac72b:'+own],cwd=ROOT,check=True,capture_output=True).stdout
    assert hashlib.sha256(oldcode).hexdigest()==prior['source_sha256'][own]
    for p,h in prior['source_sha256'].items():
        if p!=own:assert sha(ROOT/p)==h,p
    for p,h in reg['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(dict(bundle=reg['U1_local_bundle'],bundle_sha256=reg['U1_local_bundle_sha256'],geometry=reg['U1_local_geometry']))
    for n,s in actors.items():assert hashlib.sha256(s.exportBrepToString().encode()).hexdigest()==prior['actual_geometry_hashes'][n],n
    files=[src,registry,ROOT/reg['U1_local_bundle'],Path(__file__)]
    for suffix in ('native','checks','plan'):
        files.append(BASE/('body-harness-checkpoint/u1-board-grips-'+suffix+'.json'))
    native,gate,plan=[json.loads(f.read_text()) for f in files[-3:]]
    assert gate['status']=='BOARD_GRIPS_SHARED_CLEAR_NATIVE_OPEN' and not gate['contacts'] and not gate['errors']
    assert sha(ROOT/native['native'])==native['native_sha256'];files.append(ROOT/native['native'])
    assert {e for g in plan['groups'] for e in g['ends']}=={w+('/a' if w in ('XL02','XL09') else '/b') for w in U1_SEATS}
    reader=SavedShapes();tf=A.Placement(A.Vector(-80,2,-107.75),A.Rotation());identities={}
    for side in ('Left','Right'):
        key='Ref_Material_U1_Anchor'+side+'_0_0';s=reader.shape(ROOT/native['native'],'Anchor'+side);s.Placement=tf*s.Placement
        t=fixed[key];assert s.isValid() and t.isValid()
        difference=[s.copy().cut(t.copy()).Volume,t.copy().cut(s.copy()).Volume]
        assert max(difference)<1e-5,(key,difference)
        identities[key]=dict(native_bidirectional_difference_mm3=difference,world_transform=list(tf.toMatrix().A))
    checks=copy.deepcopy(prior['checks']);corrected={};failures={}
    for key,row in checks.items():
        if row['ok']:continue
        n,other=key.split('|');minimum,reason=inherited_u1_limit(n,other)
        assert reason is not None,('Do not waive foreign gap',key)
        updated=dict(row,prior_policy_ok=False,prior_minimum_mm=row['minimum_mm'],minimum_mm=minimum,intended_mate=reason)
        updated['ok']=row['gap_mm']>=minimum-1e-6
        if minimum==0:
            common=actors[n].copy().common(fixed[other].copy());assert common.isNull() or common.isValid()
            updated['actual_common_volume_mm3']=common.Volume;updated['ok'] &= common.Volume<1e-7
        checks[key]=updated;corrected[key]=updated
        if not updated['ok']:failures[key]=updated
    result=dict(status='NINE_EXISTING_U1_PREFIXES_INTRINSIC_MATES_STATIC_RECONCILED' if not failures else 'INTRINSIC_RECONCILIATION_HOLD',
        previous_map=src.relative_to(ROOT).as_posix(),original_rejection_preserved=True,checks=checks,corrected_policy_pairs=corrected,
        failures=failures,exact_native_seat_identity=identities,reused_queries=len(prior['checks']),new_wire_or_native_geometry=False,
        own_intrinsic_minimum_mm=.2,foreign_minimum_mm=1.25,not_electrical_clearance_qualification=True,
        nine_prefixes_only=True,remaining_five_U1_sources_full_corridors_motion_and_N01_OPEN=True,N01_complete=False,physical_pass=False,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in files},worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],len(corrected),len(failures),result['worker_seconds'],flush=True)
    return result


def receive(world,fixed,meta,pins,docs,source_file=None):
    tick=time.monotonic();sf=source_file or OUT/'n01-current-source-MTA-boundary-overlay.json';r=json.loads(sf.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    dest=sf.with_name(sf.stem+'-neighbors.json') if source_file else OUT/'n01-inherited-local-source-neighbor-map.json'
    assert not dest.exists(),'Read existing all-neighbour map instead of repeating it'
    archive=ROOT/r['bundle' if source_file else 'U1_local_bundle'];assert sha(archive)==r['bundle_sha256' if source_file else 'U1_local_bundle_sha256'];actors={};kinds={}
    with zipfile.ZipFile(archive) as z:
        for row in r['geometry' if source_file else 'U1_local_geometry']:
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode())
            actors[row['name']]=s;kinds[row['name']]=row
    checks={};query=SolidQueries();done=[];sources={**pins,sf.relative_to(ROOT).as_posix():sha(sf),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))}
    def save():
        result=dict(status='INHERITED_LOCAL_SOURCE_ALL_NEIGHBORS_DIAGNOSIS_NOT_N01',source_sha256=sources,
            actual_geometry_hashes={n:hashlib.sha256(s.exportBrepToString().encode()).hexdigest() for n,s in actors.items()},
            completed=done,checks=checks,failures={k:v for k,v in checks.items() if not v['ok']},
            intended_holes_NOT_manufacturer_pinout_or_pad_fit=True,N01_complete=False,native_changed=False,
            physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    for n,s in actors.items():
        for other,t in {**fixed,**actors}.items():
            if n==other or other in actors and list(actors).index(other)>list(actors).index(n):continue
            a=kinds[n];b=kinds.get(other,meta.get(other,{}));mate=None;minimum=1.25
            if other in kinds and a['wire']==b['wire']:mate='same selected bare/jacket seam';minimum=0.
            elif other=='Ref_Material_PWM1608NominalPCB_0_0':
                mate='named selected carrier solder hole in nominal PCB, physical fit open' if a['kind']=='bare' else 'own insulated pad departure'
                minimum=0. if a['kind']=='bare' else .2
            elif a['kind']=='wire' and b.get('kind') in ('wire','proposal_wire','actual_wire','curve_profile_reservation'):minimum=.2
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>minimum+1e-6:continue
            aa=s;bb=t
            if other==world.bus['name']:aa=s.copy();aa.Placement=docs['inverse']*aa.Placement;bb=world.bus['original']
            if not bb.Solids:
                radius=b.get('nominal_profile_radius_mm') or b.get('radius_mm')
                row=profile_gap(aa,bb,radius,minimum) if radius else dict(ok=False,unreceived_profile=True)
            else:
                gap=query.distance(aa,bb);row=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum,intended_mate=mate)
                if not row['ok']:row['witness_mm']=[[list(x),list(y)] for x,y in aa.distToShape(bb)[1][:1]]
            checks[n+'|'+other]=row
            if not row['ok']:print('WITNESS',n,other,row,flush=True)
        done.append(n);save();print('MAPPED',n,flush=True)
    save();print('ALL_LOCAL_SOURCES_MAPPED',len(done),len(checks),round(time.monotonic()-tick,3),flush=True)

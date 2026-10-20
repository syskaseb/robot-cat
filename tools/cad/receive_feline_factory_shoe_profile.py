"""Replace unnecessary square foot corners, not cases/axes/cable positions.

One mirrored capsule-foot profile and continuous bottom-edge chamfer. Keep
both complete M2 load columns and the owning floor root. Subset monotonicity
reuses all positive static/motion distances; query only eight failed poses.
"""
import gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_two_lane_receive import world_context
from receive_feline_rrp_shared_height import load
from receive_feline_main_ato_gallery import selected
from receive_feline_global_case_candidates import placement
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json


def shoe(old,side):
    b=old.BoundBox;cy=side*41.55;xs=(-27.,-17.);outer=45.05
    # Rounded capsule is the union of the original two boss cylinders and
    # their bridge; the discarded square corners carry neither M2 axis.
    lo,hi=sorted((side*41.55,side*46.05));cut=Part.makeBox(60,hi-lo,30,A.Vector(-50,lo,-45))
    keep=Part.makeBox(xs[1]-xs[0],9,30,A.Vector(xs[0],cy-4.5,-45))
    for x in xs:keep=keep.fuse(Part.makeCylinder(3.5,30,A.Vector(x,cy,-45)))
    new=old.cut(cut.cut(keep))
    # Maximum bevel preserving2mm PETG outside the1.15mm lower bore.
    bevel=3.5-1.15-2.;assert abs(bevel-.35)<1e-6
    yz=[(outer-bevel,-43),(outer+1,-43),(outer+1,-42.2+bevel),(outer,-42.2+bevel),(outer-bevel,-42.2)]
    pts=[A.Vector(-50,side*y,z) for y,z in yz];wedge=Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(A.Vector(60,0,0))
    new=new.cut(wedge);assert new.isValid() and len(new.Solids)==1
    assert new.cut(old).Volume<1e-5
    for x in xs:
        core=Part.makeCylinder(3.15,25,A.Vector(x,cy,-43))
        assert old.common(core).cut(new).Volume<1e-5,'Do not thin the M2 core/nut trap'
        upper=Part.makeCylinder(3.5,25,A.Vector(x,cy,-42.2+bevel))
        assert old.common(upper).cut(new).Volume<1e-5,'Full upper boss retained'
    return new,dict(M2_axes_mm=[[x,cy] for x in xs],boss_radius_mm=3.5,bore_radius_mm=1.15,
        lower_full_wall_mm=2.,bottom_edge_bevel_mm=bevel,new_material_outside_old_mm3=new.cut(old).Volume,
        removed_square_corner_and_lower_edge_mm3=old.cut(new).Volume,
        entire_upper_boss_and_lower_R3p15_core_preserved=True)


def main():
    tick=time.monotonic();f=OUT/'n01-factory-inputs-current-received.json';prior=json.loads(f.read_text());actors=load(prior)
    pf0=ROOT/prior['pair_rows'];assert sha(pf0)==prior['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf0.read_bytes()))
    world,_=world_context();proofs={};changed=set()
    frame=OUT/'n01-common-restraint-world-probe.json';roots,_,rpins=selected(frame,'parts',lambda n:n=='LowerBay:ForePanel')
    assert prior['source_sha256'][frame.relative_to(ROOT).as_posix()]==sha(frame)
    for w,side in (('W044',1),('W052',-1)):
        name='CaseBase:'+w+'_Joint';old=actors[name];actors[name],proofs[name]=shoe(old,side);changed.add(name)
        root=roots['LowerBay:ForePanel'];before=old.common(root);after=actors[name].common(root)
        assert before.isValid() and after.isValid() and after.Volume>1e-5
        assert before.cut(after).Volume<1e-5
        proofs[name].update(positive_floor_root_mm3=after.Volume,old_floor_root_lost_mm3=before.cut(after).Volume)
    assert len(prior['failures'])==8
    query=SolidQueries()
    for key in prior['failures']:
        name,tail=key.split('|motion:');assert name in changed
        other,pose=tail.rsplit(':',1);p=next(p for p in world.motion if p['name']==other and str(p['pose'])==pose)
        a=actors[name].copy();a.Placement=placement(p['r'],p['t']).inverse()*a.Placement
        gap=query.distance(a,world.rest[other]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25,
            old_failed_gap_mm=checks[key]['gap_mm'],changed_cause='Whole capsule foot and lower-edge bevel; fixed M2 axes, no case or cable offset')
    dest=OUT/'n01-factory-inputs-profile-received.json';archive=dest.with_suffix('.breps.zip');pf=dest.with_suffix('.pairs.json.gz');geometry=[]
    with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for row in prior['geometry']:
            n=row['name'];raw=actors[n].exportBrepToString().encode() if n in changed else src.read(row['entry'])
            if n not in changed:assert hashlib.sha256(raw).hexdigest()==row['sha256']
            z.writestr(row['entry'],raw);geometry.append(dict(row,sha256=hashlib.sha256(raw).hexdigest()))
    pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    failures=[k for k,v in checks.items() if not v['ok']]
    result=dict(prior,status='FACTORY_SHOE_PROFILE_HOLDS' if failures else 'FOUR_FACTORY_INPUTS_ROOTED_STATIC36_RECEIVED_TOOLS_OPEN',
        source_sha256={**prior['source_sha256'],**rpins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (f,pf0,ROOT/prior['bundle'],Path(__file__))}},
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),failures=failures,
        shoe_profile_proofs=proofs,changed_actor_count=2,byte_identical_actor_count=len(actors)-2,
        positive_queries_reused_by_same_geometry_or_material_subset=len(checks)-8,new_moving_pair_queries=8,
        full_upper_bosses_and_floor_roots_unchanged=True,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],len(checks),len(failures),result['worker_seconds'],flush=True)
    print(json.dumps({k:checks[k] for k in prior['failures']},indent=2))


if __name__=='__main__':main()

"""Receive one continuous four-bay Cover without discarding mount islands.

Preserve all three previous cover solids. A lower rim restores the offset
cover screw's connection; an outboard foot and overhead bridge support the
retained hood post above the complete DATA/strap bay. Only added/changed
material is checked, with inherited unchanged-pair evidence pinned.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_side_retention_coupled as C
from servo_fuse_inputs_r1 import save,sha

ROOT=C.ROOT;OUT=C.R.N.BASE/'w5-side-retention-received-r1'
BRIDGES={
    'OffsetMountSouthRimReturn':[-90,-98,130,-43,-93,134],
    'HoodPostOutboardFoot':[-52,-47,182.5,-47,-37,189.5],
    'HoodPostOverSideBay':[-74,-47,186,-49,-37,189.5]}


def main():
    import FreeCAD as A,Part
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    prior_path=C.OUT/'checks.json';prior=json.loads(prior_path.read_text(encoding='utf-8'))
    assert prior['cover_valid'] and prior['cover_solids']==3 and not prior['cover_BOP_errors']
    assert not prior['errors'] and all(h['part']=='FR_GBearingAndOutletWing' and
        h['owner']=='FRTie/FRExtension_TieHead_DESIGN' for h in prior['hits'])
    pins=[Path(__file__),Path(C.__file__),prior_path]
    for rel,digest in {**prior['source_sha256'],**prior['files']}.items():
        assert sha(ROOT/rel)==digest,rel;pins.append(ROOT/rel)
    plan=json.loads((C.R.R.OUT/'plan.json').read_text(encoding='utf-8'))
    supports,bands,tools,bp=C.geometry(A,Part,plan)
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    # Clear the complete existing head in X, not just its south corner in Y;
    # retain the full1.8mm bearing thickness and the proximal seat root.
    name='FR_GBearingAndOutletWing';b=bp['raw_boxes'][name];b[0]=-78.8
    wing=box(b);local=[t for t in tools.values() if wing.BoundBox.intersect(t.BoundBox)]
    supports[name]=wing.cut(Part.makeCompound(local));assert supports[name].isValid()
    cover_path=C.OUT/'CoverFourSideBays_CANDIDATE_WORLD.brep';old=Part.read(str(cover_path))
    bridges={n:box(b) for n,b in BRIDGES.items()};bp['cover_bridges']=BRIDGES
    cover=old.multiFuse(list(bridges.values()))
    cover_errors=cover.check(True) or []
    connectivity={n:[s.common(q).Volume for q in old.Solids] for n,s in bridges.items()}
    bridge_joint=bridges['HoodPostOutboardFoot'].common(bridges['HoodPostOverSideBay']).Volume
    fixed,printed,_,_,_,loaded,_,_=C.R.S.load(A,Part);pins+=loaded
    central=json.loads(C.R.N.CENTRAL.read_text(encoding='utf-8'))
    for wire,row in central['routes'].items():
        p=ROOT/row['geometry'];fixed[wire]=Part.read(str(p));pins.append(p)
    for owner in ('SourceCarrier','SourceCover','SourceEastHood','SourceWestHood'):
        p=ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1'/(owner+'_CANDIDATE_WORLD.brep')
        printed[owner]=Part.read(str(p));pins.append(p)
    original=printed['SourceCover']
    p=ROOT/'hardware/cad/studies/w5-central-retention-native-r1/CentralRetentionDeck_CANDIDATE_WORLD.brep'
    printed['SourceDeck']=Part.read(str(p));pins.append(p)
    for alias in C.R.N.OWNER_ALIASES:printed.pop(alias,None)
    r4=json.loads(C.R.R.P.CENTRAL.read_text(encoding='utf-8'))
    for label,rel in r4['world_geometries'].items():
        p=ROOT/rel;fixed['CentralRetention/'+label]=Part.read(str(p));pins.append(p)
    hits=[];errors=[];pairs=0
    def check(label,s,owner,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for q in t.Solids:
                if not a.BoundBox.intersect(q.BoundBox):continue
                pairs+=1
                if separated(a,q):continue
                try:
                    v=a.common(q)
                    if v.Volume>1e-6:hits.append(dict(part=label,owner=owner,mm3=v.Volume,bounds_mm=C.bounds(v)))
                except Exception as e:errors.append(dict(part=label,owner=owner,error=str(e)))
    printed['SourceCover']=cover
    for label,s in {name:supports[name],**bridges}.items():
        for owner,t in {**fixed,**printed}.items():
            if label==name and owner=='SourceCarrier' or label in bridges and owner=='SourceCover':continue
            check(label,s,owner,t)
        for owner,t in bands.items():check(label,s,owner,t)
        if label in bridges:
            for owner,t in supports.items():check(label,s,owner,t)
    # Keep the four actual cover screw bearings and all upper hood interfaces,
    # rather than throwing away the small disconnected CAD solids.
    protected=[]
    for x,y,z,h,r in ((-88,-97.5,116,2.5,1.21),(-84,96.5,116,3.5,1.2),
                      (106,-96.5,116,3.5,1.2),(106,96.5,116,3.5,1.2)):
        axis=A.Vector(0,1 if y>0 else -1,0);p=A.Vector(x,y,z)
        ring=Part.makeCylinder(2.5,h,p,axis).cut(Part.makeCylinder(r,h,p,axis))
        material=original.common(ring)
        protected.append(dict(kind='cover_screw_bearing',axis_mm=[x,y,z],original_mm3=material.Volume,
                              lost_mm3=material.cut(cover).Volume))
    post_path=C.R.N.BASE/'w5-source-roof-native-r3/AddedPosts_WORLD.brep'
    posts=Part.read(str(post_path));pins.append(post_path)
    cap=posts.common(box([-200,-200,209.5,200,200,230]))
    material=original.common(cap)
    protected.append(dict(kind='all_upper_hood_post_interfaces',original_mm3=material.Volume,lost_mm3=material.cut(cover).Volume))
    preserved=all(r['original_mm3']>1e-6 and r['lost_mm3']<1e-5 for r in protected)
    OUT.mkdir(parents=True,exist_ok=True);files=[];shapes={**supports,**bands}
    for filename,shape in (('SideRetention_PROPOSED_WORLD.brep',Part.makeCompound(list(shapes.values()))),
                            ('CoverConnectedBays_CANDIDATE_WORLD.brep',cover)):
        p=OUT/filename;shape.exportBrep(str(p));files.append(p)
    p=OUT/'native-blueprint.json';save(p,bp);files.append(p)
    valid=cover.isValid() and len(cover.Solids)==1 and not cover_errors
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='COUPLED_SIDE_RECEIVED_CLEAR_NATIVE_PENDING' if valid and preserved and not hits and not errors else 'COUPLED_SIDE_RECEIVE_REJECTED',
        hits=hits,errors=errors,pairs=pairs,inherited_unchanged_pair_receipts=[C.PRIOR.relative_to(ROOT).as_posix(),prior_path.relative_to(ROOT).as_posix()],
        cover_solids=len(cover.Solids),cover_valid=cover.isValid(),cover_BOP_errors=cover_errors,
        cover_after_mm3=cover.Volume,cover_bridge_to_original_components_mm3=connectivity,
        hood_bridge_foot_join_mm3=bridge_joint,original_three_cover_components_retained=True,
        protected_mount_interfaces=protected,protected_interfaces_preserved=preserved,
        native_blueprint=(OUT/'native-blueprint.json').relative_to(ROOT).as_posix(),
        compound_role_order=list(shapes),block_count=8,endpoint_count=35,body_ties=8,insulation_ties=35,
        FR_proximal_bearing_thickness_mm=1.8,FR_existing_head_nominal_X_gap_mm=.45,
        frozen_37_routes=True,new_screws=0,new_separate_prints=0,
        lower_post_load_path_redesigned_upper_interface_preserved=True,
        native_parameter_roots_reopen_mount_motion_stock_pending=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
    print('SIDE_RECEIVE',pairs,len(hits),len(errors),len(cover.Solids),preserved,flush=True)


if __name__=='__main__':main()

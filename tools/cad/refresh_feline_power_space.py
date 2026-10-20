"""Refresh the EXISTING signed-space engine for the resident current scene.

No world reload, S1 pose search, new raster algorithm or mechanical acceptance.
Reuse byte-identical source cells; rebuild the union per owner (never subtract
an owner from a union). Keep the received36-pose occupancy. Only the four
explicit whole power owners are variable; all other bought parts remain.
"""
import copy,hashlib,json,math,re,sys,zipfile
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def same_geometry(a,b):
    """Full cleaned BRep tokens, ignoring only three administrative flags."""
    def tokens(s):
        raw=s.cleaned().exportBrepToString()
        return re.sub(r'(?m)^[01]{3}([01]{4})([ \t]*\r?)$',
                      lambda m:'000'+m[1]+m[2],raw).split()
    aa,bb=tokens(a),tokens(b)
    if len(aa)!=len(bb):return False
    for x,y in zip(aa,bb):
        if x==y:continue
        try:
            if not math.isclose(float(x),float(y),rel_tol=1e-12,abs_tol=1e-10):return False
        except ValueError:return False
    return True


def receive_mesh_only_resume(parts,replayed_parts,replayed_pins):
    """Explicit one-off recovery; never accept a different pose by its name."""
    target=OUT/'power-space-current';bf=target/'source-cache-bridge.json'
    rf=target/'n01-integrated-signed-space.json';proof=target/'mesh-only-resume.json'
    assert not proof.exists(),'Receive the recorded recovery; do not repeat it'
    old=json.loads(bf.read_text());result=json.loads(rf.read_text())
    hashes={n:hashlib.sha256(parts[n].exportBrepToString().encode()).hexdigest()
            for n in old['source_geometry_sha256']}
    changed=[n for n,h in hashes.items() if h!=old['source_geometry_sha256'][n]]
    assert changed and all('Static:'+n in result['parts'] for n in changed)
    # The earlier resident composer also pinned its older script revision.
    # Receive the ENTIRE retained scene from the now reloaded pinned provider,
    # not merely its changed serializations or matching bounding boxes.
    for index,n in enumerate(hashes):
        assert same_geometry(parts[n],replayed_parts[n]),('Different geometry',n)
        if index%200==0:print('Resume whole geometry',index,'/',len(hashes),flush=True)
    provider='tools/cad/feline_current_shared_plan_context.py'
    assert replayed_pins[provider]==sha(ROOT/provider)
    for p,h in replayed_pins.items():assert sha(ROOT/p)==h,('Changed replay source',p)
    for p,h in result['source_sha256'].items():
        if p in (provider,bf.relative_to(ROOT).as_posix(),Path(__file__).relative_to(ROOT).as_posix()):continue
        assert sha(ROOT/p)==h,('Changed source',p)
    record=dict(status='MESH_ONLY_SERIALIZATION_RECOVERY_NOT_GEOMETRY_ACCEPTANCE',
        previous_bridge=old,previous_result_source_sha256=result['source_sha256'],
        current_source_geometry_sha256=hashes,changed_serializations=changed,
        full_cleaned_BRep_tokens_match_replayed_pinned_sources=True,
        geometry_numeric_abs_tolerance_mm=1e-10,geometry_numeric_rel_tolerance=1e-12,
        retained_source_masks=len(result['parts']),N01_complete=False,physical_pass=False)
    record.update(replayed_source_sha256=replayed_pins,whole_retained_geometry_received=len(hashes),
                  stale_provider_pin_received_only_after_full_geometry_comparison=True)
    save_json(proof,record)
    old['source_geometry_sha256']=hashes
    old['parents'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    old['mesh_only_resume_receipt']=proof.relative_to(ROOT).as_posix()
    save_json(bf,old)
    for p in (bf,Path(__file__),ROOT/provider):result['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p)
    result['mesh_only_resume_receipt']=proof.relative_to(ROOT).as_posix()
    save_json(rf,result)
    return dict(changed_serializations=len(changed),retained_source_masks=len(result['parts']))


def run(world,parts,metadata,pins,outer):
    import feline_integrated_space_context as context
    import build_feline_current_signed_space as engine
    oldworld,oldparts,_,_,olddocs=context.integrated()
    assert oldworld is world,'Reuse the loaded pinned world; do not allocate another'
    original=json.loads((OUT/'n01-current-signed-space.json').read_text())
    integrated=json.loads((OUT/'n01-integrated-signed-space.json').read_text())
    for packet in (original,integrated):
        assert packet['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY'
        assert packet['source_sha256']['tools/cad/feline_signed_voxels.py']==sha(ROOT/'tools/cad/feline_signed_voxels.py')
        for key in ('field','voxel_source_archive'):
            assert sha(ROOT/packet[key])==packet[key+'_sha256']
    assert integrated['layer_checkpoint']['motion_count']==len(world.motion)
    retained={n:s for n,s in parts.items() if not n.startswith(('Station:P_REAR:',
        'Station:F_PWM_whole:','JPWMSource:','JPWMGrip:')) and n not in
        ('Ref_Material_JPWM_0_0','Ref_Material_F_AUX_candidate_case_0_0')}
    target=OUT/'power-space-current';target.mkdir(exist_ok=True)
    bridgefile=target/'source-cache-bridge.json';archive=target/'received-source-cells.zip'
    def bh(s):return hashlib.sha256(s.exportBrepToString().encode()).hexdigest()
    current_hashes={n:bh(s) for n,s in retained.items()}
    same={n for n in retained if n in oldparts and current_hashes[n]==bh(oldparts[n])}
    a=outer.cut(olddocs['outer']);b=olddocs['outer'].cut(outer)
    assert (a.isNull() or a.isValid()) and (b.isNull() or b.isValid())
    assert a.Volume+b.Volume<1e-5,'Do not reuse a different torso boundary'
    records={}
    caches=[(ROOT/p['voxel_source_archive'],p['parts']) for p in (original,integrated)]
    # Archive provenance is explicit. Later integrated entries supersede the
    # original cell for the same owner; no current shape is called unchanged
    # merely because it retains its old name.
    for source,rows in caches:
        for name,row in rows.items():records[name]=(source,row)
    bridge=dict(status='DERIVED_RECEIVED_CELL_BRIDGE_NOT_GEOMETRY_PASS',
        parts={},source_geometry_sha256=current_hashes,
        byte_identical_static_sources=sorted(same),variable_owners=sorted(set(parts)-set(retained)),
        canonical_scene_not_changed=True,N01_complete=False,physical_pass=False,
        motion_field=integrated['field'],motion_field_sha256=integrated['field_sha256'],
        parents={p.relative_to(ROOT).as_posix():sha(p) for p in
                 (OUT/'n01-current-signed-space.json',OUT/'n01-integrated-signed-space.json',Path(__file__))})
    needed={n for n in records if n.startswith('Static:') and n[7:] in same}
    needed.add('ActualTorsoBoundary')
    if not archive.exists():
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as dest:
            for name in sorted(needed):
                source,row=records[name]
                with zipfile.ZipFile(source) as src:raw=src.read(row['entry'])
                assert hashlib.sha256(raw).hexdigest()==row['sha256'],name
                entry=hashlib.sha256(name.encode()).hexdigest()[:24]+'.npz'
                dest.writestr(entry,raw)
                bridge['parts'][name]=dict(row,entry=entry,source_archive=source.relative_to(ROOT).as_posix())
        bridge.update(voxel_source_archive=archive.relative_to(ROOT).as_posix(),voxel_source_archive_sha256=sha(archive))
        save_json(bridgefile,bridge)
    else:
        received=json.loads(bridgefile.read_text())
        assert received['source_geometry_sha256']==current_hashes
        assert received['parents']==bridge['parents']
        assert received['voxel_source_archive_sha256']==sha(archive)
        bridge=received
    parent=copy.deepcopy(integrated);parent['parts']=bridge['parts']
    parent['voxel_source_archive']=archive.relative_to(ROOT).as_posix()
    parent['voxel_source_archive_sha256']=sha(archive)
    parent['layer_checkpoint']['motion_count']=len(world.motion)
    effective_pins=dict(pins)
    for p in (bridgefile,archive,Path(__file__)):
        effective_pins[p.relative_to(ROOT).as_posix()]=sha(p)
    docs=dict(parent=parent,parentfile=bridgefile,archive=archive,
        field=ROOT/integrated['field'],unchanged=same,inverse=olddocs['inverse'],outer=outer)
    old_entry,old_reusable,old_out,old_args=context.integrated,context.reusable_cell,engine.OUT,sys.argv[:]
    try:
        # Meshing changes TShape triangulation/flags. Never mesh authoritative
        # resident inputs, or a second slice mistakes cached display state for
        # a new geometry revision. Hash inputs BEFORE making private copies.
        working={n:s.copy(True,True) for n,s in retained.items()}
        context.integrated=lambda:(world,working,{n:metadata[n] for n in retained},effective_pins,docs)
        context.reusable_cell=lambda name,unchanged,rows:(name=='ActualTorsoBoundary' and name in rows) or old_reusable(name,unchanged,rows)
        engine.OUT=target;sys.argv=[str(Path(engine.__file__)),'--integrated-upper']
        print('CURRENT_POWER_SPACE',len(retained),'reuse',len(same),'changed',len(retained)-len(same),flush=True)
        engine.main()
    finally:
        context.integrated,context.reusable_cell,engine.OUT,sys.argv=old_entry,old_reusable,old_out,old_args

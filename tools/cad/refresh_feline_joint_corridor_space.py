"""Use the EXISTING voxel engine with the whole received resident layout.

Reuse only source cells with byte-identical owner geometry. Keep every
current power owner fixed, reuse the pinned36-pose field, never subtract
an old owner from a union, and never mesh authoritative resident shapes.
This prepares routing proposals; it is not a curve or N01 certificate.
"""
import copy,hashlib,json,sys,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json

TARGET=OUT/'joint-corridor-space-20261021'


def run(world,parts,metadata,pins,outer,inverse):
    import types
    import build_feline_current_signed_space as engine
    import feline_integrated_space_context as context
    tick=time.monotonic();oldfile=OUT/'power-space-current/n01-integrated-signed-space.json'
    bridgefile=OUT/'power-space-current/source-cache-bridge.json'
    old=json.loads(oldfile.read_text());bridge=json.loads(bridgefile.read_text())
    assert old['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY'
    assert old['layer_checkpoint']['motion_count']==len(world.motion)==3888
    for p,h in world.pins.items():assert old['source_sha256'].get(p)==h,('Changed motion source',p)
    for p in (old,bridge):assert sha(ROOT/p['voxel_source_archive'])==p['voxel_source_archive_sha256']
    assert sha(ROOT/old['field'])==old['field_sha256']
    # Use the original saved BUS solid and the one current world transform;
    # do not voxelize a stale cached BUS placement. Both copies are private.
    original=world.bus['original'].copy(True,True);assert original.isValid() and original.Solids
    current_bus=original.copy(True,True);current_bus.Placement=inverse.inverse()*current_bus.Placement
    parts={**parts,world.bus['name']:current_bus}
    hashes={n:hashlib.sha256(s.exportBrepToString().encode()).hexdigest() for n,s in parts.items()}
    records={}
    for p in (bridge,old):
        for n,r in p['parts'].items():records[n]=(ROOT/p['voxel_source_archive'],r)
    same={n for n,h in hashes.items() if bridge['source_geometry_sha256'].get(n)==h and 'Static:'+n in records}
    TARGET.mkdir(exist_ok=True);bf=TARGET/'owner-source-cache-bridge.json';archive=TARGET/'received-owner-cells.zip'
    manifest=dict(status='EXACT_OWNER_CELL_REUSE_NOT_MECHANICAL_ACCEPTANCE',source_geometry_sha256=hashes,
        no_variable_or_dropped_power_owners=True,static_sources=len(parts),byte_identical_reused_sources=len(same),
        changed_sources_to_raster=sorted(set(parts)-same),parts={},parents={oldfile.relative_to(ROOT).as_posix():sha(oldfile),
        bridgefile.relative_to(ROOT).as_posix():sha(bridgefile)},N01_complete=False,physical_pass=False)
    if not archive.exists():
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as out:
            opened={}
            try:
                for n in sorted(same):
                    source,r=records['Static:'+n]
                    if source not in opened:opened[source]=zipfile.ZipFile(source)
                    raw=opened[source].read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
                    entry=hashlib.sha256(('Static:'+n).encode()).hexdigest()[:24]+'.npz';out.writestr(entry,raw)
                    manifest['parts']['Static:'+n]=dict(r,entry=entry,original_source_archive=source.relative_to(ROOT).as_posix())
            finally:
                for z in opened.values():z.close()
        manifest.update(voxel_source_archive=archive.relative_to(ROOT).as_posix(),voxel_source_archive_sha256=sha(archive))
        save_json(bf,manifest)
    else:
        received=json.loads(bf.read_text());assert received['source_geometry_sha256']==hashes
        assert received['parents']==manifest['parents'] and sha(archive)==received['voxel_source_archive_sha256']
        manifest=received
    parent=copy.deepcopy(old);parent['parts']=manifest['parts'];parent['voxel_source_archive']=manifest['voxel_source_archive']
    parent['voxel_source_archive_sha256']=manifest['voxel_source_archive_sha256']
    effective={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),bf.relative_to(ROOT).as_posix():sha(bf),
               archive.relative_to(ROOT).as_posix():sha(archive)}
    working={n:s.copy(True,True) for n,s in parts.items()}
    proxy=types.SimpleNamespace(bus={**world.bus,'original':original,'inverse':inverse},motion=world.motion,rest=world.rest)
    docs=dict(parent=parent,parentfile=bf,archive=archive,field=ROOT/old['field'],unchanged=same,inverse=inverse,outer=outer.copy(True,True))
    previous=(context.integrated,context.reusable_cell,engine.OUT,sys.argv[:])
    try:
        context.integrated=lambda:(proxy,working,metadata,effective,docs)
        context.reusable_cell=lambda name,unchanged,rows:name.startswith('Static:') and name[7:] in same and name in rows
        engine.OUT=TARGET;sys.argv=[str(Path(engine.__file__)),'--integrated-upper']
        print('WHOLE_JOINT_SPACE',len(parts),'exact_owner_reuse',len(same),'new_cells',len(parts)-len(same),flush=True)
        engine.main()
    finally:
        context.integrated,context.reusable_cell,engine.OUT,sys.argv=previous
    result=json.loads((TARGET/'n01-integrated-signed-space.json').read_text())
    return dict(status=result['status'],seconds=round(time.monotonic()-tick,3),errors=result['errors'],
        static_sources=len(parts),reused_sources=len(same),N01_complete=False,physical_pass=False)

"""One reconciled print map, retaining R53 without duplicating old parts.

No new geometric variants or copies of unchanged STL files. Bind each added
or replaced job to its received native/export proof. This is the pending
whole-prototype set, not a selected/print-approved release or W5 completion.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, json
from servo_fuse_inputs_r1 import sha, save
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-final-print-set-candidate-r1'

def main():
    start=datetime.now(timezone.utc)
    if (OUT/'manifest.json').exists():
        draft=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
        assert not draft['selected'] and draft['status']=='ONE_CURRENT_PROTOTYPE_PRINT_MAP_PENDING_INTEGRATED_SELECTION'
    pins={}
    def read(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    parent=ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json'
    selection=read(parent);prints=copy.deepcopy(selection['prints'])
    original_by_id={r['identity']:r for r in prints};assert len(original_by_id)==77
    for row in prints:assert sha(ROOT/row['stl'])==row['sha256'],row['identity']
    replacements={
        'electronics:Carrier service ports':('w5-side-retention-native-r1','SourceCarrier'),
        'electronics:DeckP10-cover-mount':('w5-remote-end-native-r1','CompleteDeck'),
        'body:raised-upper-cover-mount':('w5-side-retention-native-r1','SourceCover'),
        'electronics:servo-fuse-bank-left':('w5-source-bank-passage-native-r1','BankLeft'),
        'electronics:F0-XT60-source-bridge':('w5-remote-end-native-r1','SourceBridge')}
    additions=[('w5-source-platform-native-r4','Platform',1),
        ('w5-loom-fixed-native-r1','SourceEastHood',1),
        ('w5-harness-passages-qualified-r1','SourceWestHood',1),
        *[('w5-loom-fixed-native-r1',leg+'FixedFrame',1) for leg in ('FL','FR','RL','RR')],
        ('w5-source-link-native-r1','SourceClipLink',8),
        ('w5-source-hip-native-r1','SourceClipHip',4)]
    receipts={};changed=[]
    def bind(folder,role,quantity,identity):
        if folder not in receipts:
            receipt=read(BASE/folder/'checks.json');receipts[folder]=receipt
            assert not receipt.get('hits',[]) and not receipt.get('errors',[]),folder
            for rel,h in {**receipt.get('source_sha256',{}),**receipt.get('files',{})}.items():
                assert sha(ROOT/rel)==h,rel
        r=receipts[folder];files=r['files']
        stls=[p for p in files if p.endswith('.stl') and Path(p).name.startswith(role+'_')]
        if role in ('SourceClipLink','SourceClipHip'):
            stls=[p for p in files if p.endswith('.stl')]
        assert len(stls)==1,(folder,role,stls)
        masters=[p for p in files if p.endswith('.FCStd')];assert len(masters)==1,masters
        geometry=[p for p in files if p.endswith('.brep') and Path(p).name.startswith(role+'_') and '/cad/studies/' in p]
        if not geometry and role in ('SourceClipLink','SourceClipHip'):
            geometry=[p for p in files if p.endswith('.brep') and '/cad/studies/' in p]
        assert len(geometry)==1,(folder,role,geometry)
        dims=r.get('dimensions_mm');dims=dims.get(role) if isinstance(dims,dict) else dims
        if dims is None:
            dims=next(p['dimensions_mm'] for p in r['parts'] if p['owner']==role)
        if folder=='w5-loom-fixed-native-r1':dims=r['dimensions_mm'][role]
        assert len(dims)==3 and max(dims)+6<=256,(role,dims)
        row=dict(identity=identity,quantity=quantity,purpose='installed_candidate',material='PETG',
            stl=stls[0],sha256=files[stls[0]],native_file=masters[0],native_master_sha256=files[masters[0]],
            world_geometry=geometry[0],world_geometry_sha256=files[geometry[0]],
            receipt=(BASE/folder/'checks.json').relative_to(ROOT).as_posix(),
            export_role=role,dimensions_mm=dims,total_brim_allowance_mm=6,
            physical_fit_strength_creep_verified=False,slicer_checked=False)
        changed.append(row)
        return row
    for identity,(folder,role) in replacements.items():
        old=original_by_id[identity];assert old['quantity']==1
        new=bind(folder,role,1,identity)
        new['replaces_stl']=old['stl'];new['replaces_stl_sha256']=old['sha256']
        prints[prints.index(old)]=new
    for folder,role,quantity in additions:
        identity='W5:'+role
        assert identity not in original_by_id
        prints.append(bind(folder,role,quantity,identity))
    assert len(prints)==86 and len({r['identity'] for r in prints})==86
    installed=sum(r['quantity'] for r in prints if r['purpose']=='installed_candidate')
    assert installed==134,(installed,'115retained/replaced plus19new prints')
    # The exact manufacturer dimensions are already received; do not replace
    # these205mm ties by the existing shorter T18I stock just to avoid a row.
    t18l=read(ROOT/'hardware/reference/hellermann-11102189-2026-10-05/dimensions.json')
    assert t18l['sku']=='111-02189' and t18l['package_quantity']==100
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'manifest.json',dict(status='ONE_CURRENT_PROTOTYPE_PRINT_MAP_PENDING_INTEGRATED_SELECTION',
        selected_parent=parent.relative_to(ROOT).as_posix(),selected_parent_unchanged=True,
        print_jobs=86,PETG_installed=installed,new_installed_prints=19,replaced_jobs=5,
        unchanged_jobs=72,prints=prints,source_parts=changed,
        purchased_delta=dict(T18L11102189=dict(installed=12,manufacturer_package_pieces=100,order_packages_candidate=1),
            M3x16=8,M3nuts=8,T18I_fixed_frames=12,T18I_link_hip=12,T18I_AUX=1,
            source_platform_and_hood_hardware='Retain received source-platform assembly/source-roof recipes; reconcile existing stock once, not a new duplicate purchase.'),
        wiring_preparation='hardware/electronics/full-cat/w5-prototype-preparation-r2/preparation.json',
        open_gates=['Receive new rigid-grip nominal movement screen and flexible-loop space preparation.',
            'Complete current shared source/bank release recipe and changed restraint interfaces.',
            'Reconcile exact current shared order quantities and bind one selected package.'],
        selected=False,W1_complete=False,W5_complete=False,phase1_complete=False,physical_pass=False,
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print(json.dumps(dict(jobs=len(prints),installed=installed,replacements=5,new_prints=19)))

if __name__=='__main__':main()

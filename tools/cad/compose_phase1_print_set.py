"""One whole-prototype print identity map from explicit selected overlays.

No new CAD, no filename-derived quantities, no cosmetic torso. K1 remains
unqualified until the selected export geometry/preflight has no unresolved gap.
"""
import json,re,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,OUT,SHA

ALIASES={'head:Foundation':'Foundation','FoundationStationSupports':'Foundation',
    'CP2Head:LeftRiser':'LeftRiser','CP2Head:RightRiser':'RightRiser',
    'CP2:LowerCarrier':'LowerCarrier001','LowerCarrier':'LowerCarrier001','UpperCarrier':'UpperCarrier001'}
HORN='drive:MG92BPrintedHorn20T-R2'


def identity(row):
    # Current native part name supersedes an inherited CP2 display label.
    n=row.get('part') or row.get('identity') or row.get('object')
    if not n:
        stem=Path(row['path']).stem
        n=re.split(r'_(?:current|selected|final)_',stem)[0]
        assert n in ('Foundation','UpperCarrier001','E2Fixture','FTYCradle','TailLocalRail'),('Unbound physical identity',stem)
    return ALIASES.get(n,n)


def put(parts,row,module,superseded):
    n=identity(row);r=dict(row,identity=n,selection_module=module)
    if n==HORN and n in parts:
        old=parts[n];assert old['sha256']==r['sha256'] and old['path']==r['path']
        old['quantity']+=r['quantity'];old['allocations'][module]=r['quantity'];return
    if n==HORN:r['allocations']={module:r['quantity']}
    if n in parts:
        old=parts[n];assert old['quantity']==r['quantity'],('Conflicting quantity',n,old['quantity'],r['quantity'])
        superseded.append(dict(identity=n,old_path=old['path'],old_module=old['selection_module'],replacement_path=r['path'],replacement_module=module))
    parts[n]=r


def run():
    tick=time.monotonic();files={};parts={};superseded=[]
    def read(path):
        f=ROOT/path;files[path]=SHA(f);return json.loads(f.read_text())
    prefix=BASE.relative_to(ROOT).as_posix()+'/'
    walk=read('hardware/releases/walking-p0-print.json');walk_hashes={r['path']:r['sha256'] for r in walk['files']}
    retired_p0=[]
    for row in walk['print_set']:
        if not row['id'].startswith(('P0-BASE-','P0-BATTERY-')):
            retired_p0.append(dict(identity=row['id'],path=row['export'],reason='Old DeckR2/SupportR3/MAIN-R5 replaced by CP2 plate/clamps/neck-MAIN layout; retained battery and base mechanics are separate.'));continue
        path=row['export'];assert SHA(ROOT/path)==walk_hashes[path]
        put(parts,dict(identity=row['id'],path=path,sha256=walk_hashes[path],quantity=row['quantity'],
            native=row['source'],native_object=row['object'],orientation=row['orientation'],supports=row['supports']), 'P0 retained',superseded)
    modules=[('head-wiring-checkpoint/fixed-head-current-selection.json','prints'),
        ('tail-mount-checkpoint/selection.json','prints'),('mounting-checkpoint/current-M5-selection.json','print_parts'),
        ('tail-wiring-checkpoint/selection.json','prints'),('head-supply-checkpoint/selection.json','prints'),
        ('aux-wiring-checkpoint/selection.json','prints'),('body-harness-checkpoint/e1-selection.json','prints')]
    for name,key in modules:
        q=read(prefix+name)
        for raw in q[key]:
            r=dict(raw);r['path']=raw.get('path') or raw['stl']
            assert SHA(ROOT/r['path'])==r['sha256'],r['path']
            r['source_selection']=prefix+name
            put(parts,r,name,superseded)
    station=read(prefix+'body-harness-checkpoint/station-frames-native.json')
    assert station['relocated_reopen'] and station['parameter_restore_mm']==[5.5,5.7,5.5]
    foundation=next(r for r in station['exports'] if r['part']=='FoundationStationSupports')
    put(parts,dict(foundation,native=station['native'],native_object='FoundationStationSupports',
        source_selection=prefix+'body-harness-checkpoint/station-frames-native.json'), 'current rooted Foundation',superseded)
    w5=read(prefix+'body-harness-checkpoint/w5-selection.json');assert w5['W5_complete'] and w5['selected']
    for r in w5['prints']:put(parts,dict(r,source_selection=prefix+'body-harness-checkpoint/w5-selection.json'),'W5 complete',superseded)
    assert parts[HORN]['quantity']==3 and len(parts[HORN]['allocations'])==2
    assert parts['Foundation']['native_object']=='FoundationStationSupports'
    assert parts['UpperCarrier001']['selection_module']=='W5 complete'
    assert parts['LeftRiser']['selection_module']=='W5 complete'
    assert parts['LowerCarrier001']['selection_module']=='body-harness-checkpoint/e1-selection.json'
    assert not any('HeadFixedAnchor' in p['path'] for p in parts.values())
    for r in parts.values():
        assert isinstance(r['quantity'],int) and r['quantity']>0
        assert SHA(ROOT/r['path'])==r['sha256'];files[r['path']]=r['sha256']
        if r.get('native'):
            assert (ROOT/r['native']).is_file(),r['native'];files[r['native']]=SHA(ROOT/r['native'])
        r['material']='PETG';r['print_ready']=False
        r['physical_fit_gate_open']=True
    files[Path(__file__).relative_to(ROOT).as_posix()]=SHA(Path(__file__))
    p=dict(status='ONE_WHOLE_PROTOTYPE_PRINT_IDENTITY_SET_PREFLIGHT_OPEN',selected=False,K1_complete=False,
        physical_pass=False,prints=sorted(parts.values(),key=lambda r:r['identity']),unique_print_geometries=len(parts),
        installed_print_quantity=sum(r['quantity'] for r in parts.values()),superseded_exports=superseded,
        retired_p0_jobs=retired_p0,external_cosmetic_torso_included=False,
        preserves=['P0/E6','15drives','Three replaceable provisional MG92B horns','Torso325x200x160','MAIN46.52','W5 accepted geometry'],
        native_editability='Native where supplied; inherited source snapshots remain explicitly inherited, not claimed fully migrated. Whole linked assembly is A3.',
        gates=['Selected STL actual geometry/closedness/orientation and256cube+brim preflight',
               'Physical PETG/coupons/profile/loads/calibration remain phase2; no slicer or power approval'],
        source_sha256=files,worker_seconds=round(time.monotonic()-tick,3))
    f=BASE/'phase1-print-set.json';f.write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps(dict(geometries=len(parts),installed=p['installed_print_quantity'],superseded=len(superseded),seconds=p['worker_seconds'])))


if __name__=='__main__':run()

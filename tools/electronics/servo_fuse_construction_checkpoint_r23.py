"""Pin the complete matched fourth mount; whole-bank release still fails.

Preserve the exact W031 lower-rib conflict and supersede stockR2's physical
tie count. A linked native mount is not the whole12-holder milestone.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r22/manifest.json'
    m=json.loads(prev.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    def receive(rel):
        p=ROOT/rel;add(p);j=json.loads(p.read_text(encoding='utf-8'))
        for name,h in j.get('source_sha256',{}).items():assert sha(ROOT/name)==h,name;add(ROOT/name)
        return j
    add(prev)
    fit=receive('hardware/electronics/full-cat/servo-fuse-rr-mount-pair-r2/checks.json')
    assert not fit['contacts'] and not fit['errors'] and fit['bank_mounts']==4
    native=receive('hardware/electronics/full-cat/servo-fuse-rr-mount-pair-native-r1/checks.json')
    assert len(native['exports'])==2
    for r in native['exports']:
        assert r['single_solid'] and r['strict_BOP_errors']==0 and r['closed_STL'] and r['relocated_reopen']
        assert r['local_shared_parameter']['parameter_mm']==[12,12.2,12]
        assert r['local_shared_parameter']['exact_bank_symmetric_difference_mm3']==0
        gp=ROOT/r['file'];add(gp)
        for suffix in ('_WORLD.brep','_UNSELECTED.stl'):add(gp.parent/(r['tag']+suffix))
    release=receive('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r2/checks.json')
    assert release['early_rejection'] and len(release['hits'])==1 and not release['errors']
    stock=receive('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r3/stock.json')
    assert stock['T18I']['local_installed_known']==49 and stock['T18I']['feed_tie_physical_loops']==4
    for name in ('servo_fuse_rr_mount_pair_r1.py','servo_fuse_rr_mount_pair_r2.py',
                 'servo_fuse_rr_mount_pair_native_r1.py','servo_fuse_bank_fixed_rr_lift_r2.py','servo_fuse_bank_stock_budget_r3.py'):
        add(ROOT/'tools/electronics'/name)
    for folder in ('servo-fuse-rr-mount-pair-r1','servo-fuse-rr-mount-pair-r2',
                   'servo-fuse-rr-mount-pair-native-r1','servo-fuse-bank-fixed-rr-lift-r1','servo-fuse-bank-fixed-rr-lift-r2'):
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    add(Path(__file__))
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,13,22,51,tzinfo=timezone.utc)).total_seconds(),
        completed='Matched native BankRight/Deck fourth mounting pair:29changed pairs/0contacts, actual two-arm Deck bearing, originalM2x12 stack/protrusion1.8mm/tool order, continuous changed-mount100mm. Both linked parts1solid/BOP0/closedSTL/shared numeric parameter/exact R2 match/relocated nested links. No new print/fastener/wire.',
        remaining=['Whole-module lift at2mm rejected:W031 output wire hits its own closed lower rib,28.2166868mm3. Open the twelve output-rib downward exits as one interface, preserve rib legs and all four mounts.',
                   'Remaining source/P-WAGO restraint release, shared complete mount/removal, one local selection/stock/E3 contribution.',
                   'R51 selected15/20=75%; bank NOT SELECTED/W5 OPEN.'])
    m['fourth_mount_pair']=dict(source='hardware/electronics/full-cat/servo-fuse-rr-mount-pair-native-r1/checks.json',
        exports=native['exports'],changed_axis_mm=fit['changed_axis_mm'],changed_pairs=fit['pairs'],contacts=0,
        bank_mounts=4,whole_module_lift_qualified=False)
    m['whole_bank_release']=dict(source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r2/checks.json',
        status='REJECTED',first_contact=release['hits'][0],continuous_withdrawal_qualified=False)
    m['local_bank_materials'].update(source='hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r3/stock.json',
        local_installed_ties=49,corrected='4physical feed loops, not their20 BRep fragments. StockR2 is superseded, not selected.')
    m['gates']['geometry']=dict(status='open',reason='Matched four-mount pair complete; actual output-rib/module withdrawal conflict remains.')
    m['gates']['service']=dict(status='open',reason='W031 closed rib blocks2mm lift; whole bank removal NOT qualified. Fix all12 rib exits together.')
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r23';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(pins=len(files),native_parts=2,phase1_percent=75,whole_release='REJECTED')))


if __name__=='__main__':main()

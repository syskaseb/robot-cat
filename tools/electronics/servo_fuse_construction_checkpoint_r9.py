"""Pin localized native fault and conditional assembly/stock; R8 active."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    parent=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r8/manifest.json'
    m=json.loads(parent.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[parent.relative_to(ROOT).as_posix()]=sha(parent)
    reports=[]
    for folder,name,script in [
        ('servo-fuse-parent-complete-layout-r7','native-validation.json','servo_fuse_parent_complete_layout_r7.py'),
        ('servo-fuse-deck-native-fault-r1','checks.json','servo_fuse_deck_native_fault_r1.py'),
        ('servo-fuse-bank-assembly-r4','assembly.json','servo_fuse_bank_assembly_r4.py'),
        ('servo-fuse-bank-stock-budget-r1','stock.json','servo_fuse_bank_stock_budget_r1.py')]:
        p=ROOT/'hardware/electronics/full-cat'/folder/name;r=json.loads(p.read_text(encoding='utf-8'))
        code=ROOT/'tools/electronics'/script;assert sha(code)==r['script_sha256'];files[code.relative_to(ROOT).as_posix()]=sha(code)
        for rel,h in r['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for q in p.parent.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
        reports.append(r)
    native,fault,assembly,stock=reports
    assert native['strict_BOP_report'] and fault['complete'] and len(fault['stages'])==7
    stages={r['stage']:r for r in fault['stages']}
    for key in ('DeckMainHolders/ParentFeedGripFinished','DeckMainHolders/AllFourMainSeats','DeckMainHolders/AllMainTiePassTools'):
        assert not stages[key]['strict_BOP']
    assert stages['DeckMainHolders/MainTiePassFinished']['strict_BOP']
    assert assembly['terminal_ends']==24 and stock['HELU23802']['provisional_total_mm']==2330
    for q in (ROOT/'hardware/cad/studies/servo-fuse-parent-complete-layout-r7').iterdir():
        if q.suffix in ('.FCStd','.stl','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    pending=ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r8.py'
    files[pending.relative_to(ROOT).as_posix()]=sha(pending)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,2,23,39,31,tzinfo=timezone.utc)).total_seconds(),
        completed='Localized R7 failure to final channel Cut: cached base, four-saddle union and tool union valid; final and export invalid. Conditional bench20port/24end recipe and deduplicated stock budget saved. No selected new bank or native PASS.',
        remaining=['Receive active R8 simplified integral saddles, straps through existing windows/below Deck, no new channel Cut; not yet a result.',
                   'Then actual shared contacts, native front splice/rear lap/insulation grips, cover and complete module removal.',
                   'Select one complete export and stock/E3 contribution; HELU3m includes920mm UNCHECKED legacy source allowance, LAPP4m candidate. WholeW5/E3/K3 still open.'])
    m['gates']['geometry']=dict(status='open',reason='R6/R7 final Deck export rejected; first faulty native operation localized. R8 pending, no chosen bank.')
    m['service_summary'].update(native_fault_localized='MainTiePassFinished',
        bench_recipe_candidate='servo-fuse-bank-assembly-r4/assembly.json',
        stock_budget_candidate='servo-fuse-bank-stock-budget-r1/stock.json')
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r9'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(files=len(files),phase1_percent=75,selected=False,native_fault='final_channel_Cut')))


if __name__=='__main__':main()

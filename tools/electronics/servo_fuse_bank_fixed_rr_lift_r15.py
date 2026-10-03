"""Whole module uses the matched narrowed left foot and Deck hole pair.

Both are proven subsets of original BReps. This preserves only unchanged
two-bank2mm evidence; all higher shared poses are checked against owners.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r14.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='r14_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r14','servo-fuse-bank-fixed-rr-lift-r15')
marker="    previouspath=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json'"
assert marker in code
code=code.replace(marker,"""    leftpath=ROOT/'hardware/electronics/full-cat/servo-fuse-left-mount-service-native-r7/checks.json'
    pins[leftpath.relative_to(ROOT).as_posix()]=sha(leftpath);leftnative=json.loads(leftpath.read_text(encoding='utf-8'))
    assert len(leftnative['exports'])==2 and all(q['relocated_reopen'] for q in leftnative['exports'])
    originalleft=module['BankLeft'];originaldeck=owners['CandidateDeck']
    module['BankLeft']=load('hardware/cad/studies/servo-fuse-left-mount-service-native-r7/BankLeft_WORLD.brep')
    owners['CandidateDeck']=load('hardware/cad/studies/servo-fuse-left-mount-service-native-r7/Deck_WORLD.brep')
    assert module['BankLeft'].cut(originalleft).Volume<1e-5
    assert leftnative['deck_subtractive_by_native_construction']
    assert leftnative['deck_source_brep'] in pins and pins[leftnative['deck_source_brep']]==leftnative['deck_source_brep_sha256']
    previouspath=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json'""")
code=code.replace('Native subtractive replacement, no added volume; all other fixed owners unchanged','Native Guard/BankLeft/Deck subtractive replacements proved, no added volume; remaining owners unchanged')
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""One R52 with three standard cover brackets and one offset replacement."""
from pathlib import Path
import runpy
parent=Path(__file__).with_name('servo_fuse_bank_select_r7.py')
code=runpy.run_path(str(parent),run_name='selection_definition')['code']
for old,new in [('servo-fuse-bank-stock-budget-r12','servo-fuse-bank-stock-budget-r13'),('servo-fuse-bank-assembly-r11','servo-fuse-bank-assembly-r12'),('servo-fuse-bank-fixed-rr-lift-r17','servo-fuse-bank-fixed-rr-lift-r22'),('servo-fuse-cover-deck-edge-service-r2','servo-fuse-cover-offset-mount-native-r3'),('CoverDeckEdgeServiceFinished','OffsetCoverFinished')]:
    assert old in code;code=code.replace(old,new)
marker='    definitions=['
assert marker in code
code=code.replace(marker,"""    generic=next(p for p in sel['prints'] if p['identity']=='body:upper-cover-bracket')
    assert generic['quantity']==4
    generic_stl=ROOT/generic['stl'];pins[generic['stl']]=sha(generic_stl)
    generic_dest=OUT/'prints'/'Bracket_GENERIC_SELECTED_x3.stl';generic_dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(generic_stl,generic_dest)
    generic.update(quantity=3,stl=generic_dest.relative_to(ROOT).as_posix(),sha256=sha(generic_dest),
        recipe='hardware/electronics/full-cat/servo-fuse-bank-assembly-r12/assembly.json',
        note='Three standard brackets; front-left uses one offset replacement, never print four standard plus replacement.')
"""+marker)
marker="      ('Shelf','electronics:XB11-SpliceShelf'"
assert marker in code
code=code.replace(marker,"      ('Bracket','body:upper-cover-bracket-offset-FL','servo-fuse-cover-offset-mount-native-r3','OffsetBracketFinished','PETG',10),\n"+marker)
code=code.replace("==len(sel['prints'])==76","==len(sel['prints'])==77")
code=code.replace('jobs=76,installed_jobs=72','jobs=77,installed_jobs=73')
code=code.replace('print_jobs=76','print_jobs=77')
code=code.replace("'ONE_R52_LOCAL_BANK_SELECTED',76,115","'ONE_R52_LOCAL_BANK_SELECTED',77,115")
code=code.replace("added_local_prints=['electronics:servo-fuse-bank-right','electronics:servo-fuse-bank-left','electronics:FR-return-guard']", "added_local_prints=['electronics:servo-fuse-bank-right','electronics:servo-fuse-bank-left','electronics:FR-return-guard','body:upper-cover-bracket-offset-FL'],split_bracket_quantities=dict(standard=3,offset_front_left=1),new_offset_installed_count_delta=0")
code=code.replace('R52 six pinned local prints','R52 seven pinned local prints')
code=code.replace("'Shared bank/Cover removal clear", "'Front-left Cover sideaxis(-88,-91,116), same Deck screw(-84,-91); three standard brackets plus one offset replacement.',\n            'Shared bank/Cover removal clear")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

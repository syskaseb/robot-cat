"""Check the actual relieved bank plus the connected new cover and its bridge."""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_bank_restraints_fit_r1.py')
code=base.read_text(encoding='utf-8')
code=code.replace('servo-fuse-bank-restraints-fit-r1','servo-fuse-bank-restraints-fit-r2')
code=code.replace('servo-fuse-bank-restraints-r1','servo-fuse-bank-restraints-r2')
code=code.replace('target={**parts}', """target={**parts}
    cover_name='hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep'
    old_cover=owners[cover_name]
    new_cover=load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r3/Cover_WORLD.brep')
    owners[cover_name]=new_cover
    target['CoverBridgeAddedMaterial']=new_cover.cut(old_cover)""")
code=code.replace("# Holder flange/latch", """if n=='CoverBridgeAddedMaterial' and m==cover_name:continue
            # Holder flange/latch""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

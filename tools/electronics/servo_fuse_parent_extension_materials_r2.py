"""Reconcile corrected R6 source-wire/TE sleeve stock, preserving R5 account."""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_parent_extension_materials_r1.py')
code=base.read_text(encoding='utf-8')
code=code.replace('servo-fuse-parent-extension-materials-r1','servo-fuse-parent-extension-materials-r2')
code=code.replace('servo-fuse-parent-complete-layout-r5','servo-fuse-parent-complete-layout-r6')
code=code.replace('1070','1080')
code=code.replace("insulation=part('p0:HEATSHRINK'),candidate_13mm_sleeve_blank_mm=sum(joint_lengths.values()),",
    "insulation=part('insulation:Pi:RNF-100-3/8-0-STK'),candidate_TE3_8_sleeve_blank_mm=sum(joint_lengths.values()),trial_spare_sleeve_blank_mm=52,expanded_ID_mm=9.5,recovered_ID_mm=4.8,existing_stock_m=6,no_extra_pack=True,")
code=code.replace("open='Must represent stripped bare conductors separately, not intentional overlap of two insulated tubes. Provisional sleeve envelope and stocked13mm piece length/count require confirmation before selection. Add two-sided native insulation grips.'",
    "open='R6 has distinct equivalent-solid bare Cu and solder core, no insulated-wire-overlap waiver. Existing exact TE sleeve replaces unconfirmed13mm assortment detail. Two-sided native insulation grips, delivery fit/current/pull trial remain required; no physical PASS.'")
code=code.replace("'R5 shared native fit is not yet accepted.'","'R6 shared native fit is not yet accepted.'")
code=code.replace("'Rear output W045/W053 rough110mm exceeds provisional100mm; current geometric path79.0007+strip11=90.0007mm, remaining9.9993mm does not support10mm trim reserve. Resolve explicitly, not claim supplied110mm.'",
    "'Rear output W045/W053 retain path79.0007/strip11 but explicit9mm trim reserve gives rough100mm, within provisional100/side. Factory usable length is STILL an assumption, not a supplied measurement.'")
code=code.replace("assert value['factory_rows_over_assumed100mm']==['W045','W053']",
    "assert value['factory_rows_over_assumed100mm']==[]")
code=code.replace("source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (routefile,catfile,qtyfile)},",
    "source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (routefile,catfile,qtyfile,ROOT/'tools/electronics/servo_fuse_parent_extension_materials_r1.py',ROOT/'hardware/electronics/full-cat/pi-interface-final-r2/suppliers.json')},")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

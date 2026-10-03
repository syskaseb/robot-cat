"""Guarded paired mount/service and one R52 selection, not whole phase1."""
from pathlib import Path
import runpy
parent=Path(__file__).with_name('servo_fuse_bank_close_r3.py')
code=runpy.run_path(str(parent),run_name='close_definition')['code']
for old,new in [('servo-fuse-cover-source-joint-service-r5','servo-fuse-cover-offset-mount-native-r3'),('servo-fuse-bank-fixed-rr-lift-r20','servo-fuse-bank-fixed-rr-lift-r22'),('servo-fuse-construction-checkpoint-r42','servo-fuse-construction-checkpoint-r44'),("servo-fuse-construction-checkpoint-r44'\n    out.mkdir","servo-fuse-construction-checkpoint-r46'\n    out.mkdir"),("('servo-fuse-construction-checkpoint-r35','servo-fuse-construction-checkpoint-r44')","('servo-fuse-construction-checkpoint-r35','servo-fuse-construction-checkpoint-r46')"),('servo-fuse-construction-checkpoint-r45','servo-fuse-construction-checkpoint-r47'),('servo_fuse_cover_source_joint_service_r5.py','servo_fuse_cover_offset_mount_native_r3.py'),('servo_fuse_bank_fixed_rr_lift_r20.py','servo_fuse_bank_fixed_rr_lift_r22.py'),('servo_fuse_bank_close_r3.py','servo_fuse_bank_close_r4.py')]:
    assert old in code,old;code=code.replace(old,new)
code=code.replace("native['exports'][0]['relocated_reopen'] and len(native['mounts'])==4", "all(r['relocated_reopen'] for r in native['exports']) and len(native['unchanged_Cover_bearings'])==3 and native['new_Cover_bearing_missing_mm3']<1e-5 and native['Deck_OD5_bearing_missing_mm3']<1e-5")
code=code.replace("for folder in ('servo-fuse-bank-fixed-rr-lift-r19','servo-fuse-cover-source-joint-service-r4','servo-fuse-cover-offset-mount-native-r3')", "for folder in ('servo-fuse-bank-fixed-rr-lift-r20','servo-fuse-bank-fixed-rr-lift-r21','servo-fuse-cover-offset-mount-native-r1','servo-fuse-cover-offset-mount-native-r2','servo-fuse-cover-offset-mount-native-r3')")
code=code.replace("for name in ('servo_fuse_cover_source_joint_service_r4.py',", "for name in ('servo_fuse_cover_offset_mount_native_r1.py','servo_fuse_cover_offset_mount_native_r2.py','servo_fuse_bank_fixed_rr_lift_r21.py','servo_fuse_bank_select_r8.py',")
code=code.replace('NATIVE_COVER_WHOLE_JOINT_PASSAGES_AND_SERVICE_ARCH_R20_PENDING','NATIVE_COUPLED_OFFSET_COVER_BRACKET_COMPLETE_R22_PENDING')
code=code.replace('Whole insulated W042/W044/W052 passages and one native service arch joining the measured upper wall; all four original mounts preserved. R19 short bridge swept into FR; R4 missed upper wall and split. Neither selected.', 'Native offset Cover/bracket keeps fixed source grip, full slot and arch; front-left sideaxis-88, unchanged Deck screw-84, three unchanged Cover mounts. Complete rear-left bracket corner relief preserves full OD5Deck bearing. R20/R21 rejected and retained.')
code=code.replace('R20 whole new arch continuous sweep and unchanged-core evidence plus shared full-module samples;', 'R22 changed fixed bracket and shared module samples;')
code=code.replace("source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r19/checks.json',status='R19_SHORT_BRIDGE_REJECTED_R20_NEW_ARCH_PENDING'", "source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r21/checks.json',status='R21_BRACKET_WIRE_CONTACT_REJECTED_R22_PENDING'")
code=code.replace("print('RECOVERABLE_R44'","print('RECOVERABLE_R46'")
# The selection definition already names the current pair and receipts.
a=code.index("    selection=replace(expanded('servo_fuse_bank_select_r7.py')")
b=code.index('    execute(selection)',a)+len('    execute(selection)')
code=code[:a]+"    execute(expanded('servo_fuse_bank_select_r8.py'))"+code[b:]
code=code.replace('servo_fuse_bank_select_r7.py','servo_fuse_bank_select_r8.py')
marker='    execute(assembly)'
assert marker in code
code=code.replace(marker,"""    assembly=assembly.replace('retain the original Cover brackets and mounts.', 'fit three standard Cover brackets plus the offset front-left bracket; its Deck screw remains(-84,-91), Cover side screw moves to(-88,-91,116).')
    assembly=assembly.replace('retain all Cover mount hardware.', 'retain all Cover mount hardware; use front-left sideaxis(-88,-91,116), other three Cover axes unchanged. Do not fit four generic brackets plus the offset bracket.')
    assembly=assembly.replace('part_ownership=dict(', 'cover_mount_native_source="hardware/electronics/full-cat/servo-fuse-cover-offset-mount-native-r3/checks.json",cover_bracket_quantities=dict(standard=3,offset_front_left=1),front_left_Cover_axis_mm=[-88,-91,116],unchanged_front_left_Deck_axis_mm=[-84,-91,109],part_ownership=dict(')
"""+marker)
marker='    marker="    m.update(recorded_utc'
assert marker in code
code=code.replace(marker,"    code=code.replace(\"selected['jobs']==76\",\"selected['jobs']==77\")\n"+marker)
exec(compile(code,str(Path(__file__).resolve()),'exec'))

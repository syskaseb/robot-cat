"""One R52 guarded by native whole arch and shared full module R20."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_close_r2.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='close_r2_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code']
for old,new in [
    ('servo-fuse-cover-source-joint-service-r3','servo-fuse-cover-source-joint-service-r5'),
    ('servo-fuse-bank-fixed-rr-lift-r19','servo-fuse-bank-fixed-rr-lift-r20'),
    ('servo-fuse-construction-checkpoint-r40','servo-fuse-construction-checkpoint-r42'),
    ('servo-fuse-construction-checkpoint-r42\'\n    out.mkdir','servo-fuse-construction-checkpoint-r44\'\n    out.mkdir'),
    ("('servo-fuse-construction-checkpoint-r35','servo-fuse-construction-checkpoint-r42')","('servo-fuse-construction-checkpoint-r35','servo-fuse-construction-checkpoint-r44')"),
    ('servo-fuse-construction-checkpoint-r43','servo-fuse-construction-checkpoint-r45'),
    ('servo_fuse_cover_source_joint_service_r3.py','servo_fuse_cover_source_joint_service_r5.py'),
    ('servo_fuse_bank_fixed_rr_lift_r19.py','servo_fuse_bank_fixed_rr_lift_r20.py'),
    ('servo_fuse_bank_close_r2.py','servo_fuse_bank_close_r3.py')]:
    assert old in code,old;code=code.replace(old,new)
code=code.replace("for folder in ('servo-fuse-bank-fixed-rr-lift-r18',","for folder in ('servo-fuse-bank-fixed-rr-lift-r19',")
code=code.replace("'servo-fuse-cover-source-joint-service-r1','servo-fuse-cover-source-joint-service-r5'", "'servo-fuse-cover-source-joint-service-r4','servo-fuse-cover-source-joint-service-r5'")
code=code.replace("'servo_fuse_cover_source_joint_service_r1.py','servo_fuse_cover_source_joint_service_r5.py'", "'servo_fuse_cover_source_joint_service_r4.py','servo_fuse_cover_source_joint_service_r5.py'")
code=code.replace('NATIVE_COVER_FULL_JOINT_PASSAGES_AND_MATCHED_BRIDGE_R19_PENDING','NATIVE_COVER_WHOLE_JOINT_PASSAGES_AND_SERVICE_ARCH_R20_PENDING')
code=code.replace('Whole insulated W042/W044/W052 source passages and a native short bridge preserving all four original Cover mount regions. R1 split mount rejected; R17 contact30mm retained.', 'Whole insulated W042/W044/W052 passages and one native service arch joining the measured upper wall; all four original mounts preserved. R19 short bridge swept into FR; R4 missed upper wall and split. Neither selected.')
code=code.replace('R18 installed Cover and all six withdrawal samples; only clear result permits one material/assembly/R52/commit pipeline.', 'R20 whole new arch continuous sweep and unchanged-core evidence plus shared full-module samples; only clear result permits one material/assembly/R52/commit pipeline.')
code=code.replace("source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r17/checks.json',status='R18_INSTALLED_DECK_CONTACT_REMOVED_R19_PENDING'", "source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r19/checks.json',status='R19_SHORT_BRIDGE_REJECTED_R20_NEW_ARCH_PENDING'")
code=code.replace("print('RECOVERABLE_R40'", "print('RECOVERABLE_R44'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""One R52 guarded by R19 changed-bridge sweep and whole higher poses."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_close_r1.py')
code=parent.read_text(encoding='utf-8')
for old,new in [
    ('servo-fuse-cover-source-joint-service-r2','servo-fuse-cover-source-joint-service-r3'),
    ('servo-fuse-bank-fixed-rr-lift-r18','servo-fuse-bank-fixed-rr-lift-r19'),
    ('servo-fuse-construction-checkpoint-r37','servo-fuse-construction-checkpoint-r40'),
    ('servo-fuse-construction-checkpoint-r40\'\n    out.mkdir','servo-fuse-construction-checkpoint-r42\'\n    out.mkdir'),
    ('servo-fuse-construction-checkpoint-r41','servo-fuse-construction-checkpoint-r43'),
    ('servo_fuse_cover_source_joint_service_r2.py','servo_fuse_cover_source_joint_service_r3.py'),
    ('servo_fuse_bank_fixed_rr_lift_r18.py','servo_fuse_bank_fixed_rr_lift_r19.py'),
    ('servo_fuse_bank_close_r1.py','servo_fuse_bank_close_r2.py')]:
    assert old in code,old
    code=code.replace(old,new)
# Recover the completed rejected installed-position test, never a live worker.
code=code.replace("for folder in ('servo-fuse-bank-fixed-rr-lift-r17',","for folder in ('servo-fuse-bank-fixed-rr-lift-r18',")
# The final manifest derives from this recovery, not the preceding R40.
code=code.replace("('servo-fuse-construction-checkpoint-r35','servo-fuse-construction-checkpoint-r40')","('servo-fuse-construction-checkpoint-r35','servo-fuse-construction-checkpoint-r42')")
code=code.replace('R17_REJECTED_AT30MM_R18_PENDING','R18_INSTALLED_DECK_CONTACT_REMOVED_R19_PENDING')
code=code.replace("status='NATIVE_COVER_FULL_JOINT_PASSAGES_WITH_PRESERVED_MOUNTS_R18_PENDING'","status='NATIVE_COVER_FULL_JOINT_PASSAGES_AND_MATCHED_BRIDGE_R19_PENDING'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

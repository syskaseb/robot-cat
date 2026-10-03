"""Shared offset mounting after the complete rear-left base corner relief."""
from pathlib import Path
import runpy
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r21.py')
code=runpy.run_path(str(parent),run_name='service_definition')['code']
code=code.replace('servo-fuse-bank-fixed-rr-lift-r21','servo-fuse-bank-fixed-rr-lift-r22')
code=code.replace('servo-fuse-cover-offset-mount-native-r2','servo-fuse-cover-offset-mount-native-r3')
exec(compile(code,str(Path(__file__).resolve()),'exec'))

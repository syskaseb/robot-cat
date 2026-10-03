"""Embed the foot into the measured105..109mm parent plate.

R2 had no penetration: top of actual Deck is109, not110mm. No wire or
fastener relocation. New Deck width249.5mm fits256 with6mm total brim
allowance (3mm/side), not the former unnecessary10mm assumption.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_guard_fixed_deck_r2.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r2_definition_only');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-guard-fixed-deck-r2','servo-fuse-guard-fixed-deck-r3')
assert "[-113.5,82,109,-84,88,113]" in code
code=code.replace('[-113.5,82,109,-84,88,113]','[-113.5,82,108,-84,88,113]')
code=code.replace('[-88,82,109,-84,88,110]','[-88,82,108,-84,88,109]')
exec(compile(code,str(Path(__file__).resolve()),'exec'))

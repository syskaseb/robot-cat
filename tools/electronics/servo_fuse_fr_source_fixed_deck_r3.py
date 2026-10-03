"""Match the existing small edge passage instead of filling it with a pad.

R2 is contact-free but its rectangular anchor spans a real curved edge hole.
Preserve that hole with one native pad-corner relief and test the complete
remaining foot profile. R2 support positions, wires, grips/Cover unchanged.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_fr_source_fixed_deck_r2.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='fixed_fr_r2_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-fr-source-fixed-deck-r2','servo-fuse-fr-source-fixed-deck-r3')
code=code.replace("    embeds=[]", "    pad_relief=[-83.6,-92.15,104.9,-83.25,-91.9,109.1]\n    fixture=fixture.cut(box(pad_relief))\n    assert fixture.isValid() and len(fixture.Solids)==2\n    embeds=[]")
code=code.replace('        p=box(b);v=p.common(deck).Volume','        p=box(b)\n        if name==\'Extension\':p=p.cut(box(pad_relief))\n        v=p.common(deck).Volume')
code=code.replace("expected_mm3=p.Volume,actual_mm3=v,full=", "expected_mm3=p.Volume,actual_mm3=v,profile='Pad corner preserves existing Deck edge passage' if name=='Extension' else 'Rectangular',full=")
code=code.replace('open_inner_bank_passage_mm=passage,cover_reliefs=cover_reliefs,','open_inner_bank_passage_mm=passage,cover_reliefs=cover_reliefs,pad_edge_relief_mm=pad_relief,')
code=code.replace("    owners,pins,_=ns['main']();", "    owners,pins,_=ns['main']();pins['tools/electronics/servo_fuse_fr_source_fixed_deck_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_fr_source_fixed_deck_r2.py');")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""Coupled fixed source support WITH matched open-bottom Cover passages.

R1 crossed the actual FR2 fuse holder and Cover. Put the complete factory
riser inside that holder, retain the same wire/grip, and change Cover too.
Use an actual full8mm2 extension anchorage instead of the edge-cut12mm2 strip.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_fr_source_fixed_deck_r1.py')
code=parent.read_text(encoding='utf-8')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-fr-source-fixed-deck-r1','servo-fuse-fr-source-fixed-deck-r2')
replace('    owners,pins,_=ns[\'main\']();', "    owners,pins,_=ns['main']();pins['tools/electronics/servo_fuse_fr_source_fixed_deck_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_fr_source_fixed_deck_r1.py');")
replace("('FactoryPad',[-50.7,-106,105,-46.5,-103,109])", "('FactoryPad',[-50.7,-106,105,-46.5,-93,109])")
replace("('FactoryRiser',[-50.5,-106,108.8,-46.5,-103,144.9])", "('FactoryRiser',[-50.5,-100,108.8,-46.5,-97,144.9])")
replace("('FactoryBridge',[-50.5,-106,143.9,-46,-89,147.1])", "('FactoryBridge',[-50.5,-100,143.9,-46,-89,147.1])")
replace("('Extension',[-83.5,-95,108.8,-79.5,-92,109])", "('Extension',[-83.5,-94,108.8,-79.5,-92,109])")
replace('    hits=[];errors=[];pairs=0', '''    cover=owners['ModifiableCover'];cover_reliefs=[]
    for n,b in stocks:
        c=box(b).common(cover)
        if c.Volume>1e-5:
            tool=[b[0]-.25,b[1]-.25,cover.BoundBox.ZMin-.1,b[3]+.25,b[4]+.25,b[5]+.25]
            cover_reliefs.append(dict(stock=n,tool_mm=tool,prior_contact_mm3=c.Volume))
    assert cover_reliefs
    tools=[box(r['tool_mm']) for r in cover_reliefs]
    cover_candidate=cover.cut(tools[0].multiFuse(tools[1:]))
    assert cover_candidate.isValid() and len(cover_candidate.Solids)==1
    owners['ModifiableCover']=cover_candidate
    hits=[];errors=[];pairs=0''')
replace("('BankRight',candidate)]:", "('BankRight',candidate),('Cover',cover_candidate)]:")
replace('open_inner_bank_passage_mm=passage,bank_mounts_preserved=4,', 'open_inner_bank_passage_mm=passage,cover_reliefs=cover_reliefs,bank_mounts_preserved=4,')
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""Simpler integral saddles: strap via existing windows and below Deck.

The recorded native fault proves base/seat union/tools valid and final
channel Cut invalid. Remove that operation, not its check. Inset each saddle
to the actual body footprint so both strap sides lie outside it; use existing
Deck windows/outer edge and put lower bands below the105mm underside.
Both factory exits and all eight full feed routes remain the R6 layout.
"""
from pathlib import Path

parent=Path(__file__).with_name('servo_fuse_parent_complete_layout_r7.py')
ns={'__file__':str(parent),'__name__':'r7_definition_only'}
exec(compile(parent.read_text(encoding='utf-8').rsplit('exec(compile',1)[0],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-parent-complete-layout-r7','servo-fuse-parent-complete-layout-r8')


def replace(old,new):
    global code
    assert code.count(old)==1,old[:100]
    code=code.replace(old,new)


replace('    V = A.Vector', '''    V = A.Vector
    pin(ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r7.py')
    fault_path=ROOT/'hardware/electronics/full-cat/servo-fuse-deck-native-fault-r1/checks.json'
    pin(fault_path);fault=json.loads(fault_path.read_text(encoding='utf-8'))
    stages={row['stage']:row for row in fault['stages']}
    for name in ('DeckMainHolders/ParentFeedGripFinished','DeckMainHolders/AllFourMainSeats','DeckMainHolders/AllMainTiePassTools'):
        assert not stages[name]['strict_BOP'],name
    assert stages['DeckMainHolders/MainTiePassFinished']['strict_BOP']
    stock_path=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json'
    pin(stock_path);stock_rows=json.loads(stock_path.read_text(encoding='utf-8'))['lines']
    tie=next(row for row in stock_rows if row['id']=='tie:111-02370')
    assert tie['dimensions_mm']==dict(length=145,width=2.5,thickness=1.2,head_length=4.8,head_width=4.5,height_H=3.5)
    assert 2*(134.1-104.4)+2*(96.1-78.9)+15 <145 # centreline plus project insertion reserve
''')
replace('seat=[left-1,cy-10,108.8,right+1,cy+8,111.5]',
        'seat=[left-1,cy-8,108.8,right+1,cy+8,111.5]')
replace('span(78.3,79.5,107.6,134.7),span(95.5,96.7,107.6,134.7)',
        'span(78.3,79.5,103.8,134.7),span(95.5,96.7,103.8,134.7)')
replace('span(79.5,95.5,107.6,108.8)', 'span(79.5,95.5,103.8,105.0)')
replace('span(80,84,102.6,107.6,x-3,x+3)', 'span(80.4,85.2,100.3,103.8,x-2.25,x+2.25)')
begin=code.index('        pads=[]; slots=[]')
end=code.index("        previous.Label='Four integral main fuse saddles (UNSELECTED)'",begin)
code=code[:begin]+'''        pads=[]
        print('NATIVE_SIMPLE_SADDLES_START',flush=True)
        for leg,b in seats:
            pad=d.addObject('Part::Box',leg+'MainPad');pad.Length=b[3]-b[0];pad.Width=b[4]-b[1];pad.Height=b[5]-b[2];pad.Placement.Base=V(*b[:3])
            pad.setExpression('Height','MainHolderParameters.PadHeight');pads.append(pad)
        union=d.addObject('Part::MultiFuse','AllFourMainSeats');union.Shapes=[previous]+pads;union.Refine=False
        previous=union
''' +code[end:]
replace('par.PadHeight=2.7;d.recompute();assert abs(previous.Shape.Volume-volume)<1e-5',
        'par.PadHeight=2.7;d.recompute();assert abs(previous.Shape.Volume-volume)<1e-5\n        deck=previous.Shape.copy() # export restored native result, not stale initial snapshot')
replace("old_layouts='R2/R3/R4 rejected; do not repeat'", """old_layouts='R2/R3/R4 and R6/R7 final channel Cut rejected; do not repeat',
        body_straps=dict(count=8,sku='111-02370',head_mm=[4.8,4.5,3.5],new_native_channels=0,
            lower_band_z_mm=[103.8,105.0],heads_below_z_mm=103.8,
            passes='Inner bands through existing side windows; outer bands outside95mm Deck edge. Saddle foot matches body Y footprint; no new channels through complex Deck.',
            phase2='Verify physical145mm strap insertion, PETG stiffness and holder seating; not a load or physical PASS')""")
replace("raise ValueError('R7 native topology still invalid: '+str(strict_native))",
        "raise ValueError('R8 simplified native topology invalid: '+str(strict_native))")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

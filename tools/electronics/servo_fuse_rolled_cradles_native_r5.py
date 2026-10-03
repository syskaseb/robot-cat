"""Construct the actual load path and wrap the RR body, not its interior.

R4's shortened X loops pierced the RR holder and are rejected. Use two Y
loops over its full depth, outside the stop lips, with one matching lower
cover opening. Restore the clear RR foot strip, add integral base shoulders
under the overhanging bearing slices, and use a front solid strip outside
the bank holes. No body movement, no assumed physical strength/PASS.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_cradles_native_r4.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r4'", "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r5'")
replace("CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r4'", "CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r5'")
replace("    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r3.py')", "    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r4.py')\n    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r3.py')")
replace("cover_slot=[30,-99,old_cover.BoundBox.ZMin-1,62,-97,116]", "cover_slot=[30,-101,old_cover.BoundBox.ZMin-1,64,-97,131.2]")
replace("tool.Length=32;tool.Width=2;", "tool.Length=34;tool.Width=4;")
replace("fy0,fy1=(-91,-89) if leg=='RR'", "fy0,fy1=(-94,-92) if leg=='RR'")
replace("        for j,x in enumerate((b[0]+4,-65 if leg in ('FL','FR') else b[3]-8)):", "        for j,x in enumerate((-77.5,-72.5) if leg in ('FL','FR') else (b[0]+4,b[3]-8)):")
replace("    strap_y=dict(FL=(69,73),FR=(-66,-79),RL=(66,79),RR=(-82,-77))", """    # Each shoulder is joined to the existing native Deck along its retained
    # material, and gives the full4x2mm RR foot its own integral bearing plane.
    foundation=[]
    for j,x in enumerate((31.5,54.5)):
        q=[x,-94.5,107,x+6,-91.5,109]
        integral.append(('RRFoundation'+str(j),q,None,1.5))
        parts['RR_Foundation_'+str(j)]=box(q);foundation.append(parts['RR_Foundation_'+str(j)])
    original_base=base
    base=base.fuse(foundation)
    assert base.isValid() and len(base.Solids)==1
    save(OUT/'foundation-intent.json',dict(selected=False,physical_pass=False,
        original_mm3=original_base.Volume,with_shoulders_mm3=base.Volume,
        note='Bearing is on new native shoulders, not falsely claimed on the old incomplete Deck slice. Native union/physical PETG strength still require their respective checks.'))
    strap_y=dict(FL=(69,73),FR=(-66,-79),RL=(66,79),RR=(-82,-77))""")
replace("    save(OUT/'intent.json',dict(selected=False,holders=rows,straps=straps,mounts=mount,", """    # Replace all rejected shortened RR X loops before any shared fit check.
    for n in list(parts):
        if n.startswith('RR_Tie_'):del parts[n]
    straps=[r for r in straps if r['leg']!='RR']
    b=next(h['bounds_mm'] for h in holders if h['leg']=='RR')
    z0=b[2]-1.5-1.2;z1=b[5]+1.2;outer=-98.5
    for j,x in enumerate((42,61)):
        bands=[(x-1.25,outer-1.2,z0,x+1.25,outer,z1),
               (x-1.25,b[4],z0,x+1.25,b[4]+1.2,z1),
               (x-1.25,outer,z0,x+1.25,b[4],b[2]-1.5),
               (x-1.25,outer,b[5],x+1.25,b[4],z1)]
        for k,q in enumerate(bands):parts[f'RR_Tie_{j}_Band_{k}']=box(q)
        head=[x-2.25,b[4]-4.8,z1,x+2.25,b[4],z1+3.5]
        parts[f'RR_Tie_{j}_Head']=box(head)
        length=2*((b[4]-outer)+1.2+(z1-z0)-1.2);assert length+15<=145
        straps.append(dict(leg='RR',index=j,axis='Y',x_mm=x,sku='111-02370',centreline_mm=length,reserve_mm=15,head_bounds_mm=head))
    save(OUT/'intent.json',dict(selected=False,holders=rows,straps=straps,mounts=mount,""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""Simplify the RR retention instead of forcing ties through its wiring.

Keep the clear original front pedestal, omit its conflicting second foot.
RR has native shoulder-supported feet and four manually released PETG clips
at the previously clear X strap sides. No lower/top Y band crosses XB23/XS23.
Prototype clip flex/creep and cantilever strength are phase2 trials, not PASS.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_cradles_native_r6.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r6'", "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r7'")
replace("CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r6'", "CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7'")
replace("    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r5.py')", "    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r6.py')\n    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r5.py')")
replace("cover_slot=[30,-101,old_cover.BoundBox.ZMin-1,64,-97,131.2]", "cover_slot=[30,-99,old_cover.BoundBox.ZMin-1,62,-97,116]")
replace("tool.Length=34;tool.Width=4;", "tool.Length=32;tool.Width=2;")
replace("q=[x,-94.5,107,x+6,-91.5,109]", "q=[x,-94.5,107,x+5.5,-91.5,109]")
replace("        for j,x in enumerate((-77.5,-72.5) if leg in ('FL','FR') else (b[0]+4,b[3]-8)):", "        for j,x in enumerate((-75.5,) if leg in ('FL','FR') else (b[0]+4,b[3]-8)):")
replace("    save(OUT/'intent.json',dict(selected=False,holders=rows,straps=straps,mounts=mount,", """    # Retention is deliberately changed: no impossible RR Y loops are kept.
    for n in list(parts):
        if n.startswith('RR_Tie_'):del parts[n]
    straps=[r for r in straps if r['leg']!='RR']
    clips=[]
    for j,y in enumerate((-82,-77)):
        for side in ('L','R'):
            if side=='L':
                column=[26.9,y-1.25,112,28.1,y+1.25,131.1]
                lip=[26.9,y-1.25,129.9,31.5,y+1.25,131.1]
                anchor=[26.9,y-1.25,111.5,31,y+1.25,113.5]
            else:
                column=[63.9,y-1.25,112,65.1,y+1.25,131.1]
                lip=[60.5,y-1.25,129.9,65.1,y+1.25,131.1]
                anchor=[61,y-1.25,111.5,65.1,y+1.25,113.5]
            for role,q in (('Column',column),('Lip',lip),('Anchor',anchor)):
                name=f'RRClip{j}{side}{role}';integral.append((name,q,None,1.5));parts[name]=box(q)
            clips.append(dict(index=j,side=side,column_mm=column,lip_mm=lip,anchor_mm=anchor,
                material='PETG',nominal_wall_mm=1.2,body_side_clearance_mm=.4,top_clearance_mm=.4,
                release='Unpowered removed Deck: manually flex both pairs outward, lower body, release; hold clips open before lifting body. No insertion ramp or assumed automatic snap. Tool/finger corridor and flex proof remain OPEN.',
                physical_pass=False))
    save(OUT/'clip-intent.json',dict(selected=False,physical_pass=False,clips=clips,RR_body_ties=0,
        reason='Replace crossing RR Y loops with four printed native retainers; do not call prototype flex or release physically qualified.'))
    save(OUT/'intent.json',dict(selected=False,holders=rows,straps=straps,mounts=mount,""")
replace("Two outer-strip feet support a PETG cantilever. Body seated on roof, two transverse T18I ties and0.5mm stop-lip nominal clearance. Thin RR1.5mm roof/bridge/creep/tie insertion require actual prototype trials, no strength claim.",
        "One known-clear front pedestal or two rear shoulder-supported feet carry the native roof. Six body T18I ties retained; RR uses four manually released PETG clips with0.4mm body clearance. Cantilever/clip flex/creep/insertion remain physical phase2 trials; no strength or service PASS claim.")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

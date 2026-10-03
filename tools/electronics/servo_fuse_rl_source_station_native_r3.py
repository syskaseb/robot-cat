"""RL foot north of the measured Deck slot; retain an unchanged Cover.

R2's westward foot still touched the same slot end. Use its exact north
edge plus0.3mm clearance, with the original X land and direct post. Do not
invent a new Cover cut when the existing RR Cover already clears RL.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rl_source_station_native_r2.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rl-source-station-native-r2'","servo-fuse-rl-source-station-native-r3'")
code=code.replace('fx=missing.BoundBox.XMin-.3-4','fx=cx+.5;fy=missing.BoundBox.YMax+.3')
code=code.replace("[fx,j['centre_mm'][1]-2,108.8,fx+4,j['centre_mm'][1]+2,109]", '[fx,fy,108.8,fx+4,fy+4,109]')
code=code.replace("[fx,j['centre_mm'][1]-2,108.8,fx+4,j['centre_mm'][1]+2,z]", '[fx,fy,108.8,fx+4,fy+4,z]')
code=code.replace("    prospective=prospective.fuse(box([fx,j['centre_mm'][1]-2,z-8,cx+4.5,j['centre_mm'][1]+2,z]))\n",'')
code=code.replace("        stocks.append(nativebox(d,'RLSourceFootCrossArm',[fx,j['centre_mm'][1]-2,z-8,cx+4.5,j['centre_mm'][1]+2,z]))\n",'')
a=code.index('        assert cutters\n')
b=code.index('        for o in d.Objects:',a)
existing=code[a:b].replace('        assert cutters\n','',1)
code=code[:a]+('        if cutters:\n'+''.join('    '+line if line.strip() else line for line in existing.splitlines(True))+
    '        else:\n            final=parent;cover=base.copy();cv=cover.Volume;cprobe=cv\n')+code[b:]
assert 'final.Visibility=True;d.saveAs(str(coverdest))' in code
code=code.replace('final.Visibility=True;d.saveAs(str(coverdest))',
    'final.Visibility=True\n        if cutters:d.saveAs(str(coverdest))')
needle="        s.exportBrep(str(CAD/(tag+'_WORLD.brep')))"
assert needle in code
code=code.replace(needle,'''        if tag=='Cover' and not openings:
            p=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-station-native-r4/checks.json';pin(p)
            old=json.loads(p.read_text(encoding='utf-8'))
            assert not old['hits'] and not old['errors']
            row=dict(next(r for r in old['exports'] if r['tag']=='Cover'))
            assert row['single_solid'] and row['strict_BOP_errors']==0 and row['closed_STL'] and row['relocated_reopen']
            row['inherited_unchanged']=True;exports.append(row);continue
        s.exportBrep(str(CAD/(tag+'_WORLD.brep')))''')
code=code.replace('    pins={};V=A.Vector',"    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rl_source_station_native_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_rl_source_station_native_r2.py')")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

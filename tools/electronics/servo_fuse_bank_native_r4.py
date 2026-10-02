"""Same bank: move feet off selected cover brackets and onto actual Deck.

R3 front bolts were outside Deck, not acceptable support. R4 keeps every
fuse and route in R9, changes only bank posts/feet and their four bolts.
"""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_bank_native.py')
code=base.read_text(encoding='utf-8')
code=code.replace('servo-fuse-bank-native-r1','servo-fuse-bank-native-r4')
code=code.replace('servo_fuse_side_bank_r7','servo_fuse_side_bank_r9')
code=code.replace('side*130','side*136').replace('cx=base+26*i;cy=side*110',
    "cx=base+26*i;cy=side*116\n                if side==1 and base==-69 and i==1:cx-=3\n                if side==1 and base==-69 and i==2:cx+=6")
code=code.replace('[-97,lo,144.5,107,hi,146.5]','[-97,lo,144.5,124,hi,146.5]')
code=code.replace('for x in (-95,105):','for x in (-57,122):')
code=code.replace("hx=x+(-6 if x<0 else 6);hy=side*93", "hx=x+(-6 if x<0 else 6);hy=side*92")
code=code.replace("block(tag+'Foot'+str(abs(x)),[x-9,a,109,x+9,b,113])", 
    "block(tag+'Foot'+str(abs(x)),[x-9,min(side*89,side*97),109,x+9,max(side*89,side*97),113])")
code=code.replace("sources={route_checks.relative_to(ROOT).as_posix():sha(route_checks),",
    "sources={'tools/electronics/servo_fuse_bank_native.py':sha(ROOT/'tools/electronics/servo_fuse_bank_native.py'),'tools/electronics/servo_fuse_side_bank_r8.py':sha(ROOT/'tools/electronics/servo_fuse_side_bank_r8.py'),route_checks.relative_to(ROOT).as_posix():sha(route_checks),")
code=code.replace("hardware={};tool_reserves={}", """hardware={};tool_reserves={};bearing_checks=[]
    neighbor_dir=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1'
    for p in neighbor_dir.glob('CoverBracket_*.brep'):
        owners['ActualCover/'+p.stem]=Part.read(str(p));sources[p.relative_to(ROOT).as_posix()]=sha(p)
    # Full washer bearing annulus at plate top and bottom, not merely a bolt
    # hole somewhere in the bounding box. Existing holes are excluded.
    for x,y in axes:
        footprint=cyl(x,y,105.1,wd['OD']/2,3.8).cut(cyl(x,y,105,1.2,4.1))
        missing=footprint.cut(deck).Volume
        bearing_checks.append(dict(xy=[x,y],missing_mm3=missing))
        assert missing<1e-5,('Missing Deck bearing',x,y,missing)""")
code=code.replace('deck_bolt_xy=axes,nominal_added_hardware=', 'deck_bolt_xy=axes,bearing_checks=bearing_checks,nominal_added_hardware=')
exec(compile(code,str(Path(__file__).resolve()),'exec'))

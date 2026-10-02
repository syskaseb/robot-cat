"""Witness-driven carrier correction, retaining R2 straight feed grips.

R3 failed because the S began inside those grips, four foot axes crossed
old holes, and RR hardware touched the ground shelf. Shift all feet to
X=cx+3 and Y64/70, with towers further from that shelf. Lower cover reliefs
only above the retained mount plane; use the completed native CoverR4.
Both factory exits remain represented. Source-side reach is still OPEN.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_parent_carriers_r2.py')
code=parent.read_text(encoding='utf-8')
code=code.replace('servo-fuse-parent-carriers-r2','servo-fuse-parent-carriers-r4')
code=code.replace('(11,0,0,17,10,2.5)','(-1,0,0,11,10,2.5)')
code=code.replace('(16.5,4,2.3,18.5,8,13.5)','(7.5,4,2.3,9.5,8,13.5)')
code=code.replace('(16.5,7,11.5,18.5,29.6,13.5)','(7.5,7,11.5,9.5,35.6,13.5)')
code=code.replace('(10,29.5,11.5,18.5,32,13.5)','(7.5,35.5,11.5,12,38,13.5)')
code=code.replace('(10,29.5,9.5,12,32,13.5)','(10,35.5,9.5,12,38,13.5)')
code=code.replace('(-12,29.5,9.5,12,67.5,11.5)','(-12,35.5,9.5,12,70.5,11.5)')
# Moving the foot frame to Y62 preserves the pad worldY97.5..132.5,
# body datums, tie stations and R2 wire geometry.
code=code.replace('A.Vector(cx,side*68,109)','A.Vector(cx,side*62,109)')
code=code.replace('((43.5,60.5))','((49.5,66.5))')
code=code.replace('enumerate((43.5,60.5))','enumerate((49.5,66.5))')
code=code.replace('A.Vector(14,y,-.1)','A.Vector(3,y,-.1)')
code=code.replace('enumerate((side*70,side*76))','enumerate((side*64,side*70))')
code=code.replace('x=cx+14;axes.append','x=cx+3;axes.append')
code=code.replace("oldcover=owners.pop(coverkey)",
    "owners.pop(coverkey)\n    oldcover=load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r4/Cover_WORLD.brep')")
code=code.replace("b=span(cx-12.5,97.4,116,cx+19,100.6,144.2);cuts.append(b);cover=cover.cut(box(b))",
    "b=span(cx-12.5,95.6,118.3,cx+12.5,100.6,144.2);cuts.append(b);cover=cover.cut(box(b))")
code=code.replace("installed[r['upstream_wire']+'_EXIT_ONLY']=cyl(cx,side*133,131.5,2.5,10)\n        ",'')
code=code.replace("owners,more,_=layout.current_owners();hashes.update(more)",
    "owners,more,_=layout.current_owners();hashes.update(more)\n    pin(ROOT/'tools/electronics/servo_fuse_parent_carriers_r2.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-parent-carriers-r3/checks.json')")
code=code.replace('hits=[];errors=[];access=[];pairs=0','hits=[];errors=[];access=[];installed_access=[];pairs=0')
code=code.replace('target=access if is_tool else hits;target.append(row)',
    'target=(installed_access if is_tool==2 else access) if is_tool else hits;target.append(row)')
code=code.replace("for m,t in {**owners,**installed}.items():\n            # Own foot hole/tool approach tested by actual clearance; no own body waiver.\n            check(n,s,m,t,True)",
    "for m,t in {**owners,**installed}.items():check(n,s,m,t,2)\n        for m,t in {'BareDeck':deck,**carriers}.items():check(n,s,m,t,True)")
code=code.replace('hits=hits,access_hits=access,errors=errors,pairs=pairs,',
    "hits=hits,access_hits=access,installed_access_hits=installed_access,tools_assembly_condition='Bare removed Deck before source/electronics/wiring; carriers remain stationary during bank removal.',errors=errors,pairs=pairs,")
code=code.replace("assembly='Power absent. Fasten carriers to removed Deck,",
    "assembly='Power absent. Fasten carriers to BARE removed Deck BEFORE source/electronics/wiring,")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

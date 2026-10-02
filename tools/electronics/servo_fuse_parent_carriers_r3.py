"""Correct measured R2 contacts and missing Deck bearing, keep failed R2.

Axes five mm left of the original window edge, pad shortened below the
bank ribs, lower tower clear of the RR Deck wall. Earlier wire S bypasses
W066/XS23. Cover openings preserve the actual mounting level below120.4.
Tools on a bare removed Deck are the assembly condition, not in-situ access.
Both upstream factory leads are still an unresolved connection, not chosen.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_parent_carriers_r2.py')
code=parent.read_text(encoding='utf-8')
code=code.replace('servo-fuse-parent-carriers-r2','servo-fuse-parent-carriers-r3')
code=code.replace('(-12,29.5,9.5,12,67.5,11.5)','(-12,29.5,9.5,12,64.5,11.5)')
code=code.replace('(11,0,0,17,10,2.5)','(3,0,0,9,10,2.5)')
code=code.replace('(16.5,4,2.3,18.5,8,13.5)','(8,4,2.3,10,8,13.5)')
code=code.replace('(16.5,7,11.5,18.5,29.6,13.5)','(8,7,11.5,10,29.6,13.5)')
code=code.replace('(10,29.5,11.5,18.5,32,13.5)','(8,29.5,11.5,12,32,13.5)')
code=code.replace('cx=x-10.5','cx=x-7.5')
code=code.replace('p=start+out*9;edges=[Part.makeLine(start,p)]','p=A.Vector(start);edges=[]')
code=code.replace('A.Vector(14,y,-.1)','A.Vector(6,y,-.1)')
code=code.replace('x=cx+14;axes.append','x=cx+6;axes.append')
code=code.replace("b=span(cx-12.5,97.4,116,cx+19,100.6,144.2);cuts.append(b);cover=cover.cut(box(b))",
    "for b in [span(cx-12.5,95.6,120.4,cx+12.5,100.6,144.2),span(cx-12.5,85,124,cx+12.5,100.6,135)]:\n            cuts.append(b);cover=cover.cut(box(b))")
code=code.replace("installed[r['upstream_wire']+'_EXIT_ONLY']=cyl(cx,side*133,131.5,2.5,10)\n        ",'')
code=code.replace("owners,more,_=layout.current_owners();hashes.update(more)",
    "owners,more,_=layout.current_owners();hashes.update(more)\n    pin(ROOT/'tools/electronics/servo_fuse_parent_carriers_r2.py')\n    rejected=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-carriers-r2/checks.json';pin(rejected)\n    failure=json.loads(rejected.read_text(encoding='utf-8'));assert len(failure['hits'])==22 and len(failure['access_hits'])==5 and not failure['errors']")
code=code.replace('hits=[];errors=[];access=[];pairs=0','hits=[];errors=[];access=[];installed_access=[];pairs=0')
code=code.replace("target=access if is_tool else hits;target.append(row)",
    "target=(installed_access if is_tool==2 else access) if is_tool else hits;target.append(row)")
code=code.replace("for m,t in {**owners,**installed}.items():\n            # Own foot hole/tool approach tested by actual clearance; no own body waiver.\n            check(n,s,m,t,True)",
    "for m,t in {**owners,**installed}.items():\n            check(n,s,m,t,2)\n        # Mount before source, WAGO, holders and wiring are installed.\n        # Independent carriers stay fixed during bank removal: do not claim\n        # nut tools can be used through the installed wires.\n        for m,t in {'BareDeck':deck,**carriers}.items():check(n,s,m,t,True)")
code=code.replace('hits=hits,access_hits=access,errors=errors,pairs=pairs,',
    "hits=hits,access_hits=access,installed_access_hits=installed_access,tools_assembly_condition='Bare removed Deck before source/electronics/wiring; no in-situ carrier removal qualification.',errors=errors,pairs=pairs,")
code=code.replace("assembly='Power absent. Fasten carriers to removed Deck, prewire loose P-WAGOs then close levers.",
    "assembly='Power absent. Fasten carriers to BARE removed Deck before source/electronics/wiring; only then add source assembly. Prewire loose P-WAGOs then close levers.")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

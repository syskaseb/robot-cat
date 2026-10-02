"""Construct diagonal lower service U loops outside the R3 contact witnesses.

R3's deep vertical spines atY97.9 hit source/Pi parts. Move those spines
10mm outwards and24.8mm sideways using an R12.4 S below the fixed upper
turn. A diagonal U keeps at least26.59mm between its arms even at release,
unlike the impossible19.6mm planar U. No minimum bend radius is relaxed.
Full new installed routes plus four release poses; still not a swept or
physical test. Sources and rejected R3 geometry remain preserved.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_connected_release_r3.py')
code=parent.read_text(encoding='utf-8')
code=code.replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r3'",
                  "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4'")
begin=code.index("    code=code.replace('R=12.4):'")
end=code.index("    ns={'math':math}",begin)
replacement='''    code=code.replace('R=12.4):','R=12.4, release=0):')
    first=code.index('    assert p.z>end[2]')
    last=code.index('    for a,b in zip(edges,edges[1:]):',first)
    tail="""    transverse=A.Vector(-2*R,side*10,0)
    shift=transverse.Length;transverse=transverse/shift
    arc(dz,transverse,math.pi/2)
    line(p+transverse*(shift-2*R))
    arc(transverse,dz,math.pi/2)
    cross=A.Vector(end[0]-p.x,end[1]-p.y,0)
    gap=cross.Length;assert gap>2*R
    installed_gap=math.hypot(2*R,25.1-10)
    drop=(installed_gap-gap)/2
    assert -1e-6<=drop<2
    assert p.z>end[2]-35-drop
    line(A.Vector(p.x,p.y,end[2]-35-drop))
    across=cross/gap
    arc(dz,across,math.pi/2)
    line(p+across*(gap-2*R))
    arc(across,up,math.pi/2)
    line(A.Vector(*end))
    assert (p-A.Vector(*end)).Length<1e-6
"""
    code=code[:first]+tail+code[last:]
    extra=50+12.4*math.pi+math.hypot(24.8,10)-49.6+math.hypot(24.8,15.1)-25.1
'''
code=code[:begin]+replacement+code[end:]
code=code.replace("    source=ROOT/'tools/electronics/servo_fuse_side_bank_r8.py';pin(source)",
    "    source=ROOT/'tools/electronics/servo_fuse_side_bank_r8.py';pin(source)\n    pin(ROOT/'tools/electronics/servo_fuse_bank_connected_release_r3.py')\n    rejected=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r3/checks.json';pin(rejected)\n    failure=json.loads(rejected.read_text(encoding='utf-8'));assert failure['hits'] and not failure['errors']")
code=code.replace("added_insulated_path_mm_per_wire=50", "added_insulated_path_mm_per_wire=extra")
code=code.replace("service_S_start_z_mm=80", "service_S_start_z_mm=96.1,lower_spine_outward_mm=10,lower_spine_X_shift_mm=-24.8")
code=code.replace("constant_length_identity_mm='S_arc_excess-2*U_rise=0'", "constant_length_identity_mm='U_gap_reduction-2*U_drop=0'")
code=code.replace("nominal_bank_input_stock_mm=spec['planned_required_blank_mm']+12*50", "nominal_bank_input_stock_mm=sum(math.ceil((r['path_mm']+extra+14+8.30+10)/10)*10 for r in spec['lengths'])")
code=code.replace("nominal_bank_input_and_W001_mm=spec['planned_required_blank_mm']+12*50+140", "nominal_bank_input_and_W001_mm=sum(math.ceil((r['path_mm']+extra+14+8.30+10)/10)*10 for r in spec['lengths'])+140")
code=code.replace("sequence='Power absent. Use inputs50mm longer, prewire loose WAGO and close levers before mounting. Thread bare wires through Deck before TE crimps; form deeper installedU. Remove ATO/unclip holders and raise10mm; cut24bank ties. Keep upper fans fixed; release inputTE5.5mm inward using only lower serviceS/U. OutputTE stay fixed. Barebank/cover lift inherited from service-r3 only if wires clear. New lower spans need actual current Deck/P0 fit; do not assume old portals suffice.'",
    "sequence='Power absent. Use explicit longer blanks from this construction, prewire looseWAGO and close levers before mounting. Thread bare wires beforeTE crimps. Form lower diagonalU beyond source/Pi obstacles; upperfans fixed. RemoveATO/unclip holders/raise10mm, cut24bank ties. Release inputTE5.5mm inward by rotating the lowerU direction and lowering its bottom to preserve wirelength. OutputTE stationary; bank/cover lift needs shared fit. No continuous or physical motion qualification.'")
code=code.replace("target=row['path_mm']+50", "target=row['path_mm']+extra")
code=code.replace("blank_mm=r['nominal_unselected_blank_mm']+50", "blank_mm=math.ceil((r['path_mm']+extra+14+8.30+10)/10)*10")
code=code.replace('FIXED_PORTAL_LOWER_U_RELEASE','DIAGONAL_LOWER_SERVICE_U')
code=code.replace("print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs))", "print(json.dumps(dict(hit_count=len(hits),error_count=len(errors),pairs=pairs))")
exec(compile(code,str(Path(__file__).resolve()),'exec'))

"""Complete named obstacle scope and actual CAD sections before route changes.

This is a planning map, not route/clearance acceptance. Retained parts,
replaceable supports, delivery reservations and rejected candidate stations
remain distinct. No source CAD is saved or rebuilt.
"""
from datetime import datetime, timezone
from pathlib import Path
import html, json, math, re, time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds
from open_prototype_entry_chambers import MOUNTS, CONTEXT

OUT=BASE/'wiring-checkpoint'
DEST=OUT/'obstacle-sections.json'
VIEW=OUT/'obstacle-sections.html'
TAIL=OUT/'TailLocalCurrent.FCStd'
NATIVE=OUT/'CommonMtaMounts.FCStd'
PLAN=OUT/'power-harness-plan.json'
LEVELS=[22.677,47.72,67.99,82.72,96,110,120,130,140,147]
COLORS={'retained':'#334155','replaceable_support':'#e2a03b',
        'candidate_station':'#c0392b','service_budget':'#36a3bf',
        'delivery_reservation':'#9861bd'}


def main():
    import FreeCAD as A
    import Part
    assert not DEST.exists() and not VIEW.exists(),'Receive map, do not rerun unchanged'
    tick=time.monotonic();paths=[MOUNTS,CONTEXT,TAIL,NATIVE,PLAN,Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    docs=[A.openDocument(str(p)) for p in paths[:4]]
    mount,ctx,tail,native=docs;plan=read(PLAN);scene={};errors=[]
    def put(name,s,kind,basis):
        if not s.isValid() or not s.Solids:
            errors.append(dict(part=name,error='Invalid/non-solid input'));return
        scene[name]=(s,kind,basis)
    try:
        for ob in ctx.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():continue
            n=ob.Name
            bank=bool(re.fullmatch(r'F_[LR][1-6]_CP2_(Housing|ATO|IN|OUT)',n))
            if n=='P0_MG92BMount29':continue # CurrentTailSupport replaces it
            if n.startswith(('P0_','Head_','TailBridge','S0_','S1_')) or bank or n=='F_PWM_CP2' or n in ('LeftRiserWithMain','RightRiser','MainSupplierFamily'):
                kind='service_budget' if any(k in n.lower() for k in ('driver','key','tool')) else 'retained'
                put(n,ob.Shape,kind,'Canonical CP2 world-space reference; no second placement')
        bank_names=[n for n in scene if re.fullmatch(r'F_[LR][1-6]_CP2_(Housing|ATO|IN|OUT)',n)]
        assert len(bank_names)==48,bank_names
        assert 'F_PWM_CP2' in scene
        put('CurrentTailSupport',tail.CurrentTailSupport.Shape,'retained','Replacement of P0_MG92BMount29; current +15mm already in saved world shape')
        for ob in native.Objects:
            if ob.TypeId=='PartDesign::Body':put(ob.Name,ob.Shape,'replaceable_support','Existing support invalidated by proposed station moves; NOT silently waived')
        for ob in mount.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():continue
            if ob.Name.endswith('NominalPCB') or ob.Name.startswith('BUSsupplier') or ob.Name=='U1BoardAllowance':
                put(ob.Name,ob.Shape,'delivery_reservation' if ob.Name=='U1BoardAllowance' else 'retained','Current board/reference; U1 supplied pad/thickness/outer module map remains unknown')
            if 'Group' in ob.PropertiesList and 'Hardware' in ob.Name:
                for child in ob.Group:
                    if 'Shape' in child.PropertiesList and not child.Shape.isNull():
                        put(child.Name,child.Shape,'service_budget' if 'driver' in child.Name.lower() else 'retained','Current mounting hardware, not support template at origin')
        # Unknown delivered components are not assumed absent. This NEW12mm
        # design reservation above the board is provisional, not a catalogue
        # dimension or a supplier pad map, and cannot qualify U1 after delivery.
        b=mount.U1BoardAllowance.Shape.BoundBox
        put('U1UnknownModuleReservation',Part.makeBox(b.XLength,b.YLength,12,A.Vector(b.XMin,b.YMin,b.ZMax)),
            'delivery_reservation','PROJECT12mm above current board, not measured/supplier height; replace after delivery')
        for row in plan['distribution']+plan['mts']:
            ob=mount.getObject(row['native']) or ctx.getObject(row['native']);s=ob.Shape.copy();b=s.BoundBox
            s.translate(-A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2))
            if row.get('rotation_z_deg'):s.rotate(A.Vector(),A.Vector(0,0,1),row['rotation_z_deg'])
            s.translate(A.Vector(*row['centre_mm']));put(row['native'],s,'candidate_station','REJECTED power hypothesis overlay; movable, never a selected/fixed constraint')
        for row in plan['holders']:
            s=mount.getObject(row['holder']+'_body_budget_CurrentReference').Shape.copy();b=s.BoundBox
            s.translate(-A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2))
            rot=A.Rotation(A.Vector(1,0,0),A.Vector(*row['axis']))
            s.rotate(A.Vector(),rot.Axis,math.degrees(rot.Angle))
            s.translate(A.Vector(*row['input_mm'])+A.Vector(*row['axis'])*25.5+A.Vector(0,0,1))
            put(row['holder'],s,'candidate_station','Rejected FHAC pose, existing nominal case reference, not delivered lead data')
        torso=ctx.TorsoEnvelope.Shape;assert torso.isValid()
        inventory=[dict(name=n,kind=k,basis=b,bounds_mm=[round(x,4) for x in bounds(s)]) for n,(s,k,b) in scene.items()]
        sections=[];panels=[]
        for z in LEVELS:
            contours=[];svg=[]
            for n,(s,kind,basis) in [('TorsoEnvelope',(torso,'retained','Accepted outline'))]+list(scene.items()):
                if not s.BoundBox.ZMin<z<s.BoundBox.ZMax:continue
                try:
                    for wire in s.slice(A.Vector(0,0,1),z):
                        points=wire.discretize(Deflection=.25)
                        xy=[[round(p.x,3),round(p.y,3)] for p in points]
                        if len(xy)<2:continue
                        contours.append(dict(part=n,kind=kind,xy_mm=xy))
                        pts=' '.join(f'{x},{-y}' for x,y in xy)
                        color='#111827' if n=='TorsoEnvelope' else COLORS[kind]
                        svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{1.3 if n=="TorsoEnvelope" else .65}"><title>{html.escape(n)}</title></polyline>')
                except Exception as exc:errors.append(dict(part=n,z_mm=z,error=str(exc)))
            sections.append(dict(z_mm=z,contours=contours))
            panels.append(f'<section><h2>Z {z:g} mm</h2><svg viewBox="-120 -106 325 212">'+''.join(svg)+'</svg></section>')
            print(f'section Z{z:g}: {len(contours)} contours',flush=True)
        result=dict(status='COMPLETE_NAMED_OBSTACLE_SECTION_MAP_NOT_ROUTE_ACCEPTANCE',
            selected=False,stage_completed=False,physical_pass=False,source_sha256=pins,
            bank_reference_count=len(bank_names),objects=inventory,sections=sections,errors=errors,
            scope_additions=['48R47 housing/ATO/TE references','F_PWM_CP2','CurrentTailSupport','Neck MAIN family/risers','U1 unknown module PROJECT reservation'],
            scope_limitations=['Does not qualify delivered parts or all moving ranges','Planes/0.25mm contour discretization are a planning aid, not full conductor/curve/grip clearance','Candidate station poses are REJECTED, not fixed obstacles','Support and hardware replacement needs an explicit native load path','Original four S1 rings retained; down-facing rejected replacements are not accepted'],
            next='Allocate complete power corridors with R25.2 bends, clear bank/boards/retained structure, independent grips and service space; only then detail matched supports')
        VIEW.write_text('<!doctype html><meta charset="utf-8"><title>Robot-cat: plan przestrzeni</title><style>body{font:15px system-ui;background:#f8fafc;color:#172033;margin:22px}main{display:grid;grid-template-columns:repeat(2,minmax(320px,1fr));gap:16px}section{background:white;border:1px solid #ddd;padding:10px}svg{width:100%;height:auto}h2{margin:4px}</style><h1>Rzeczywiste przekroje CAD, planowanie etapu3</h1><p>Szare: zachowane części. Pomarańczowe: podpory wymagające uzgodnienia. Czerwone: ODRZUCONY układ kupnych części. Niebieskie: narzędzia. Fioletowe: rezerwacje do pomiaru. Jednostki mm, X poziomo, +Y do góry. Tułów325×200×160 bez poszerzania. To nie dowód wolnej trasy ani fizycznego PASS.</p><main>'+''.join(panels)+'</main>',encoding='utf-8')
    finally:
        for d in docs:A.closeDocument(d.Name)
    result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
    DEST.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    assert all(sha(ROOT/n)==v for n,v in pins.items())
    assert not errors,errors
    print(json.dumps(dict(status=result['status'],objects=len(scene),bank=48,sections=len(sections),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()

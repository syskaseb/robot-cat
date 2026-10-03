"""One coherent fourth-bank-mount/Deck pair outside the fixed RR cage.

Move the original Foot57/Post57 together16mm outboard. Preserve three other
mounts, actual M2x12 stack and all wires. Check only new stock/stack/access
and its continuous straight withdrawal against the current full owners.
No repeated full-part Boolean checks of unchanged surfaces.
"""
from pathlib import Path
from datetime import datetime, timezone
import math, json, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save
OUT = ROOT / 'hardware/electronics/full-cat/servo-fuse-rr-mount-pair-r1'


def main():
    import FreeCAD as A
    import Part
    start = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'checks.json').exists()
    loader = ROOT / 'tools/electronics/servo_fuse_rr_clip_approach_r1.py'
    code = loader.read_text(encoding='utf-8').split('    # These boxes are exactly')[0]
    code = code.replace('servo-fuse-rr-clip-approach-r1', 'servo-fuse-rr-mount-pair-r1') + '    return owners,pins,final\n'
    ns = dict(__file__=str(loader), __name__='mount_owner_recipe')
    exec(compile(code, str(loader), 'exec'), ns)
    owners, pins, exports = ns['main']()
    pins[loader.relative_to(ROOT).as_posix()] = sha(loader)

    def load(rel):
        p = ROOT / rel; pins[rel] = sha(p)
        return Part.read(str(p))

    def box(b):
        return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))

    def cyl(x, y, z, r, h):
        return Part.makeCylinder(r, h, A.Vector(x, y, z))

    def bounds(s):
        return [getattr(s.BoundBox, k) for k in ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax')]

    deck = load('hardware/cad/studies/servo-fuse-rr-fixed-station-native-r1/Deck_WORLD.brep')
    bank = load('hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRight_WORLD.brep')
    module = dict(BankLeft=owners.pop('Bank/LeftClipAccessFinished_WORLD'), Cover=owners.pop('ModifiableCover'))
    owners.pop('Bank/RightClipAccessFinished_WORLD')
    owners['CandidateDeck'] = deck
    fp = ROOT / 'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRightRearOutputPassages.FCStd'
    pins[fp.relative_to(ROOT).as_posix()] = sha(fp)
    d = A.openDocument(str(fp))
    try:
        oldfoot = d.RightFoot57.Shape.copy()
        oldpost = d.RightPost57.Shape.copy()
    finally:
        A.closeDocument(d.Name)
    assert bounds(oldfoot) == [-66., -97., 109., -48., -89., 113.], bounds(oldfoot)
    assert bounds(oldpost) == [-59., -97., 109., -55., -91., 144.7], bounds(oldpost)
    shift = -16.
    foot = oldfoot.copy(); foot.translate(A.Vector(0, shift, 0))
    post = oldpost.copy(); post.translate(A.Vector(0, shift, 0))
    axis = [-63., -108.5]
    hole = cyl(*axis, 104.9, 1.2, 8.2)
    bank_remainder = bank.cut(oldfoot.fuse(oldpost))
    bank_new = bank_remainder.multiFuse([foot, post]).cut(hole)
    assert bank_new.isValid() and len(bank_new.Solids) == 1 and not bank_new.check(True)
    module['BankRight'] = bank_new
    # A4mm plate shoulder carries the same washer/foot stack as the original.
    ledge_bounds = [-73., -117., 105., -48., -92., 109.]
    ledge = box(ledge_bounds).cut(hole)
    embedded = ledge.common(deck).Volume
    assert embedded > 1e-5, ('No real Deck support', embedded)
    cartpath = ROOT / 'hardware/manufacturing/fixed-fastener-skus-r1/cart.json'
    pins[cartpath.relative_to(ROOT).as_posix()] = sha(cartpath)
    rows = json.loads(cartpath.read_text(encoding='utf-8'))['rows']
    bolt = next(r for r in rows if r['supplier_sku']=='0912A2-M020X012VISK')
    nut = next(r for r in rows if r['supplier_sku']=='SKL000381')
    washer = next(r for r in rows if r['supplier_sku']=='00125202')
    bd, nd, wd = bolt['dimensions_mm'], nut['dimensions_mm'], washer['dimensions_mm']
    assert bd['L']==12 and bd['d']==2
    x, y = axis; underhead = 113 + wd['t']; tip = underhead-bd['L']
    nut_top = 105-wd['t']; nut_z = nut_top-nd['H']
    protrusion = nut_z-tip
    assert protrusion >= bd['pitch'], protrusion
    def ring(z):
        return cyl(x,y,z,wd['OD']/2,wd['t']).cut(cyl(x,y,z-.1,wd['ID']/2,wd['t']+.2))
    rad=nd['AF']/math.sqrt(3)
    points=[A.Vector(x+rad*math.cos(k*math.pi/3),y+rad*math.sin(k*math.pi/3),nut_z) for k in range(6)]
    hw=dict(Bolt=cyl(x,y,tip,1,bd['L']).fuse(cyl(x,y,underhead,bd['head_d']/2,bd['head_h'])),
        Washers=Part.makeCompound([ring(113),ring(105-wd['t'])]),
        Nut=Part.Face(Part.makePolygon(points+[points[0]])).extrude(A.Vector(0,0,nd['H'])).cut(cyl(x,y,nut_z-.1,1,nd['H']+.2)))
    tools=dict(Allen=cyl(x,y,underhead+bd['head_h'],2,28),
        NutTool=cyl(x,y,nut_z-20,3.5,20).cut(cyl(x,y,nut_z-20.1,1.1,20.2)))
    hits=[];errors=[];pairs=0
    def check(phase, name, s, key, t, intended=None):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox): return
        pairs += 1
        try:
            c=s.common(t)
            if intended is not None and c.Volume>1e-5: c=c.cut(intended)
            if c.Volume>1e-5:
                hits.append(dict(phase=phase,part=name,owner=key,mm3=c.Volume,bounds_mm=bounds(c)))
                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as exc: errors.append(dict(phase=phase,part=name,owner=key,error=str(exc)))
    for name,s in dict(Foot=foot.cut(hole),Post=post,DeckLedge=ledge,**hw).items():
        for key,t in owners.items():
            # Only the actual new ledge embedding in its parent is intentional.
            if name=='DeckLedge' and key=='CandidateDeck': continue
            check('installed_delta',name,s,key,t)
        if name=='DeckLedge':
            for key,t in module.items(): check('installed_delta',name,s,key,t)
    for name,s in hw.items():
        for key,t in module.items(): check('stack',name,s,key,t)
        check('stack',name,s,'DeckLedge',ledge)
    for name,s in tools.items():
        for key,t in dict(owners,**module,DeckLedge=ledge).items(): check('tool_access',name,s,key,t)
    print('RR_MOUNT_PAIR_STATIC',pairs,len(hits),len(errors),flush=True)
    # A rectangular enclosure is exact for translated rectangular mounting stock.
    # The hole is conservatively filled, not used to waive a collision.
    for name,s in [('Foot',foot),('Post',post)]:
        b=bounds(s); b[5] += 100
        sweep=box(b); sweep.exportBrep(str(OUT/(name+'_LIFT_ENVELOPE.brep')))
        for key,t in owners.items(): check('continuous_changed_mount_100mm',name,sweep,key,t)
    print('RR_MOUNT_PAIR_WITHDRAWAL',pairs,len(hits),len(errors),flush=True)
    # No repeat of expensive global Deck BOP when a local contact already rejects it.
    for name,s in dict(BankRight=bank_new,Foot=foot,Post=post,DeckLedge=ledge,**hw,**tools).items():
        s.exportBrep(str(OUT/(name+'_CANDIDATE.brep')))
    footprint=cyl(x,y,105.1,wd['OD']/2,3.8).cut(cyl(x,y,105,1.2,4.1))
    bearing_missing=footprint.cut(ledge).Volume
    assert bearing_missing<1e-5, bearing_missing
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='RR_MOUNT_PAIR_DELTA_CLEAR' if not hits and not errors else 'RR_MOUNT_PAIR_CONFLICTS',
        selected=False,physical_pass=False,W5_complete=False,bank_mounts=4,changed_axis_mm=axis,
        prior_axis_mm=[-63,-92.5],shift_y_mm=shift,ledge_bounds_mm=ledge_bounds,
        actual_parent_embed_mm3=embedded,washer_bearing_missing_mm3=bearing_missing,
        bank_single_solid=True,bank_strict_BOP_errors=0,fasteners_reused=[bolt['supplier_sku'],nut['supplier_sku'],washer['supplier_sku']],
        additional_fasteners=0,additional_prints=0,protruding_thread_mm=protrusion,
        contacts=hits,errors=errors,pairs=pairs,changed_mount_continuous_lift_mm=100,
        entire_bank_lift_qualified=False,native_export_complete=False,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('RR_MOUNT_PAIR_RESULT',json.dumps(dict(pairs=pairs,contacts=len(hits),errors=len(errors),selected=False)),flush=True)


if __name__=='__main__': main()

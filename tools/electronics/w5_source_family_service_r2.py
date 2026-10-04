"""Receive unchanged bank lift; check complete changed interfaces only.

Direct R1 was stopped in its first large inherited bank/Deck Boolean after
793.89 CPU seconds. It produced no bank-lift result. Do not repeat it.
Subtractive native changes inherit R22 only for identical fixed material;
all added Carrier/Deck/platform/BUS/source interfaces are checked afresh.
"""
from pathlib import Path
BASE = Path(__file__).with_name('w5_source_family_service_r1.py')
code = BASE.read_text(encoding='utf-8').replace('w5-source-family-service-r1', 'w5-source-family-service-r2')
begin = code.index('    completed = []\n')
end = code.index('    end = datetime.now(timezone.utc)', begin)
code = code[:begin] + '''    # Existing R22 checked all unchanged installed material at these poses.
    # Native BankLeft and Cover passages remove only material. New posts,
    # Carrier insulation seats, platform/pads and BUS additions do NOT inherit.
    receipts = {}
    for name in ('w5-source-bank-passage-native-r1', 'w5-source-cover-passages-native-r1',
                 'w5-source-carrier-native-r1', 'w5-source-grips-native-r2',
                 'w5-source-platform-native-r4', 'w5-source-roof-native-r3',
                 'w5-bus-native-grips-r4'):
        receipt = read('hardware/electronics/full-cat/' + name + '/checks.json')
        assert not receipt['hits'] and not receipt.get('errors', [])
        assert all(sha(ROOT/k) == v for k,v in
                   {**receipt['source_sha256'], **receipt.get('files', {})}.items())
        receipts[name] = receipt
    assert receipts['w5-source-bank-passage-native-r1']['unchanged_parent_mounts']
    assert receipts['w5-source-carrier-native-r1']['parent_supports_preserved_by_subtraction']
    assert receipts['w5-source-grips-native-r2']['received_carrier_material_preserved']
    assert receipts['w5-source-roof-native-r3']['original_Cover_material_preserved']
    # Match actual selected baseline parents to the R22 proof, not merely their names.
    for rel in ('hardware/cad/studies/servo-fuse-left-mount-service-native-r7/BankLeft_WORLD.brep',
                'hardware/cad/studies/servo-fuse-bank-inner-feed-service-r1/BankRight_WORLD.brep',
                'hardware/cad/studies/servo-fuse-cover-offset-mount-native-r3/Cover_WORLD.brep'):
        assert oldproof['source_sha256'][rel] == sha(ROOT/rel), rel
        pins.append(ROOT/rel)
    changed = {k:v for k,v in owners.items() if
               k.startswith(('R53BUS/', 'SourceInlet/')) or k in
               ('SourcePlatform','P_SYS_received','W066_received','W043_received','S1_reserved_casing')}
    changed['CarrierAddedSeats'] = load('hardware/electronics/full-cat/w5-source-grips-native-r2/ADDED_SEATS_WORLD.brep')
    changed['SourceDeckBearingPad'] = load('hardware/electronics/full-cat/w5-source-platform-native-r4/DeckBearingPad_WORLD.brep')
    # Full uncut support primitives conservatively include every added BUS
    # support. R4 only cuts slots from R3; the G1 parent only removes material.
    import w5_bus_restraints_r3 as bus
    intent = read('hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json')
    sx = sum(intent['source_lead_datums'][w][0] for w in ('W002','W003'))/2
    for label,b in bus.supports(sx):
        changed['BusSupportEnvelope/'+label] = Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    pins.append(Path(bus.__file__))
    added_posts = load('hardware/electronics/full-cat/w5-source-roof-native-r3/AddedPosts_WORLD.brep')
    completed = []
    for dz in (2, 5, 10, 30, 60, 100):
        before = len(hits)+len(errors)
        for label, shape in module.items():
            moved = shape.copy(); moved.translate(A.Vector(0,0,dz))
            check('changed_fixed_lift_'+str(dz),label,moved,changed)
        moved = added_posts.copy(); moved.translate(A.Vector(0,0,dz))
        check('new_posts_lift_'+str(dz),'AddedCoverPosts',moved,owners)
        print('SOURCE_CHANGED_BANK_COVER_LIFT',dz,pairs,len(hits),len(errors),flush=True)
        if len(hits)+len(errors) != before:
            break
        completed.append(dz)
''' + code[end:]
code = code.replace('samples_not_continuous=True, Carrier_kept_fixed=True,',
    'samples_not_continuous=True, Carrier_kept_fixed=True, inherited_unchanged_bank_lift=oldproof["completed_clear_lifts_mm"], changed_fixed_owners=list(changed), direct_R1_withdrawal_not_qualified=True,')
code = code.replace('dict.fromkeys([*pins, Path(__file__)])', 'dict.fromkeys([*pins, Path(__file__), BASE])')
exec(compile(code, str(Path(__file__).resolve()), 'exec'))

"""Remove the whole self-crossing graph loop, not move the purchased endpoint.

Planning recipe only. Actual scene, motion and completeness remain separate.
"""
import json
import feline_tangent_routes as ft
from plan_feline_layout import OUT


def recipe():
    source = OUT / 'W009-W069-harness-corridor/W009-saved-portals.json'
    old = next(r for r in json.loads(source.read_text())['proposals']
               if r['end_heading'] == 0)
    before, after = old['parts'][:20], old['parts'][31:]
    assert before[-1]['end'] == [72.0, -10.0, 38.0]
    assert after[0]['start'] == [32.0, -18.0, 38.0]
    # Replace the graph's eleven-segment crossing loop by one tangent biarc.
    link = ft.biarc(before[-1]['end'], (-1, 0, 0),
                    after[0]['start'], (-1, 0, 0))
    parts = before + link + after
    assert ft.min_radius(parts) >= 12.4
    assert parts[0]['start'] == old['parts'][0]['start']
    assert parts[-1]['end'] == old['parts'][-1]['end']
    return dict(parts=parts, radius_mm=1.55, length_mm=ft.length(parts),
                minimum_R_mm=ft.min_radius(parts),
                actual_whole_scene_and_motion_open=True)


def preserve(actor, result, metadata, context):
    """Classify existing exact distances, pin recovered wire identities, save."""
    import hashlib
    import zipfile
    from pathlib import Path
    from check_main_p0_placement import ROOT, sha
    from feline_fore_power_pair import pair_spacing
    from feline_atomic_save import save_json
    folder = OUT / 'W009-W069-harness-corridor'
    dest = folder / 'W009-east-loop-removed.json'
    assert not dest.exists()
    frpath = OUT / 'n01-FR-vertical9-rooted-space.json'
    fr = json.loads(frpath.read_text())
    records = {r['name']: r for r in fr['geometry']}
    recovered = {r['name']: r for r in context['geometry']}
    own = {'VerticalCuff:W009/body/start', 'Station:D_FR:wire:D_FR.3'}
    checks = {}
    for name, row in result['checks'].items():
        typed = dict(metadata.get(name, {}))
        if name in fr['source_recipes']:
            assert recovered[name]['recovered_source'][2] == records[name]['sha256']
            typed.update(kind='wire', wire=fr['source_recipes'][name]['wire'])
        minimum = 0 if name in own else pair_spacing(
            'CurrentMiddle:W009', dict(kind='wire', wire='W009'), name, typed)
        ok = row['gap_mm'] >= minimum - 1e-6
        if name in own:
            ok = ok and row['gap_mm'] < 1e-6 and row.get('common_mm3', 1) < 1e-5
        checks[name] = dict(row, minimum_mm=minimum, ok=ok)
    archive = dest.with_suffix('.breps.zip')
    raw = actor.exportBrepToString().encode()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('W009.brep', raw)
    packet = dict(status='RECOVERED_SUBSET_SPACING_POSITIVE' if
                  all(r['ok'] for r in checks.values()) and not result['errors'] else 'HOLD',
                  recipe=recipe(), checks=checks, errors=result['errors'],
                  unrecovered=result['unrecovered'], whole_scene_received=False,
                  N01_complete=False, physical_pass=False,
                  geometry=[dict(name='CurrentMiddle:W009', entry='W009.brep',
                                 sha256=hashlib.sha256(raw).hexdigest())],
                  bundle=archive.relative_to(ROOT).as_posix(), bundle_sha256=sha(archive),
                  source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in
                      [frpath, folder/'recovered-context.json', folder/'W009-saved-portals.json',
                       folder/'W009-east-loop-removed-subset.json', Path(__file__)]})
    save_json(dest, packet)
    print(packet['status'], [n for n, r in checks.items() if not r['ok']], flush=True)
    return packet

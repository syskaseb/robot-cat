"""Re-adjudicate the frozen necessary bounds, not repeat BRep queries.

Keep all old witnesses and all foreign obstructions. A bound no longer
rejecting a named own groove does NOT become a route or clearance PASS.
"""
import collections, gzip, json, time
from pathlib import Path
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from compose_feline_output_boundaries import current
from feline_received_own_channels import own_channel
from feline_terminal_escape import bound
from feline_atomic_save import save_json


def main():
    tick = time.monotonic()
    _, ends, files = current(); index = {e['id']: e for e in ends}
    sf = OUT/'n01-whole-terminal-escape.json'; screen = json.loads(sf.read_text())
    rf = ROOT/screen['rows']; assert sha(rf) == screen['rows_sha256']
    old = json.loads(gzip.decompress(rf.read_bytes()))
    pi = OUT/'n01-shared-Pi-carrier-r3-core-received.json'
    receipt = json.loads(pi.read_text())
    assert screen['source_sha256'][pi.relative_to(ROOT).as_posix()] == sha(pi)
    assert all(k['nominal_channel_clearance_mm'] == .15 for k in receipt['recipe']['Pi_full_grip_kits'])
    assert abs(receipt['recipe']['nominal_DG_channel_radius_mm']-receipt['recipe']['jacket_radius_mm']-.15) < 1e-6
    rows = {}; changed = []
    for name, r in old.items():
        if not r.get('blocks'):
            continue
        keep, no_longer_rejecting = [], []
        for witness in r['blocks']:
            gap = own_channel(index[name], witness['owner'])
            b = bound(witness['minimum_project_R_mm'], witness['axial_plane_distance_mm'],
                witness['signed_material_distance_at_axis_mm'], witness['jacket_radius_mm'], gap)
            value = dict(witness, **b)
            value['original_required_gap_mm'] = witness['required_gap_mm']
            if gap != witness['required_gap_mm']:
                value['basis'] = 'Named owning constructor groove; no foreign material waiver'
                changed.append(dict(end=name, owner=witness['owner'], old_gap_mm=witness['required_gap_mm'], own_gap_mm=gap))
            (keep if value['no_admissible_clearance_path'] else no_longer_rejecting).append(value)
        rows[name] = dict(status='NECESSARY_TERMINAL_BLOCK_RETAINED' if keep else 'OWN_GROOVE_NECESSITY_NONREJECTION_NOT_ROUTE_PASS',
            blocks=keep, own_contract_nonrejections=no_longer_rejecting)
    pins = {p.relative_to(ROOT).as_posix():sha(p) for p in (*files, sf, rf, pi, Path(__file__),
        ROOT/'tools/cad/feline_received_own_channels.py', ROOT/'tools/cad/feline_gallery_tail_support.py',
        ROOT/'tools/cad/feline_shared_pi_carrier.py', ROOT/'tools/cad/feline_s1_flexible_fans.py',
        ROOT/'tools/cad/plan_feline_remaining_inline_kits.py')}
    result = dict(status='NAMED_TERMINAL_OWNERSHIP_RECEIVED_FOREIGN_BLOCKS_OPEN', rows=rows,
        summary=dict(collections.Counter(r['status'] for r in rows.values())), changes=changed,
        new_BRep_queries=0, old_witnesses_retained=True, foreign_gap_mm=1.25,
        N01_complete=False, physical_pass=False, source_sha256=pins,
        worker_seconds=round(time.monotonic()-tick, 3))
    assert rows['W045/custom/end']['blocks'] and rows['W053/custom/end']['blocks']
    save_json(OUT/'n01-terminal-ownership-reconciliation.json', result)
    print(json.dumps(dict(summary=result['summary'], changed_pairs=len(changed), seconds=result['worker_seconds'])), flush=True)


if __name__ == '__main__': main()

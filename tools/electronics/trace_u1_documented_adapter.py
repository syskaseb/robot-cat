"""Trace ONE manufacturer-published adapter candidate, never the unknown575070.

Adafruit1208's TSSOP footprint is on the bottom/mirrored EAGLE side. Chip24
uses pads1..12 and17..28 of the28-pin footprint. JP identifiers here refer to
EAGLE, NOT printed chip pin numbers. No board selection or physical PASS.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'hardware/reference/adafruit1208-dbd7a192'
OUT = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/u1-documented-adapter.json'
BOARD = REF / '28-pin SOIC+TSSOP.brd'
COMMIT = 'dbd7a1928c2b668a9edf3d53277063eac4c3e938'
EXPECTED_SHA = '0e5c355106d9531b9e28526dc643164064becfd8aef09f2118e39866ad792f87'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive(board):
    packages = {p.attrib['name']: p for p in board.findall('./libraries/library/packages/package')}
    elements = {e.attrib['name']: e for e in board.findall('./elements/element')}
    assert elements['U$2'].attrib['package'] == 'TSSOP28-NW'
    assert elements['U$2'].attrib['rot'] == 'MR0', 'Mirrored bottom footprint must not be treated as top'

    def contact(element, pad):
        e = elements[element]
        p = next(p for p in packages[e.attrib['package']] if p.tag in ('smd', 'pad') and p.attrib['name'] == pad)
        x, y = float(p.attrib['x']), float(p.attrib['y'])
        rot = e.attrib.get('rot', 'R0')
        if 'M' in rot:
            x = -x
        angle = math.radians(float(rot.split('R')[-1]))
        px = float(e.attrib['x']) + x * math.cos(angle) - y * math.sin(angle)
        py = float(e.attrib['y']) + x * math.sin(angle) + y * math.cos(angle)
        layer = int(p.attrib['layer']) if p.tag == 'smd' else None
        if layer is not None and 'M' in rot:
            layer = {1: 16, 16: 1}[layer]
        return round(px, 6), round(py, 6), layer

    def key(x, y, layer):
        return round(float(x), 6), round(float(y), 6), layer

    links = {}
    for signal in board.findall('./signals/signal'):
        graph = {}

        def edge(a, b):
            graph.setdefault(a, set()).add(b)
            graph.setdefault(b, set()).add(a)

        for w in signal.findall('wire'):
            assert int(w.attrib['layer']) in (1, 16), 'Unrouted or unsupported copper'
            assert float(w.attrib['width']) > 0
            layer = int(w.attrib['layer'])
            edge(key(w.attrib['x1'], w.attrib['y1'], layer), key(w.attrib['x2'], w.attrib['y2'], layer))
        refs = signal.findall('contactref')
        assert len(refs) == 3, 'One TSSOP, one SOIC and one through-hole expected'
        nodes = []
        for r in refs:
            x, y, layer = contact(r.attrib['element'], r.attrib['pad'])
            if layer is None:
                edge((x, y, 1), (x, y, 16))
                layer = 1
            nodes.append((x, y, layer))
        for via in signal.findall('via'):
            assert via.attrib['extent'] == '1-16', 'Only through vias supported'
            x, y = float(via.attrib['x']), float(via.attrib['y'])
            edge(key(x, y, 1), key(x, y, 16))
        seen, todo = set(), [nodes[0]]
        while todo:
            node = todo.pop()
            if node in seen:
                continue
            seen.add(node)
            todo.extend(graph.get(node, ()))
        assert all(n in seen for n in nodes), (signal.attrib['name'], 'Not routed continuously at pad centres')
        smd = next(r for r in refs if r.attrib['element'] == 'U$2')
        header = next(r for r in refs if r.attrib['element'] in ('JP1', 'JP2'))
        pad = int(smd.attrib['pad'].removeprefix('P$'))
        assert pad not in links
        links[pad] = dict(header=header.attrib['element'], hole=int(header.attrib['pad']),
                          eagle_xy_mm=list(contact(header.attrib['element'], header.attrib['pad'])[:2]),
                          footprint_eagle_xy_mm=list(contact('U$2', smd.attrib['pad'])[:2]),
                          routed_net=signal.attrib['name'])
    assert sorted(links) == list(range(1, 29))
    rows = []
    roles = {int(r['physical_pin']): r['role'] for r in json.loads((ROOT / 'hardware/electronics/full-cat/connection-map-e4-r1/pinouts.json').read_text()) if r['device'] == 'U1'}
    for pin in range(1, 25):
        footprint = pin if pin <= 12 else pin + 4
        row = dict(chip_pin=pin, role=roles[pin], footprint_pad=footprint, **links[footprint])
        x, y = row['eagle_xy_mm']
        row['TSSOP_face_up_xy_mm'] = [round(17.78 - x, 6), y]
        rows.append(row)
    used = {(r['header'], r['hole']) for r in rows}
    assert len(used) == 24
    # Verify actual24 lead positions against0.65mm pitch after+0.65mm chip shift.
    for row in rows:
        p = row['chip_pin']
        y = 17.78 + .65 + (3.575 - .65 * (p - 1) if p <= 12 else -3.575 + .65 * (p - 13))
        assert abs(y - row['footprint_eagle_xy_mm'][1]) < 1e-6
    outline = [[float(w.attrib[k]) for k in ('x1', 'y1', 'x2', 'y2')] for w in board.findall('./plain/wire') if w.attrib['layer'] == '20']
    assert len(outline) == 8
    return dict(rows=rows, unpopulated_footprint_pads=[13, 14, 15, 16],
                unused_header_holes=[dict(header=h, hole=p) for h in ('JP1', 'JP2') for p in (13, 14)],
                board_outline_segments_mm=outline, board_size_xy_mm=[17.78, 35.56],
                chip_center_eagle_xy_mm=[8.89, 18.43], header_row_spacing_mm=15.24,
                header_pitch_mm=2.54, header_drill_mm=1.016, footprint_pitch_mm=.65,
                footprint_pad_size_mm=[2.4, .35], footprint_pad_row_spacing_mm=6.3,
                board_thickness_project_mm=1.6, board_thickness_supplier_verified=False,
                chip_PW_lead_span_mm=[6.2, 6.6], chip_PW_max_height_mm=1.2,
                TSSOP_side='BOTTOM in EAGLE; flip board about Y before assembling TSSOP face up',
                assembled_numbering='Chip1..12 on EAGLE JP2.1..12; chip13..24 on JP1.12..1. NOT silk1..24.',
                copper_check='28 continuous wire graphs at pad centres on layers1/16; not ERC/DRC or actual continuity')


def main():
    tick = time.monotonic()
    assert sha(BOARD) == EXPECTED_SHA
    result = derive(ET.parse(BOARD).find('./drawing/board'))
    result.update(status='DOCUMENTED_U1_ADAPTER_CANDIDATE_NOT_SELECTED', candidate_sku='Adafruit1208', chip_sku='SN74LVC8T245PW',
                  manufacturer_product='https://www.adafruit.com/product/1208', source_commit=COMMIT,
                  source_url=f'https://github.com/adafruit/Adafruit-SMT-Breakout-PCBs/blob/{COMMIT}/28-pin%20SOIC%2BTSSOP.brd',
                  chip_datasheet='https://www.ti.com/lit/ds/symlink/sn74lvc8t245.pdf', TI_drawing='PW0024A4220208/A02/2017, datasheetSCES584D May2026',
                  source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in (BOARD, Path(__file__), ROOT / 'hardware/electronics/full-cat/connection-map-e4-r1/pinouts.json')},
                  required_before_selection=['Replace ambiguous575070 BOM line explicitly; do not reuse its pin labels or holes',
                                             'Native nonconductive support for actual28-hole outline, accessible soldering and independent wire grips',
                                             'Rebind all24 actual pad endpoints and local passive connections; verify whole changed material/routing/assembly',
                                             'Update one current selection, hardware/stock and E1 package before awarding E1'],
                  delivery_gates=['Confirm genuine1208 board matches pinned artwork, thickness and solder clearances',
                                  'Unpowered continuity and no shorts after soldering24pin chip; check four unused holes/pads remain unconnected'],
                  selected=False, phase1_result_awarded=False, physical_pass=False,
                  checked_utc=datetime.now(timezone.utc).isoformat(), worker_seconds=round(time.monotonic()-tick, 4))
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'board_size_xy_mm', 'assembled_numbering', 'worker_seconds')}))


if __name__ == '__main__':
    main()

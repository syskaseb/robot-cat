"""Endpoint conservation and sourced process, without launching CAD."""
import json
from pathlib import Path
import runpy
import unittest

ROOT=Path(__file__).resolve().parents[2]


class CoupledLegEndpointsTests(unittest.TestCase):
    def test_exactly_twelve_continuous_looms_and_thirty_six_roles(self):
        mapped=json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-source-map-r1/interface.json').read_text(encoding='utf-8'))
        corridors=json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r3/intent.json').read_text(encoding='utf-8'))
        expected={r['loom']:r['electrical'] for r in mapped['looms']}
        wires=[]
        for row in corridors['routes']:
            self.assertEqual(row['wire_roles'],expected[row['loom']])
            self.assertEqual(set(row['wire_roles']),{'D','G','V'})
            self.assertEqual(row['wire_roles']['V']['body_end'],'F_'+row['loom']+'.out')
            wires.extend(s['wire'] for s in row['wire_roles'].values())
        self.assertEqual(len(expected),12)
        self.assertEqual(len(wires),36)
        self.assertEqual(len(set(wires)),36)

    def test_single_wire_process_uses_exact_k8_table(self):
        ns=runpy.run_path(str(ROOT/'tools/electronics/w5_leg_fanouts_r2.py'),run_name='definitions_only')
        out=ns['termination']('V','W020','F_FL1.out')
        facts=json.loads((ROOT/'hardware/reference/leg-cable-2026-10-04/TE-output-process.json').read_text(encoding='utf-8'))
        self.assertEqual(out['strip_mm'],facts['single_wire_strip_nominal_mm'])
        self.assertEqual(out['strip_tolerance_mm'],facts['single_wire_strip_tolerance_mm'])
        self.assertEqual(out['tool'],facts['tool'])
        self.assertFalse(facts['factory_core_section_verified'])
        self.assertEqual(facts['page_1_based'],9)


if __name__=='__main__':unittest.main()

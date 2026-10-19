import copy
import json
from pathlib import Path
import sys
import unittest
import FreeCAD
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from check_main_p0_placement import sha
from plan_feline_layout import OUT
from feline_compact_station_receive import adopt_receipt_pins


class ActualReceiptMigration(unittest.TestCase):
    def test_three_actual_receipts_keep_every_clear_and_negative_unit_unchanged(self):
        for name in ('n01-compact-station-static.json','n01-legacy-compact-static.json','n01-power-rise-static.json'):
            result=json.loads((OUT/name).read_text());units=copy.deepcopy(result['units'])
            pins=dict(result['source_sha256'])
            for n in ('tools/cad/feline_compact_station_fan.py','tools/cad/feline_compact_station_receive.py'):pins[n]=sha(ROOT/n)
            adopt_receipt_pins(result,pins)
            self.assertEqual(result['source_sha256'],pins)
            self.assertEqual(result['units'],units)
            self.assertFalse(result['N01_complete'])

    def test_changed_architecture_is_not_treated_as_additive_code(self):
        result=json.loads((OUT/'n01-legacy-compact-static.json').read_text());pins=dict(result['source_sha256'])
        pins['hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/n01-flat-station-architecture.json']='not-the-same-source'
        with self.assertRaises(AssertionError):adopt_receipt_pins(result,pins)


if __name__=='__main__':unittest.main()

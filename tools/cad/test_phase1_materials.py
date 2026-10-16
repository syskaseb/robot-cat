import unittest
from phase1_filament_budget import volume
from compose_phase1_materials import canonical_sku


class Materials(unittest.TestCase):
    def test_sku_not_split_by_colour_annotation(self):
        self.assertEqual(canonical_sku('HELU23302 red0.5mm2'),'HELU23302')
        self.assertEqual(canonical_sku('LAPP4126002S blue LiY0.25mm2'),'LAPP4126002S')

    def test_malformed_mesh_not_budgeted(self):
        with self.assertRaises(AssertionError):volume(b'solid empty\nendsolid')


if __name__=='__main__':unittest.main()

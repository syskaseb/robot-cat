import copy
import unittest
import xml.etree.ElementTree as ET
import trace_u1_documented_adapter as U


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.board = ET.parse(U.BOARD).find('./drawing/board')

    def test_actual_24_pin_mapping_and_four_unused_holes(self):
        result = U.derive(self.board)
        self.assertEqual([(r['header'], r['hole']) for r in result['rows']],
                         [('JP2', i) for i in range(1, 13)] + [('JP1', i) for i in range(12, 0, -1)])
        self.assertEqual(result['unpopulated_footprint_pads'], [13, 14, 15, 16])
        self.assertEqual(len(result['unused_header_holes']), 4)
        self.assertEqual(result['rows'][0]['role'], 'VCCA3V3')
        self.assertEqual(result['rows'][-1]['role'], 'VCCB5V')

    def test_bottom_face_coordinates_and_drill_spacing(self):
        result = U.derive(self.board)
        left, right = result['rows'][0], result['rows'][-1]
        self.assertEqual(left['TSSOP_face_up_xy_mm'], [1.27, 34.29])
        self.assertEqual(right['TSSOP_face_up_xy_mm'], [16.51, 34.29])
        self.assertAlmostEqual(right['TSSOP_face_up_xy_mm'][0] - left['TSSOP_face_up_xy_mm'][0], 15.24)

    def test_omitted_mirror_is_rejected(self):
        self.board.find("./elements/element[@name='U$2']").set('rot', 'R0')
        with self.assertRaises(AssertionError):
            U.derive(self.board)

    def test_broken_trace_is_rejected(self):
        signal = self.board.find('./signals/signal')
        trace = next(w for w in signal.findall('wire') if w.attrib['layer'] == '16')
        signal.remove(trace)
        with self.assertRaises(AssertionError):
            U.derive(self.board)

    def test_swapped_footprint_contact_is_rejected(self):
        signal = self.board.find('./signals/signal')
        signal.find("contactref[@element='U$2']").set('pad', 'P$27')
        with self.assertRaises(AssertionError):
            U.derive(self.board)


if __name__ == '__main__':
    unittest.main()

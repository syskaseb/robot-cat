"""Unclipping is explicit, temporary and cannot alter the historical loader."""
import unittest
from unittest.mock import patch
import numpy as np
import whole_current_body_material as W


class WholeSceneTest(unittest.TestCase):
    def test_full_window_during_load_then_restore_original_objects(self):
        low,high=W.M.S.LOW,W.M.S.HIGH
        def inspect():
            self.assertTrue(np.isneginf(W.M.S.LOW).all())
            self.assertTrue(np.isposinf(W.M.S.HIGH).all())
            return {'whole':'geometry'},{'wire':'curve'},{}
        with patch.object(W.M,'load',side_effect=inspect):
            targets,wires,pins=W.load()
        self.assertEqual(targets,{'whole':'geometry'})
        self.assertTrue(pins)
        self.assertIs(W.M.S.LOW,low);self.assertIs(W.M.S.HIGH,high)

    def test_exception_also_restores_body_scope(self):
        low,high=W.M.S.LOW,W.M.S.HIGH
        with patch.object(W.M,'load',side_effect=ValueError('test')):
            with self.assertRaises(ValueError):W.load()
        self.assertIs(W.M.S.LOW,low);self.assertIs(W.M.S.HIGH,high)


if __name__=='__main__':unittest.main()

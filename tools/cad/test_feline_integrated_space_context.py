import unittest
from feline_integrated_space_context import reusable_cell


class ReuseGuard(unittest.TestCase):
    def test_only_unchanged_fixed_sources_and_motion_are_reused(self):
        parent={'Static:fixed':{},'Static:moved':{},'Rest:leg':{},'ActualTorsoBoundary':{}}
        self.assertTrue(reusable_cell('Static:fixed',{'fixed'},parent))
        self.assertTrue(reusable_cell('Rest:leg',{'fixed'},parent))
        self.assertFalse(reusable_cell('Static:moved',{'fixed'},parent))
        self.assertFalse(reusable_cell('ActualTorsoBoundary',{'fixed'},parent))
        self.assertFalse(reusable_cell('Static:missing',{'missing'},parent))


if __name__=='__main__':unittest.main()

import unittest
from compose_feline_whole_wire_profiles import governing_radius


class WireProfiles(unittest.TestCase):
    def test_helu_not_thinned_to_bad_local_cap(self):
        self.assertAlmostEqual(governing_radius(1.55,[1.55,2.1],2.1),2.1)

    def test_whole_fixed_logic_recipe_replaces_generic_fallback(self):
        self.assertAlmostEqual(governing_radius(1.05,[.4,.4],.4),.4)

    def test_larger_actual_source_not_silently_erased(self):
        self.assertAlmostEqual(governing_radius(1.05,[1.55],.925),1.55)

    def test_unknown_keeps_conservative_budget(self):
        self.assertAlmostEqual(governing_radius(2.1,[1.55]),2.1)


if __name__=='__main__':unittest.main()

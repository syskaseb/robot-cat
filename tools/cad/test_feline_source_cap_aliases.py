import unittest
from receive_feline_source_links_exact import cap_owner


class NamedCaps(unittest.TestCase):
    def test_only_named_role_of_known_station_alias(self):
        end=dict(wire='W041',group='WAGO:P_FRONT_new',role='P_FRONT.2',prefix_geometry_owners=None)
        self.assertFalse(cap_owner('Station:P_FRONT:wire:P_FRONT.2',{},end))
        self.assertTrue(cap_owner('Station:P_FRONT:wire:P_FRONT.2',{},end,True))
        self.assertFalse(cap_owner('Station:P_FRONT:wire:P_FRONT.3',{},end,True))
        self.assertFalse(cap_owner('Station:P_REAR:wire:P_FRONT.2',{},end,True))

    def test_explicit_endpoint_not_inferred_cavity(self):
        end=dict(wire='XA04',group='WAGO:W3Ref_G_AUX_case',endpoint='G_AUX.2',physical_cavity=3)
        self.assertTrue(cap_owner('Station:G_AUX:wire:G_AUX.2',{},end,True))
        self.assertFalse(cap_owner('Station:G_AUX:wire:G_AUX.3',{},end,True))
        end['group']='WAGO:UNKNOWN'
        self.assertFalse(cap_owner('Station:G_AUX:wire:G_AUX.2',{},end,True))


if __name__=='__main__':unittest.main()

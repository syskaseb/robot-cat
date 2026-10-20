import unittest
from reconcile_feline_source_portal_contracts import own_channel


class OwnChannels(unittest.TestCase):
    def test_named_own_cuff_only(self):
        e=dict(id='W004/body/start',endpoint='FL1/fixed_boundary',group='NineWireCuffFL',wire='W004')
        self.assertEqual(own_channel(e,'BundleCuff:FL'),.2)
        self.assertEqual(own_channel(e,'BundleCuff:FR'),1.25)

    def test_owned_pwm_logic_channel_does_not_waive_pcb(self):
        e=dict(id='XS11/extra/start',endpoint='PCA.CH0.S',group='PWM9685',wire='XS11')
        self.assertEqual(own_channel(e,'ShelfPWM:XScomb:lower'),.15)
        self.assertEqual(own_channel(e,'Ref_Material_PWM1608NominalPCB_0_0'),1.25)
        self.assertEqual(own_channel(e,'ShelfPWM:XLcomb:lower'),1.25)


if __name__=='__main__':unittest.main()

import unittest
from feline_received_own_channels import own_channel


class ReceivedChannels(unittest.TestCase):
    def test_bus_cap_only_owns_its_own_tag(self):
        e=dict(id='W002/retained0/start',wire='W002',group='BUS',endpoint='BUS.D',prefix_geometry_owner='CurrentBUS:BUS.D')
        self.assertEqual(own_channel(e,'DGGrip:D:cap'),.15)
        self.assertEqual(own_channel(e,'SharedBUS:TailCarrier'),.15)
        self.assertEqual(own_channel(e,'DGGrip:G:cap'),1.25)
        self.assertEqual(own_channel(e,'PiBudget:AdapterBody'),1.25)

    def test_pi_requires_received_prefix_identity(self):
        e=dict(id='XL01/extra/start',wire='XL01',group='Pi4',endpoint='PI.H1',prefix_geometry_owner='PiGPIO:PI.H1')
        self.assertEqual(own_channel(e,'SharedPi:Carrier'),.15)
        self.assertEqual(own_channel(e,'Ref_Material_Pi4PCB'),1.25)
        e['prefix_geometry_owner']=''
        self.assertEqual(own_channel(e,'SharedPi:Carrier'),1.25)

    def test_fhac_own_custom_saddle_is_not_any_neighbor(self):
        e=dict(id='XB11/extra/end',wire='XB11',group='F_HY',endpoint='F_HY.in')
        self.assertEqual(own_channel(e,'ForeFHAC:in:custom:saddle'),.15)
        self.assertEqual(own_channel(e,'ForeFHAC:out:custom:saddle'),1.25)
        self.assertEqual(own_channel(e,'RearFHAC:F_HP'),1.25)

    def test_neighbor_bank_caps_keep_foreign_gap(self):
        e=dict(id='W031/body/end',wire='W031',group='BankRight',endpoint='FR1.GND')
        self.assertEqual(own_channel(e,'Station:Bank:W028/single/end:split_cap_exterior'),1.25)


if __name__ == '__main__': unittest.main()

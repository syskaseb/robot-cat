import copy,json,unittest
from reconcile_retained_body_guides import OUT,ROOT,SHA,data_aliases


class RetainedGuideTests(unittest.TestCase):
    def test_nineteen_existing_recipes_preserved_with_exact_station_ends(self):
        report=json.loads((OUT/'retained-body-guides-inventory.json').read_text())
        self.assertEqual(len(report['guides']),19)
        self.assertEqual(len(report['station_endpoint_checks']),11)
        self.assertFalse(report['stale_station_ends'])
        self.assertFalse(report['W5_complete'] or report['selected'] or report['physical_pass'])
        self.assertEqual(report['same_DATA_rail_aliases'],{'D_RL.1':'D_RL.5'})
        for name,digest in report['source_sha256'].items():self.assertEqual(SHA(ROOT/name),digest,name)

    def test_occupied_destination_and_cross_rail_aliases_rejected(self):
        data=json.loads((OUT/'data-bridges-plan.json').read_text())
        with self.assertRaises(AssertionError):data_aliases(data,{'x':{'roles':['D_RL.5']}})
        bad=copy.deepcopy(data);bad['physical_port_reassignment']['G_RL']=bad['physical_port_reassignment'].pop('D_RL')
        with self.assertRaises(AssertionError):data_aliases(bad,{})


if __name__=='__main__':unittest.main()

import json, unittest
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from compose_feline_output_boundaries import current
from compose_feline_integrated_boundaries import apply_updates


class PrefixAtlas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=json.loads((OUT/'n01-current-prefix-atlas.json').read_text())

    def test_owned_nine_outlets_not_thirty_six_invented_prefixes(self):
        self.assertEqual(len(self.a['updates']),9)
        self.assertEqual(self.a['summary']['KINEMATIC_CUFF_BOUNDARY_NO_OWNED_PREFIX_SOLID'],27)
        for row in self.a['updates'].values():
            self.assertEqual(row['source_prefix_length_mm'],9)
            self.assertTrue(row['moving_boundary_not_relocated'])
            self.assertTrue(row['selected_profile_enclosed'])
            self.assertTrue(row['complete_individual_termination_relief_NOT_inferred'])

    def test_electrical_ids_and_fixed_kinematic_boundaries_do_not_move(self):
        base, before,_=current(); after=apply_updates(before,self.a['updates'])
        self.assertEqual(len(base['portions']),123); self.assertEqual(len(after),246)
        for a,b in zip(before,after):
            for k in ('id','wire','portion_id','endpoint','group','point_mm','departure_axis'):
                self.assertEqual(a.get(k),b.get(k))

    def test_main_profile_conflicts_are_not_silently_thinned(self):
        rows=[r for r in self.a['rows'].values() if r['group']=='MAIN']
        self.assertEqual(len(rows),4)
        for r in rows:
            self.assertEqual(r['required_radius_mm'],1.55)
            self.assertEqual(r['status'],'ACTUAL_CAP_PROFILE_CONFLICT_NOT_NEW_GEOMETRY')

    def test_sources_are_pinned_and_no_n01_or_native_claim(self):
        for p,h in self.a['source_sha256'].items(): self.assertEqual(sha(ROOT/p),h,p)
        self.assertFalse(self.a['N01_complete']); self.assertFalse(self.a['native_changed'])
        self.assertFalse(self.a['physical_pass'])

    def test_working_composition_uses_received_outlets(self):
        from feline_adjudicated_boundaries import current as working
        _, rows, _=working(); index={e['id']:e for e in rows}
        for name, update in self.a['updates'].items():
            self.assertEqual(index[name]['routing_exit_mm'],update['routing_exit_mm'])


if __name__=='__main__': unittest.main()

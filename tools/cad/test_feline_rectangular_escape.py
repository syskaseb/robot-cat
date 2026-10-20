import unittest
import hashlib,json
from unittest.mock import patch
from feline_rectangular_escape import certificate
import receive_feline_current_face_escape as receiver


class RectangularEscapeTests(unittest.TestCase):
    def test_three_current_gtail_exits_cannot_keep_selected_foreign_margin(self):
        for R,r,m in ((12.4,.925,2.26),(15.,1.25,1.425),(12.6,1.05,1.575)):
            p=certificate(R,8.75,m,r)
            self.assertTrue(p['no_admissible_clearance_path'])
        # This is a margin hold, NOT a fabricated physical collision claim.
        self.assertFalse(certificate(12.4,8.75,2.26,.925)['unavoidable_jacket_material_intersection'])

    def test_a_small_face_cannot_be_promoted_to_an_infinite_wall(self):
        self.assertFalse(certificate(12.4,8.75,.01,.925)['no_admissible_clearance_path'])

    def test_bound_is_not_extrapolated_past_quarter_turn(self):
        with self.assertRaises(AssertionError):certificate(12.4,15,3.,.925)

    def test_receiver_gate_stops_more_JPWM_searches_at_three_unchanged_sources(self):
        rows=[dict(id=w,wire=w.split('/')[0],group='receiver') for w in
            ('XP02.source/extra/start','XP03.source/extra/start','XP02.module/extra/end','XP03.module/extra/end')]
        holds=[r['id'] for r in rows[1:]]
        view=dict(current_ends_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
            raw_receipt='proof.json',raw_receipt_sha256='kept',raw_rows='rows.gz',raw_rows_sha256='kept',
            active_clearance_holds={eid:[0] for eid in holds})
        with patch('pathlib.Path.read_text',return_value=json.dumps(view)),patch.object(receiver,'sha',return_value='kept'):
            with self.assertRaisesRegex(ValueError,'BEFORE any JPWM middle/pose'):
                receiver.require_receivers(rows,changed_source_ids=('XP02.source/extra/start',))
            receiver.require_receivers(rows,changed_source_ids=holds)


if __name__=='__main__':unittest.main()

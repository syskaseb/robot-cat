import copy
import unittest
from package_current_e1 import require_clear, current_routes, read, OUT


class CurrentE1Package(unittest.TestCase):
    def test_missing_clearance_evidence_rejected(self):
        with self.assertRaises(AssertionError):require_clear({'status':'unknown','errors':[]})

    def test_contact_and_kernel_error_rejected(self):
        for field in ('contacts','errors','reservation_resolutions','wire_contacts','material_resolutions','USB_fit_reservations'):
            p={'status':'candidate','contacts':[],'errors':[]};p[field]=['bad']
            with self.assertRaises(AssertionError):require_clear(p)

    def test_exact_current_thirteen_routes(self):
        rows=current_routes(read(OUT/'u1-common-wiring-plan.json'),read(OUT/'u1-service-departures-plan.json'))
        self.assertEqual(len(rows),13)
        self.assertEqual(sum(r['nominal_fit_blank_mm'] for r in rows if r['sku']=='LAPP4126002S'),474)
        self.assertEqual(sum(r['nominal_fit_blank_mm'] for r in rows if r['sku']=='Adafruit1446'),449)
        self.assertTrue(all(r['actual_cut_mm'] is None for r in rows))

    def test_old_short_departure_not_selected(self):
        p=read(OUT/'u1-service-departures-plan.json');p=copy.deepcopy(p)
        p['replacements']['XL09']['nominal_blank_mm']=118
        with self.assertRaises(AssertionError):current_routes(read(OUT/'u1-common-wiring-plan.json'),p)


if __name__=='__main__':unittest.main()

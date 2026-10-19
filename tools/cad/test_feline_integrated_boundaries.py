import unittest
from compose_feline_integrated_boundaries import apply_updates


class BoundaryOverlay(unittest.TestCase):
    def test_overlay_does_not_mutate_parent_or_internal_contact(self):
        parent=[dict(id='a',wire='W',endpoint='internal',point_mm=None)]
        result=apply_updates(parent,{'a':dict(jacket_routing_point_mm=[1,2,3])})
        self.assertIsNone(result[0]['point_mm']);self.assertNotIn('jacket_routing_point_mm',parent[0])

    def test_unknown_or_reidentified_endpoint_is_rejected(self):
        parent=[dict(id='a',wire='W')]
        with self.assertRaises(AssertionError):apply_updates(parent,{'missing':{}})
        with self.assertRaises(AssertionError):apply_updates(parent,{'a':dict(wire='new')})


if __name__=='__main__':unittest.main()

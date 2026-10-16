import unittest
from geometry_text_equivalence import compare
class Equivalent(unittest.TestCase):
 def test_same(self):self.assertTrue(compare(b'Vertex 2 0.123\n',b'Vertex 2 0.123\n')['equal'])
 def test_roundoff(self):self.assertTrue(compare('Vertex 2 0.12300000000000001','Vertex 2 0.123')['equal'])
 def test_real_shift(self):self.assertFalse(compare('Vertex 2 0.123','Vertex 2 0.124')['equal'])
 def test_topology(self):self.assertFalse(compare('Vertex 2 0.123','Vertex 3 0.123')['equal'])
 def test_structure(self):self.assertFalse(compare('Vertex 2 0.123','Edge 2 0.123')['equal'])
 def test_checked(self):self.assertTrue(compare('TShapes 1\nVe\n0101000\n*\n','TShapes 1\nVe\n0111000\n*\n')['equal'])
 def test_other_flag(self):self.assertFalse(compare('TShapes 1\nVe\n0101000\n*\n','TShapes 1\nVe\n0101100\n*\n')['equal'])
 def test_not_shape_flags(self):self.assertFalse(compare('0101000\n*\n','0111000\n*\n')['equal'])
if __name__=='__main__':unittest.main()

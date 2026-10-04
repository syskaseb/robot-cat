"""Cheap analytic checks for the changed mount, before CAD execution."""
import ast
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name('w5_xa05_native_r2.py')

def boxes():
    result={}
    for n in ast.walk(ast.parse(SOURCE.read_text(encoding='utf-8'))):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='box':
            if isinstance(n.args[0],ast.Constant):
                result[n.args[0].value]=ast.literal_eval(n.args[1])
    return result

class XA05MountTests(unittest.TestCase):
    def test_complete_washer_bearing(self):
        foot=boxes()['Foot']
        for y in (36,44):
            self.assertGreaterEqual(131-3.5,foot[0])
            self.assertLessEqual(131+3.5,foot[3])
            self.assertGreaterEqual(y-3.5,foot[1])
            self.assertLessEqual(y+3.5,foot[4])
        self.assertEqual(foot[5]-foot[2],3)

    def test_driver_column_clear_of_upper_stem_and_bridge(self):
        for key in ('Stem','Bridge','Rail','Seat'):
            self.assertGreaterEqual(boxes()[key][0]-(131+3.5),.6-1e-8)

    def test_stem_joins_foot_and_bridge_with_real_width(self):
        b=boxes();stem=b['Stem'];foot=b['Foot'];bridge=b['Bridge']
        self.assertGreater(stem[3]-stem[0],2.5)
        self.assertLess(stem[2],foot[5])
        self.assertLess(stem[0],foot[3])
        self.assertLess(bridge[2],stem[5])
        self.assertLess(bridge[0],stem[3])

if __name__=='__main__':unittest.main()

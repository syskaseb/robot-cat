import unittest
import FreeCAD as A
import Part
from test_current_bank_datums import BankDatumTests
from underdeck_bank_layout import layout


class UnderdeckTests(unittest.TestCase):
    def test_rigid_parts_terminal_binding_and_affected_scope(self):
        scene=BankDatumTests().scene();rows=[];ends=[]
        for leg in ('FL','FR','RL','RR'):
            side='L' if leg.endswith('L') else 'R';sign=1 if side=='L' else -1
            for i in (1,2,3):
                j=i+(3 if leg.startswith('R') else 0);x=j*30;y=sign*62
                # Synthetic TE boxes include their declared wire mouths.
                scene[f'F_{side}{j}_CP2_IN/0/0']=Part.makeBox(10,10,24,A.Vector(x-5,y+sign*7-5,73))
                scene[f'F_{side}{j}_CP2_OUT/0/0']=Part.makeBox(10,6,22,A.Vector(x-5,y-sign*7-3,75))
                rows.append(dict(core='V',loom=leg+str(i),wire='V'+leg+str(i),
                    receiver_point_mm=[x,y-sign*7,75.402],receiver_outward_axis=[-1,0,0],
                    bundle_root_world_mm=[0,0,0],capacity_before_terminal_mm=900,terminal_allowance_project_mm=11))
                ends.append(dict(role='F_'+leg+str(i)+'.in',wire='P'+leg+str(i),point_world_mm=[x,y+sign*7,73.37]))
        ends.append(dict(role='F_PI.in',wire='W043',point_world_mm=[0,0,0]))
        q=layout(scene,dict(rows=rows),dict(ends=ends))
        self.assertEqual(len(q['parts']),48);self.assertEqual(len(q['changed_wire_ids']),24)
        self.assertEqual(len(q['panel'].Solids),4);self.assertEqual(len(q['sweeps']),12)
        for r in q['records']:
            self.assertAlmostEqual(abs(r['input_point_mm'][1]),12.37)
            self.assertAlmostEqual(abs(r['output_point_mm'][1]),14.402)
            self.assertAlmostEqual(r['new_flange_world_mm'][2],47)
        self.assertFalse(q['selected']);self.assertFalse(q['W5_complete'])


if __name__=='__main__':unittest.main()

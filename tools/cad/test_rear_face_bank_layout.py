import unittest
from test_current_bank_datums import BankDatumTests
from rear_face_bank_layout import layout,COLUMNS


class RearBankTests(unittest.TestCase):
    def test_all48_parts_rigidly_transform_and_no_factory_capacity_faked(self):
        targets=BankDatumTests().scene();rows=[];ends=[]
        for leg in ('FL','FR','RL','RR'):
            for i in (1,2,3):
                side='L' if leg.endswith('L') else 'R';j=i+(3 if leg.startswith('R') else 0)
                old_x=j*30;old_y=62 if side=='L' else -62
                rows.append(dict(core='V',loom=leg+str(i),wire='V'+leg+str(i),
                    receiver_point_mm=[old_x,old_y,75.402],receiver_outward_axis=[-1,0,0],
                    bundle_root_world_mm=[0,0,0],capacity_before_terminal_mm=900,terminal_allowance_project_mm=11))
                ends.append(dict(role='F_'+leg+str(i)+'.in',wire='P'+leg+str(i),point_world_mm=[old_x,old_y,73.37]))
        ends.append(dict(role='F_PI.in',wire='W043',point_world_mm=[0,0,0]))
        q=layout(targets,dict(rows=rows),dict(ends=ends))
        self.assertEqual(len(q['parts']),48);self.assertEqual(len(q['records']),12)
        self.assertEqual(len(q['changed_wire_ids']),24)
        self.assertEqual(len(q['retired_targets']),48)
        for r in q['records']:
            self.assertAlmostEqual(r['input_point_mm'][0],117.37)
            self.assertAlmostEqual(r['output_point_mm'][0],119.402)
            self.assertEqual(r['new_flange_world_mm'][1],COLUMNS[r['loom'][:2]])
        boxes=list(q['parts'].items())
        for i,(name,a) in enumerate(boxes):
            for other,b in boxes[i+1:]:
                if name.split('/')[1]==other.split('/')[1]:continue
                if a.BoundBox.intersect(b.BoundBox):self.assertLess(a.common(b).Volume,1e-6,(name,other))


if __name__=='__main__':unittest.main()

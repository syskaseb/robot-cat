"""Cheap construction gates before receiving any joint-source hypothesis."""
import math,unittest
import FreeCAD as A
import Part
from plan_feline_battery_f0_joint import path,pose
from plan_feline_n01_shared import pipe


class BatteryF0Geometry(unittest.TestCase):
    def test_selected_fork_preserves_other_source_actors_and_full_pair_gate(self):
        from plan_feline_battery_f0_fork_exit import construction
        actors,recipes,pairs,names,datums,extra=construction({},{})
        self.assertEqual(len(pairs),21)
        self.assertTrue(all(v['ok'] for v in pairs.values()))
        self.assertEqual(extra['changed_actor_names'],['W076_custom_prefix'])
        self.assertEqual(recipes['W075_factory']['length_mm'],20)
        self.assertAlmostEqual(recipes['W076_factory']['length_mm'],57.71746251349628,places=6)
        self.assertEqual(recipes['W076_custom_prefix']['R_mm'],25.2)
        self.assertTrue(extra['full_R25_2_and9mm_retained'])

    def test_transverse_whole_kit21_pairs_and_both_factory_lengths(self):
        from plan_feline_battery_f0_transverse import construction
        from receive_feline_existing_lower_caps import current
        _,rows,_=current();ends={r['id']:r for r in rows}
        f=Part.makeBox(51,20.25,22,A.Vector(-25.5,-10.125,-11))
        f.Placement=A.Placement(A.Vector(68,0,-13.75),A.Rotation(A.Vector(0,0,1),45))
        x=Part.makeBox(23.9,9.2,16.4,A.Vector(131.049996948242,-4.599996948242,-43.2))
        p=Part.makeBox(9,19,14,A.Vector(138.500000762939,-44.5,35))
        actors,recipes,pairs,names,datums=construction({
            'Ref_Material_F0_CP2_0_0':f,'Ref_Material_XT60_CP2_0_0':x,
            'Ref_Material_PostF0Splice_CP2_0_0':p},ends)
        self.assertEqual(len(pairs),21)
        self.assertTrue(all(r['ok'] for r in pairs.values()))
        for n in ('W075_factory','W076_factory'):
            self.assertGreaterEqual(recipes[n]['minimum_R_mm'],12.4)
            self.assertGreater(89.5-recipes[n]['length_mm']-21,48)
        # Whole cross-section/lid direction, not unconstrained shortest rotation.
        b=actors[names['F0']].BoundBox
        self.assertAlmostEqual(b.XLength,22,places=6)
        self.assertAlmostEqual(b.YLength,51,places=6)
        self.assertAlmostEqual(b.ZLength,20.25,places=6)

    def test_positive_factory_whole_path_and_profile(self):
        r=path([150.6,0,-38.5],[1,0,0],[('line',3),('turn',[0,0,1]),('line',9.6)],12.4)
        self.assertLess((A.Vector(*r['end'])-A.Vector(166,0,-16.5)).Length,1e-8)
        self.assertEqual(r['end_tangent'],[0.,0.,1.])
        s=pipe(r['parts'],1.55)
        self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
        self.assertAlmostEqual(s.Volume,math.pi*1.55**2*r['length_mm'],places=4)
        self.assertGreater(89.5-r['length_mm']-8.73-10,0)

    def test_rejected_vertical_polarities_are_not_clear(self):
        a=path([150.6,0,-38.5],[1,0,0],[('line',3),('turn',[0,0,1]),('line',9.6)],12.4)
        b=path([150.6,0,-31.5],[1,0,0],[('line',3),('turn',[0,1,0]),('turn',[0,0,1]),('line',9)],12.4)
        aa,bb=pipe(a['parts'],1.55),pipe(b['parts'],1.55)
        # Preserve the actual rejected0.911mm gap; it must never become PASS.
        self.assertLess(aa.distToShape(bb)[0],1.25)
        self.assertAlmostEqual(aa.distToShape(bb)[0],.91145612327,places=6)
        self.assertLess(aa.common(bb).Volume,1e-6)

    def test_pose_preserves_one_world_transform(self):
        s=Part.makeBox(51,20.25,22,A.Vector(-25.5,-10.125,-11))
        s.Placement=A.Placement(A.Vector(68,0,-13.75),A.Rotation(A.Vector(0,0,1),45))
        out,tf=pose(s,[68,0,-13.75],A.Rotation(A.Vector(0,1,0),-90)*A.Rotation(A.Vector(0,0,1),-45),[166,0,9])
        self.assertLess((out.CenterOfMass-A.Vector(166,0,9)).Length,1e-6)
        b=out.BoundBox
        self.assertAlmostEqual(b.XLength,22,places=6)
        self.assertAlmostEqual(b.YLength,20.25,places=6)
        self.assertAlmostEqual(b.ZLength,51,places=6)
        self.assertAlmostEqual(out.Volume,s.Volume,places=5)


if __name__=='__main__':unittest.main()

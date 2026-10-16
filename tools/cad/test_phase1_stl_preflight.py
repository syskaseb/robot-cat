import struct,unittest
from phase1_stl_preflight import inspect,fit


class STLTests(unittest.TestCase):
    def test_tetrahedron_and_missing_face(self):
        a,b,c,d=(0.,0.,0.),(1.,0.,0.),(0.,1.,0.),(0.,0.,1.)
        faces=[(a,b,c),(a,d,b),(a,c,d),(b,d,c)]
        def raw(fs):return b' '*80+struct.pack('<I',len(fs))+b''.join(struct.pack('<12fH',0,0,0,*sum((list(p) for p in t),[]),0) for t in fs)
        q=inspect(raw(faces));self.assertTrue(q['closed']);self.assertEqual(q['components'],1)
        self.assertFalse(inspect(raw(faces[:-1]))['closed'])
    def test_brim_is_horizontal_not_free(self):
        self.assertTrue(fit([246,246,256]));self.assertFalse(fit([246.01,100,10]))


if __name__=='__main__':unittest.main()

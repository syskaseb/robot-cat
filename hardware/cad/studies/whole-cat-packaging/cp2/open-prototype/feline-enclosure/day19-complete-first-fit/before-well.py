from common import *
p=P/'whole-cat19I.20261119-220455.FCBak';s=Saved(p)
assert sha(p)=='a774efd593373891c4cedbef0debf3a8c9d9271c8f607c37c2ddfc2c0b2a6c32'
(P/'before-well.tmp.brep').write_bytes(s.zip.read(s.members['H19_FrontFrame']))

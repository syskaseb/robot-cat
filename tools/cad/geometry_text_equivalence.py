"""Strict serialized topology/parameter comparison with bounded float noise.

Integer topology references/counts and nonnumeric structure must be identical.
Only floating literals may differ, at1e-12 absolute/relative. This is not mesh
similarity, bounding-box equality or permission to accept a geometric edit.
"""
import re,math
NUMBER=re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?')
FLAGS=re.compile(r'(?m)^([01]{2})[01]([01]{4})(?=\r?\n(?:[+-]\d+ \d+|\*))')

def checked_normalized(text):
 # OCCT TopTools_ShapeSet::Write/Read (V7_8_1) stores Checked at bit2.
 # Restrict normalization to the TShapes table, exact7bit flag lines followed
 # by an oriented subshape reference or null terminator. No geometry/IDs waived.
 parts=re.split(r'(?m)(^TShapes \d+\r?\n)',text,maxsplit=1)
 if len(parts)!=3:return text
 parts[2]=FLAGS.sub(lambda m:m[1]+'0'+m[2],parts[2])
 return ''.join(parts)
def compare(a,b,tolerance=1e-12):
 if a==b:return dict(equal=True,max_float_delta=0,changed_float_literals=0)
 if isinstance(a,bytes):a=a.decode('utf-8');b=b.decode('utf-8')
 ca,cb=checked_normalized(a),checked_normalized(b)
 flag_changes=sum(x!=y for x,y in zip(a.splitlines(),b.splitlines()) if re.fullmatch('[01]{7}',x) and re.fullmatch('[01]{7}',y) and x[:2]+x[3:]==y[:2]+y[3:])
 a,b=ca,cb
 aa=NUMBER.split(a);bb=NUMBER.split(b)
 if aa!=bb:return dict(equal=False,reason='Nonnumeric structure differs')
 x=NUMBER.findall(a);y=NUMBER.findall(b)
 if len(x)!=len(y):return dict(equal=False,reason='Numeric field count differs')
 maxdelta=0;changed=0
 for i,(u,v) in enumerate(zip(x,y)):
  if u==v:continue
  if not any(c in u+v for c in '.eE'):
   if int(u)!=int(v):return dict(equal=False,reason='Integer topology/count differs',field=i)
  else:
   f,g=float(u),float(v)
   if not math.isfinite(f) or not math.isfinite(g) or not math.isclose(f,g,rel_tol=tolerance,abs_tol=tolerance):return dict(equal=False,reason='Float parameter differs',field=i,before=u,after=v)
   maxdelta=max(maxdelta,abs(f-g));changed+=1
 return dict(equal=True,max_float_delta=maxdelta,changed_float_literals=changed,checked_flag_changes=flag_changes)
